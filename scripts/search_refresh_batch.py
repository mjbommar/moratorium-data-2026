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
SECTORS = {'data_center', 'battery_storage', 'solar', 'wind', 'cryptocurrency'}
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
    import bc_spec.models, bc_spec.plan, bc_web.search, bc_web.fusion, bc_core.rankfusion
    paths = [Path(__file__), Path(__file__).with_name('research_client.py')]
    paths += [Path(inspect.getfile(m)) for m in (bc_spec.models, bc_spec.plan, bc_web.search, bc_web.fusion, bc_core.rankfusion)]
    files = {str(p.resolve()): sha(p.read_bytes()) for p in paths}
    native_root = Path(inspect.getfile(bc_web.search)).parents[3]
    commit = subprocess.check_output(['git', '-C', str(native_root), 'rev-parse', 'HEAD'], text=True).strip()
    return {'bc_modules_commit': commit, 'implementation_files': files}


def preview(plan):
    from bc_spec.models import Dimension, Point, Space, Value
    from bc_spec.plan import check, sample, estimate
    from bc_web.search import SearchQuery
    require(set(plan) == {'schema_version', 'registry', 'cells', 'sample', 'caps', 'allow_unpriced'}, 'Wrong plan fields')
    require(plan['schema_version'] == 'refresh-search-plan-1', 'Unsupported plan')
    require(isinstance(plan['allow_unpriced'], bool), 'Explicit unpriced policy required')
    registry = {r['id']: r for r in plan['registry']}
    require(len(registry) == len(plan['registry']) and registry, 'Unique closed registry IDs required')
    for row in registry.values():
        require(set(row) == {'id', 'label', 'aliases', 'official_hosts'}, 'Wrong registry fields')
        require(row['id'] and row['label'] and isinstance(row['aliases'], list), 'Incomplete registry identity')
        for source in row['official_hosts']:
            require(set(source) == {'host', 'source_url', 'body_sha256', 'locator'}, 'Wrong host evidence fields')
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


async def execute(plan, directory, *, settings=None, transport=None):
    from bc_web.search import Searcher, SearchQuery
    from bc_web.settings import BcWebSettings
    prepared = preview(plan)
    require(plan['allow_unpriced'], 'Execution requires explicit bounded unpriced-call authorization; no prices inferred')
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory/'run.private.json'
    runtime = runtime_fingerprint()
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        require(manifest['plan_sha256'] == prepared['plan_sha256'], 'Run directory belongs to another plan')
        require(manifest['runtime'] == runtime, 'Runtime changed; retained results require explicit review')
        artifact = directory/'result.private.json'
        seal = directory/'completed.private.json'
        require(artifact.exists() and seal.exists(), 'Existing run is unfinished; inspect its retained handles/ledger, never auto-restart')
        require(sha(artifact.read_bytes()) == json.loads(seal.read_text())['result_sha256'], 'Retained result drift')
        result = json.loads(artifact.read_text())
        for item in result['artifact_hashes']:
            require(Path(item['path']).name == item['path'], 'Invalid retained artifact path')
            require(sha((directory/item['path']).read_bytes()) == item['sha256'], 'Retained search artifact drift')
        return {**result, 'replay': True}
    # Exclusive marker precedes reservations and all transport. A crash leaves an
    # inspectable reservation, never permission for an automatic retry.
    save(manifest_path, {'plan_sha256': prepared['plan_sha256'], 'runtime': runtime, 'started_at': datetime.now(timezone.utc).isoformat(), 'state': 'reserved_no_automatic_retry'})
    config = directory/'client-config.json'
    require(not config.exists(), 'Use a fresh batch directory; existing unrelated config is not overwritten')
    save(config, {'caps': plan['caps']})
    save(directory/'plan.private.json', plan)
    settings = settings or BcWebSettings(search_throttle_retries=0)
    secrets = [getattr(settings, k).get_secret_value() for k in ('exa_api_key', 'serpapi_api_key') if getattr(settings, k, None)]
    def redact(raw):
        for secret in secrets: raw = raw.replace(secret.encode(), b'[REDACTED]')
        return raw
    exchanges, artifacts, results = [], [], []
    def persist(name, raw):
        path = directory/name
        with path.open('xb') as stream: stream.write(raw)
        artifacts.append({'path': name, 'sha256': sha(raw)})
    for cell in prepared['selected_cells']:
        variants = {v['name']: SearchQuery.model_validate({k: x for k, x in v.items() if k != 'name'}) for v in cell['variants']}
        attempts = {name: reserve(directory, q.backend, intent={'cell_id': cell['id'], 'variant': name, 'plan_sha256': prepared['plan_sha256'],
                    'query': q.query, 'publication_window': {'since': q.start_date.isoformat() if q.start_date else None,
                    'until': q.end_date.isoformat() if q.end_date else None}, 'search_query': q.model_dump(mode='json')}) for name, q in variants.items()}
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
        searcher = TaggedSearcher(settings, transport=transport, on_response=sink)
        try:
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
        finally: await searcher.close()
    persist('exchanges.private.json', canonical(exchanges))
    artifacts += [{'path': name, 'sha256': sha((directory/name).read_bytes())} for name in ('run.private.json', 'client-config.json', 'plan.private.json', 'attempts.private.jsonl', 'exchanges.private.jsonl') if (directory/name).exists()]
    result = {'plan_sha256': prepared['plan_sha256'], 'cells': results, 'artifact_hashes': artifacts,
              'scope': 'Private search/fusion observations only; no factual promotion, no absent-instrument inference. Known subtotal excludes unpriced/failed calls.', 'replay': False}
    save(directory/'result.private.json', result)
    save(directory/'completed.private.json', {'result_sha256': sha((directory/'result.private.json').read_bytes())})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--execute', type=Path, metavar='PRIVATE_RUN_DIRECTORY')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    print(json.dumps(asyncio.run(execute(plan, args.execute)) if args.execute else preview(plan), indent=2))
