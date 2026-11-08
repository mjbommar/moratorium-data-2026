#!/usr/bin/env python3
"""Offline prospective rule-unit accounting. See the private implementation report.

Input is an explicitly normalized v1 bundle, not a transport journal. No threshold
scoring is implemented: request/response capture integration is not yet verified.
"""
import argparse
import base64
import hashlib
import json
from collections import Counter
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_keys(obj, keys, label):
    require(isinstance(obj, dict) and set(obj) == set(keys), f'invalid {label} fields')


def raw_bytes(value, expected, label):
    require(isinstance(value, str) and isinstance(expected, str), f'invalid {label}')
    try:
        data = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError(f'invalid {label} base64') from exc
    require(hashlib.sha256(data).hexdigest() == expected, f'{label} hash mismatch')
    return data


def audit(bundle):
    exact_keys(bundle, ('schema_version', 'state', 'state_sha256', 'source_body_b64', 'packet', 'captures', 'reviews', 'protocol'), 'bundle')
    require(bundle['schema_version'] == 'rule-unit-trial-bundle-1', 'unsupported bundle version')
    state, packet = bundle['state'], bundle['packet']
    exact_keys(state, ('context', 'context_sha256', 'attempts', 'successes', 'budget_stop'), 'state')
    require(digest(state) == bundle['state_sha256'], 'state hash mismatch')
    ctx = state['context']
    require(digest(ctx) == state['context_sha256'], 'context hash mismatch')
    doc, plan = ctx['document'], ctx['plan']
    raw_bytes(bundle['source_body_b64'], doc['body_sha256'], 'source body')
    text = doc['text']
    require(hashlib.sha256(text.encode()).hexdigest() == doc['text_sha256'] == plan['source_text_sha256'], 'source hash mismatch')
    units = plan['units']
    ids = [u['unit_id'] for u in units]
    require(ids and len(ids) == len(set(ids)), 'duplicate or empty plan')
    require(isinstance(state['attempts'], list) and isinstance(state['successes'], dict), 'invalid ledger')
    require(set(state['successes']) <= set(ids), 'success outside plan')
    attempts = state['attempts']
    per_unit = Counter()
    for a in attempts:
        uid = a['unit_id']
        require(uid in ids and a['status'] in ('reserved', 'failed', 'succeeded'), 'invalid attempt')
        require(per_unit[uid] == 0 or not any(x['unit_id'] == uid and x['status'] == 'succeeded' for x in attempts[:sum(per_unit.values())]), 'attempt after success')
        # The extractor's logical request identity; this is not the outgoing HTTP request.
        unit = units[ids.index(uid)]
        dc = {'reviewed_source_role': doc.get('reviewed_source_role', 'unknown')}
        if 'title' in doc:
            dc['title'] = doc['title']
        prompt = ('Document context (JSON):\n' + json.dumps(dc, ensure_ascii=False, sort_keys=True)
                  + '\nFull source:\n' + text + '\nLocal slot (JSON):\n'
                  + json.dumps(unit, ensure_ascii=False, sort_keys=True))
        logical = dict(role=ctx['role'], stage='rule_unit', prompt=prompt, system=ctx['system'], schema=ctx['schema'], settings=ctx['settings'])
        require(a['request_sha256'] == digest(logical), 'logical request hash mismatch')
        per_unit[uid] += 1
    succeeded = [a['unit_id'] for a in attempts if a['status'] == 'succeeded']
    require(len(succeeded) == len(set(succeeded)) and set(succeeded) == set(state['successes']), 'success population mismatch')
    require(sum(a['status'] == 'reserved' for a in attempts) <= 1 and not any(a['status'] == 'reserved' for a in attempts[:-1]), 'invalid interruption ordering')
    require(isinstance(packet, dict) and packet.get('context_sha256') == state['context_sha256'] and packet.get('source_text_sha256') == doc['text_sha256'] and packet.get('source_body_sha256') == doc['body_sha256'] and packet.get('plan_sha256') == digest(plan), 'packet identity mismatch')
    outputs = packet.get('units')
    require(isinstance(outputs, list), 'packet units missing')
    packet_ids = [p['unit_id'] for p in outputs]
    require(len(packet_ids) == len(set(packet_ids)) and set(packet_ids) == set(ids), 'incomplete or duplicate packet population')
    by_id = {p['unit_id']: p for p in outputs}
    for uid, entry in state['successes'].items():
        require(digest(entry['output']) == entry['output_sha256'], 'output hash mismatch')
        matching = [a for a in attempts if a['unit_id'] == uid and a['status'] == 'succeeded']
        require(entry['request_sha256'] == matching[0]['request_sha256'], 'success request mismatch')
        p = by_id[uid]
        require(p.get('original_output') == entry['output'] and p.get('output_sha256') == entry['output_sha256'] and p.get('request_sha256') == entry['request_sha256'], 'packet output identity mismatch')
        raw = entry['output']
        if isinstance(raw, dict) and raw.get('clause') is not None:
            require(p.get('clause') == raw['clause'], 'packet clause mismatch')
    require(isinstance(bundle['captures'], list) and isinstance(bundle['reviews'], list), 'invalid evidence lists')
    captures = {}
    for c in bundle['captures']:
        exact_keys(c, ('schema_version', 'attempt_index', 'unit_id', 'request_b64', 'request_sha256', 'response_b64', 'response_sha256'), 'capture')
        require(c['schema_version'] == 'normalized-http-capture-1', 'unsupported capture version')
        i = c['attempt_index']
        require(type(i) is int and 0 <= i < len(attempts) and i not in captures and c['unit_id'] == attempts[i]['unit_id'], 'duplicate or mismatched capture')
        raw_bytes(c['request_b64'], c['request_sha256'], 'request capture')
        if c['response_b64'] is None or c['response_sha256'] is None:
            require(c['response_b64'] is None and c['response_sha256'] is None, 'partial response capture')
        else:
            raw_bytes(c['response_b64'], c['response_sha256'], 'response capture')
        captures[i] = c
    blockers = []
    def block(message):
        if message not in blockers:
            blockers.append(message)
    if len(captures) != len(attempts): block('missing raw request capture for one or more attempts')
    if any(i not in captures or captures[i]['response_b64'] is None for i, a in enumerate(attempts) if a['status'] != 'reserved'):
        block('missing raw response capture for one or more terminal attempts')
    # The normalized bundle does not claim an implemented mapping to the changing journal.
    block('raw capture journal integration and raw-to-boundary response mapping not verified')
    if any(u not in per_unit for u in ids): block('planned units not attempted')
    if any(a['status'] == 'reserved' for a in attempts): block('interrupted reservation')
    if any(u not in state['successes'] for u in ids): block('planned units without successful boundary output')
    if any(a['status'] == 'failed' for a in attempts): block('failed attempts require reconciliation')
    counts_for_unknown_attempts = sum(a['status'] != 'succeeded' for a in attempts)
    if counts_for_unknown_attempts:
        block('failed or interrupted attempts have unknown output cardinality')
    counts = Counter({key: 0 for key in ('generated_clauses_known', 'unscorable_outputs', 'unknown_cardinality_outputs', 'local_candidate', 'local_unresolved', 'local_missing')})
    targets = {}
    for uid in ids:
        p = by_id[uid]
        counts['local_' + str(p.get('outcome', 'missing'))] += 1
        if uid not in state['successes']:
            continue
        entry = state['successes'][uid]
        raw = entry['output']
        flags = p.get('review_flags', [])
        require(isinstance(flags, list), 'invalid review flags')
        unscorable = (not isinstance(raw, dict) or set(raw) != {'unit_id', 'outcome', 'clause', 'supporting_quotes', 'unresolved_reason'} or 'native_response_unscorable' in flags or raw.get('unit_id') != uid or raw.get('outcome') not in ('candidate', 'unresolved') or not isinstance(raw.get('supporting_quotes'), list) or (raw.get('outcome') == 'candidate' and not isinstance(raw.get('clause'), dict)) or (raw.get('outcome') == 'unresolved' and (raw.get('clause') is not None or not isinstance(raw.get('unresolved_reason'), str))))
        if unscorable:
            counts['unscorable_outputs'] += 1
            block('unscorable boundary outputs')
        # On malformed objects a present top-level clause is still known evidence;
        # its absence does not establish a zero cardinality.
        if isinstance(raw, dict) and raw.get('clause') is not None:
            counts['generated_clauses_known'] += 1
            targets[uid] = entry
        if unscorable:
            counts['unknown_cardinality_outputs'] += 1
        if flags:
            block('local source, schema, role or representation flags')
        if isinstance(raw, dict) and isinstance(raw.get('clause'), dict):
            if doc.get('reviewed_source_role') == 'proposed' and raw['clause'].get('assertion_context') == 'enacted_text':
                block('reviewed source role conflict')
    review_map = {}
    for r in bundle['reviews']:
        exact_keys(r, ('unit_id', 'reviewer_id', 'source_text_sha256', 'source_body_sha256', 'context_sha256', 'request_sha256', 'output_sha256', 'raw_request_sha256', 'raw_response_sha256', 'judgment', 'dimensions', 'evidence'), 'review')
        uid = r['unit_id']
        require(uid in targets, 'review target has no generated clause')
        entry = targets[uid]
        require((r['source_text_sha256'], r['source_body_sha256'], r['context_sha256'], r['request_sha256'], r['output_sha256']) == (doc['text_sha256'], doc['body_sha256'], state['context_sha256'], entry['request_sha256'], entry['output_sha256']), 'review identity mismatch')
        attempt_index = next(i for i, a in enumerate(attempts) if a['unit_id'] == uid and a['status'] == 'succeeded')
        capture = captures.get(attempt_index)
        require(capture is not None and capture['response_sha256'] is not None and r['raw_request_sha256'] == capture['request_sha256'] and r['raw_response_sha256'] == capture['response_sha256'], 'review raw capture identity mismatch')
        require(isinstance(r['reviewer_id'], str) and r['reviewer_id'].strip(), 'reviewer required')
        require(r['judgment'] in ('supported', 'unsupported', 'uncertain'), 'unsupported review judgment or override')
        dims = ('relevance', 'assertions', 'actors', 'dates', 'polarity', 'conditions', 'consequences', 'qualifications', 'omissions', 'role', 'expression_binding')
        exact_keys(r['dimensions'], dims, 'review dimensions')
        require(all(v in ('supported', 'unsupported', 'uncertain', 'not_applicable') for v in r['dimensions'].values()), 'invalid dimension judgment')
        require(isinstance(r['evidence'], str) and r['evidence'].strip(), 'review evidence required')
        key = (uid, r['reviewer_id'])
        require(key not in review_map, 'duplicate review')
        review_map[key] = r
    for uid in targets:
        reviews = [r for (u, _), r in review_map.items() if u == uid]
        if len(reviews) < 2:
            block('missing independent semantic judgments')
        if any(r['judgment'] != 'supported' or any(v in ('unsupported', 'uncertain') for v in r['dimensions'].values()) for r in reviews):
            block('unsupported, uncertain or unresolved semantic judgments')
        if len({r['judgment'] for r in reviews}) > 1:
            block('unresolved reviewer disagreement')
    protocol = bundle['protocol']
    if protocol is None:
        block('no frozen prospective protocol and reference contract')
    else:
        # Deliberately no ad-hoc thresholds or caller-provided overrides.
        block('prospective protocol validation and threshold scoring not implemented')
    unit_accounting = []
    for uid in ids:
        unit_attempts = [a for a in attempts if a['unit_id'] == uid]
        attempt_details = []
        for i, a in enumerate(attempts):
            if a['unit_id'] != uid:
                continue
            capture = captures.get(i)
            attempt_details.append({'attempt_index': i, 'status': a['status'],
                                    'capture_disposition': ('missing' if capture is None else
                                        'response_missing' if capture['response_b64'] is None else
                                        'normalized_pair_unverified'),
                                    'output_cardinality': 'boundary_observed' if a['status'] == 'succeeded' else 'unknown'})
        unit_accounting.append({'unit_id': uid, 'attempt_statuses': [a['status'] for a in unit_attempts],
                                'attempts': attempt_details,
                                'planned_output_state': 'boundary_observed' if uid in state['successes'] else 'unknown_not_observed',
                                'disposition': 'succeeded' if uid in state['successes'] else (unit_attempts[-1]['status'] if unit_attempts else 'not_attempted'),
                                'local_outcome': by_id[uid].get('outcome'),
                                'boundary_output_sha256': state['successes'][uid]['output_sha256'] if uid in state['successes'] else None})
    counts['unknown_cardinality_attempts'] = counts_for_unknown_attempts
    counts.update(planned_units=len(ids), attempts=len(attempts), attempted_units=len(per_unit),
                  unattempted_units=sum(u not in per_unit for u in ids),
                  planned_units_without_boundary_output=sum(u not in state['successes'] for u in ids),
                  succeeded_units=len(succeeded), failed_attempts=sum(a['status'] == 'failed' for a in attempts),
                  interrupted_attempts=sum(a['status'] == 'reserved' for a in attempts),
                  original_boundary_outputs=len(state['successes']), reviews=len(review_map),
                  raw_requests_captured=len(captures), raw_responses_captured=sum(c['response_b64'] is not None for c in captures.values()))
    return {'schema_version': 'rule-unit-trial-audit-1', 'state_sha256': bundle['state_sha256'],
            'counts': dict(counts), 'units': unit_accounting, 'generated_clause_count_is_lower_bound': bool(counts['unknown_cardinality_outputs'] or counts['unknown_cardinality_attempts'] or counts['planned_units_without_boundary_output']),
            'observed_generated_clause_count_is_lower_bound': bool(counts['unknown_cardinality_outputs'] or counts['unknown_cardinality_attempts']),
            'planned_output_cardinality_unknown': bool(counts['planned_units_without_boundary_output']),
            'population_accounted': set(packet_ids) == set(ids),
            'boundary_output_accounting_complete': not any(u not in state['successes'] for u in ids) and not counts['unknown_cardinality_outputs'] and not counts['unknown_cardinality_attempts'],
            'response_accounting_complete': False,
            'quality': 'not_scored', 'blockers': blockers}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON object member')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path, help='private JSON bundle')
    args = parser.parse_args()
    try:
        result = audit(json.loads(args.bundle.read_text(encoding='utf-8'), object_pairs_hook=unique_object))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.exit(2, f'Invalid audit input: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 1 if result["blockers"] or not result["response_accounting_complete"] or result["quality"] == "not_scored" else 0


if __name__ == '__main__':
    raise SystemExit(main())
