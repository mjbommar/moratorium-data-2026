#!/usr/bin/env python3
"""Freeze reviewed private plans and actual runtime settings; never send requests."""
import dataclasses
import datetime as dt
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PRIVATE = Path('/data0/moratorium-refresh-2026/frozen-domain-evaluation/direct-rule-unit-evaluation')
PREPARED = Path('/data0/moratorium-refresh-2026/direct-rule-unit-evaluation-2026-11-07/preparation')
INVENTORIES = Path('/data0/moratorium-refresh-2026/rule-unit-extraction-2026-11-07')
PATHS = ['/home/mjbommar/projects/bc/bc-modules-evidence-chunk-policy/bc-evidence/python',
         '/home/mjbommar/projects/bc/bc-modules-sdk-retries/bc-llm/python']
CAP = 128 * 1024 * 1024


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    require(not (HERE/'protocol.json').exists(), 'Protocol already exists; never refreeze in place')
    require(not PRIVATE.exists(), 'Fresh private namespace required')
    needed = [HERE/name for name in ('run.py', 'audit.py', 'prepare_inputs.py', 'reviewer-instructions.md',
                                     'required-slots.json', 'offline_sdk_test.py')]
    require(all(p.is_file() for p in needed), 'Driver/auditor/instructions must exist before freeze')
    sys.path[:0] = PATHS + [str(ROOT/'scripts')]
    from bc_llm import BcLlmSettings, ModelSpec, PydanticAIBackend
    from pydantic_ai.models.openai import OpenAIResponsesModel
    from private_run_storage import PrivateRunStorage
    import extract_rule_units as rules
    import runtime_file_pins

    prior = json.loads((ROOT/'work/research/2026-11-07/compound-contract-evaluation/protocol.json').read_text())
    old_slots = json.loads((ROOT/'work/research/2026-11-07/compound-contract-evaluation/required-slots.json').read_text())
    slots = json.loads((HERE/'required-slots.json').read_text())
    require(slots['families'] == old_slots['families'], 'Semantic criteria changed')
    inventory_audit = ROOT/'work/audit/rule-unit-extraction-2026-11-07/audit.json'
    accepted_hashes = json.loads(inventory_audit.read_text())['source_inventory']['private_artifacts_sha256']
    for name, expected in accepted_hashes.items():
        require(sha(INVENTORIES/name) == expected, 'Reviewed input/review changed: ' + name)

    cases = []
    inputs = [inventory_audit, HERE/'inventory-validation.json']
    inputs += [INVENTORIES/name for name in accepted_hashes]
    for family, filename, count in [('mandan', 'mandan-rule-plan-revised.private.json', 20),
                                     ('harwood', 'harwood-rule-plan-boundary-fixed.private.json', 66)]:
        source = next(c for c in prior['cases'] if c['family'] == family)
        require(sha(source['body_path']) == source['body_sha256'] and
                sha(source['text_path']) == source['text_sha256'], 'Source changed')
        raw = json.loads((INVENTORIES/filename).read_text())
        plan_path = PREPARED/(family+'-adapter-plan.private.json')
        plan = json.loads(plan_path.read_text())
        require(plan['source_text_sha256'] == source['text_sha256'] and len(plan['units']) == count,
                'Transformed plan population/source mismatch')
        require(raw['text_sha256'] == source['text_sha256'] and raw['body_sha256'] == source['body_sha256']
                and raw['source_document_id'] == source['source_document_id'], 'Inventory identity mismatch')
        text = Path(source['text_path']).read_text()
        by_id = {u['unit_id']: u for u in raw['units']}
        for original, converted in zip(raw['units'], plan['units'], strict=True):
            require(set(converted) == {'unit_id', 'anchor_quote', 'label', 'instruction'}, 'Plan field drift')
            require(all(converted[k] == original[k] for k in ('unit_id', 'anchor_quote', 'label')), 'Locator drift')
            require(text.count(original['anchor_quote']) == 1, 'Anchor not exact unique')
            a, b = original['anchor_span']
            require(text[a:b] == original['anchor_quote'], 'Anchor coordinates changed')
            context = original['boundary_context']
            locators = [context['printed_source_span']]
            locators += [ref['locator'] for ref in context['context_locators']]
            for locator in locators:
                a, b = locator['span']
                require(type(a) is int and type(b) is int and 0 <= a < b <= len(text), 'Invalid locator bounds')
                segment = text[a:b]
                require(hashlib.sha256(segment.encode()).hexdigest() == locator['text_sha256'] and
                        segment.startswith(locator['start_anchor']) and segment.endswith(locator['end_anchor']),
                        'Boundary locator mismatch')
            for ref in context['context_locators']:
                require(ref['locator'] == by_id[ref['unit_id']]['boundary_context']['printed_source_span'],
                        'Context target drift')
            neutral = {'printed_source_span': context['printed_source_span'],
                       'context_locators': [{'unit_id': r['unit_id'], 'locator': r['locator']}
                                            for r in context['context_locators']]}
            if 'layout_note' in context:
                neutral['layout_note'] = context['layout_note']
            require(converted['instruction'] == json.dumps(neutral, ensure_ascii=False, sort_keys=True),
                    'Plan instruction is not the exact neutral conversion')
        inputs += [plan_path, Path(source['body_path']), Path(source['text_path'])]
        cases.append({k: source[k] for k in ('source_document_id', 'title', 'url', 'body_path', 'text_path',
                                               'body_sha256', 'text_sha256')} | dict(
            case_id=family+'-direct', family=family, plan_path=str(plan_path), plan_sha256=sha(plan_path),
            units=count, max_calls=count, max_usd=count*.75, reservation_usd=.75))

    outputs = [PRIVATE, PRIVATE/'preflight', PRIVATE/'provider', PRIVATE/'provider/http']
    outputs += [PRIVATE/'provider'/case['case_id'] for case in cases]
    layout = ROOT/'work/audit/legacy-source-storage-layout-2026-11-06.json'
    guard = Path('/home/mjbommar/projects/bc/bc-modules/scripts/check-storage-layout.py')
    command = [sys.executable, str(guard), str(layout)]
    for output in outputs:
        command += ['--output', str(output)]
    checked = subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True)
    (HERE/'storage-preflight.json').write_text(checked.stdout)
    require(json.loads(checked.stdout)['ok'], 'Storage admission failed')
    admission = dict(outputs=list(map(str, outputs)), layout=str(layout), private_byte_cap=CAP,
                     new_namespace=True, old_evaluation_caps_unchanged=True)
    (HERE/'storage-admission.json').write_text(json.dumps(admission, indent=2)+'\n')
    PRIVATE.mkdir(mode=0o700)
    PrivateRunStorage(PRIVATE, CAP)
    settings = BcLlmSettings()
    spec = ModelSpec(model='openai:gpt-6-sol', reasoning_effort='low', output_mode='native',
                     max_tokens=14000, timeout_s=120)
    pricing = dataclasses.asdict(settings.pricing().get(spec.model))
    proxy = {'proxy': settings.proxy_url(), **{key: os.environ.get(key) for key in (
        'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'OPENAI_BASE_URL', 'OPENAI_ORG_ID', 'OPENAI_PROJECT_ID')}}
    runtime_path = HERE/'runtime-files.json'
    runtime_hash = runtime_file_pins.write_manifest(runtime_path)
    code = needed + [Path(__file__).resolve(), HERE/'storage-admission.json', layout, guard]
    code += [ROOT/'scripts'/name for name in ('extract_rule_units.py', 'condition_expression.py',
        'extract_document_resumable.py', 'controlled_model_transport.py', 'private_run_storage.py', 'runtime_file_pins.py')]
    code += [Path(inspect.getfile(obj)).resolve() for obj in (PydanticAIBackend, ModelSpec, BcLlmSettings,
                                                             OpenAIResponsesModel)]
    for path in PATHS:
        code += sorted(Path(path).glob('*/*.py'))
    code = list(dict.fromkeys(code))
    snapshot = (ROOT/'data/expanded').resolve()
    canonical = sorted(snapshot.glob('*.jsonl')) + [snapshot/'publication.json',
        ROOT/'data/moratorium_inventory.csv', ROOT/'data/state_legislation.csv', ROOT/'data/identities/expanded.jsonl']
    protocol = dict(schema_version='direct-rule-unit-development-1',
        prepared_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        scope='Known-source development only; not holdout, general accuracy, source freshness, P4 closure or promotion.',
        private_root=str(PRIVATE), max_http_requests=86, max_private_bytes=CAP, max_source_bytes=200000,
        runtime_import_paths=PATHS, runtime_files_path=str(runtime_path), runtime_files_sha256=runtime_hash,
        runtime_files_boundary=runtime_file_pins.BOUNDARY,
        code_sha256={str(p): sha(p) for p in code}, inputs_sha256={str(p): sha(p) for p in inputs},
        canonical_inputs_sha256={str(p): sha(p) for p in canonical}, canonical_snapshot=snapshot.name,
        source_cohort_date='2026-11-05', model_spec=spec.model_dump(mode='json'), pricing=pricing,
        routing_fingerprint=hashlib.sha256(encoded(proxy)).hexdigest(),
        dependency_versions={n: importlib.metadata.version(n) for n in (
            'openai', 'pydantic-ai-slim', 'pydantic', 'httpx2', 'bc-llm', 'bc-evidence', 'bc-content')},
        backend_policy=dict(max_attempts=1, agent_retries=0, max_model_requests=1, flex_fallback=False),
        tool_configuration=dict(toolsets=[], tools=[]), execution_order=[c['case_id'] for c in cases], cases=cases,
        thresholds=prior['thresholds'], required_slots_sha256=sha(HERE/'required-slots.json'),
        pricing_basis='Pinned local SDK overlay; estimated reservations64.5USD, not invoice ceiling or current pricing verification.',
        case_failure_policy='No case retry. Continue the other fixed case only while all global pins and controls remain valid.',
        limitations=['86 source-inventory units versus prior generic candidate population; not a causal comparison.',
                     'Reviewed retained proposed texts have OCR/layout and legal interpretation limits.',
                     'Source-informed AI reviews are fallible and not human gold.',
                     'Canonical and original-payload identity are pinned; text fidelity is not proved by hashes alone.'])
    (HERE/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    print(json.dumps(dict(protocol_sha256=sha(HERE/'protocol.json'), units=86, http_cap=86,
                         estimated_reservation_usd=64.5, provider_executed=False), indent=2))


if __name__ == '__main__':
    main()
