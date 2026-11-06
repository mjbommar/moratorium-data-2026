#!/usr/bin/env python3
"""Audit an explicit retained-ledger cohort offline; never infer legal coverage."""
import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from normalize_search_provenance import normalize, digest


def audit(root, ledger_paths):
    root = root.resolve()
    paths = [Path(p).resolve() for p in ledger_paths]
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate ledger input')
    if any(not p.is_relative_to(root) or p.name != 'attempts.private.jsonl' for p in paths):
        raise ValueError('Ledger outside cohort root or wrong filename')
    records, ids, totals, backends = [], set(), Counter(), Counter()
    known_cost = Decimal(0)
    for path in sorted(paths):
        before = digest(path)
        record = {'directory': str(path.parent.relative_to(root)), 'ledger_sha256': before}
        try:
            packet = normalize(path.parent)
        except (KeyError, ValueError, OSError) as exc:
            # Never publish exception text: paths, raw content or credentials can
            # occur in transport/JSON errors. Known format gaps get scoped labels.
            reason = ('legacy_missing_client_hash' if isinstance(exc, KeyError) and exc.args == ('client_sha256',)
                      else 'terminal_without_reservation' if str(exc) == 'Terminal event without reservation'
                      else 'unverified_artifact_or_ledger')
            record.update(state='requires_review', reason=reason, error_type=type(exc).__name__)
        else:
            attempt_ids = {a['attempt_id'] for a in packet['attempts']}
            if ids & attempt_ids:
                raise ValueError('Search attempt occurs in multiple cohort ledgers')
            ids.update(attempt_ids)
            backends.update(a['backend'] for a in packet['attempts'])
            summary = packet['summary']
            known_cost += Decimal(str(summary['priced_subtotal_usd']))
            totals.update({k: v for k, v in summary.items() if k != 'priced_subtotal_usd'})
            raw = (json.dumps(packet, indent=2, ensure_ascii=False)+'\n').encode()
            record.update(state='verified', summary=summary, sightings=len(packet['sightings']),
                          exchange_ledger_sha256=packet['exchange_ledger_sha256'],
                          review_packet_sha256=hashlib.sha256(raw).hexdigest())
        if digest(path) != before:
            raise ValueError('Ledger changed during cohort audit')
        records.append(record)
    return {'schema_version': 'search-cohort-audit-1',
            'scope': 'Explicit retained paths only; no new API calls, canonical promotion, current-force acceptance, exhaustive jurisdiction coverage or complete spend asserted. Interrupted denotes a reservation without a terminal ledger event, not an independently verified process state.',
            'normalizer_sha256': digest(Path(__file__).with_name('normalize_search_provenance.py')),
            'summary': {'directories': len(records),
                        'verified_directories': sum(r['state'] == 'verified' for r in records),
                        'verified_directories_with_searches': sum(r.get('summary', {}).get('search_attempts', 0) > 0 for r in records),
                        'requires_review_directories': sum(r['state'] == 'requires_review' for r in records),
                        'verified_unique_search_attempts': len(ids),
                        'verified_sightings': sum(r.get('sightings', 0) for r in records),
                        'verified_attempts_by_backend': dict(sorted(backends.items())),
                        'verified_attempt_totals': dict(totals),
                        'verified_priced_subtotal_usd': str(known_cost),
                        'review_reasons': dict(Counter(r['reason'] for r in records if r['state'] == 'requires_review'))},
            'directories': records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--ledger-list', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.ledger_list.read_bytes()
    report = audit(args.root, [p for p in raw.decode().splitlines() if p.strip()])
    report['input_list_sha256'] = hashlib.sha256(raw).hexdigest()
    report['generator_sha256'] = digest(Path(__file__))
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['summary'], indent=2))
