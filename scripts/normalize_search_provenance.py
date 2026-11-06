#!/usr/bin/env python3
"""Normalize retained research-client searches for review, without new API calls.

Output is a review packet, not a canonical publication or coverage assertion.
Raw provider bodies, snippets and credentials never belong in this packet.
"""
import argparse
import hashlib
import json
from pathlib import Path

SEARCH = {'exa', 'serpapi', 'googlenews', 'gdelt'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(directory, value):
    path = Path(value)
    if not path.is_absolute():
        path = directory / path
    path = path.resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError('Artifact outside supplied private directory')
    return path


def normalize(directory):
    directory = Path(directory)
    ledger = directory / 'attempts.private.jsonl'
    events = [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
    reservations, terminal = {}, {}
    for event in events:
        ident = event['attempt_id']
        target = reservations if event['state'] == 'reserved' else terminal
        if event['state'] not in {'reserved', 'finished'} or ident in target:
            raise ValueError('Unknown state or duplicate ledger event')
        target[ident] = event
    if terminal.keys() - reservations.keys():
        raise ValueError('Terminal event without reservation')
    exchange_path = directory / 'exchanges.private.jsonl'
    exchange_events = [json.loads(line) for line in exchange_path.read_text().splitlines()
                       if line.strip()] if exchange_path.exists() else []
    by_attempt = {}
    for exchange in exchange_events:
        if exchange['attempt_id'] not in reservations:
            raise ValueError('Exchange without reservation')
        by_attempt.setdefault(exchange['attempt_id'], []).append(
            {k: v for k, v in exchange.items() if k != 'attempt_id'})
    attempts, sightings = [], []
    for ident, reserved in sorted(reservations.items()):
        if reserved['kind'] not in SEARCH:
            continue
        done = terminal.get(ident)
        row = {'attempt_id': ident, 'backend': reserved['kind'],
               'started_at': reserved['reserved_at'],
               'client_sha256': reserved['client_sha256'],
               'config_sha256': reserved['config_sha256'],
               'outcome': 'interrupted' if done is None else 'error',
               'query': None, 'spend_usd': None, 'response_sha256': None,
               'hit_count': None, 'exchanges': [], 'error_type': None,
               'publication_window': None, 'declined': None}
        intent = reserved.get('intent', {})
        row.update(query=intent.get('query'), publication_window=intent.get('publication_window'))
        recorded = by_attempt.get(ident, [])
        embedded = done.get('exchanges', []) if done else []
        if recorded and embedded and recorded != embedded:
            raise ValueError('Exchange ledger/terminal mismatch')
        # Successful terminals embed the same ordered exchanges. Read the separate
        # ledger for errors/interruption; do not count duplicated copies twice.
        exchanges = recorded or embedded
        seen_artifacts = set()
        for exchange in exchanges:
            body = local_file(directory, exchange['artifact'])
            if body in seen_artifacts:
                raise ValueError('Duplicate exchange artifact')
            seen_artifacts.add(body)
            if digest(body) != exchange['stored_body_sha256']:
                raise ValueError('Provider response hash mismatch')
            row['exchanges'].append({k: exchange[k] for k in
                ('status', 'original_body_sha256', 'stored_body_sha256', 'redacted')})
        if done:
            if done.get('intent', {}) != intent:
                raise ValueError('Reservation/terminal intent mismatch')
            for field in ('kind', 'reserved_at', 'client_sha256', 'config_sha256'):
                if done[field] != reserved[field]:
                    raise ValueError('Reservation/terminal identity mismatch')
            row['error_type'] = done.get('error_type')
            if done['outcome'] == 'response':
                path = local_file(directory, done['artifact'])
                payload = json.loads(path.read_text())
                if payload['backend'] != reserved['kind'] or payload['query'] != done['query']:
                    raise ValueError('Response identity mismatch')
                if intent and (intent['query'] != done['query'] or
                               intent['publication_window'] != done.get('publication_window')):
                    raise ValueError('Reservation/response intent mismatch')
                if len(payload['hits']) != done['hits']:
                    raise ValueError('Response count mismatch')
                row.update(query=done['query'], spend_usd=done.get('cost_usd'),
                           response_sha256=digest(path), hit_count=len(payload['hits']),
                           publication_window=done.get('publication_window'),
                           declined=payload.get('declined'),
                           outcome='partial' if payload.get('declined') else 'success')
                for index, hit in enumerate(payload['hits'], 1):
                    sightings.append({'attempt_id': ident, 'returned_order': index,
                                      'provider_position': hit.get('position'), 'url': hit['url'],
                                      'seen_at': done['finished_at']})
            elif done['outcome'] != 'error':
                raise ValueError('Unknown terminal outcome')
        attempts.append(row)
    return {'schema_version': 'review-search-provenance-1',
            'scope': 'Review only. No canonical IDs, source acceptance, rank fusion or jurisdiction-wide completeness asserted. Missing query/window for failed or interrupted legacy reservations remains unknown.',
            'ledger_sha256': digest(ledger),
            'exchange_ledger_sha256': digest(exchange_path) if exchange_path.exists() else None,
            'attempts': attempts, 'sightings': sightings,
            'summary': {'search_attempts': len(attempts),
                        'successful_zero_hit_attempts': sum(a['outcome'] == 'success' and a['hit_count'] == 0 for a in attempts),
                        'failed_attempts': sum(a['outcome'] == 'error' for a in attempts),
                        'interrupted_attempts': sum(a['outcome'] == 'interrupted' for a in attempts),
                        'partial_attempts': sum(a['outcome'] == 'partial' for a in attempts),
                        'priced_subtotal_usd': round(sum(a['spend_usd'] or 0 for a in attempts), 9),
                        'unpriced_attempts': sum(a['spend_usd'] is None for a in attempts)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(normalize(args.directory), indent=2, ensure_ascii=False))
