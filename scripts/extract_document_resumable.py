"""Private, resumable bc-evidence extraction; outputs remain unreviewed candidates.

One workspace is bound to one document, cell set and model configuration. The
durable request cap includes failures and interrupted reservations across restarts.
The supplied backend must separately enforce a dollar budget and retain its ledger.
This adapter does not mark EvidenceDB documents complete or promote domain facts.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
import inspect
import math
from pathlib import Path
from types import SimpleNamespace


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('wb') as stream:
        stream.write(encoded(value) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)
    descriptor = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


async def run(directory, doc, cells, *, backend, model_identity, question, today,
              max_calls, role='extractor', max_chunks=None, budget_policy=None):
    """Run actual bc-evidence map/reduce with cached typed calls and coverage.

    ``model_identity`` must include the resolved provider/model/settings, not just
    a role name. Successful cache entries are hashed and schema-validated on reuse.
    A failed or interrupted request consumes a reservation; raising max_calls in
    the same workspace is intentionally rejected. Use a separately reviewed policy
    change/new run rather than silently replenishing the existing budget.
    """
    from bc_core.budget import BudgetExceeded
    from bc_content.chunk import chunk_text
    import bc_evidence.extract as extractor

    if type(max_calls) is not int or max_calls < 1:
        raise ValueError('max_calls must be a positive integer')
    if max_chunks is not None and (type(max_chunks) is not int or max_chunks < 1):
        raise ValueError('max_chunks must be a positive integer or None')
    if not doc['text'].strip() or not cells or len(cells) > extractor.MAX_CELLS_SHOWN:
        raise ValueError('Nonempty text and 1..16 explicit cells are required')
    if not model_identity or not model_identity.get('model'):
        raise ValueError('Resolved model identity is required')
    if not isinstance(today, dt.date):
        raise ValueError('Explicit date cutoff required')
    if budget_policy is not None:
        for name in ('max_usd', 'reservation_usd'):
            value = budget_policy.get(name)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value <= 0):
                raise ValueError('Budget requires positive finite max_usd and reservation_usd')
        if budget_policy['reservation_usd'] > budget_policy['max_usd']:
            raise ValueError('Per-call reservation exceeds run budget')
    source = Path(extractor.__file__)
    prompt_files = sorted((source.parent / 'prompts').glob('extract*'))
    context = dict(document=doc, cells=cells, model_identity=model_identity,
                   question=question, today=today.isoformat(), role=role,
                   max_calls=max_calls, max_chunks=max_chunks,
                   budget_policy=budget_policy,
                   adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   chunker_sha256=hashlib.sha256(Path(inspect.getfile(chunk_text)).read_bytes()).hexdigest(),
                   extractor_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   prompt_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in prompt_files})
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    # A workspace contains full source text, prompts and model outputs. Never use
    # a public research packet path for it.
    with (directory / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state_path = directory / 'state.private.json'
        if state_path.exists():
            state = json.loads(state_path.read_text())
            if state['context_sha256'] != digest(context):
                raise ValueError('Workspace context changed; refusing cache/budget reuse')
            if state.get('budget_stop'):
                raise BudgetExceeded(state['budget_stop'], 'llm')
        else:
            state = dict(context_sha256=digest(context), context=context,
                         attempts=[], successes={}, status='not_started')
        chunks = chunk_text(doc['text'], size=extractor.CHUNK, overlap=extractor.OVERLAP)
        state['chunks'] = [dict(index=i, start=c.start, end=c.end,
                                text_sha256=hashlib.sha256(c.text.encode()).hexdigest(),
                                status='unattempted') for i, c in enumerate(chunks)]
        selected = len(chunks) if max_chunks is None else min(len(chunks), max_chunks)
        # The generator uses this exact prompt. Pin the source/template hashes
        # above and reject unexpected extraction requests rather than guessing.
        listing = '\n'.join(
            f"[{i}] {c['subject_label']} -- {c['topic_label']} -- "
            + (f"what is scheduled/expected {c['window_start']}..; " if c['prospective'] else '')
            + f"window {c['window_start']} to {c['window_end']}"
            for i, c in enumerate(cells))
        expected = {}
        for i, chunk in enumerate(chunks):
            prompt = extractor.PROMPTS.render(
                'extract', question=question, today=today.isoformat(), cells=listing,
                title=doc['title'] or '', url=doc['final_url'] or doc['url'],
                published=doc['published'] or 'unknown', text=chunk.text)
            expected.setdefault(hashlib.sha256(prompt.encode()).hexdigest(), []).append(i)
            if i >= selected:
                state['chunks'][i]['status'] = 'omitted_by_ceiling'

        class CachedBackend:
            async def generate(self, **kwargs):
                output_type = kwargs['output_type']
                request = {k: v for k, v in kwargs.items() if k != 'output_type'}
                request['schema'] = output_type.model_json_schema()
                key = digest(request)
                indexes = []
                if kwargs['stage'] == 'extract':
                    indexes = [i for i in expected.get(
                        hashlib.sha256(kwargs['prompt'].encode()).hexdigest(), []) if i < selected]
                    if not indexes:
                        raise ValueError('Unexpected chunk prompt')
                if key in state['successes']:
                    cached = state['successes'][key]
                    if digest(cached['output']) != cached['output_sha256']:
                        raise ValueError('Cached output hash mismatch')
                    output = output_type.model_validate(cached['output'])
                else:
                    if len(state['attempts']) >= max_calls:
                        raise BudgetExceeded('Persistent extraction request cap exhausted', 'llm')
                    if budget_policy is not None:
                        charged = sum(a.get('charged_usd', a['reserved_usd'])
                                      for a in state['attempts'])
                        if charged + budget_policy['reservation_usd'] > budget_policy['max_usd'] + 1e-12:
                            raise BudgetExceeded('Persistent extraction dollar reservations exhausted', 'llm')
                    attempt = dict(request_sha256=key, stage=kwargs['stage'],
                                   chunk_indexes=indexes, status='reserved')
                    if budget_policy is not None:
                        attempt['reserved_usd'] = budget_policy['reservation_usd']
                    state['attempts'].append(attempt)
                    for i in indexes:
                        state['chunks'][i]['status'] = 'attempted'
                    save(state_path, state)  # reserve before any model request
                    try:
                        result = await backend.generate(**kwargs)
                        attempt['accounting'] = {field: getattr(result, field, None) for field in
                                                 ('model', 'input_tokens', 'output_tokens',
                                                  'cost_usd', 'priced')}
                        if budget_policy is not None:
                            cost = result.cost_usd
                            if not result.priced or cost is None:
                                state['budget_stop'] = 'Unpriced result; retaining full reservation'
                                raise BudgetExceeded(state['budget_stop'], 'llm')
                            if not math.isfinite(cost) or cost < 0:
                                state['budget_stop'] = 'Invalid cost; retaining full reservation'
                                raise BudgetExceeded(state['budget_stop'], 'llm')
                            if cost > attempt['reserved_usd'] + 1e-12:
                                attempt['charged_usd'] = cost
                                state['budget_stop'] = 'Call exceeded reservation; stop for reconciliation'
                                raise BudgetExceeded(state['budget_stop'], 'llm')
                        if result.model != model_identity['model']:
                            raise ValueError('Backend returned an unpinned model')
                        output = output_type.model_validate(result.output.model_dump(mode='json'))
                        value = output.model_dump(mode='json')
                        state['successes'][key] = dict(output=value, output_sha256=digest(value))
                        attempt['status'] = 'succeeded'
                        if budget_policy is not None:
                            attempt['charged_usd'] = result.cost_usd
                    except BaseException as error:
                        attempt['status'] = 'failed'
                        attempt['error_type'] = type(error).__name__
                        for i in indexes:
                            state['chunks'][i]['status'] = 'failed'
                        save(state_path, state)
                        raise
                for i in indexes:
                    state['chunks'][i]['status'] = 'succeeded'
                save(state_path, state)
                return SimpleNamespace(output=output)

        state['status'] = 'running'
        # Never leave a prior success artifact alongside a failed/in-progress replay.
        (directory / 'result.private.json').unlink(missing_ok=True)
        save(state_path, state)
        try:
            claims, relevance, summary = await extractor.extract_document(
                doc, cells, backend=CachedBackend(), question=question, today=today,
                role=role, max_chunks=max_chunks, chunk_concurrency=1)
            complete = bool(chunks) and all(c['status'] == 'succeeded' for c in state['chunks'])
            result = dict(claims=claims, relevance=relevance, summary=summary,
                          full_text_chunk_coverage=complete, domain_review_complete=False,
                          limitations=['Text coverage does not prove PDF/page/OCR completeness.',
                                       'Prompt requests at most 12 claims per chunk.',
                                       'Outputs are unreviewed candidates, not accepted legal facts.'])
            save(directory / 'result.private.json', result)
            state['status'] = 'full_text_chunks_processed' if complete else 'partial'
        except BaseException as error:
            state['status'] = 'incomplete'
            state['error_type'] = type(error).__name__
            save(state_path, state)
            raise
        save(state_path, state)
        return result
