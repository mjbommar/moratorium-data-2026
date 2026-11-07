#!/usr/bin/env python3
"""Audit the retained provider execution and three source-informed reviews.

This is a read-only audit. Review judgments are not evidence of ground truth;
public output contains counts and hashes, never source text or model output.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
LABELS = {'supported', 'unsupported', 'ambiguous', 'off_target'}
FACT_KEYS = ('target_table', 'target_field', 'subject_label', 'quote',
             'assertion_context', 'supporting_passages', 'value')


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def jsonl(path):
    raw = Path(path).read_text(encoding='utf-8')
    require(not raw or raw.endswith('\n'), 'Incomplete ledger')
    return [json.loads(line) for line in raw.splitlines()]


def money(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def close(a, b):
    return money(a) and money(b) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def attempt_accounting(attempts, ledger, successes, case, model):
    """The pinned backend emits CallRecord only on return, not on exceptions.

    CachedBackend's durable attempt reservation is authoritative for failures.
    Consume a result record only when that attempt received accounting; a failed
    request before a backend return has no record and retains its full reserve.
    """
    require(len(attempts) <= case['max_calls'], 'Attempt population mismatch')
    keys=set();cursor=0;accounted=priced=held=0.0;unpriced=0
    for attempt in attempts:
        key,status=attempt['request_sha256'],attempt['status']
        require(isinstance(key,str) and re.fullmatch(r'[0-9a-f]{64}',key) and key not in keys
                and status in ('failed','succeeded') and attempt['reserved_usd']==case['reservation_usd'],
                'Call accounting mismatch')
        account=attempt.get('accounting')
        row=None
        if account is not None:
            require(isinstance(account,dict) and cursor<len(ledger),'Missing backend result record')
            row=ledger[cursor];cursor+=1
            require(type(row.get('attempts')) is int and row['attempts']==1,'Backend attempt count mismatch')
        reliable=(isinstance(account,dict) and account.get('priced') is True
                  and account.get('model')==model and money(account.get('cost_usd')))
        if reliable:
            require(close(row.get('cost_usd'),account['cost_usd']),'Call accounting mismatch')
            priced+=account['cost_usd']
        if status=='succeeded':
            require(reliable and key in successes and 'charged_usd' in attempt
                    and close(attempt['charged_usd'],account['cost_usd']),'Successful call accounting mismatch')
            require(digest(successes[key]['output'])==successes[key]['output_sha256'],'Output hash mismatch')
            keys.add(key)
        if 'charged_usd' in attempt:
            require(reliable and close(attempt['charged_usd'],account['cost_usd'])
                    and attempt['charged_usd']<=attempt['reserved_usd']+1e-9,'Call charge mismatch')
            accounted+=attempt['charged_usd']
        else:
            require(status=='failed','Successful call lacks charge')
            accounted+=attempt['reserved_usd']
        if not reliable:
            require(status=='failed' and 'charged_usd' not in attempt,'Unpriced call lost reservation')
            unpriced+=1;held+=attempt['reserved_usd']
    require(cursor==len(ledger),'Unexpected backend result records')
    require(keys==set(successes),'Success inventory mismatch')
    require(money(accounted) and accounted<=case['max_usd']+1e-9,'Case budget exceeded')
    return dict(accounted_usd=accounted,priced_cost_estimate_usd=priced,unpriced_attempts=unpriced,
                held_unpriced_reservations_usd=held,estimated_accounting_complete=unpriced==0,successful_keys=keys)


def check_hashes(mapping):
    require(isinstance(mapping, dict) and mapping, 'Missing frozen hashes')
    for name, expected in mapping.items():
        require(isinstance(name, str) and Path(name).is_absolute() and
                isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected)
                and sha(name) == expected, 'Frozen file changed')


def spans_for(text, quote):
    require(isinstance(quote, str) and bool(quote), 'Empty quote')
    spans, start = [], 0
    while (found := text.find(quote, start)) >= 0:
        spans.append([found, found + len(quote)])
        start = found + 1
    return spans


def condition_locations(value, text):
    locations = []
    def visit(item, path):
        if isinstance(item, dict):
            if 'source_text' in item:
                locations.append({'path': path, 'quote': item['source_text'],
                                  'exact_quote_spans': spans_for(text, item['source_text'])})
            for key, child in item.items():
                visit(child, path + [key])
        elif isinstance(item, list):
            for index, child in enumerate(item):
                visit(child, path + [index])
    visit(value, [])
    return locations


def quote_integrity(candidate, text):
    primary = spans_for(text, candidate['quote'])
    require(candidate['exact_quote_spans'] == primary, 'Primary locations changed')
    passages = candidate['supporting_passages']
    locations = candidate['supporting_passage_locations']
    require(isinstance(passages, list) and isinstance(locations, list) and
            len(passages) == len(locations), 'Support inventory changed')
    all_locations = [primary]
    for passage, located in zip(passages, locations):
        expected = {**passage, 'exact_quote_spans': spans_for(text, passage['quote'])}
        require(located == expected, 'Support locations changed')
        all_locations.append(expected['exact_quote_spans'])
    if candidate['target_field'] == 'condition_clauses':
        expected = condition_locations(candidate['value'], text)
        require(candidate['condition_source_locations'] == expected, 'Condition locations changed')
        all_locations.extend(item['exact_quote_spans'] for item in expected)
    return all(len(item) == 1 for item in all_locations)


def valid_spans(spans, text):
    return (isinstance(spans, list) and all(isinstance(s, list) and len(s) == 2 and
            all(type(n) is int for n in s) and 0 <= s[0] < s[1] <= len(text)
            for s in spans))


def agreement(a, b):
    require(a.keys() == b.keys(), 'Review populations differ')
    n = len(a)
    if not n:
        return {'candidate_count': 0, 'matching_labels': 0,
                'observed_agreement': None, 'cohens_kappa': None,
                'scope': 'Two source-informed AI reviews; agreement is not accuracy or truth.'}
    same = sum(a[k] == b[k] for k in a)
    x, y = Counter(a.values()), Counter(b.values())
    expected = sum(x[k] * y[k] for k in x.keys() | y.keys()) / n**2
    observed = same / n
    return {'candidate_count': n, 'matching_labels': same, 'observed_agreement': observed,
            'cohens_kappa': (observed - expected) / (1 - expected) if expected < 1 else None,
            'scope': 'Two source-informed AI reviews; agreement is not accuracy or truth.'}


def audit(protocol_path, coordinator_path, reviewer_paths, *, fixture_root=None):
    protocol_path = Path(protocol_path)
    coordinator_path = Path(coordinator_path)
    reviewer_paths = [Path(p) for p in reviewer_paths]
    require(len(reviewer_paths) == 2, 'Exactly two reviewers required')
    protocol = load(protocol_path)
    protocol_hash = sha(protocol_path)
    check_hashes(protocol['code_sha256'])
    check_hashes(protocol['canonical_inputs_sha256'])
    require((ROOT / 'data/expanded').resolve().name == protocol['canonical_snapshot'],
            'Canonical snapshot changed')
    slots_path = protocol_path.parent / 'required-slots.json'
    slots_hash = sha(slots_path)
    require(slots_hash == protocol['required_slots_sha256'] and
            slots_hash in set(protocol['code_sha256'].values()) | set(protocol['canonical_inputs_sha256'].values()),
            'Required slots are not frozen')
    families = load(slots_path)['families']
    require(set(families) == {'mandan', 'harwood'}, 'Unexpected slot families')
    require(protocol['thresholds']['supported_fraction'] == 0.95, 'Unexpected support threshold')
    cases = protocol['cases']
    require(isinstance(cases, list) and len(cases) == 4, 'Four cases required')
    case_by_id = {}
    for case in cases:
        ident = case['case_id']
        require(isinstance(ident, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', ident)
                and ident not in case_by_id and case['family'] in families and
                isinstance(case['policy'], str) and case['policy'], 'Invalid case identity')
        case_by_id[ident] = case
    policies = {c['policy'] for c in cases}
    require(len(policies) == 2 and all({c['family'] for c in cases if c['policy'] == p} == set(families)
            and sum(c['policy'] == p for c in cases) == 2 for p in policies), 'Invalid policy matrix')
    expected_slots = {}
    for ident, case in case_by_id.items():
        entries = families[case['family']]
        require(isinstance(entries, list) and entries, 'Missing required slots')
        for slot in entries:
            key = (ident, slot['slot_id'])
            require(isinstance(slot['slot_id'], str) and slot['slot_id'] and key not in expected_slots,
                    'Duplicate or invalid slot')
            expected_slots[key] = slot

    paths = protocol['runtime_import_paths']
    require(isinstance(paths, list) and all(isinstance(p, str) and Path(p).is_absolute() and Path(p).is_dir() for p in paths),
            'Invalid runtime import paths')
    sys.path[:0] = paths + [str(ROOT / 'scripts')]
    import extract_domain_candidates as domain
    schema = load(domain.SCHEMA)
    mode='provider' if fixture_root is None else 'offline_mock'
    root=Path(protocol['private_root'])/'provider' if fixture_root is None else Path(fixture_root).resolve()
    if fixture_root is not None:
        require(root.is_relative_to((Path(protocol['private_root'])/'preflight').resolve()),'Fixture must stay in admitted preflight area')
    marker = load(root / 'execution.private.json')
    terminal = load(root / 'terminal.private.json')
    require(isinstance(marker, dict) and
            all(marker.get(k) == v for k, v in {'mode': mode, 'protocol_sha256': protocol_hash, 'state': 'started'}.items()) and
            set(marker) <= {'mode', 'protocol_sha256', 'state', 'pid', 'started_at', 'driver_sha256', 'git_commit'} and
            ('driver_sha256' not in marker or marker['driver_sha256'] == protocol['code_sha256'][str(protocol_path.parent.resolve() / 'run.py')]) and
            terminal['mode'] == mode and terminal['status'] == 'finished' and
            terminal['all_replays_no_extra_calls'] is True, 'Provider run is not finished')
    if fixture_root is None:
        for filename, expected in protocol['code_sha256'].items():
            require(sha(root / 'executed-code' / (expected + '-' + Path(filename).name)) == expected,
                    'Retained executed code changed')
    artifacts = {}
    def record(path):
        artifacts[str(path)] = sha(path)
    for path in (root / 'execution.private.json', root / 'terminal.private.json',
                 root / 'http/http-policy.private.json', root / 'http/http-attempts.private.jsonl'):
        record(path)
    http_policy = load(root / 'http/http-policy.private.json')
    require(protocol['max_http_requests'] == 16 and http_policy ==
            {'schema_version': 'controlled-model-http-1', 'max_requests': 16,
             'context_sha256': protocol_hash}, 'HTTP policy changed')
    events = jsonl(root / 'http/http-attempts.private.jsonl')
    reserved, responses = {}, {}
    for event in events:
        ident = event['attempt_id']
        require(isinstance(ident, str) and ident, 'Invalid HTTP attempt')
        if event['state'] == 'reserved':
            require(ident not in reserved and ident not in responses, 'Duplicate HTTP reservation')
            reserved[ident] = event
        elif event['state'] == 'response':
            require(ident in reserved and ident not in responses and type(event['status']) is int,
                    'Invalid HTTP response')
            responses[ident] = event
        else:
            require(False, 'Unknown HTTP event')
    require(len(reserved) <= 16, 'HTTP cap exceeded')
    http_failures = sum(not 200 <= e['status'] < 300 for e in responses.values())
    http_missing = len(reserved) - len(responses)
    terminal_cases = {x['case_id']: x for x in terminal['cases']}
    require(len(terminal['cases']) == 4 and terminal_cases.keys() == case_by_id.keys(), 'Terminal case population mismatch')
    candidates, texts, case_reports = {}, {}, {}
    total_calls, total_cost, total_priced, total_unpriced, total_held, failed_attempts = 0, 0.0, 0.0, 0, 0.0, 0
    total_records = 0
    for ident, case in case_by_id.items():
        directory = root / ident
        for name in ('state.private.json', 'domain-candidates.private.json', 'calls.private.jsonl', 'terminal.private.json'):
            record(directory / name)
        state = load(directory / 'state.private.json')
        result = load(directory / 'domain-candidates.private.json')
        report = load(directory / 'terminal.private.json')
        require(report == terminal_cases[ident] and report['status'] == 'finished' and
                report['replay_without_calls'] is True and report['result_sha256'] == sha(directory / 'domain-candidates.private.json'),
                'Case terminal mismatch')
        for field in ('body', 'text'):
            require(Path(case[field + '_path']).is_absolute() and sha(case[field + '_path']) == case[field + '_sha256'],
                    'Source changed')
        text = Path(case['text_path']).read_text(encoding='utf-8')
        texts[ident] = text
        context = state['context']
        require(digest(context) == state['context_sha256'] == result['context_sha256'], 'Context hash mismatch')
        doc = context['document']
        require(doc['text'] == text and doc['doc_id'] == case['source_document_id'] and
                doc['body_sha256'] == case['body_sha256'] and doc['text_sha256'] == case['text_sha256'] and
                doc['title'] == case['title'] and doc['url'] == case['url'], 'Document context mismatch')
        instruction = domain.INSTRUCTIONS.format(fields=json.dumps({k: sorted(v) for k,v in domain.FIELDS.items()}))
        require(context['question'] == protocol['question'] + '\n' + instruction and
                context['today'] == protocol['source_cohort_date'] and
                context['chunk_policy'] == {'size': case['chunk_size'], 'overlap': case['chunk_overlap']} and
                context['max_calls'] == case['max_calls'] and context['max_chunks'] is None and
                context['budget_policy'] == {'max_usd': case['max_usd'], 'reservation_usd': case['reservation_usd']},
                'Extraction settings mismatch')
        identity = context['model_identity']
        expected_identity = {**protocol['model_spec'], 'pricing': protocol['pricing'], 'max_attempts': 1,
                             'agent_retries': 0, 'max_model_requests': 1, 'flex_fallback': False,
                             'execution_mode': mode}
        require(all(identity.get(k) == v for k, v in expected_identity.items()), 'Model settings mismatch')
        inventory = set(protocol['code_sha256'].values())
        require(all(context[k] in inventory for k in ('adapter_sha256', 'chunker_sha256', 'extractor_sha256')) and
                all(h in inventory for h in context['prompt_hashes'].values()) and
                all(identity[k] in inventory for k in ('domain_adapter_sha256', 'expanded_schema_sha256', 'condition_contract_sha256')),
                'Context code is not frozen')
        chunks = state['chunks']
        from bc_content.chunk import chunk_text
        expected_chunks=chunk_text(text,size=case['chunk_size'],overlap=case['chunk_overlap'])
        require([(c['start'],c['end']) for c in chunks]==[(c.start,c.end) for c in expected_chunks],'Native chunk boundaries differ')
        require(isinstance(chunks, list) and chunks and state['status'] == 'full_text_chunks_processed' and
                result['full_text_chunk_coverage'] is True, 'Incomplete chunk coverage')
        end = 0
        for i, chunk in enumerate(chunks):
            a, b = chunk['start'], chunk['end']
            require(chunk['index'] == i and type(a) is int and type(b) is int and 0 <= a < b <= len(text) and
                    a <= end and b > end and chunk['status'] == 'succeeded' and
                    hashlib.sha256(text[a:b].encode()).hexdigest() == chunk['text_sha256'], 'Invalid chunk coverage')
            end = b
        require(end == len(text), 'Source not fully covered')
        attempts = state['attempts']
        successes = state['successes']
        ledger = jsonl(directory / 'calls.private.jsonl')
        accounting = attempt_accounting(attempts, ledger, successes, case, protocol['model_spec']['model'])
        keys = accounting['successful_keys']
        cost = accounting['accounted_usd']
        failures = sum(a['status'] == 'failed' for a in attempts)
        require(report['backend_calls'] == len(attempts) and report['ledger_calls'] == len(ledger) and
                close(report['estimated_cost_usd'], cost) and report['chunks'] == len(chunks) and
                report['candidate_count'] == len(result['candidates']), 'Case accounting mismatch')
        require(result['canonical_records_written'] == 0 and result['domain_review_complete'] is False,
                'Canonical write or automatic review')
        total_calls += len(attempts)
        total_records += len(ledger)
        total_cost += cost
        total_priced += accounting['priced_cost_estimate_usd']
        total_unpriced += accounting['unpriced_attempts']
        total_held += accounting['held_unpriced_reservations_usd']
        failed_attempts += failures
        valid = {}
        for candidate in result['candidates']:
            key = (ident, candidate['candidate_id'])
            require(key not in candidates and candidate['candidate_id'] == digest({k: candidate[k] for k in FACT_KEYS}) and
                    candidate['source_document_id'] == case['source_document_id'] and
                    candidate['body_sha256'] == case['body_sha256'] and candidate['text_sha256'] == case['text_sha256'] and
                    candidate['accepted'] is False and candidate['review_status'] == 'unreviewed' and
                    candidate['request_hashes'] and set(candidate['request_hashes']) <= keys,
                    'Candidate identity mismatch')
            validator = domain.field_validator(schema, candidate['target_table'], candidate['target_field'])
            schema_ok = validator is not None and not list(validator.iter_errors(candidate['value']))
            if candidate['target_field'] == 'condition_clauses':
                from condition_expression import validate_condition_clauses
                schema_ok = schema_ok and not validate_condition_clauses(candidate['value'])
            flags = candidate['review_flags']
            require(isinstance(flags, list) and isinstance(candidate['field_schema_errors'], list), 'Invalid candidate flags')
            blocked_flags = {'field_schema_invalid', 'quote_unlocated', 'quote_location_ambiguous',
                             'supporting_quote_unlocated', 'supporting_quote_location_ambiguous',
                             'condition_source_quote_unlocated', 'condition_source_quote_location_ambiguous',
                             'condition_context_conflict', 'conflicting_field_candidates'}
            context_ok = (candidate['target_field'] != 'condition_clauses' or
                          all(clause['assertion_context'] == candidate['assertion_context'] for clause in candidate['value']))
            valid[key] = (quote_integrity(candidate, text) and schema_ok and not candidate['field_schema_errors']
                          and not blocked_flags.intersection(flags) and context_ok)
            candidates[key] = candidate
        case_reports[ident] = {'case_id': ident, 'family': case['family'], 'policy': case['policy'],
                               'candidate_count': len(result['candidates']), 'calls': len(attempts),
                               'cost_usd': accounting['priced_cost_estimate_usd'] if accounting['estimated_accounting_complete'] else None, 'accounted_usd': cost,
                               'priced_cost_estimate_usd': accounting['priced_cost_estimate_usd'],
                               'unpriced_attempts': accounting['unpriced_attempts'],
                               'held_unpriced_reservations_usd': accounting['held_unpriced_reservations_usd'],
                               'failed_attempts': failures, 'chunks': len(chunks), 'full_source_chunk_coverage': True,
                               'valid_candidates': sum(valid.values()), '_valid': valid}
    require(len(reserved) <= total_calls and
            total_calls == terminal['backend_reservation_count'] and total_records == terminal['backend_result_records'] and
            len(reserved) == terminal['http_reservation_count'] and terminal['provider_requests'] == (len(reserved) if mode=='provider' else 0) and
            len(events) == terminal['http_event_count'] and
            (not (http_failures or http_missing) or failed_attempts > 0),
            'Provider request accounting mismatch')
    accounting_complete = (total_unpriced == 0 and len(reserved) == total_calls and
                           http_missing == 0 and http_failures == 0)

    reviews = []
    for path in [coordinator_path, *reviewer_paths]:
        review = load(path)
        require(review['protocol_sha256'] == protocol_hash and isinstance(review['reviewer'], str) and
                review['reviewer'].strip(), 'Invalid review identity')
        labels, entries, slots = {}, {}, {}
        for row in review['candidates']:
            key = (row['case_id'], row['candidate_id'])
            require(key in candidates and key not in labels and row['disposition'] in LABELS and
                    type(row['high_impact']) is bool and isinstance(row['rationale'], str) and row['rationale'].strip() and
                    valid_spans(row['source_spans'], texts[key[0]]) and
                    (row['disposition'] != 'supported' or row['source_spans']) and
                    (candidates[key]['target_field'] == 'title' or row['high_impact']), 'Invalid candidate review')
            labels[key] = row['disposition']
            entries[key] = row
        require(labels.keys() == candidates.keys(), 'Review candidate population mismatch')
        for row in review['slots']:
            key = (row['case_id'], row['slot_id'])
            require(key in expected_slots and key not in slots and type(row['covered']) is bool and
                    isinstance(row['rationale'], str) and row['rationale'].strip() and
                    valid_spans(row['source_spans'], texts[key[0]]) and isinstance(row['candidate_ids'], list) and
                    isinstance(row['clause_indexes'], list), 'Invalid slot review')
            ids, indexes = row['candidate_ids'], row['clause_indexes']
            require(len(ids) == len(set(ids)) and len(indexes) == len(set(indexes)) and
                    all(type(index) is int and index >= 0 for index in indexes), 'Invalid slot references')
            for cid in ids:
                ck = (key[0], cid)
                require(ck in candidates and labels[ck] == 'supported' and
                        candidates[ck]['target_field'] == 'condition_clauses' and
                        isinstance(candidates[ck]['value'], list) and
                        all(index < len(candidates[ck]['value']) for index in indexes), 'Invalid condition reference')
            if row['covered']:
                require(len(ids) == 1 and len(indexes) == 1 and row['source_spans'], 'Covered slot needs one complete clause')
            slots[key] = row['covered']
        require(slots.keys() == expected_slots.keys(), 'Review slot population mismatch')
        reviews.append({'reviewer': review['reviewer'], 'labels': labels, 'entries': entries,
                        'slots': slots, 'sha256': sha(path)})
    require(len({r['reviewer'] for r in reviews}) == 3, 'Reviewer identities must differ')
    final = reviews[0]
    for ident, report in case_reports.items():
        keys = [k for k in candidates if k[0] == ident]
        counts = Counter(final['labels'][k] for k in keys)
        supported = counts['supported']
        critical = sum(final['entries'][k]['high_impact'] and final['labels'][k] != 'supported' for k in keys)
        slot_keys = [k for k in expected_slots if k[0] == ident]
        covered = sum(final['slots'][k] for k in slot_keys)
        fraction = supported / len(keys) if keys else None
        report.update(labels={label: counts[label] for label in sorted(LABELS)}, supported_fraction=fraction,
                      critical_non_supported=critical, slots_total=len(slot_keys), slots_covered=covered,
                      quote_and_schema_valid=all(report.pop('_valid').values()), canonical_records_written=0)
        report['ready'] = bool(keys and fraction >= 0.95 and critical == 0 and covered == len(slot_keys)
                               and report['quote_and_schema_valid'] and report['full_source_chunk_coverage'])
    policy_reports = {}
    for policy in sorted(policies):
        group = [r for r in case_reports.values() if r['policy'] == policy]
        count = sum(r['candidate_count'] for r in group)
        supported = sum(r['labels']['supported'] for r in group)
        fraction = supported / count if count else None
        source_quality_gate = bool(count and fraction >= 0.95 and all(r['ready'] for r in group))
        policy_reports[policy] = {'candidate_count': count, 'supported': supported, 'supported_fraction': fraction,
                                  'labels': {label: sum(r['labels'][label] for r in group) for label in sorted(LABELS)},
                                  'calls': sum(r['calls'] for r in group),
                                  'cost_usd': sum(r['priced_cost_estimate_usd'] for r in group) if accounting_complete else None,
                                  'accounted_usd': sum(r['accounted_usd'] for r in group),
                                  'priced_cost_estimate_usd': sum(r['priced_cost_estimate_usd'] for r in group),
                                  'failed_attempts': sum(r['failed_attempts'] for r in group),
                                  'unpriced_attempts': sum(r['unpriced_attempts'] for r in group),
                                  'held_unpriced_reservations_usd': sum(r['held_unpriced_reservations_usd'] for r in group),
                                  'slots_total': sum(r['slots_total'] for r in group),
                                  'slots_covered': sum(r['slots_covered'] for r in group),
                                  'source_quality_gate_passed': source_quality_gate,
                                  'gate_passed': source_quality_gate and accounting_complete}
    if fixture_root is not None:
        for row in case_reports.values():row['ready']=False
        for row in policy_reports.values():row['source_quality_gate_passed']=row['gate_passed']=False
    return {'schema_version': 'compound-chunk-policy-audit-1', 'execution_mode':mode,'fixture_only':fixture_root is not None, 'protocol_sha256': protocol_hash,
            'required_slots_sha256': slots_hash, 'cases': list(case_reports.values()), 'policies': policy_reports,
            'calls': total_calls, 'backend_result_records': total_records, 'cost_usd': total_priced if accounting_complete else None, 'accounted_usd': total_cost,
            'priced_cost_estimate_usd': total_priced, 'unpriced_attempts': total_unpriced,
            'held_unpriced_reservations_usd': total_held, 'failed_attempts': failed_attempts,
            'estimated_accounting_complete': accounting_complete,
            'http_failed_responses': http_failures, 'http_missing_responses': http_missing,
            'http_reservations': len(reserved),
            'http_responses': len(responses), 'http_events': len(events), 'http_cap': 16,
            'coordinator_review_sha256': reviews[0]['sha256'],
            'reviewer_file_sha256': [r['sha256'] for r in reviews[1:]],
            'ai_reviewer_agreement': agreement(reviews[1]['labels'], reviews[2]['labels']),
            'private_file_sha256': artifacts, 'canonical_records_written': 0,
            'overall_p4_closed': False,
            'scope': 'Two known documents; coordinator labels govern gates. Estimated accounting is not an invoice ceiling. AI review agreement is not human truth or accuracy.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('--coordinator', type=Path, required=True)
    parser.add_argument('--reviewer', type=Path, action='append', required=True)
    args = parser.parse_args()
    result = audit(args.protocol, args.coordinator, args.reviewer)
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({'status': 'failed', 'error_class': type(error).__name__}), file=sys.stderr)
        sys.exit(1)
