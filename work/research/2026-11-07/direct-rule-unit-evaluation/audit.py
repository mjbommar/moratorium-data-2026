#!/usr/bin/env python3
"""Read-only audit of a frozen direct rule-unit execution and three AI reviews."""
import argparse
from collections import Counter
import datetime as dt
import dataclasses
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[4]
LABELS = {'supported', 'unsupported', 'ambiguous', 'off_target', 'unresolved'}
POLICY = {'max_attempts': 1, 'agent_retries': 0, 'max_model_requests': 1, 'flex_fallback': False}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def jsonl(path):
    p = Path(path)
    if not p.exists():
        return []
    raw = p.read_text(encoding='utf-8')
    require(not raw or raw.endswith('\n'), 'Incomplete ledger')
    return [json.loads(line) for line in raw.splitlines()]


def money(x):
    return type(x) in (int, float) and math.isfinite(x) and x >= 0


def close(a, b):
    return money(a) and money(b) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def check_hashes(mapping):
    require(isinstance(mapping, dict) and bool(mapping), 'Missing frozen hashes')
    for name, expected in mapping.items():
        require(isinstance(name, str) and Path(name).is_absolute() and isinstance(expected, str)
                and re.fullmatch('[0-9a-f]{64}', expected) and sha(name) == expected, 'Frozen file changed')


def tree_bytes(root):
    total = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            info = (Path(base) / name).lstat()
            require(not stat.S_ISLNK(info.st_mode), 'Symlink in private storage')
            if stat.S_ISREG(info.st_mode):
                require(info.st_nlink == 1, 'Hard link in private storage')
                total += info.st_size
            else:
                require(stat.S_ISDIR(info.st_mode), 'Unexpected storage object')
    return total


def attempt_accounting(attempts, ledger, successes, case, model, pricing=None):
    """Reconcile adapter reservations to returned backend records, including failures."""
    require(len(attempts) <= case['max_calls'], 'Attempt cap exceeded')
    seen, cursor = set(), 0
    priced = held = accounted = 0.0
    unknown = 0
    for index, a in enumerate(attempts):
        uid, status = a['unit_id'], a['status']
        require(uid not in seen and status in ('succeeded', 'failed', 'reserved') and
                a['reserved_usd'] == case['reservation_usd'], 'Duplicate or invalid attempt')
        seen.add(uid)
        ac = a.get('accounting')
        remaining_accounted = sum(x.get('accounting') is not None for x in attempts[index + 1:])
        has_record = ac is not None or len(ledger) - cursor > remaining_accounted
        if has_record:
            require(cursor < len(ledger), 'Missing backend record')
            row = ledger[cursor]; cursor += 1
            require(row.get('attempts') == 1 and row.get('cached') is False and
                    row.get('role') == 'extractor' and row.get('stage') == 'rule_unit', 'Backend record mismatch')
            if pricing is not None and row.get('model') == model and money(row.get('cost_usd')):
                from bc_llm.pricing import Price
                price = Price(**pricing)
                require(close(row['cost_usd'], price.cost(row['input_tokens'], row['output_tokens'],
                    cache_read_tokens=row['cache_read_tokens'], cache_write_tokens=row['cache_write_tokens'],
                    service_tier=row['service_tier'])), 'Backend price estimate mismatch')
            if ac is not None:
                require(row.get('model') == ac.get('model') and close(row.get('cost_usd'), ac.get('cost_usd')) and
                        all(row.get(k) == ac.get(k) for k in ('input_tokens', 'output_tokens')), 'Backend accounting mismatch')
            else:
                require(status == 'failed' and (row.get('cost_usd') is None or not money(row.get('cost_usd'))), 'Unmatched backend record')
        reliable = (isinstance(ac, dict) and ac.get('priced') is True and ac.get('model') == model
                    and money(ac.get('cost_usd')))
        if reliable:
            priced += ac['cost_usd']
        if status == 'succeeded':
            require(reliable and uid in successes and close(a.get('charged_usd'), ac['cost_usd']), 'Invalid success charge')
        if 'charged_usd' in a:
            require(ac is not None and close(a['charged_usd'], ac.get('cost_usd')), 'Invalid charge')
            accounted += a['charged_usd']
        else:
            require(status != 'succeeded', 'Missing success charge')
            accounted += a['reserved_usd']
            if not reliable:
                unknown += 1; held += a['reserved_usd']
        if status != 'succeeded':
            require(uid not in successes, 'Failed unit has success')
    require(cursor == len(ledger) and {a['unit_id'] for a in attempts if a['status'] == 'succeeded'} == set(successes), 'Backend inventory mismatch')
    return dict(accounted_usd=accounted, priced_cost_estimate_usd=priced, unpriced_attempts=unknown,
                held_unpriced_reservations_usd=held, estimated_accounting_complete=unknown == 0,
                budget_within_cap=accounted <= case['max_usd'] + 1e-9)


def valid_spans(spans, text):
    return isinstance(spans, list) and all(isinstance(s, list) and len(s) == 2 and
        all(type(x) is int for x in s) and 0 <= s[0] < s[1] <= len(text) for s in spans)


def validate_review(review, protocol_hash, units, expected_slots, texts):
    require(isinstance(review, dict) and review.get('protocol_sha256') == protocol_hash and
            isinstance(review.get('reviewer'), str) and review['reviewer'].strip(), 'Invalid review identity')
    rows, slots = {}, {}
    require(isinstance(review.get('units'), list) and isinstance(review.get('slots'), list), 'Missing review populations')
    for row in review['units']:
        key = (row['case_id'], row['unit_id'])
        require(key in units and key not in rows and row.get('disposition') in LABELS and
                row.get('high_impact') is True and 'source_extractable' in row and row['source_extractable'] in (True, False, None) and
                (row.get('source_extractable') is None or type(row['source_extractable']) is bool) and
                isinstance(row.get('rationale'), str) and row['rationale'].strip() and
                valid_spans(row.get('source_spans'), texts[key[0]]), 'Invalid unit review')
        clause = 'clause' in units[key] and units[key]['clause'] is not None
        require((row['disposition'] != 'unresolved') == clause, 'Clause disposition mismatch')
        require(row['disposition'] != 'supported' or bool(row['source_spans']), 'Supported clause needs source span')
        rows[key] = row
    require(rows.keys() == units.keys(), 'Unit review population mismatch')
    for row in review['slots']:
        key = (row['case_id'], row['slot_id'])
        require(key in expected_slots and key not in slots and type(row.get('covered')) is bool and
                isinstance(row.get('rationale'), str) and row['rationale'].strip() and
                valid_spans(row.get('source_spans'), texts[key[0]]) and
                isinstance(row.get('unit_ids'), list) and isinstance(row.get('clause_indexes'), list), 'Invalid slot review')
        ids, indexes = row['unit_ids'], row['clause_indexes']
        if row['covered']:
            require(len(ids) == 1 and indexes == [0] and type(indexes[0]) is int and row['source_spans'] and
                    (key[0], ids[0]) in rows and rows[(key[0], ids[0])]['disposition'] == 'supported' and
                    units[(key[0], ids[0])].get('clause') is not None, 'Slot requires one supported complete clause')
        else:
            require(not ids and not indexes, 'Uncovered slot has references')
        slots[key] = row
    require(slots.keys() == expected_slots.keys(), 'Slot review population mismatch')
    return rows, slots


def audit(protocol_path, coordinator_path, reviewer_paths, *, fixture_root=None):
    protocol_path = Path(protocol_path).resolve()
    require(len(reviewer_paths) == 2, 'Exactly two independent reviewers required')
    p = load(protocol_path); ph = sha(protocol_path)
    require(p['schema_version'] == 'direct-rule-unit-development-1' and p['backend_policy'] == POLICY and
            p['max_http_requests'] == 86 and p['max_private_bytes'] == 134217728 and p['max_source_bytes'] == 200000,
            'Protocol limits changed')
    for key in ('code_sha256', 'inputs_sha256', 'canonical_inputs_sha256'):
        check_hashes(p[key])
    required_code = [protocol_path.parent / 'run.py', protocol_path.parent / 'audit.py',
                     *(ROOT / 'scripts' / name for name in ('extract_rule_units.py', 'condition_expression.py',
                       'extract_document_resumable.py', 'controlled_model_transport.py', 'private_run_storage.py', 'runtime_file_pins.py'))]
    require(all(str(path) in p['code_sha256'] for path in required_code), 'Required code not frozen')
    require((ROOT / 'data/expanded').resolve().name == p['canonical_snapshot'], 'Canonical snapshot changed')
    slots_path = protocol_path.parent / 'required-slots.json'
    require(sha(slots_path) == p['required_slots_sha256'] and p['required_slots_sha256'] in
            set(p['code_sha256'].values()) | set(p['inputs_sha256'].values()) | set(p['canonical_inputs_sha256'].values()), 'Slots not frozen')
    families = load(slots_path)['families']
    cases = p['cases']
    require([(c['case_id'], c['family'], c['units'], c['max_calls'], c['max_usd'], c['reservation_usd']) for c in cases] ==
            [('mandan-direct', 'mandan', 20, 20, 15, .75), ('harwood-direct', 'harwood', 66, 66, 49.5, .75)], 'Case contract changed')
    t = p['thresholds']
    require(t['supported_fraction'] == .95 and t['critical_unsupported_or_ambiguous'] == 0 and
            t['all_required_slots'] is True and t['source_quote_integrity'] is True and t['full_supplied_text_coverage'] is True, 'Thresholds changed')
    require(isinstance(p['runtime_import_paths'], list) and all(Path(x).is_absolute() and Path(x).is_dir() for x in p['runtime_import_paths']), 'Invalid runtime paths')
    sys.path[:0] = p['runtime_import_paths'] + [str(ROOT / 'scripts')]
    import extract_rule_units as rules
    import runtime_file_pins
    from bc_llm import BcLlmSettings
    settings = BcLlmSettings()
    proxy = {'proxy': settings.proxy_url(), **{k: os.environ.get(k) for k in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'OPENAI_BASE_URL', 'OPENAI_ORG_ID', 'OPENAI_PROJECT_ID')}}
    require(digest(proxy) == p['routing_fingerprint'] and dataclasses.asdict(settings.pricing().get(p['model_spec']['model'])) == p['pricing'] and
            p.get('tool_configuration') == {'toolsets': [], 'tools': []}, 'Runtime routing or pricing changed')
    runtime_file_pins.verify_manifest(p['runtime_files_path'], p['runtime_files_sha256'])
    for name, version in p['dependency_versions'].items():
        require(importlib.metadata.version(name) == version, 'Dependency version changed')
    mode = 'provider' if fixture_root is None else 'offline_mock'
    root = Path(p['private_root']) / 'provider' if fixture_root is None else Path(fixture_root).resolve()
    if fixture_root is not None:
        require(root.is_relative_to((Path(p['private_root']) / 'preflight').resolve()) and root != (Path(p['private_root']) / 'preflight').resolve(), 'Fixture outside preflight')
    storage_root = Path(p['private_root']).resolve()
    require(root.is_dir() and not root.is_symlink() and tree_bytes(storage_root) <= p['max_private_bytes'], 'Private storage invalid')
    require(load(storage_root / '.storage-policy.json') == {'root': str(storage_root), 'max_bytes': p['max_private_bytes']}, 'Storage policy changed')
    marker = load(root / 'execution.private.json'); terminal = load(root / 'terminal.private.json')
    require(marker.get('mode') == mode and marker.get('protocol_sha256') == ph and marker.get('state') == 'started' and terminal.get('mode') == mode and marker.get('driver_sha256') == p['code_sha256'][str(protocol_path.parent / 'run.py')], 'Execution binding mismatch')
    for filename, expected in p['code_sha256'].items():
        require(sha(root / 'executed-code' / (expected + '-' + Path(filename).name)) == expected, 'Executed code changed')
    require(load(root / 'http/http-policy.private.json') == {'schema_version': 'controlled-model-http-1', 'max_requests': 86, 'context_sha256': ph}, 'HTTP policy changed')
    events = jsonl(root / 'http/http-attempts.private.jsonl'); reserved, responses = {}, {}
    for event in events:
        ident = event['attempt_id']; require(isinstance(ident, str) and ident, 'Invalid HTTP ID')
        if event['state'] == 'reserved':
            require(ident not in reserved, 'Duplicate HTTP reservation'); reserved[ident] = event
        elif event['state'] == 'response':
            require(ident in reserved and ident not in responses and type(event.get('status')) is int, 'Invalid HTTP response'); responses[ident] = event
        else:
            require(False, 'Unknown HTTP event')
    require(len(reserved) <= 86, 'HTTP cap exceeded')
    tc = {x['case_id']: x for x in terminal['cases']}
    require(len(terminal['cases']) == 2 and set(tc) == {c['case_id'] for c in cases}, 'Terminal population mismatch')
    units, texts, expected_slots, reports = {}, {}, {}, []
    for case in cases:
        ident = case['case_id']; directory = root / ident
        for field in ('body', 'text', 'plan'):
            require(Path(case[field + '_path']).is_absolute() and sha(case[field + '_path']) == case[field + '_sha256'], 'Source or plan changed')
        text = Path(case['text_path']).read_text(encoding='utf-8'); plan = load(case['plan_path']); texts[ident] = text
        require(len(text.encode()) <= p['max_source_bytes'] and plan['source_text_sha256'] == case['text_sha256'] and len(plan['units']) == case['units'], 'Plan binding mismatch')
        for slot in families[case['family']]:
            key = (ident, slot['slot_id']); require(key not in expected_slots, 'Duplicate slot'); expected_slots[key] = slot
        report = load(directory / 'terminal.private.json'); require(report == tc[ident], 'Case terminal mismatch')
        state_path = directory / 'rule-units-state.private.json'
        if not state_path.exists():
            require(report['status'] in ('not_attempted', 'failed') and report['backend_calls'] == 0 and
                    report['ledger_calls'] == 0 and report['replay_without_calls'] is False and
                    report['planned_count'] == case['units'] and report['candidate_count'] == 0 and
                    report['unresolved_count'] == case['units'] and not jsonl(directory / 'calls.private.jsonl') and
                    not (directory / 'rule-units-seal.private.json').exists() and
                    not (directory / 'rule-units-candidates.private.json').exists(), 'Missing state with inconsistent terminal')
            for unit in plan['units']:
                key = (ident, unit['unit_id']); require(key not in units, 'Duplicate unit')
                units[key] = {'unit_id': unit['unit_id'], 'status': 'not_attempted', 'outcome': 'unresolved'}
            reports.append(dict(case_id=ident, status=report['status'], planned_units=case['units'], attempted_units=0,
                successful_units=0, failed_units=0, not_attempted_units=case['units'], unresolved_units=case['units'],
                returned_clauses=0, backend_calls=0, backend_result_records=0,
                **attempt_accounting([], [], {}, case, p['model_spec']['model'], p['pricing'])))
            continue
        state = load(state_path); result = load(directory / 'rule-units-candidates.private.json')
        require(load(directory / 'rule-units-seal.private.json') == {'sha256': digest(state)}, 'Seal mismatch')
        context = state['context']; doc = context['document']
        require(doc.get('text') == text and doc.get('doc_id') == case['source_document_id'] and doc.get('title') == case['title'] and
                doc.get('url') == case['url'] and doc.get('body_sha256') == case['body_sha256'] and doc.get('text_sha256') == case['text_sha256'], 'Document context mismatch')
        identity = {**p['model_spec'], 'pricing': p['pricing'], **POLICY, 'execution_mode': mode}
        require(context['model_identity'] == identity and context['plan'] == plan and context['today'] == p['source_cohort_date'] and
                context['max_calls'] == case['max_calls'] and context['max_usd'] == case['max_usd'] and
                context['reservation_usd'] == case['reservation_usd'] and context['max_source_bytes'] == p['max_source_bytes'] and
                context['role'] == 'extractor' and context['settings'] == {} and context['storage_policy'] == {'root': str(storage_root), 'max_bytes': p['max_private_bytes']} and
                context['system'] == rules.SYSTEM and context['schema'] == rules.Response.model_json_schema() and
                context['implementation_sha256'] == sha(ROOT / 'scripts/extract_rule_units.py') and context['condition_sha256'] == sha(ROOT / 'scripts/condition_expression.py'), 'Context settings changed')
        # prepare also enforces unique source-located anchors, source binding and caps; no writes.
        class Storage:
            def describe(self): return {'root': str(storage_root), 'max_bytes': p['max_private_bytes']}
        expected = rules.prepare(doc, plan, model_identity=identity, today=dt.date.fromisoformat(p['source_cohort_date']),
            max_calls=case['max_calls'], max_usd=case['max_usd'], reservation_usd=case['reservation_usd'],
            max_source_bytes=p['max_source_bytes'], role='extractor', settings={}, storage_policy=Storage())
        rules.validate_state(state, expected)
        require(result == rules.packet(state, expected), 'Packet derivative mismatch')
        attempts = state['attempts']; ledger = jsonl(directory / 'calls.private.jsonl')
        accounting = attempt_accounting(attempts, ledger, state['successes'], case, p['model_spec']['model'], p['pricing'])
        require(report['backend_calls'] == len(attempts) and report['ledger_calls'] == len(ledger) and
                report['planned_count'] == result['planned_count'] and report['candidate_count'] == result['candidate_count'] and
                report['unresolved_count'] == result['unresolved_count'], 'Terminal counts mismatch')
        require([a['unit_id'] for a in attempts] == [u['unit_id'] for u in plan['units'][:len(attempts)]] and
                all(a['status'] == 'succeeded' for a in attempts[:-1]), 'Attempt order, retry or stop policy mismatch')
        if report['status'] == 'finished':
            require(len(attempts) == case['units'] and len(state['successes']) == case['units'] and report['replay_without_calls'] is True, 'Invalid completed case')
        else:
            require(report['status'] == 'failed' and type(report['replay_without_calls']) is bool, 'Invalid case terminal')
        for unit in result['units']:
            key = (ident, unit['unit_id']); require(key not in units, 'Duplicate unit'); units[key] = unit
        reports.append(dict(case_id=ident, status=report['status'], planned_units=case['units'], attempted_units=len(attempts),
            successful_units=len(state['successes']), failed_units=sum(a['status'] == 'failed' for a in attempts),
            not_attempted_units=case['units'] - len(attempts), unresolved_units=result['unresolved_count'],
            returned_clauses=sum(u.get('clause') is not None for u in result['units']), backend_calls=len(attempts),
            backend_result_records=len(ledger), **accounting))
    require(len(expected_slots) == 12, 'Expected twelve slots')
    require(terminal.get('failure_policy') == 'Stop the failing case without retry; continue the other fixed case only after global pins, storage and transport revalidate.' and
            terminal.get('all_successful_replays_no_extra_calls') == all(tc[c['case_id']]['replay_without_calls'] is True for c in cases if tc[c['case_id']]['status'] == 'finished'), 'Failure or replay policy mismatch')
    calls = sum(r['backend_calls'] for r in reports); records = sum(r['backend_result_records'] for r in reports)
    require(terminal['backend_result_records'] == records and terminal['http_reservation_count'] == len(reserved) and
            terminal['http_response_count'] == len(responses) and terminal['provider_requests'] == (len(reserved) if mode == 'provider' else 0) and
            len(reserved) <= calls and records <= len(responses), 'Global accounting mismatch')
    execution_complete = (terminal['status'] == 'finished' and all(r['status'] == 'finished' for r in reports) and
                          terminal['all_successful_replays_no_extra_calls'] is True and calls == 86 and
                          len(reserved) == calls == len(responses) and all(200 <= x['status'] < 300 for x in responses.values()))
    require(terminal['status'] in ('finished', 'failed') and (terminal['status'] != 'finished' or execution_complete), 'Invalid global terminal')
    reviews = []
    for path in [coordinator_path, *reviewer_paths]:
        review = load(path); rows, slots = validate_review(review, ph, units, expected_slots, texts)
        reviews.append((review['reviewer'], rows, slots, sha(path)))
    require(len({r[0] for r in reviews}) == 3, 'Reviewer identities must differ')
    rows, slots = reviews[0][1:3]
    for report in reports:
        ident = report['case_id']; keys = [k for k in units if k[0] == ident]; clauses = [k for k in keys if units[k].get('clause') is not None]
        counts = Counter(rows[k]['disposition'] for k in clauses); n = len(clauses)
        flags = Counter(flag for k in clauses for flag in units[k].get('review_flags', []))
        omissions = sum(rows[k]['source_extractable'] is True and rows[k]['disposition'] != 'supported' for k in keys)
        fraction = counts['supported'] / n if n else None
        covered = sum(slots[k]['covered'] for k in slots if k[0] == ident)
        report.update(dispositions={k: counts[k] for k in sorted(LABELS)}, supported_fraction=fraction,
            critical_non_supported=sum(counts[k] for k in ('unsupported', 'ambiguous', 'off_target')),
            source_extractable_omissions=omissions, source_extractability_unknown=sum(rows[k]['source_extractable'] is None for k in keys),
            validation_flags=dict(flags), slots_covered=covered, slots_total=sum(k[0] == ident for k in slots))
        report['quality_gate_passed'] = bool(mode == 'provider' and execution_complete and n and fraction >= .95 and
            report['critical_non_supported'] == 0 and covered == report['slots_total'] and not flags and
            omissions == 0 and report['source_extractability_unknown'] == 0 and report['budget_within_cap'])
    total_clauses = sum(r['returned_clauses'] for r in reports); supported = sum(r['dispositions']['supported'] for r in reports)
    disagreements = sum(reviews[1][1][k]['disposition'] != reviews[2][1][k]['disposition'] for k in units)
    slot_disagreements = sum(reviews[1][2][k]['covered'] != reviews[2][2][k]['covered'] for k in expected_slots)
    complete_accounting = all(r['estimated_accounting_complete'] and r['budget_within_cap'] for r in reports) and len(reserved) == calls == len(responses) and all(200 <= x['status'] < 300 for x in responses.values())
    return dict(schema_version='direct-rule-unit-audit-1', protocol_sha256=ph, execution_mode=mode, fixture_only=fixture_root is not None,
        execution_complete=execution_complete, cases=reports, returned_clauses=total_clauses, supported_clauses=supported,
        supported_fraction=supported / total_clauses if total_clauses else None,
        quality_gate_passed=bool(mode == 'provider' and execution_complete and complete_accounting and all(r['quality_gate_passed'] for r in reports)),
        backend_calls=calls, backend_result_records=records, http_reservations=len(reserved), http_responses=len(responses),
        http_failed_responses=sum(not 200 <= x['status'] < 300 for x in responses.values()), http_missing_responses=len(reserved)-len(responses),
        priced_cost_estimate_usd=sum(r['priced_cost_estimate_usd'] for r in reports), accounted_usd=sum(r['accounted_usd'] for r in reports),
        unpriced_attempts=sum(r['unpriced_attempts'] for r in reports), held_unpriced_reservations_usd=sum(r['held_unpriced_reservations_usd'] for r in reports),
        estimated_accounting_complete=complete_accounting, coordinator_review_sha256=reviews[0][3], reviewer_file_sha256=[r[3] for r in reviews[1:]],
        independent_unit_disagreements=disagreements, independent_slot_disagreements=slot_disagreements,
        canonical_records_written=0, overall_p4_closed=False,
        scope='Two known documents; source-informed AI judgments are not human truth. Estimates are not invoices. No source freshness or promotion claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path); parser.add_argument('--coordinator', type=Path, required=True)
    parser.add_argument('--reviewer', type=Path, action='append', required=True); parser.add_argument('--fixture-root', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.protocol, args.coordinator, args.reviewer, fixture_root=args.fixture_root), sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({'status': 'failed', 'error_class': type(error).__name__}), file=sys.stderr)
        sys.exit(1)
