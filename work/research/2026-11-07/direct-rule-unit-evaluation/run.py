#!/usr/bin/env python3
"""Fresh-only direct rule-unit evaluation. Public diagnostics contain error classes only."""
import argparse
import asyncio
import dataclasses
import datetime as dt
import hashlib
import importlib.metadata
import json
import logging
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
PRIVATE_ROOT = '/data0/moratorium-refresh-2026/frozen-domain-evaluation/direct-rule-unit-evaluation'
PYTHON = '/home/mjbommar/projects/bc/bc-modules/.venv/bin/python3.14'
CAP = 134217728
POLICY = dict(max_attempts=1, agent_retries=0, max_model_requests=1, flex_fallback=False)
MODEL = dict(model='openai:gpt-6-sol', service_tier=None, reasoning_effort='low', temperature=None, max_tokens=14000, timeout_s=120.0, cache_instructions=False, output_mode='native')


def require(condition):
    if not condition:
        raise ValueError('Execution invariant failed')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()


def check_hashes(mapping):
    require(isinstance(mapping, dict) and bool(mapping))
    for name, value in mapping.items():
        require(isinstance(name, str) and Path(name).is_absolute() and isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None)
        require(sha(name) == value)


def tree_bytes(root):
    total = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            p = Path(base) / name
            info = p.lstat()
            require(not stat.S_ISLNK(info.st_mode))
            if stat.S_ISREG(info.st_mode):
                require(info.st_nlink == 1)
                total += info.st_size
            else:
                require(stat.S_ISDIR(info.st_mode))
    return total


def verify_sources(protocol):
    from runtime_file_pins import verify_manifest
    verify_manifest(protocol['runtime_files_path'], protocol['runtime_files_sha256'])
    for key in ('code_sha256', 'inputs_sha256', 'canonical_inputs_sha256'):
        check_hashes(protocol[key])
    require((ROOT / 'data/expanded').resolve().name == protocol['canonical_snapshot'])
    for case in protocol['cases']:
        for field in ('body', 'text', 'plan'):
            p = Path(case[field + '_path'])
            require(p.is_absolute() and sha(p) == case[field + '_sha256'])
        require(Path(case['text_path']).stat().st_size <= 200000)


def verify_runtime(protocol):
    from bc_llm import BcLlmSettings, ModelSpec
    require(Path(sys.executable).absolute() == Path(PYTHON))
    for name, version in protocol['dependency_versions'].items():
        require(importlib.metadata.version(name) == version)
    settings = BcLlmSettings()
    proxy = {'proxy': settings.proxy_url(), **{key: os.environ.get(key) for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'OPENAI_BASE_URL', 'OPENAI_ORG_ID', 'OPENAI_PROJECT_ID')}}
    require(digest(encoded(proxy)) == protocol['routing_fingerprint'])
    spec = ModelSpec.model_validate(protocol['model_spec'])
    require(spec.model_dump(mode='json') == MODEL)
    pricing = settings.pricing()
    require(pricing.get(spec.model) is not None and dataclasses.asdict(pricing.get(spec.model)) == protocol['pricing'])
    return settings, spec, pricing


def preflight(protocol, protocol_path, raw, mock):
    require(Path(sys.executable).absolute() == Path(PYTHON))
    require(protocol['schema_version'] == 'direct-rule-unit-development-1')
    require(protocol['private_root'] == PRIVATE_ROOT)
    root = Path(PRIVATE_ROOT)
    require(root.is_dir() and not root.is_symlink() and stat.S_IMODE(root.stat().st_mode) & 0o077 == 0)
    require(type(protocol['max_http_requests']) is int and protocol['max_http_requests'] == 86)
    require(type(protocol['max_private_bytes']) is int and protocol['max_private_bytes'] == CAP)
    require(type(protocol['max_source_bytes']) is int and protocol['max_source_bytes'] == 200000)
    require(protocol['backend_policy'] == POLICY and protocol['tool_configuration'] == {'toolsets': [], 'tools': []} and tree_bytes(root) <= CAP)
    cases = protocol['cases']
    require(isinstance(cases, list) and len(cases) == 2)
    for case, case_id, family, count, dollars in zip(cases, ('mandan-direct', 'harwood-direct'), ('mandan', 'harwood'), (20, 66), (15, 49.5)):
        require(case['case_id'] == case_id and case['family'] == family)
        require(type(case['units']) is int and case['units'] == count and type(case['max_calls']) is int and case['max_calls'] == count)
        require(type(case['max_usd']) in (int, float) and case['max_usd'] == dollars and type(case['reservation_usd']) in (int, float) and case['reservation_usd'] == .75)
        require(all(isinstance(case[k], str) and case[k] for k in ('source_document_id', 'title', 'url')))
        plan = json.loads(Path(case['plan_path']).read_bytes())
        require(len(plan['units']) == count and plan['source_text_sha256'] == case['text_sha256'])
    require(protocol.get('execution_order', [c['case_id'] for c in cases]) == [c['case_id'] for c in cases])
    require(protocol['required_slots_sha256'] in set(protocol['code_sha256'].values()) | set(protocol['inputs_sha256'].values()) | set(protocol['canonical_inputs_sha256'].values()))
    require(isinstance(protocol['dependency_versions'], dict) and bool(protocol['dependency_versions']))
    for name, version in protocol['dependency_versions'].items():
        require(importlib.metadata.version(name) == version)
    dt.date.fromisoformat(protocol['source_cohort_date'])
    required = [Path(__file__).resolve(), *(ROOT / 'scripts' / n for n in ('extract_rule_units.py', 'condition_expression.py', 'extract_document_resumable.py', 'controlled_model_transport.py', 'private_run_storage.py', 'runtime_file_pins.py'))]
    require(all(str(p) in protocol['code_sha256'] for p in required))
    verify_sources(protocol)
    admission_path = protocol_path.with_name('storage-admission.json')
    admission = json.loads(admission_path.read_text())
    layout = ROOT / admission['layout']
    expected = {str(root), str(root/'preflight'), str(root/'provider'), str(root/'provider/http'), *(str(root/'provider'/c['case_id']) for c in cases)}
    require(set(admission['outputs']) == expected and admission['private_byte_cap'] == CAP)
    require(str(admission_path.resolve()) in protocol['code_sha256'] and str(layout.resolve()) in protocol['code_sha256'])
    cmd = [sys.executable, '/home/mjbommar/projects/bc/bc-modules/scripts/check-storage-layout.py', str(layout)]
    for output in admission['outputs']:
        cmd.extend(['--output', output])
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not mock:
        require(not (root/'provider').exists() and not (root/'provider').is_symlink())
        relative = protocol_path.resolve().relative_to(ROOT)
        committed = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:' + relative.as_posix()], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
        require(committed == raw)
    return root, cases


def verify_execution(protocol, protocol_path, raw, execution, mock):
    require(protocol_path.read_bytes() == raw)
    for filename, expected in protocol['code_sha256'].items():
        require(sha(execution/'executed-code'/(expected+'-'+Path(filename).name)) == expected)
    admission = json.loads(protocol_path.with_name('storage-admission.json').read_bytes())
    cmd = [sys.executable, '/home/mjbommar/projects/bc/bc-modules/scripts/check-storage-layout.py', admission['layout']]
    for output in admission['outputs']:
        cmd.extend(['--output', output])
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not mock:
        relative = protocol_path.resolve().relative_to(ROOT)
        committed = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:' + relative.as_posix()], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
        require(committed == raw)


def line_count(path):
    return len(path.read_bytes().splitlines()) if path.exists() else 0


def http_counts(audit):
    with audit.ledger.open() as stream:
        rows = audit.events(stream)
    require(json.loads((audit.directory/'http-policy.private.json').read_bytes()) == audit.policy)
    return sum(r['state'] == 'reserved' for r in rows), sum(r['state'] == 'response' for r in rows)


def mock_response(request, calls, fail_first):
    import httpx2
    payload = json.loads(request.content)
    require(payload['text']['format']['type'] == 'json_schema' and not payload.get('tools'))
    calls.append(1)
    if fail_first and len(calls) == 1:
        return httpx2.Response(503, json={'error': {'message': 'offline synthetic failure'}})
    # The local slot is encoded at the end of the source prompt.
    marker = 'Local slot (JSON):\n'
    # Read the actual SDK message structure instead of depending on an ordering queue.
    def strings(v):
        if isinstance(v, str): yield v
        elif isinstance(v, dict):
            for x in v.values(): yield from strings(x)
        elif isinstance(v, list):
            for x in v: yield from strings(x)
    prompts = [s for s in strings(payload) if marker in s]
    require(len(prompts) == 1)
    uid = json.loads(prompts[0].rsplit(marker, 1)[1])['unit_id']
    output = dict(unit_id=uid, outcome='unresolved', clause=None, supporting_quotes=[], unresolved_reason='Offline synthetic unresolved')
    response = dict(id='resp_mock', object='response', created_at=0, status='completed', model='gpt-6-sol', output=[dict(type='message', id='msg_mock', role='assistant', status='completed', content=[dict(type='output_text', text=json.dumps(output), annotations=[])])], usage=dict(input_tokens=10, output_tokens=5, total_tokens=15))
    return httpx2.Response(200, json=response)


def case_report(directory, case, status, replay, error=None):
    state_path = directory/'rule-units-state.private.json'
    packet_path = directory/'rule-units-candidates.private.json'
    state = json.loads(state_path.read_bytes()) if state_path.exists() else None
    packet = json.loads(packet_path.read_bytes()) if packet_path.exists() else None
    report = dict(case_id=case['case_id'], status=status, backend_calls=len(state['attempts']) if state else 0, ledger_calls=line_count(directory/'calls.private.jsonl'), planned_count=case['units'], candidate_count=packet['candidate_count'] if packet else 0, unresolved_count=packet['unresolved_count'] if packet else case['units'], replay_without_calls=replay)
    if state:
        report['held_reservations_usd'] = sum(a['reserved_usd'] for a in state['attempts'] if a['status'] != 'succeeded' and 'charged_usd' not in a)
    if error: report['error_class'] = error
    return report


async def execute(protocol, root, cases, raw, mock, settings, spec, pricing, first_failure, storage, protocol_path=None):
    import httpx2
    import extract_rule_units as rules
    from bc_llm import PydanticAIBackend, RoleRegistry
    from controlled_model_transport import ControlledModelTransport
    mode = 'offline_mock' if mock else 'provider'
    http = root/'http'; http.mkdir(mode=0o700)
    audit = ControlledModelTransport(http, max_requests=86, context_sha256=digest(raw), storage_policy=storage)
    calls, reports = [], []
    global_error = None
    identity = {**spec.model_dump(mode='json'), 'pricing': dataclasses.asdict(pricing.get(spec.model)), **POLICY, 'execution_mode': mode}
    for case in cases:
        directory = root/case['case_id']; directory.mkdir(mode=0o700)
        backend = None; status = 'failed'; error = None; replay = False
        try:
            verify_sources(protocol); verify_runtime(protocol)
            if protocol_path is not None: verify_execution(protocol, protocol_path, raw, root, mock)
            require(tree_bytes(Path(PRIVATE_ROOT)) <= CAP)
            http_counts(audit)
            ledger = directory/'calls.private.jsonl'
            def record(row): storage.append_jsonl(ledger, row.model_dump(mode='json'))
            if mock:
                from openai import AsyncOpenAI
                from pydantic_ai.models.openai import OpenAIResponsesModel
                from pydantic_ai.providers.openai import OpenAIProvider
                client = audit.client_factory(None, transport=httpx2.MockTransport(lambda request: mock_response(request, calls, first_failure)))
                sdk = AsyncOpenAI(api_key='offline-test', http_client=client, max_retries=0)
                resolved = audit.require_model(OpenAIResponsesModel('gpt-6-sol', provider=OpenAIProvider(openai_client=sdk)))
                backend = PydanticAIBackend(RoleRegistry(roles={'extractor': spec}), pricing=pricing, ledger=record, model_resolver=lambda _: audit.require_model(resolved), toolsets=(), **POLICY)
            else:
                backend = PydanticAIBackend(RoleRegistry(roles={'extractor': spec}), pricing=pricing, ledger=record, proxy=settings.proxy_url(), http_client_factory=audit.client_factory, toolsets=(), **POLICY)
                resolve = backend.model_resolver
                backend.model_resolver = lambda requested: audit.require_model(resolve(requested))
                backend.model_resolver(spec)
            require(not backend.toolsets and backend.max_attempts == 1 and backend.agent_retries == 0 and not backend.flex_fallback and backend.usage_limits.request_limit == 1)
            doc = dict(doc_id=case['source_document_id'], text=Path(case['text_path']).read_text(encoding='utf-8'), title=case['title'], url=case['url'], body_sha256=case['body_sha256'], text_sha256=case['text_sha256'])
            plan = json.loads(Path(case['plan_path']).read_bytes())
            kwargs = dict(backend=backend, model_identity=identity, today=dt.date.fromisoformat(protocol['source_cohort_date']), max_calls=case['max_calls'], max_usd=case['max_usd'], reservation_usd=case['reservation_usd'], max_source_bytes=200000, settings={}, storage_policy=storage)
            result = await rules.run(directory, doc, plan, **kwargs)
            require(result['planned_count'] == case['units'] and result['source_coverage']['successful_units'] == case['units'] and backend.ledger_errors == 0)
            before = (line_count(ledger), http_counts(audit))
            again = await rules.run(directory, doc, plan, **kwargs)
            require(result == again and before == (line_count(ledger), http_counts(audit)) and backend.ledger_errors == 0)
            replay = True; status = 'finished'
        except Exception as exc:
            error = type(exc).__name__
        finally:
            if backend is not None:
                try:
                    await backend.aclose()
                    if mock: await sdk.close()
                except Exception as exc:
                    status = 'failed'; error = type(exc).__name__
        report = case_report(directory, case, status, replay, error)
        storage.save_json(directory/'terminal.private.json', report, exclusive=True)
        reports.append(report)
        # A failed case is never replayed. Continue only after global controls revalidate.
        try:
            verify_sources(protocol); verify_runtime(protocol)
            if protocol_path is not None: verify_execution(protocol, protocol_path, raw, root, mock)
            require(tree_bytes(Path(PRIVATE_ROOT)) <= CAP)
            reservations, responses = http_counts(audit)
            require(reservations <= 86 and responses <= reservations and reservations == sum(r['backend_calls'] for r in reports))
        except Exception as exc:
            global_error = type(exc).__name__
            break
    for case in cases[len(reports):]:
        directory = root/case['case_id']; directory.mkdir(mode=0o700)
        report = case_report(directory, case, 'not_attempted', False)
        storage.save_json(directory/'terminal.private.json', report, exclusive=True); reports.append(report)
    try:
        verify_sources(protocol); verify_runtime(protocol)
        if protocol_path is not None: verify_execution(protocol, protocol_path, raw, root, mock)
        require(tree_bytes(Path(PRIVATE_ROOT)) <= CAP)
        reservations, responses = http_counts(audit)
    except Exception as exc:
        global_error = type(exc).__name__; reservations = responses = None
    success = not global_error and all(r['status'] == 'finished' for r in reports)
    terminal = dict(mode=mode, status='finished' if success else 'failed', cases=reports, http_reservation_count=reservations, http_response_count=responses, backend_result_records=sum(r['ledger_calls'] for r in reports), provider_requests=0 if mock else reservations, all_successful_replays_no_extra_calls=all(r['replay_without_calls'] for r in reports if r['status'] == 'finished'), failure_policy='Stop the failing case without retry; continue the other fixed case only after global pins, storage and transport revalidate.')
    if global_error: terminal['postflight_error_class'] = global_error
    if mock: terminal['mock_http_requests'] = len(calls)
    storage.save_json(root/'terminal.private.json', terminal, exclusive=True)
    return terminal


def main():
    logging.disable(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument('protocol', type=Path); parser.add_argument('--mock', action='store_true'); parser.add_argument('--mock-first-failure', action='store_true')
    args = parser.parse_args(); require(not args.mock_first_failure or args.mock)
    raw = args.protocol.read_bytes(); protocol = json.loads(raw)
    paths = protocol['runtime_import_paths']
    require(isinstance(paths, list) and all(isinstance(p, str) and Path(p).is_absolute() and Path(p).is_dir() for p in paths))
    sys.path[:0] = paths + [str(ROOT/'scripts')]
    root, cases = preflight(protocol, args.protocol, raw, args.mock)
    settings, spec, pricing = verify_runtime(protocol)
    from private_run_storage import PrivateRunStorage
    storage = PrivateRunStorage(root, CAP)
    # Validate both complete plans and every anchor before either case may dispatch.
    import extract_rule_units as rules
    identity = {**spec.model_dump(mode='json'), 'pricing': dataclasses.asdict(pricing.get(spec.model)), **POLICY, 'execution_mode': 'offline_mock' if args.mock else 'provider'}
    for case in cases:
        doc = dict(doc_id=case['source_document_id'], text=Path(case['text_path']).read_text(encoding='utf-8'), title=case['title'], url=case['url'], body_sha256=case['body_sha256'], text_sha256=case['text_sha256'])
        rules.prepare(doc, json.loads(Path(case['plan_path']).read_bytes()), model_identity=identity, today=dt.date.fromisoformat(protocol['source_cohort_date']), max_calls=case['max_calls'], max_usd=case['max_usd'], reservation_usd=case['reservation_usd'], max_source_bytes=200000, role='extractor', settings={}, storage_policy=storage)
    if args.mock:
        pre = root/'preflight'; pre.mkdir(mode=0o700, exist_ok=True)
        require(pre.is_dir() and not pre.is_symlink() and stat.S_IMODE(pre.stat().st_mode) & 0o077 == 0)
        execution = Path(tempfile.mkdtemp(prefix='driver-', dir=pre))
    else:
        execution = root/'provider'; execution.mkdir(mode=0o700)
    storage.save_json(execution/'execution.private.json', dict(mode='offline_mock' if args.mock else 'provider', protocol_sha256=digest(raw), state='started', driver_sha256=sha(__file__), started_at=dt.datetime.now(dt.timezone.utc).isoformat()), exclusive=True)
    try:
        code = execution/'executed-code'; code.mkdir(mode=0o700)
        for filename, expected in protocol['code_sha256'].items():
            target = code/(expected+'-'+Path(filename).name)
            if not target.exists(): storage.put_bytes(target, Path(filename).read_bytes(), exclusive=True, mode=0o400)
            require(sha(target) == expected)
        terminal = asyncio.run(execute(protocol, execution, cases, raw, args.mock, settings, spec, pricing, args.mock_first_failure, storage, args.protocol))
    except Exception as exc:
        terminal = dict(mode='offline_mock' if args.mock else 'provider', status='failed', error_class=type(exc).__name__, cases=[], http_reservation_count=None, http_response_count=None, backend_result_records=None, provider_requests=0 if args.mock else None, all_successful_replays_no_extra_calls=False)
        storage.save_json(execution/'terminal.private.json', terminal, exclusive=True)
    print(json.dumps(terminal, sort_keys=True, allow_nan=False))
    return 0 if terminal['status'] == 'finished' else 1


if __name__ == '__main__':
    try: sys.exit(main())
    except Exception as exc:
        print(json.dumps(dict(status='failed', error_class=type(exc).__name__)), file=sys.stderr)
        sys.exit(1)
