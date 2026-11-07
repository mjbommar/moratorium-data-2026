#!/usr/bin/env python3
"""Run the frozen chunk-policy comparison, or exercise it offline with --mock.

Hash dictionaries map absolute filenames to SHA-256 hex digests. The required
slots digest must also occur in one of those dictionaries. Pricing is the full
serialized bc-llm Price (input, output, cache_read, cache_write, source).
The proxy fingerprint hashes sorted UTF-8 JSON with keys proxy, HTTP_PROXY,
HTTPS_PROXY, ALL_PROXY, NO_PROXY, OPENAI_BASE_URL, OPENAI_ORG_ID and
OPENAI_PROJECT_ID, including nulls for unset values.
"""
import argparse
import asyncio
import dataclasses
import datetime as dt
import hashlib
import importlib.metadata
import json
import logging
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
POLICY = dict(max_attempts=1, agent_retries=0, max_model_requests=1, flex_fallback=False)
CAP = 67108864


def require(condition):
    if not condition:
        raise ValueError('Preflight or execution invariant failed')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()


def sha(path):
    return digest(Path(path).read_bytes())


def check_hashes(mapping):
    require(isinstance(mapping, dict) and bool(mapping))
    for name, expected in mapping.items():
        require(isinstance(name, str) and Path(name).is_absolute())
        require(isinstance(expected, str) and re.fullmatch(r'[0-9a-f]{64}', expected))
        require(sha(name) == expected)


def tree_bytes(root):
    total = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(base) / name
            require(not path.is_symlink())
            if path.is_file():
                total += path.stat().st_size
    return total


def durable_json(path, value, exclusive=False, storage_policy=None):
    require(storage_policy is not None)
    storage_policy.save_json(path, value, exclusive=exclusive)


def verify_sources(protocol):
    from runtime_file_pins import verify_manifest
    verify_manifest(protocol['runtime_files_path'], protocol['runtime_files_sha256'])
    check_hashes(protocol['code_sha256'])
    check_hashes(protocol['canonical_inputs_sha256'])
    require((ROOT / 'data/expanded').resolve().name == protocol['canonical_snapshot'])
    for case in protocol['cases']:
        for field in ('body', 'text'):
            path = Path(case[field + '_path'])
            require(path.is_absolute() and sha(path) == case[field + '_sha256'])


def preflight(protocol, protocol_path, raw, mock):
    require(protocol['schema_version'] == 'compound-contract-development-1')
    require(protocol['experiment_identity'] == 'revised-complete-condition-contract-development-2026-11-07')
    require(protocol['private_root'] == '/data0/moratorium-refresh-2026/frozen-domain-evaluation/compound-contract-evaluation')
    root = Path(protocol['private_root'])
    require(root.is_absolute() and root.is_dir() and not root.is_symlink())
    require(protocol['max_http_requests'] == 16 and type(protocol['max_http_requests']) is int)
    require(protocol['max_private_bytes'] == CAP and type(protocol['max_private_bytes']) is int)
    require(tree_bytes(root) <= CAP)
    verify_sources(protocol)
    admission_path = protocol_path.with_name('storage-admission.json')
    admission = json.loads(admission_path.read_text())
    layout = ROOT / admission['layout']
    expected = {str(root), str(root/'preflight'), str(root/'provider'), str(root/'provider/http')}
    expected.update(str(root/'provider'/case['case_id']) for case in protocol['cases'])
    require(set(admission['outputs']) == expected and len(admission['outputs']) == 8)
    require(admission['private_byte_cap'] == CAP)
    require(str(admission_path.resolve()) in protocol['code_sha256'])
    require(str(layout.resolve()) in protocol['code_sha256'])
    command = [sys.executable, '/home/mjbommar/projects/bc/bc-modules/scripts/check-storage-layout.py', str(layout)]
    for output in admission['outputs']:
        command.extend(['--output', output])
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    slots = protocol['required_slots_sha256']
    require(isinstance(slots, str) and slots in set(protocol['canonical_inputs_sha256'].values()) | set(protocol['code_sha256'].values()))
    versions = protocol['dependency_versions']
    require(isinstance(versions, dict) and bool(versions))
    for name, version in versions.items():
        require(isinstance(name, str) and isinstance(version, str) and importlib.metadata.version(name) == version)
    cases = protocol['cases']
    require(isinstance(cases, list) and len(cases) == 4)
    ids = [case['case_id'] for case in cases]
    require(len(set(ids)) == 4 and all(isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', x) for x in ids))
    order = protocol['execution_order']
    require(isinstance(order, list) and len(order) == 4 and set(order) == set(ids))
    ordered = [next(c for c in cases if c['case_id'] == name) for name in order]
    require([c['max_calls'] for c in ordered] == [4, 8, 2, 2])
    require(all(type(c['max_calls']) is int and c['reservation_usd'] == 0.75 for c in ordered))
    require(all(type(c['max_usd']) in (int, float) and math.isfinite(c['max_usd']) and c['max_usd'] >= 0.75 for c in ordered))
    require(abs(sum(c['max_usd'] for c in ordered) - 12) < 1e-9)
    require(all(abs(c['max_usd']-c['max_calls']*c['reservation_usd'])<1e-9 for c in ordered))
    for case in ordered:
        require(type(case['chunk_size']) is int and case['chunk_size'] > 0)
        require(type(case['chunk_overlap']) is int and 0 <= case['chunk_overlap'] < case['chunk_size'])
        require(all(isinstance(case[k], str) and case[k] for k in ('source_document_id', 'title', 'subject_label', 'url')))
        require(bool(Path(case['text_path']).read_text(encoding='utf-8').strip()))
    require(isinstance(protocol['question'], str) and bool(protocol['question'].strip()))
    dt.date.fromisoformat(protocol['source_cohort_date'])
    if not mock:
        require(not (root / 'provider').exists() and not (root / 'provider').is_symlink())
        relative = protocol_path.resolve().relative_to(ROOT)
        committed = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:' + relative.as_posix()], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
        require(committed == raw)
    return root, ordered


def mock_response(request, count, first_failure=False):
    import httpx2
    count.append(1)
    if first_failure and len(count)==1:
        return httpx2.Response(503,json={'error':{'message':'Offline synthetic failure'}})
    payload = json.loads(request.content)
    schema = payload['text']['format']['schema']
    properties = schema['properties']
    if 'claims' in properties:
        output = dict(relevance=1, summary='Offline fixture '+str(len(count)), claims=[], unresolved_fields=[])
    else:
        require(set(properties) == {'summary'})
        output = dict(summary='Offline fixture')
    response = dict(id='resp_mock', object='response', created_at=0, status='completed', model='gpt-6-sol', output=[dict(type='message', id='msg_mock', role='assistant', status='completed', content=[dict(type='output_text', text=json.dumps(output), annotations=[])])], usage=dict(input_tokens=10, output_tokens=5, total_tokens=15))
    return httpx2.Response(200, json=response)


def http_counts(audit):
    with audit.ledger.open() as stream:
        rows = audit.events(stream)
    return len(rows), sum(row['state'] == 'reserved' for row in rows)


def ledger_writer(path, storage_policy):
    def record(row):
        storage_policy.append_jsonl(path, row.model_dump(mode='json'))
    return record


def line_count(path):
    return len(path.read_bytes().splitlines()) if path.exists() else 0


async def execute(protocol, root, ordered, raw, mock, settings, spec, pricing, first_failure=False, protocol_path=None, storage_policy=None):
    import httpx2
    import extract_domain_candidates as domain
    from bc_llm import PydanticAIBackend, RoleRegistry
    from controlled_model_transport import ControlledModelTransport

    mode = 'offline_mock' if mock else 'provider'
    http = root / 'http'
    http.mkdir(mode=0o700)
    audit = ControlledModelTransport(http, max_requests=16, context_sha256=digest(raw), storage_policy=storage_policy)
    mock_requests = []
    summaries = []
    failed = False
    identity = {**spec.model_dump(mode='json'), 'pricing': dataclasses.asdict(pricing.get(spec.model)), **POLICY, 'execution_mode': mode}
    today = dt.date.fromisoformat(protocol['source_cohort_date'])
    for case in ordered:
        if failed:
            summaries.append(dict(case_id=case['case_id'], status='not_attempted'))
            continue
        directory = root / case['case_id']
        directory.mkdir(mode=0o700)
        ledger = directory / 'calls.private.jsonl'
        backend = None
        report = dict(case_id=case['case_id'], status='failed', replay_without_calls=False)
        try:
            verify_sources(protocol)
            require(tree_bytes(Path(protocol['private_root'])) <= CAP)
            if mock:
                factory = lambda _: audit.client_factory(None, transport=httpx2.MockTransport(lambda request: mock_response(request, mock_requests, first_failure)))
            else:
                factory = audit.client_factory
            backend = PydanticAIBackend(RoleRegistry(roles={'extractor': spec}), pricing=pricing, ledger=ledger_writer(ledger, storage_policy), proxy=None if mock else settings.proxy_url(), http_client_factory=factory, **POLICY)
            resolve = backend.model_resolver
            backend.model_resolver = lambda requested: audit.require_model(resolve(requested))
            backend.model_resolver(spec)
            text = Path(case['text_path']).read_text(encoding='utf-8')
            doc = dict(doc_id=case['source_document_id'], text=text, title=case['title'], url=case['url'], final_url=None, published=None, language='en', body_sha256=case['body_sha256'], text_sha256=case['text_sha256'])
            cells = [dict(cell_id=case['case_id'], subject_label=case['subject_label'], topic_label='conditions', prospective=False, window_start='2026-01-01', window_end=today.isoformat())]
            kwargs = dict(storage_policy=storage_policy, doc=doc, cells=cells, backend=backend, question=protocol['question'], today=today, max_calls=case['max_calls'], model_identity=identity, budget_policy=dict(max_usd=case['max_usd'], reservation_usd=case['reservation_usd']), chunk_size=case['chunk_size'], chunk_overlap=case['chunk_overlap'])
            result = await domain.run(directory, **kwargs)
            require(result['full_text_chunk_coverage'] and result['canonical_records_written'] == 0 and all(c['accepted'] is False for c in result['candidates']))
            require(backend.ledger_errors == 0)
            before = (line_count(ledger), http_counts(audit))
            replay = await domain.run(directory, **kwargs)
            require(replay == result and before == (line_count(ledger), http_counts(audit)) and backend.ledger_errors == 0)
            state = json.loads((directory / 'state.private.json').read_text())
            report.update(status='finished', replay_without_calls=True, chunks=len(state['chunks']), backend_calls=len(state['attempts']), ledger_calls=line_count(ledger), candidate_count=len(result['candidates']), estimated_cost_usd=sum(a.get('charged_usd', a.get('reserved_usd', 0)) for a in state['attempts']), result_sha256=sha(directory / 'domain-candidates.private.json'))
            if mock:
                require(report['backend_calls'] == ([4,7,1,1] if first_failure else [3,7,1,1])[len(summaries)])
                from audit import attempt_accounting
                records=[json.loads(line) for line in ledger.read_text().splitlines()]
                accounting=attempt_accounting(state['attempts'],records,state['successes'],case,spec.model)
                report['mock_unpriced_attempts']=accounting['unpriced_attempts']
                report['mock_held_reservations_usd']=accounting['held_unpriced_reservations_usd']
                require(accounting['unpriced_attempts']==(1 if first_failure and not summaries else 0))
                require(abs(accounting['accounted_usd']-report['estimated_cost_usd'])<1e-9)
            require(tree_bytes(Path(protocol['private_root'])) <= CAP)
        except Exception as error:
            report.update(status='failed', error_class=type(error).__name__)
            failed = True
        finally:
            if backend is not None:
                try:
                    await backend.aclose()
                except Exception as error:
                    report.update(status='failed', error_class=type(error).__name__)
                    failed = True
        state_path = directory / 'state.private.json'
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text())
                report['backend_calls'] = len(state['attempts'])
                report['ledger_calls'] = line_count(ledger)
                report['estimated_cost_usd'] = sum(a.get('charged_usd', a.get('reserved_usd', 0)) for a in state['attempts'])
            except Exception as error:
                report.update(status='failed', error_class=type(error).__name__)
                failed = True
        durable_json(directory / 'terminal.private.json', report, storage_policy=storage_policy)
        summaries.append(report)
    verify_error = None
    try:
        verify_sources(protocol)
        require(tree_bytes(Path(protocol['private_root'])) <= CAP)
    except Exception as error:
        verify_error = type(error).__name__
        failed = True
    events, reservations = http_counts(audit)
    terminal = dict(mode=mode, status='failed' if failed else 'finished', cases=summaries, backend_result_records=sum(x.get('ledger_calls', 0) for x in summaries), backend_reservation_count=sum(x.get('backend_calls', 0) for x in summaries), http_reservation_count=reservations, http_event_count=events, provider_requests=0 if mock else reservations, all_replays_no_extra_calls=not failed and all(x['replay_without_calls'] for x in summaries))
    if verify_error:
        terminal['postflight_error_class'] = verify_error
    if mock:
        terminal['mock_http_requests'] = len(mock_requests)
        if not failed:
            require(len(mock_requests) == (13 if first_failure else 12) and reservations == len(mock_requests))
    durable_json(root / 'terminal.private.json', terminal, storage_policy=storage_policy)
    if mock and not failed:
        import audit as comparison_audit
        require(protocol_path is not None)
        durable_json(root/'execution.private.json',dict(mode='offline_mock',protocol_sha256=digest(raw),state='started'),exclusive=True,storage_policy=storage_policy)
        slots=json.loads(protocol_path.with_name('required-slots.json').read_text())['families']
        review_paths=[]
        for label in ('coordinator','reviewer1','reviewer2'):
            review=dict(protocol_sha256=digest(raw),reviewer='offline-'+label,candidates=[],slots=[dict(case_id=c['case_id'],slot_id=slot['slot_id'],covered=False,candidate_ids=[],clause_indexes=[],rationale='Offline mock has no source facts; no quality score.',source_spans=[]) for c in ordered for slot in slots[c['family']]])
            target=root/(label+'.private.json');durable_json(target,review,storage_policy=storage_policy);review_paths.append(target)
        checked=comparison_audit.audit(protocol_path,review_paths[0],review_paths[1:],fixture_root=root)
        require(checked['fixture_only'] and not any(p['gate_passed'] for p in checked['policies'].values()))
        terminal['offline_auditor_passed']=True
        terminal['offline_audited_attempts']=checked['calls']
        terminal['offline_audited_result_records']=checked['backend_result_records']
        terminal['offline_audited_unpriced_attempts']=checked['unpriced_attempts']
        terminal['offline_audited_held_reservations_usd']=checked['held_unpriced_reservations_usd']
        durable_json(root/'terminal.private.json',terminal,storage_policy=storage_policy)
    if tree_bytes(Path(protocol['private_root'])) > CAP:
        terminal['status'] = 'failed'
        terminal['postflight_error_class'] = 'PrivateStorageExceeded'
        durable_json(root / 'terminal.private.json', terminal, storage_policy=storage_policy)
    return terminal


def main():
    # Library errors may contain provider response bodies; only classes are reported.
    logging.disable(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument('protocol', type=Path)
    parser.add_argument('--mock', action='store_true')
    parser.add_argument('--mock-first-failure',action='store_true')
    args = parser.parse_args()
    require(not args.mock_first_failure or args.mock)
    raw = args.protocol.read_bytes()
    protocol = json.loads(raw)
    paths = protocol['runtime_import_paths']
    require(isinstance(paths, list) and all(isinstance(p, str) and Path(p).is_absolute() and Path(p).is_dir() for p in paths))
    sys.path[:0] = paths + [str(ROOT / 'scripts')]
    root, ordered = preflight(protocol, args.protocol, raw, args.mock)
    from bc_llm import BcLlmSettings, ModelSpec
    import inspect
    import bc_evidence.extract as extractor
    from bc_content.chunk import chunk_text
    import extract_domain_candidates as domain
    settings = BcLlmSettings()
    proxy = {'proxy': settings.proxy_url(), **{key: os.environ.get(key) for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY','OPENAI_BASE_URL','OPENAI_ORG_ID','OPENAI_PROJECT_ID')}}
    require(digest(encoded(proxy)) == protocol['routing_fingerprint'])
    spec = ModelSpec.model_validate(protocol['model_spec'])
    require(spec.model == 'openai:gpt-6-sol' and spec.output_mode == 'native')
    pricing = settings.pricing()
    require(pricing.get(spec.model) is not None and dataclasses.asdict(pricing.get(spec.model)) == protocol['pricing'])
    # Require the actual adapters and this runner in the frozen code inventory.
    required = [Path(__file__).resolve(), ROOT / 'scripts/extract_domain_candidates.py', ROOT / 'scripts/extract_document_resumable.py', ROOT / 'scripts/controlled_model_transport.py', ROOT / 'scripts/condition_expression.py', domain.SCHEMA, Path(extractor.__file__).resolve(), Path(inspect.getfile(chunk_text)).resolve(), *sorted((Path(extractor.__file__).resolve().parent / 'prompts').glob('extract*'))]
    require(all(str(p) in protocol['code_sha256'] for p in required))
    from private_run_storage import PrivateRunStorage
    storage_policy = PrivateRunStorage(root, CAP)
    if args.mock:
        preflight_root = root / 'preflight'
        preflight_root.mkdir(mode=0o700, exist_ok=True)
        require(preflight_root.is_dir() and not preflight_root.is_symlink())
        with tempfile.TemporaryDirectory(dir=preflight_root) as tmp, patch.dict(os.environ, {'OPENAI_API_KEY': 'offline-test', 'PYDANTIC_AI_NO_BANNER': '1'}):
            terminal = asyncio.run(execute(protocol, Path(tmp), ordered, raw, True, settings, spec, pricing,args.mock_first_failure,args.protocol,storage_policy))
    else:
        provider = root / 'provider'
        provider.mkdir(mode=0o700)
        durable_json(provider / 'execution.private.json', dict(mode='provider', protocol_sha256=digest(raw), state='started', pid=os.getpid(), started_at=dt.datetime.now(dt.timezone.utc).isoformat(), driver_sha256=sha(__file__), git_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()), exclusive=True, storage_policy=storage_policy)
        code_dir = provider / 'executed-code'
        code_dir.mkdir(mode=0o700)
        for filename, expected in protocol['code_sha256'].items():
            target = code_dir / (expected + '-' + Path(filename).name)
            if not target.exists():
                storage_policy.put_bytes(target, Path(filename).read_bytes(), exclusive=True, mode=0o400)
            require(sha(target) == expected)
        try:
            terminal = asyncio.run(execute(protocol, provider, ordered, raw, False, settings, spec, pricing, storage_policy=storage_policy))
        except Exception as error:
            ledger = provider / 'http/http-attempts.private.jsonl'
            reservations = 0
            if ledger.exists():
                try:
                    reservations = sum(json.loads(line)['state'] == 'reserved' for line in ledger.read_text().splitlines())
                except Exception:
                    reservations = None
            terminal = dict(mode='provider', status='failed', error_class=type(error).__name__, backend_result_records=None, http_reservation_count=reservations, cases=[dict(case_id=c['case_id'], status='not_attempted') for c in ordered])
            durable_json(provider / 'terminal.private.json', terminal, storage_policy=storage_policy)
    print(json.dumps(terminal, sort_keys=True, allow_nan=False))
    return 0 if terminal['status'] == 'finished' else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps(dict(status='failed', error_class=type(error).__name__)), file=sys.stderr)
        sys.exit(1)
