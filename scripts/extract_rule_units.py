"""Opt-in, private, source-bound rule-unit candidate extraction."""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import stat
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator
from bc_core.budget import BudgetExceeded
from condition_expression import NativeConditionClause, validate_condition_clauses
from extract_document_resumable import digest, save, WorkspaceContextChanged


SYSTEM = '''Extract the single rule unit identified by the local slot from the entire supplied source.
Return one complete condition clause, preserving its conditions, exceptions and relevant definitions,
with exact supporting quotations from anywhere in the source. Do not combine distinct rule units.
Each clause.source_text must be one nonempty contiguous literal Unicode substring of Full source;
preserve all line breaks, indentation and line numbers. Each supporting quote must individually
be an exact unique literal substring. The source_text must also occur exactly once. Never join,
normalize, paraphrase or insert ellipses into quotations. The relevant source_text together with
the supporting passages must jointly support EVERY assertion, actor, date, polarity, consequence,
condition and governing qualification of the complete clause, including dispersed definitions
and exceptions. Completeness takes priority over shortness. If sufficient exact unique passages
cannot be supplied, return unresolved. If unavailable markup obscures operation, express uncertainty;
do not infer it. Do not infer operational conclusions from expression ordering or grouping without
source support. Exact matches and expression grouping do not themselves establish entailment.
Use typed all, any, at_least and thresholds where directly supported. Use text_predicate for source-qualified gates, negation, and parts the types cannot represent. Do not reduce the entire rule to raw text when structure is supported. If necessary facts are missing or the unit cannot be represented reliably, return unresolved and explain why. Do not infer legal
status, canonical identifiers or missing facts. The reviewed source role is caller-supplied context;
unknown means no reviewed role was supplied. An enrolled label or title alone does not establish
adoption or approval. The supplied slot is a locator, not an answer.'''


class Response(BaseModel):
    model_config = ConfigDict(extra='forbid')
    unit_id: str
    outcome: Literal['candidate', 'unresolved']
    clause: NativeConditionClause | None
    supporting_quotes: list[str]
    unresolved_reason: str | None

    @model_validator(mode='after')
    def coherent(self):
        if self.outcome == 'candidate':
            if self.clause is None or not self.supporting_quotes or self.unresolved_reason is not None:
                raise ValueError('candidate requires one clause and supporting quotes')
        elif self.clause is not None or not self.unresolved_reason:
            raise ValueError('unresolved requires a reason and no clause')
        return self


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def spans(text, quote):
    if not isinstance(quote, str) or not quote:
        return []
    found, start = [], 0
    while (index := text.find(quote, start)) >= 0:
        found.append([index, index + len(quote)])
        start = index + 1
    return found


def prepare(doc, plan, *, model_identity, today, max_calls, max_usd,
            reservation_usd, max_source_bytes, role, settings, storage_policy):
    if not isinstance(doc, dict) or not isinstance(doc.get('text'), str) or not doc['text'].strip():
        raise ValueError('Nonempty source text required')
    if 'title' in doc and (not isinstance(doc['title'], str) or not doc['title'].strip()):
        raise ValueError('Document title must be a nonempty string when supplied')
    if 'reviewed_source_role' in doc and doc['reviewed_source_role'] not in (
            'proposed', 'source_reported', 'enacted_text', 'unknown'):
        raise ValueError('Invalid reviewed source role')
    text = doc['text']
    if doc.get('text_sha256') != sha(text):
        raise ValueError('Source text hash mismatch')
    body = doc.get('body_sha256')
    if not isinstance(body, str) or len(body) != 64 or any(c not in '0123456789abcdef' for c in body):
        raise ValueError('Source body SHA256 required')
    if type(max_source_bytes) is not int or max_source_bytes < 1 or len(text.encode()) > max_source_bytes:
        raise ValueError('Source exceeds explicit byte ceiling or ceiling invalid')
    if not isinstance(plan, dict) or set(plan) != {'source_text_sha256', 'units'} or plan['source_text_sha256'] != sha(text):
        raise ValueError('Plan must bind exact source text hash')
    if not isinstance(plan['units'], list) or not plan['units']:
        raise ValueError('Plan needs at least one unit')
    ids, anchors = set(), set()
    for unit in plan['units']:
        if not isinstance(unit, dict) or set(unit) != {'unit_id', 'anchor_quote', 'label', 'instruction'}:
            raise ValueError('Plan unit must contain only local ID, anchor, label and instruction')
        if any(not isinstance(v, str) or not v.strip() for v in unit.values()):
            raise ValueError('Plan unit values must be nonempty strings')
        if unit['unit_id'] in ids or unit['anchor_quote'] in anchors or len(spans(text, unit['anchor_quote'])) != 1:
            raise ValueError('Duplicate ID or duplicate, ambiguous or unlocated anchor')
        ids.add(unit['unit_id']); anchors.add(unit['anchor_quote'])
    if type(max_calls) is not int or max_calls <= 0:
        raise ValueError('Positive request cap required')
    for value in (max_usd, reservation_usd):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError('Positive finite dollar cap and reservation required')
    if reservation_usd > max_usd:
        raise ValueError('Reservation exceeds cap')
    if not isinstance(model_identity, dict) or not isinstance(model_identity.get('model'), str) or not model_identity['model'].strip():
        raise ValueError('Resolved model identity required')
    if type(today) is not dt.date or not isinstance(role, str) or not role.strip() or not isinstance(settings, dict):
        raise ValueError('Explicit date, role and settings required')
    if set(settings) & {'role', 'stage', 'prompt', 'system', 'output_type', 'attachments', 'max_calls', 'max_usd', 'reservation_usd', 'budget', 'budget_policy', 'self', 'kwargs'}:
        raise ValueError('Settings cannot override request identity')
    context = dict(document=doc, plan=plan, model_identity=model_identity, today=today.isoformat(),
                   role=role, settings=settings, max_calls=max_calls, max_usd=max_usd,
                   reservation_usd=reservation_usd, max_source_bytes=max_source_bytes,
                   system=SYSTEM, schema=Response.model_json_schema(),
                   implementation_sha256=sha(Path(__file__).read_text()),
                   condition_sha256=sha((Path(__file__).parent / 'condition_expression.py').read_text()),
                   storage_policy=storage_policy.describe() if storage_policy else None)
    # Fail on non-JSON settings/identity and non-finite numbers before touching state.
    digest(context)
    return context


def packet(state, context):
    text = context['document']['text']
    outputs = []
    for unit in context['plan']['units']:
        entry = state['successes'].get(unit['unit_id'])
        attempts = [a for a in state['attempts'] if a['unit_id'] == unit['unit_id']]
        status = 'succeeded' if entry else (attempts[-1]['status'] if attempts else 'not_attempted')
        base = dict(unit_id=unit['unit_id'], status=status, anchor_quote=unit['anchor_quote'],
                    anchor_spans=spans(text, unit['anchor_quote']), accepted=False, review_required=True)
        if entry is None:
            outputs.append({**base, 'outcome': 'unresolved', 'reason': 'No successful response',
                            'request_sha256': attempts[-1]['request_sha256'] if attempts else None})
            continue
        if digest(entry['output']) != entry['output_sha256']:
            raise ValueError('Cached output hash mismatch')
        raw = entry['output']
        lineage = dict(request_sha256=entry['request_sha256'], output_sha256=entry['output_sha256'],
                       original_output=raw, original_outcome=raw.get('outcome') if isinstance(raw, dict) else None)
        try:
            response = Response.model_validate(raw)
            if response.unit_id != unit['unit_id']:
                raise ValueError('Response unit ID mismatch')
            if digest(response.model_dump(mode='json')) != digest(raw):
                raise ValueError('Response was coerced or changed by native validation')
        except ValueError as error:
            outputs.append({**base, **lineage, 'outcome': 'unresolved', 'reason': 'Unscorable native response',
                            'clause': raw.get('clause') if isinstance(raw, dict) else None,
                            'review_flags': ['native_response_unscorable'], 'native_error': str(error)})
            continue
        if response.outcome == 'unresolved':
            outputs.append({**base, **lineage, 'outcome': 'unresolved', 'reason': response.unresolved_reason})
            continue
        clause = response.clause.model_dump(mode='json')
        locations = []
        def visit(value, path):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == 'source_text':
                        locations.append(dict(path=path+[key], quote=child, spans=spans(text, child)))
                    visit(child, path+[key])
            elif isinstance(value, list):
                for i, child in enumerate(value): visit(child, path+[i])
        visit(clause, [])
        quotes = [dict(quote=q, spans=spans(text, q)) for q in response.supporting_quotes]
        errors = validate_condition_clauses([clause])
        def has_unknown(value):
            if isinstance(value, dict):
                return value.get('type') == 'unknown' or any(has_unknown(v) for v in value.values())
            return isinstance(value, list) and any(has_unknown(v) for v in value)
        unknown = has_unknown(clause['expression'])
        flags = []
        if unknown: flags.append('unknown_expression')
        if errors: flags.append('condition_schema_invalid')
        if any(len(q['spans']) != 1 for q in quotes + locations): flags.append('quote_unlocated_or_ambiguous')
        if (context['document'].get('reviewed_source_role') == 'proposed'
                and clause['assertion_context'] == 'enacted_text'):
            flags.append('reviewed_source_role_conflict')
        reasons = (['Condition expression contains unknown'] if unknown else [])
        if errors: reasons.append('Condition expression fails strict validation')
        if 'quote_unlocated_or_ambiguous' in flags: reasons.append('Exact source quotation missing or ambiguous')
        if 'reviewed_source_role_conflict' in flags: reasons.append('Reviewed source role conflicts with assertion')
        outputs.append({**base, **lineage, 'outcome': 'unresolved' if reasons else 'candidate',
                        'reason': '; '.join(reasons) if reasons else None,
                        'clause': clause, 'supporting_quotes': quotes,
                        'condition_quote_locations': locations, 'schema_errors': errors, 'review_flags': flags,
                        'request_sha256': entry['request_sha256']})
    count = sum(o['outcome'] == 'candidate' for o in outputs)
    generated = sum(isinstance(o.get('original_output'), dict) and o['original_output'].get('clause') is not None for o in outputs)
    unscorable = sum('native_response_unscorable' in o.get('review_flags', []) for o in outputs)
    return dict(context_sha256=state['context_sha256'], source_text_sha256=sha(text),
                source_body_sha256=context['document']['body_sha256'],
                provenance={k: context['document'][k] for k in ('doc_id', 'document_id', 'id', 'title', 'url', 'final_url', 'reviewed_source_role') if k in context['document']}, plan_sha256=digest(context['plan']),
                planned_count=len(outputs), candidate_count=count, unresolved_count=len(outputs)-count,
                generated_clause_count=generated, unscorable_response_count=unscorable,
                response_accounting_complete=not unscorable and all(o['status'] == 'succeeded' for o in outputs),
                source_coverage=dict(full_source_supplied_per_attempt=True,
                                     attempted_units=len({a['unit_id'] for a in state['attempts']}),
                                     successful_units=len(state['successes'])), inventory_complete=False,
                accepted=False, review_required=True, units=outputs)


def request_for(unit, context):
    doc = context['document']
    document_context = {'reviewed_source_role': doc.get('reviewed_source_role', 'unknown')}
    if 'title' in doc:
        document_context['title'] = doc['title']
    prompt = ('Document context (JSON):\n' + json.dumps(document_context, ensure_ascii=False, sort_keys=True)
              + '\nFull source:\n' + doc['text'] + '\nLocal slot (JSON):\n'
              + json.dumps(unit, ensure_ascii=False, sort_keys=True))
    return dict(role=context['role'], stage='rule_unit', prompt=prompt, system=SYSTEM,
                schema=Response.model_json_schema(), settings=context['settings'])


def _number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


def validate_state(state, context):
    if not isinstance(state, dict) or set(state) != {'context', 'context_sha256', 'attempts', 'successes', 'budget_stop'}:
        raise ValueError('Invalid ledger structure')
    if digest(state['context']) != state['context_sha256'] or state['context_sha256'] != digest(context):
        raise WorkspaceContextChanged('Workspace context changed or context hash mismatch')
    attempts, successes, stop = state['attempts'], state['successes'], state['budget_stop']
    if not isinstance(attempts, list) or not isinstance(successes, dict) or (stop is not None and (not isinstance(stop, str) or not stop)):
        raise ValueError('Invalid ledger fields')
    units = {u['unit_id']: u for u in context['plan']['units']}
    if len(attempts) > context['max_calls'] or not set(successes) <= set(units):
        raise ValueError('Invalid ledger units or count')
    if stop not in (None, 'Unpriced or invalid accounting; reconcile reservation', 'Cost exceeds reservation; reconcile', 'Backend model identity mismatch; reconcile'):
        raise ValueError('Unknown reconciliation stop')
    succeeded = set()
    spent = 0
    for a in attempts:
        if not isinstance(a, dict) or not {'unit_id', 'request_sha256', 'reserved_usd', 'status'} <= set(a) or set(a) - {'unit_id', 'request_sha256', 'reserved_usd', 'status', 'charged_usd', 'accounting', 'error_type'}:
            raise ValueError('Invalid attempt structure')
        uid = a['unit_id']
        if uid not in units or a['request_sha256'] != digest(request_for(units[uid], context)) or a['reserved_usd'] != context['reservation_usd'] or not _number(a['reserved_usd']):
            raise ValueError('Invalid attempt request or reservation')
        if spent + context['reservation_usd'] > context['max_usd'] + 1e-12:
            raise ValueError('Attempt dispatched beyond cap')
        spent += a.get('charged_usd', a['reserved_usd']) if _number(a.get('charged_usd', a['reserved_usd'])) else 0
        status = a['status']
        if status not in ('reserved', 'failed', 'succeeded') or uid in succeeded:
            raise ValueError('Invalid attempt status or ordering')
        if status == 'reserved' and set(a) != {'unit_id', 'request_sha256', 'reserved_usd', 'status'}:
            raise ValueError('Invalid reserved attempt')
        if status == 'failed' and (not isinstance(a.get('error_type'), str) or not a['error_type']):
            raise ValueError('Invalid failed attempt')
        if status == 'succeeded':
            if 'error_type' in a or 'accounting' not in a or 'charged_usd' not in a:
                raise ValueError('Invalid succeeded attempt')
            succeeded.add(uid)
        if 'charged_usd' in a and (not _number(a['charged_usd']) or 'accounting' not in a or a['charged_usd'] != a['accounting'].get('cost_usd')):
            raise ValueError('Invalid charge')
        if 'accounting' in a:
            ac = a['accounting']
            if not isinstance(ac, dict) or set(ac) != {'model', 'priced', 'cost_usd', 'input_tokens', 'output_tokens'} or not isinstance(ac['model'], str) or not ac['model'] or ac['priced'] is not True or not _number(ac['cost_usd']) or any(v is not None and (type(v) is not int or v < 0) for v in (ac['input_tokens'], ac['output_tokens'])):
                raise ValueError('Invalid accounting')
            if status == 'succeeded' and (ac['model'] != context['model_identity']['model'] or ac['cost_usd'] > a['reserved_usd'] + 1e-12):
                raise ValueError('Invalid successful accounting')
            if (ac['model'] != context['model_identity']['model'] or ac['cost_usd'] > a['reserved_usd'] + 1e-12) and not stop:
                raise ValueError('Missing reconciliation stop')
    if stop and (not attempts or attempts[-1]['status'] != 'failed'):
        raise ValueError('Reconciliation stop without failed attempt')
    if stop:
        last = attempts[-1]; accounting = last.get('accounting')
        if stop == 'Unpriced or invalid accounting; reconcile reservation' and accounting is not None:
            raise ValueError('Invalid accounting stop')
        if stop == 'Cost exceeds reservation; reconcile' and (not accounting or accounting['cost_usd'] <= last['reserved_usd'] + 1e-12 or last.get('charged_usd') != accounting['cost_usd']):
            raise ValueError('Invalid over-reservation stop')
        if stop == 'Backend model identity mismatch; reconcile' and (not accounting or accounting['model'] == context['model_identity']['model']):
            raise ValueError('Invalid model stop')
    if any(a['status'] == 'failed' and 'charged_usd' in a for a in attempts) and stop != 'Cost exceeds reservation; reconcile':
        raise ValueError('Unexpected failed charge')
    if succeeded != set(successes):
        raise ValueError('Success attempt mismatch')
    for uid, entry in successes.items():
        if not isinstance(entry, dict) or set(entry) != {'request_sha256', 'output', 'output_sha256'} or entry['request_sha256'] != digest(request_for(units[uid], context)) or digest(entry['output']) != entry['output_sha256']:
            raise ValueError('Cached request or output hash mismatch')
    if sum(a['status'] == 'reserved' for a in attempts) > 1 or (any(a['status'] == 'reserved' for a in attempts) and attempts[-1]['status'] != 'reserved'):
        raise ValueError('Invalid interrupted reservation ordering')
    if sum(a.get('charged_usd', a['reserved_usd']) for a in attempts) > context['max_usd'] + 1e-12 and not stop:
        raise ValueError('Ledger exceeds cap without stop')
    packet(state, context)


def _admit(directory, policy):
    directory = Path(os.path.abspath(directory))
    for path in reversed((directory, *directory.parents)):
        if path.is_symlink():
            raise ValueError('Symlink in workspace path')
    if policy is not None:
        from private_run_storage import PrivateRunStorage
        if not isinstance(policy, PrivateRunStorage) or not directory.is_relative_to(policy.root) or directory == policy.root:
            raise ValueError('Storage policy root bounds invalid')
    if not directory.exists():
        directory.mkdir(mode=0o700, parents=False)
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise ValueError('Workspace must be an owner-private directory')
    for name in ('rule-units.lock', 'rule-units-state.private.json', 'rule-units-seal.private.json', 'rule-units-candidates.private.json'):
        path = directory / name
        try: info = path.lstat()
        except FileNotFoundError: continue
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError('Unsafe workspace file: ' + name)
    return directory


def _write(path, value, policy):
    if policy is not None:
        policy.save_json(path, value)
        return
    data = (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()
    fd, name = tempfile.mkstemp(prefix='.rule-units-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(name, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if os.path.exists(name): os.unlink(name)


async def run(directory, doc, plan, *, backend, model_identity, today, max_calls, max_usd,
              reservation_usd, max_source_bytes, settings, role='extractor', storage_policy=None):
    context = prepare(doc, plan, model_identity=model_identity, today=today, max_calls=max_calls,
                      max_usd=max_usd, reservation_usd=reservation_usd, max_source_bytes=max_source_bytes,
                      role=role, settings=settings, storage_policy=storage_policy)
    directory = _admit(directory, storage_policy)
    lock_path = directory / 'rule-units.lock'
    existed = lock_path.exists()
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as lock:
        os.fchmod(lock.fileno(), 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state_path = directory / 'rule-units-state.private.json'
        seal_path = directory / 'rule-units-seal.private.json'
        packet_path = directory / 'rule-units-candidates.private.json'
        def write_state():
            _write(state_path, state, storage_policy)
            _write(seal_path, {'sha256': digest(state)}, storage_policy)
        if state_path.exists() or seal_path.exists():
            if not state_path.exists() or not seal_path.exists():
                raise ValueError('Missing ledger or seal; reconcile')
            state = json.loads(state_path.read_text())
            seal = json.loads(seal_path.read_text())
            if seal != {'sha256': digest(state)}:
                raise ValueError('Ledger seal hash mismatch; reconcile')
            validate_state(state, context)
        else:
            if existed or packet_path.exists():
                raise ValueError('Missing ledger and seal; reconcile')
            state = dict(context=context, context_sha256=digest(context), attempts=[], successes={}, budget_stop=None)
            write_state()
        # Packet is a disposable derivative, refreshed only after context and ledger validation.
        _write(packet_path, packet(state, context), storage_policy)
        if state['budget_stop']:
            raise BudgetExceeded(state['budget_stop'], 'llm')
        if any(a['status'] == 'reserved' for a in state['attempts']):
            raise BudgetExceeded('Interrupted reservation; reconcile before dispatch', 'llm')
        for unit in plan['units']:
            request = request_for(unit, context)
            key = digest(request)
            if unit['unit_id'] in state['successes']:
                continue
            if len(state['attempts']) >= max_calls or sum(a.get('charged_usd', a['reserved_usd']) for a in state['attempts']) + reservation_usd > max_usd + 1e-12:
                _write(packet_path, packet(state, context), storage_policy)
                raise BudgetExceeded('Persistent request or dollar cap exhausted', 'llm')
            attempt = dict(unit_id=unit['unit_id'], request_sha256=key, reserved_usd=reservation_usd, status='reserved')
            state['attempts'].append(attempt)
            write_state()
            try:
                result = await backend.generate(role=role, stage='rule_unit', prompt=request['prompt'], system=SYSTEM,
                                                output_type=Response, **settings)
                cost = getattr(result, 'cost_usd', None)
                accounting = {k: getattr(result, k, None) for k in ('model', 'priced', 'cost_usd', 'input_tokens', 'output_tokens')}
                if (not isinstance(accounting['model'], str) or not accounting['model'] or accounting['priced'] is not True
                    or not _number(cost) or any(v is not None and (type(v) is not int or v < 0) for v in (accounting['input_tokens'], accounting['output_tokens']))):
                    state['budget_stop'] = 'Unpriced or invalid accounting; reconcile reservation'
                    raise BudgetExceeded(state['budget_stop'], 'llm')
                attempt['accounting'] = accounting
                if cost > reservation_usd + 1e-12:
                    attempt['charged_usd'] = cost
                    state['budget_stop'] = 'Cost exceeds reservation; reconcile'
                    raise BudgetExceeded(state['budget_stop'], 'llm')
                if result.model != model_identity['model']:
                    state['budget_stop'] = 'Backend model identity mismatch; reconcile'
                    raise ValueError(state['budget_stop'])
                value = (result.output.model_dump(mode='json') if isinstance(result.output, BaseModel)
                         else result.output)
                # Retain the JSON value as received at this boundary, even when it is malformed.
                # The typed backend may already have validated/coerced or rejected earlier.
                digest(value)
                state['successes'][unit['unit_id']] = dict(request_sha256=key, output=value, output_sha256=digest(value))
                attempt.update(status='succeeded', charged_usd=cost)
            except BaseException as error:
                attempt.update(status='failed', error_type=type(error).__name__)
                write_state()
                _write(packet_path, packet(state, context), storage_policy)
                raise
            write_state()
            _write(packet_path, packet(state, context), storage_policy)
        result = packet(state, context)
        _write(packet_path, result, storage_policy)
        return result
