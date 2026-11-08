"""Validate and partition explicit reviewed policy-scope decisions.

The record hash identifies the historical reviewed observation; it is not a lock
on the current row. Identity guard fields, in contrast, must still match exactly.
An absent registry means no decisions, not that unreviewed rows are included.
"""
from datetime import datetime
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from uuid import UUID

_FIELDS = frozenset({'schema_version', 'decision_id', 'policy_action_id', 'decision',
                     'analytical_scope', 'record_identity_guard', 'reviewed_record_sha256',
                     'reviewer', 'reviewed_at', 'rationale', 'source_evidence', 'supersedes'})
_GUARD = frozenset({'state_abbrev', 'bill', 'policy_instrument_type'})
_EVIDENCE = frozenset({'url', 'body_sha256', 'locator'})
_HASH = re.compile(r'[0-9a-f]{64}\Z')
_TIMESTAMP = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\Z')
INFRASTRUCTURE_SCOPE = 'data-center infrastructure policy analytical census'
OUTCOMES = ('reviewed_include', 'reviewed_exclude', 'reviewed_unresolved', 'unreviewed')
METADATA_FIELDS = ('scope_review_status', 'scope_decision_id')


def _object(value, fields, name):
    if not isinstance(value, dict) or value.keys() != fields:
        raise ValueError(f'{name} must contain exactly {sorted(fields)}')


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a nonempty string')


def _uuid(value, name):
    try:
        if not isinstance(value, str) or str(UUID(value)) != value:
            raise ValueError
    except (ValueError, AttributeError):
        raise ValueError(f'{name} must be a canonical UUID') from None


def _hash(value, name):
    if not isinstance(value, str) or not _HASH.fullmatch(value):
        raise ValueError(f'{name} must be a lowercase SHA-256 digest')


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON field {key!r}')
        result[key] = value
    return result


def load_reviews(path, rows):
    """Return the latest explicit decision for each ID; reject ambiguous history."""
    try:
        raw = Path(path).read_bytes()
    except FileNotFoundError:
        return {}
    if raw and not raw.endswith(b'\n'):
        raise ValueError('scope registry must end with a newline')

    by_id = {}
    for row in rows:
        ident = row.get('policy_action_id')
        by_id.setdefault(ident, []).append(row)
    active, events = {}, {}
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line, object_pairs_hook=_pairs,
                               parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f'invalid JSON constant {x}')))
            _object(event, _FIELDS, 'review')
            if event['schema_version'] != '1.0.0':
                raise ValueError('unsupported schema_version')
            _uuid(event['decision_id'], 'decision_id')
            if event['decision_id'] in events:
                raise ValueError('duplicate decision_id')
            ident = event['policy_action_id']
            _text(ident, 'policy_action_id')
            if len(by_id.get(ident, [])) != 1:
                raise ValueError(f'policy_action_id {ident!r} must identify exactly one dataset row')
            if event['decision'] not in ('include', 'exclude', 'unresolved'):
                raise ValueError('invalid decision')
            for field in ('analytical_scope', 'reviewer', 'rationale'):
                _text(event[field], field)
            guard = event['record_identity_guard']
            _object(guard, _GUARD, 'record_identity_guard')
            for field in _GUARD:
                _text(guard[field], f'record_identity_guard.{field}')
            _hash(event['reviewed_record_sha256'], 'reviewed_record_sha256')
            stamp = event['reviewed_at']
            if not isinstance(stamp, str) or not _TIMESTAMP.fullmatch(stamp):
                raise ValueError('reviewed_at must be a timezone-aware ISO timestamp')
            try:
                datetime.fromisoformat(stamp.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('invalid reviewed_at timestamp') from None
            evidence = event['source_evidence']
            if not isinstance(evidence, list) or not evidence:
                raise ValueError('source_evidence must be a nonempty list')
            for source in evidence:
                _object(source, _EVIDENCE, 'source_evidence entry')
                _text(source['url'], 'source_evidence.url')
                url = urlsplit(source['url'])
                if url.scheme not in ('http', 'https') or not url.netloc or any(c.isspace() for c in source['url']):
                    raise ValueError('source_evidence.url must be an absolute HTTP(S) URL')
                _hash(source['body_sha256'], 'source_evidence.body_sha256')
                _text(source['locator'], 'source_evidence.locator')
            prior = event['supersedes']
            if prior is not None:
                _uuid(prior, 'supersedes')
                if prior not in events:
                    raise ValueError('unknown or forward supersedes')
                if events[prior]['policy_action_id'] != ident:
                    raise ValueError('cross-identity supersession')
            previous = active.get(ident)
            if previous is None:
                if prior is not None:
                    raise ValueError('unexpected supersedes')
            else:
                if prior != previous['decision_id']:
                    raise ValueError('unlinked decision or branch in decision history')
                if event['analytical_scope'] != previous['analytical_scope']:
                    raise ValueError('analytical_scope differs from prior decision')
            events[event['decision_id']] = event
            active[ident] = event
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError(f'scope registry line {number}: {exc}') from exc
    # Superseded guards describe historical observations. A new reviewed decision
    # can account for a corrected title or legal form without rewriting history.
    for ident, event in active.items():
        for field in _GUARD:
            if event['record_identity_guard'][field] != by_id[ident][0].get(field):
                raise ValueError(f'record_identity_guard mismatch for {ident}: {field}')
    return active


def partition_reviews(rows, registry_path, *, scope):
    """Partition ordered observations; only reviewed_include is analytical inclusion.

    Return lists of (original row, active decision or None) in raw order. Every
    ID is validated even when the registry is absent. No input is modified.
    """
    _text(scope, 'scope')
    rows = list(rows)
    seen = set()
    for row in rows:
        ident = row.get('policy_action_id')
        _text(ident, 'policy_action_id')
        if ident in seen:
            raise ValueError(f'duplicate policy_action_id {ident!r}')
        seen.add(ident)
        collision = set(row) & set(METADATA_FIELDS)
        if collision:
            raise ValueError(f'scope metadata collision: {sorted(collision)}')
    decisions = load_reviews(registry_path, rows)
    for event in decisions.values():
        if event['analytical_scope'] != scope:
            raise ValueError(f"incompatible analytical_scope for {event['policy_action_id']}: {event['analytical_scope']!r}")
    result = {outcome: [] for outcome in OUTCOMES}
    for row in rows:
        event = decisions.get(row['policy_action_id'])
        outcome = 'reviewed_' + event['decision'] if event else 'unreviewed'
        result[outcome].append((row, event))
    return result
