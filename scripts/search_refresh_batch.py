#!/usr/bin/env python3
"""Explicit sparse bc-spec plans and bounded native bc-web search_many runs.

Preview is read-only. Execution never promotes facts. Private payloads remain in
an explicit run directory; a retained run cannot silently spend again.
"""
import argparse
import asyncio
from collections import Counter
from contextvars import ContextVar
from datetime import datetime, timezone
import hashlib
import inspect
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

from research_client import reserve, finish, search_scope

BACKENDS = {'exa', 'serpapi', 'googlenews', 'gdelt'}
LANES = {'inventory_refresh', 'election_census', 'gap_discovery'}
SECTORS = {'data_center', 'battery_storage', 'solar', 'wind', 'cryptocurrency', 'sector_unresolved'}
DIMENSIONS = ('lane', 'jurisdiction_id', 'sector', 'period', 'intent', 'known_id')
CURRENT_VARIANT = ContextVar('refresh_search_variant')


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
def require(ok, message):
    if not ok: raise ValueError(message)
def save(path, value):
    raw = json.dumps(value, indent=2, ensure_ascii=False)+'\n'
    with path.open('x', encoding='utf-8') as stream:
        stream.write(raw); stream.flush()
        import os
        os.fsync(stream.fileno())


def runtime_fingerprint():
    import bc_spec.models, bc_spec.plan, bc_web.search, bc_web.fusion, bc_web.settings, bc_core.rankfusion, bc_core.budget
    paths = [Path(__file__), Path(__file__).with_name('research_client.py')]
    paths += [Path(inspect.getfile(m)) for m in (bc_spec.models, bc_spec.plan, bc_web.search, bc_web.fusion, bc_web.settings, bc_core.rankfusion, bc_core.budget)]
    files = {str(p.resolve()): sha(p.read_bytes()) for p in paths}
    native_root = Path(inspect.getfile(bc_web.search)).parents[3]
    commit = subprocess.check_output(['git', '-C', str(native_root), 'rev-parse', 'HEAD'], text=True).strip()
    return {'bc_modules_commit': commit, 'implementation_files': files}


def preview(plan):
    from bc_spec.models import Dimension, Point, Space, Value
    from bc_spec.plan import check, sample, estimate
    from bc_web.search import SearchQuery
    require(set(plan) == {'schema_version', 'registry', 'cells', 'sample', 'caps', 'allow_unpriced'}, 'Wrong plan fields')
    require(plan['schema_version'] in ('refresh-search-plan-1','refresh-search-plan-2'), 'Unsupported plan')
    require(isinstance(plan['allow_unpriced'], bool), 'Explicit unpriced policy required')
    registry = {r['id']: r for r in plan['registry']}
    require(len(registry) == len(plan['registry']) and registry, 'Unique closed registry IDs required')
    for row in registry.values():
        require(set(row) == {'id', 'label', 'aliases', 'official_hosts'}, 'Wrong registry fields')
        require(row['id'] and row['label'] and isinstance(row['aliases'], list), 'Incomplete registry identity')
        for source in row['official_hosts']:
            require({'host', 'source_url', 'body_sha256', 'locator'} <= set(source) <= {'host', 'source_url', 'body_sha256', 'locator', 'authority_review'}, 'Wrong host evidence fields')
            if 'authority_review' in source:
                review=source['authority_review']
                require(all(review.get(k) for k in ('path','sha256','authority_basis','reviewed_at','reviewer')), 'Incomplete authority review')
                require(review.get('role') in ('government','election','records') and re.fullmatch('[0-9a-f]{64}',review['sha256']), 'Invalid authority review role/hash')
                require(datetime.fromisoformat(review['reviewed_at']).tzinfo is not None,'Authority review timezone required')
                require(review.get('jurisdiction_id')==row['id'] and review.get('host')==source['host'] and review.get('source_url')==source['source_url'] and review.get('body_sha256')==source['body_sha256'], 'Authority review scope mismatch')
            require(source['host'] == urlsplit('https://'+source['host']).hostname and
                    urlsplit(source['source_url']).scheme in ('http', 'https') and source['locator'] and
                    re.fullmatch('[0-9a-f]{64}', source['body_sha256']), 'Invalid reviewed host provenance')
    cells = plan['cells']
    require(cells and len({c['id'] for c in cells}) == len(cells), 'Unique explicit cells required')
    for cell in cells:
        require(set(cell) == {'id', *DIMENSIONS, 'variants'}, 'Wrong cell fields')
        require(all(isinstance(cell[k], str) and cell[k] for k in ('id', *DIMENSIONS)), 'Nonblank coordinates required')
        require(cell['lane'] in LANES and cell['sector'] in SECTORS and cell['jurisdiction_id'] in registry, 'Unknown closed coordinate')
        variants = cell['variants']
        require(variants and len({v['name'] for v in variants}) == len(variants), 'Unique named variants required')
        hosts = {r['host'] for r in registry[cell['jurisdiction_id']]['official_hosts']}
        for variant in variants:
            query = SearchQuery.model_validate({k: v for k, v in variant.items() if k != 'name'})
            require(set(variant) <= {'name', *SearchQuery.model_fields} and variant['name'], 'Invalid variant fields')
            require(query.backend in BACKENDS, 'Explicit supported backend required')
            require(all(h in hosts for h in query.include_domains), 'Domain filter lacks reviewed host')
            if plan['schema_version']=='refresh-search-plan-2':
                require(all(any(s['host']==h and 'authority_review' in s for s in registry[cell['jurisdiction_id']]['official_hosts']) for h in query.include_domains),'Domain filter requires authority review')
            require(query.start_date is None or query.end_date is None or query.start_date <= query.end_date, 'Reversed publication window')
    space = Space(question='Moratorium refresh: explicit sparse research cells', dimensions=tuple(
        Dimension(name=k, values=tuple(Value(id=v, label=v) for v in sorted({c[k] for c in cells}))) for k in DIMENSIONS))
    require(not any(p.fatal for p in check(space)), 'Invalid bc-spec dimensions')
    values = {d.name: {v.label: v for v in d.values} for d in space.dimensions}
    points = [Point(id=Point.make_id(space.id, {k: values[k][c[k]].id for k in DIMENSIONS}),
                    coordinates={k: values[k][c[k]].id for k in DIMENSIONS},
                    values={k: values[k][c[k]] for k in DIMENSIONS}) for c in cells]
    require(len({p.id for p in points}) == len(points), 'Duplicate sparse coordinates')
    require(set(plan['sample']) <= {'strategy', 'n', 'dimension', 'per', 'seed'} and 'seed' in plan['sample'], 'Explicit sampling seed required')
    selected = {p.id for p in sample(points, **plan['sample'])}
    selected_cells = [{**c, 'point_id': p.id} for c, p in zip(cells, points, strict=True) if p.id in selected]
    counts = Counter(v['backend'] for c in selected_cells for v in c['variants'])
    require(set(plan['caps']) == {*BACKENDS, 'search_total'} and all(type(v) is int and v >= 0 for v in plan['caps'].values()), 'Explicit nonnegative call caps required')
    require(all(n <= plan['caps'][b] for b, n in counts.items()) and sum(counts.values()) <= plan['caps']['search_total'], 'Planned calls exceed persistent caps')
    costs = estimate(sum(counts.values()), queries_per_point=1, documents_per_query=0, model_calls_per_document=0)
    return {'schema_version': 'refresh-search-preview-1', 'plan_sha256': sha(canonical(plan)), 'space_id': space.id,
            'explicit_cells': len(cells), 'selected_cells': selected_cells, 'excluded_cell_ids': [c['id'] for c, p in zip(cells, points, strict=True) if p.id not in selected],
            'sample': plan['sample'], 'provider_calls': dict(counts), 'estimated_calls': costs.queries,
            'estimated_total_usd': costs.total_usd, 'unpriced_components': list(costs.unpriced),
            'scope': 'Sparse reviewed-registry input only; no Cartesian expansion, no API calls, no legal/event-date filtering or completeness inference.'}


def coverage(fused, names):
    states = {name: ('error' if name in fused.errors else 'declined' if fused.responses[name].declined else
                    'zero_hits' if not fused.responses[name].hits else 'returned_hits') for name in names}
    return {'variants': states, 'status': 'partial' if any(v in ('error', 'declined') for v in states.values()) else 'completed_bounded_search',
            'scope': 'Returned search coverage only; zero indexed hits do not establish absence or complete jurisdiction/election coverage.'}


def domain_diagnostics(fused, variants):
    return {n: search_scope(' '.join('site:'+d for d in q.include_domains),
                           [h.model_dump(mode='json') for h in fused.responses[n].hits])
            for n, q in variants.items() if n in fused.responses and q.include_domains}


def settings_fingerprint(settings):
    # Credentials are neither persisted nor included in the context hash.
    excluded = {'exa_api_key', 'serpapi_api_key', 'proxy', 'rate_limit_coordinator_token'}
    return sha(canonical(settings.model_dump(mode='json', exclude=excluded)))


def verify_completed_search(directory):
    """Validate the seal and retained search evidence before replay or fetching."""
    artifact = directory/'result.private.json'
    seal = directory/'completed.private.json'
    require(artifact.is_file() and seal.is_file(), 'Existing run is unfinished; inspect its retained handles/ledger, never auto-restart')
    commitment = json.loads(seal.read_text())
    require(isinstance(commitment, dict) and set(commitment) == {'result_sha256'}, 'Invalid completed search seal')
    raw_result = artifact.read_bytes()
    require(sha(raw_result) == commitment['result_sha256'], 'Retained result drift')
    result = json.loads(raw_result)
    for item in result['artifact_hashes']:
        require(Path(item['path']).name == item['path'], 'Invalid retained artifact path')
        raw = (directory/item['path']).read_bytes()
        if 'prefix_bytes' in item:
            require(len(raw) >= item['prefix_bytes'], 'Retained search artifact drift')
            raw = raw[:item['prefix_bytes']]
        require(sha(raw) == item['sha256'], 'Retained search artifact drift')
    return result


def validate_budget(plan, prepared, settings, contract_raw, expected_hash, runtime):
    require(re.fullmatch('[0-9a-f]{64}', expected_hash or '') is not None and sha(contract_raw) == expected_hash, 'Budget contract hash mismatch')
    contract = json.loads(contract_raw)
    keys = {'schema_version', 'plan_sha256', 'runtime', 'settings_sha256', 'plan_caps', 'max_usd', 'hold_usd', 'search_attempts', 'llm_calls', 'fetch_attempts', 'browser_attempts', 'browser_contexts', 'prices'}
    require(set(contract) == keys and contract['schema_version'] == 'refresh-priced-budget-1', 'Invalid budget contract fields')
    require(contract['plan_sha256'] == prepared['plan_sha256'] and contract['plan_caps'] == plan['caps'], 'Budget plan drift')
    require(contract['runtime'] == runtime and contract['settings_sha256'] == settings_fingerprint(settings), 'Budget runtime/settings drift')
    require((contract['max_usd'], contract['hold_usd'], contract['search_attempts'], contract['llm_calls'], contract['fetch_attempts'], contract['browser_attempts'], contract['browser_contexts']) == (25, .02, 1200, 0, 500, 20, 2), 'Invalid phase caps')
    prices = contract['prices']
    require(prices == {'exa_auto_le_10_usd': .007, 'serpapi_allocated_usd': .01}, 'Invalid configured price')
    require(settings.serpapi_cost_per_search == prices['serpapi_allocated_usd'], 'SerpAPI configured price mismatch')
    require(settings.serpapi_rate_per_hour is not None and settings.serpapi_rate_per_hour > 0, 'SerpAPI account pacing required')
    require(not plan['allow_unpriced'], 'Priced contract requires false unpriced policy')
    require(plan['caps']['search_total'] <= 1200 and prepared['estimated_calls'] <= 1200, 'Search cap exceeds phase')
    for cell in prepared['selected_cells']:
        for v in cell['variants']:
            require(v['backend'] in ('exa', 'serpapi'), 'Unpriced backend')
            if v['backend'] == 'exa':
                require(v.get('exa_type', 'auto') == 'auto' and 1 <= v.get('max_results', 10) <= 10, 'Exa price context mismatch')
                require(v.get('category') is None, 'Exa category price context not admitted')
                require(not any(v.get(k, False) for k in ('include_text', 'include_highlights', 'include_summary')), 'Exa content pricing not admitted')
            else:
                require(v.get('engine', 'google') == 'google', 'SerpAPI price context mismatch')
    return contract


async def execute(plan, directory, *, settings=None, transport=None, budget_path=None, budget_sha256=None):
    from bc_web.search import Searcher, SearchQuery
    from bc_web.settings import BcWebSettings
    prepared = preview(plan)
    settings = settings or BcWebSettings(search_throttle_retries=0)
    runtime = runtime_fingerprint()
    contract_raw = Path(budget_path).read_bytes() if budget_path else None
    require((budget_path is None) == (budget_sha256 is None), 'Both budget contract and independent hash required')
    contract = validate_budget(plan, prepared, settings, contract_raw, budget_sha256, runtime) if contract_raw is not None else None
    require(contract is not None or plan['allow_unpriced'], 'Execution requires explicit bounded unpriced-call authorization or priced contract')
    manifest_path = directory/'run.private.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        require(manifest['plan_sha256'] == prepared['plan_sha256'], 'Run directory belongs to another plan')
        require(manifest['runtime'] == runtime, 'Runtime changed; retained results require explicit review')
        require(manifest.get('budget_contract_sha256') == budget_sha256, 'Run budget contract mismatch')
        result = verify_completed_search(directory)
        return {**result, 'replay': True}
    require(plan['schema_version']=='refresh-search-plan-2','New execution requires plan version 2; version 1 is historical preview/replay only')
    for cell in prepared['selected_cells']:
        registry_row=next(r for r in plan['registry'] if r['id']==cell['jurisdiction_id'])
        used={h for v in cell['variants'] for h in v.get('include_domains',[])}
        for source in registry_row['official_hosts']:
            if source['host'] not in used: continue
            review=source['authority_review'];path=Path(review['path'])
            if not path.is_absolute(): path=Path(__file__).resolve().parents[1]/path
            raw=path.read_bytes()
            require(sha(raw)==review['sha256'],'Authority review file drift')
            require(json.loads(raw)=={k:v for k,v in review.items() if k not in ('path','sha256')},'Authority review record drift')
    require(not directory.exists() or not any(directory.iterdir()), 'Existing directory is not empty; inspect retained state')
    directory.mkdir(parents=True, exist_ok=True)
    # Exclusive marker precedes reservations and all transport. A crash leaves an
    # inspectable reservation, never permission for an automatic retry.
    save(manifest_path, {'plan_sha256': prepared['plan_sha256'], 'runtime': runtime, 'started_at': datetime.now(timezone.utc).isoformat(), 'state': 'reserved_no_automatic_retry', 'budget_contract_sha256': budget_sha256})
    config = directory/'client-config.json'
    require(not config.exists(), 'Use a fresh batch directory; existing unrelated config is not overwritten')
    phase = {'contract_sha256': budget_sha256, **{k: contract[k] for k in ('max_usd','hold_usd','search_attempts','browser_attempts')}} if contract else None
    save(config, {'caps': {**plan['caps'], 'fetch': contract['fetch_attempts']}, 'priced_phase': phase} if contract else {'caps': plan['caps']})
    save(directory/'plan.private.json', plan)
    if contract:
        with (directory/'budget-contract.private.json').open('xb') as f:
            f.write(contract_raw); f.flush(); import os; os.fsync(f.fileno())
    secrets = [getattr(settings, k).get_secret_value() for k in ('exa_api_key', 'serpapi_api_key') if getattr(settings, k, None)]
    def redact(raw):
        for secret in secrets: raw = raw.replace(secret.encode(), b'[REDACTED]')
        return raw
    exchanges, artifacts, results = [], [], []
    def persist(name, raw):
        path = directory/name
        with path.open('xb') as stream: stream.write(raw)
        artifacts.append({'path': name, 'sha256': sha(raw)})
    # Context tagging is the only override of the pinned native transport.
    # search_many, fusion, backend requests and parsing remain library code.
    class TaggedSearcher(Searcher):
        async def _metered(self, backend, query):
            name = next(n for n, q in variants.items() if q is query)
            token = CURRENT_VARIANT.set(name)
            try: return await super()._metered(backend, query)
            finally: CURRENT_VARIANT.reset(token)
    def sink(exchange):
        name = CURRENT_VARIANT.get()
        original, stored = exchange.body, redact(exchange.body)
        filename = f"{attempts[name]['attempt_id']}-response-{len(exchanges):04}.private.body"
        persist(filename, stored)
        event = {'cell_id': cell['id'], 'variant': name, 'attempt_id': attempts[name]['attempt_id'],
                 'backend': exchange.backend, 'status': exchange.status, 'artifact': filename,
                 'original_body_sha256': sha(original), 'stored_body_sha256': sha(stored), 'redacted': original != stored}
        exchanges.append(event)
        with (directory/'exchanges.private.jsonl').open('a') as stream:
            stream.write(json.dumps(event)+'\n'); stream.flush()
            import os
            os.fsync(stream.fileno())
    from bc_core import BudgetMeter
    meter = BudgetMeter(caps={'search': 1200, 'llm': 0}) if contract else None
    searcher = TaggedSearcher(settings, transport=transport, on_response=sink, meter=meter)

    try:
        for cell in prepared['selected_cells']:
            variants = {v['name']: SearchQuery.model_validate({**({'include_highlights': False} if contract and v['backend'] == 'exa' else {}), **{k: x for k, x in v.items() if k != 'name'}}) for v in cell['variants']}
            attempts = {name: reserve(directory, q.backend, intent={'cell_id': cell['id'], 'variant': name, 'plan_sha256': prepared['plan_sha256'],
                        'budget_contract_sha256': budget_sha256, 'query': q.query, 'publication_window': {'since': q.start_date.isoformat() if q.start_date else None,
                        'until': q.end_date.isoformat() if q.end_date else None}, 'search_query': q.model_dump(mode='json')}) for name, q in variants.items()}
            for q in variants.values():
                backend = searcher.backend(q.backend); backend.retries = 0; backend.throttle_retries = 0
            fused = await searcher.search_many(variants)
            # Raw exception messages can contain provider URLs or credentials.
            safe = fused.model_dump(mode='json')
            safe['errors'] = {k: v.split(':', 1)[0] for k, v in safe['errors'].items()}
            payload = redact(json.dumps(safe, ensure_ascii=False).encode())
            filename = f"{cell['point_id']}.private.json"; persist(filename, payload)
            for name, q in variants.items():
                response = fused.responses.get(name)
                response_filename = f"{attempts[name]['attempt_id']}.private.json"
                if response is not None:
                    persist(response_filename, redact(json.dumps(response.model_dump(mode='json'), ensure_ascii=False).encode()))
                finish(directory, attempts[name], outcome='error' if response is None else 'response',
                       query=q.query, publication_window=attempts[name]['intent']['publication_window'],
                       error_type=safe['errors'].get(name), hits=len(response.hits) if response else None,
                       cost_usd=response.cost_usd if response else None, unpriced=response is None or response.cost_usd is None,
                       cost_basis=('serpapi_subscription_allocation' if q.backend == 'serpapi' and contract else 'provider_response' if q.backend == 'exa' else 'legacy_or_unknown'),
                       declined=response.declined if response else None, artifact=str(directory/response_filename) if response else None,
                       exchanges=[{k: v for k, v in e.items() if k != 'attempt_id'} for e in exchanges if e['attempt_id'] == attempts[name]['attempt_id']])
            diagnostics = domain_diagnostics(fused, variants)
            scope_status = 'partial_domain_mismatch' if any(d['nonmatching_hits'] for d in diagnostics.values()) else 'no_returned_domain_mismatch'
            results.append({'cell_id': cell['id'], 'point_id': cell['point_id'], 'artifact': filename,
                            'coverage': coverage(fused, variants), 'response_variants': sorted(fused.responses),
                            'domain_diagnostics': diagnostics, 'query_scope_status': scope_status,
                            'variant_contribution': {n: {'fused_urls': sum(n in h.ranks for h in fused.hits),
                                 'unique_fused_urls': sum(list(h.ranks) == [n] for h in fused.hits)} for n in variants},
                            'sightings': sum(len(r.hits) for r in fused.responses.values()), 'fused_urls': len(fused.hits),
                            'known_search_subtotal_usd': sum(r.cost_usd or 0 for r in fused.responses.values()),
                            'unpriced_or_failed_variants': [n for n in variants if n not in fused.responses or fused.responses[n].cost_usd is None]})
    finally:
        await searcher.close()
    persist('exchanges.private.json', canonical(exchanges))
    artifacts += [{'path': name, 'sha256': sha((directory/name).read_bytes())} for name in ('run.private.json', 'client-config.json', 'plan.private.json', 'attempts.private.jsonl', 'exchanges.private.jsonl', 'budget-contract.private.json') if (directory/name).exists()]
    if contract:
        for item in artifacts:
            if item['path'] == 'attempts.private.jsonl':
                item['prefix_bytes'] = (directory/item['path']).stat().st_size
    result = {'plan_sha256': prepared['plan_sha256'], 'cells': results, 'artifact_hashes': artifacts,
              'scope': 'Private search/fusion observations only; no factual promotion, no absent-instrument inference. Known subtotal excludes unpriced/failed calls.', 'replay': False}
    if contract:
        events = [json.loads(line) for line in (directory/'attempts.private.jsonl').read_text().splitlines()]
        finished = [e for e in events if e['state'] == 'finished']
        result['budget_observation'] = {
            'reserved_search_attempts': sum(e['state'] == 'reserved' for e in events),
            'allocated_hold_usd': round(sum(e.get('allocated_hold_usd', 0) for e in events if e['state'] == 'reserved'), 2),
            'known_exa_response_usd': sum(e['cost_usd'] for e in finished if e['kind'] == 'exa' and e.get('cost_usd') is not None),
            'known_serpapi_subscription_allocation_usd': sum(e['cost_usd'] for e in finished if e['kind'] == 'serpapi' and e.get('cost_usd') is not None),
            'unknown_cost_attempts': sum(e.get('cost_usd') is None for e in finished),
            'invoice_usd': None,
            'scope': 'Holds are retained independently of reported/allocated costs. Subscription allocation is not an invoice; unknown is not zero.'}
    save(directory/'result.private.json', result)
    save(directory/'completed.private.json', {'result_sha256': sha((directory/'result.private.json').read_bytes())})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--execute', type=Path, metavar='PRIVATE_RUN_DIRECTORY')
    parser.add_argument('--budget-contract', type=Path)
    parser.add_argument('--budget-sha256')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    print(json.dumps(asyncio.run(execute(plan, args.execute, budget_path=args.budget_contract, budget_sha256=args.budget_sha256)) if args.execute else preview(plan), indent=2))
