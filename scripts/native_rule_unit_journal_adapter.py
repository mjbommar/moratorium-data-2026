"""Read-only native journal reconciliation; endpoint and semantic gates remain open."""
import json
import math
from decimal import Decimal


CONTRACT = 'openai-responses-native-rule-unit-pair-1'


def _open_nofollow(path, directory=False):
    """Open each path component without following links; never block on FIFOs.

    Privacy is checked on the target, not every ancestor. This supports a
    cooperative workspace, not a hostile owner able to rename directories.
    """
    import os
    parts = os.path.abspath(path).split(os.sep)[1:]
    fd = os.open(os.sep, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for index, part in enumerate(parts):
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            if index < len(parts) - 1 or directory:
                flags |= os.O_DIRECTORY
            new = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = new
        return fd
    except BaseException:
        os.close(fd)
        raise


def _private_file(path):
    import os, stat
    fd = _open_nofollow(path)
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_uid != os.geteuid() or st.st_nlink != 1 or st.st_mode & 0o077:
        os.close(fd)
        raise ValueError('file is not owner-private regular single-link')
    return fd


def _read_private(path):
    import os
    fd = _private_file(path)
    try:
        st = os.fstat(fd)
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read()
        after = os.fstat(fd)
        if (st.st_size, st.st_mtime_ns, st.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('file changed during read')
        return data
    finally:
        os.close(fd)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON member')
        result[key] = value
    return result


def _constant(value):
    raise ValueError('non-finite JSON number')


def _float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('non-finite JSON number')
    if Decimal(value) != Decimal(str(number)):
        raise ValueError('JSON number loses precision')
    return number


def strict_json(raw):
    return json.loads(raw, object_pairs_hook=_object, parse_constant=_constant, parse_float=_float)


def same_json(a, b):
    """Compare JSON values without Python's bool/int or int/float coercion."""
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same_json(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same_json(x, y) for x, y in zip(a, b))
    return a == b


def raw_output(response_bytes):
    """Extract only one unambiguous completed assistant output_text object.

    Reject extra output items, content blocks, refusals and incomplete envelopes;
    the caller retains the original response, including on rejection.
    """
    envelope = strict_json(response_bytes)
    if not isinstance(envelope, dict) or envelope.get('object') != 'response' or envelope.get('status') != 'completed':
        raise ValueError('unsupported or incomplete response envelope')
    output = envelope.get('output')
    if not isinstance(output, list) or len(output) != 1 or not isinstance(output[0], dict):
        raise ValueError('ambiguous response output')
    message = output[0]
    if message.get('type') != 'message' or message.get('role') != 'assistant' or message.get('status') != 'completed':
        raise ValueError('unsupported response message')
    content = message.get('content')
    if not isinstance(content, list) or len(content) != 1 or not isinstance(content[0], dict) or content[0].get('type') != 'output_text' or not isinstance(content[0].get('text'), str):
        raise ValueError('ambiguous or missing output text')
    return strict_json(content[0]['text'])

# Read-only contract. Expectations are supplied independently of the evidence.
RECONCILIATION_VERSION = 'native-rule-unit-reconciliation-1'


def reconcile(*, run_dir, http_dir, source_body, expected_context, expected_http_policy,
              expected_capture_policy):
    """Inspect a quiescent private run without creating or modifying any artifact.

    expected_context is the complete frozen context object; policies are complete
    expected JSON objects. source_body is a path to the actual private source bytes.
    Dispositions contain no source or response bytes. Errors block verification.
    """
    import datetime
    import fcntl
    import hashlib
    import os
    import stat
    from pathlib import Path
    from contextlib import ExitStack
    import extract_rule_units as rules
    from controlled_model_transport import ControlledModelTransport as Transport

    errors = []
    result = dict(schema_version=RECONCILIATION_VERSION, status='incomplete', errors=errors,
        retained_records_consistent=False, structural_evidence_complete=False, planned_trace_complete=False, endpoint_identity_complete=False,
        wire_contract_complete=False, semantic_completeness=False, response_accounting_complete=False,
        quality='not_scored', accepted=False, review_required=True,
        gates=['endpoint_identity_unavailable', 'wire_contract_unverified', 'semantic_review_required',
               'condition_consequence_semantics_required', 'fresh_frozen_calibration_and_holdout_required',
               'prospective_audit_integration_required'], plans=[], logical_invocations=[], http_attempts=[],
        unjournaled_artifacts=[], counts={}, known_generated_lower_bound=0,
        generated_cardinality='unknown', evidence_hashes={},
        evidence_scope='cooperative private workspace; advisory locks; no hostile owner or rollback protection',
        output_comparison_scope='raw response versus retained boundary output only; request integrity is separate',
        generated_lower_bound_scope='planned units with a matching observed clause; not all generated outputs')
    def error(code, detail=None):
        errors.append(dict(code=code, detail=str(detail) if detail is not None else None))
    def safe_dir(path):
        p = Path(os.path.abspath(path))
        fd = _open_nofollow(p, directory=True)
        try: s = os.fstat(fd)
        finally: os.close(fd)
        if not stat.S_ISDIR(s.st_mode) or s.st_uid != os.geteuid() or s.st_mode & 0o077:
            raise ValueError('directory is not owner-private')
        return p
    def read(path):
        return _read_private(path)
    def jsonfile(path, code):
        try:
            return strict_json(read(path))
        except (OSError, ValueError, TypeError, UnicodeError) as exc:
            error(code, exc)
            return None
    def ishex(x, n):
        return isinstance(x, str) and len(x) == n and all(c in '0123456789abcdef' for c in x)
    def artifact(directory, name, expected, size=None, sha=None):
        if name != expected:
            error('artifact_name_invalid', expected)
            return None
        try:
            data = read(directory / expected)
            if size is not None and (type(size) is not int or len(data) != size):
                error('artifact_length_mismatch', expected)
                return None
            if sha is not None and (not ishex(sha, 64) or hashlib.sha256(data).hexdigest() != sha):
                error('artifact_digest_mismatch', expected)
                return None
            return data
        except (OSError, ValueError) as exc:
            error('artifact_unavailable', f'{expected}: {exc}')
            return None

    state = None
    rows = []
    expected_artifacts = set()
    with ExitStack() as stack:
        try:
            run = safe_dir(run_dir)
            http = safe_dir(http_dir)
            # Shared locks avoid observing the writer between its durable steps.
            for p in (run / 'rule-units.lock', http / 'http-attempts.private.jsonl'):
                fd = _private_file(p)
                stack.callback(os.close, fd)
                fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except (OSError, ValueError) as exc:
            error('workspace_or_lock_unavailable', exc)
            run = http = None
        if run is not None:
            state = jsonfile(run / 'rule-units-state.private.json', 'state_unavailable')
            seal = jsonfile(run / 'rule-units-seal.private.json', 'seal_unavailable')
            packet = jsonfile(run / 'rule-units-candidates.private.json', 'packet_unavailable')
            try:
                if not isinstance(expected_context, dict):
                    raise ValueError('complete expected context required')
                c = expected_context
                body = read(source_body)
                result['evidence_hashes'] = dict(source_body_sha256=hashlib.sha256(body).hexdigest(),
                    source_text_sha256=rules.sha(c['document']['text']), context_sha256=rules.digest(c),
                    plan_sha256=rules.digest(c['plan']))
                if hashlib.sha256(body).hexdigest() != c['document']['body_sha256']:
                    error('source_body_hash_mismatch')
                # Rebuild using the current implementation, including schema, source,
                # plan and source text validation. Storage policy is frozen explicitly.
                rebuilt = rules.prepare(c['document'], c['plan'], model_identity=c['model_identity'],
                    today=datetime.date.fromisoformat(c['today']), max_calls=c['max_calls'], max_usd=c['max_usd'],
                    reservation_usd=c['reservation_usd'], max_source_bytes=c['max_source_bytes'],
                    role=c['role'], settings=c['settings'], storage_policy=None)
                rebuilt['storage_policy'] = c['storage_policy']
                storage = c['storage_policy']
                if storage is not None:
                    if (not isinstance(storage, dict) or set(storage) != {'root','max_bytes'} or
                        not isinstance(storage['root'], str) or type(storage['max_bytes']) is not int or storage['max_bytes'] < 0):
                        raise ValueError('invalid frozen storage policy')
                    root = safe_dir(storage['root'])
                    for directory in (run, http):
                        if not directory.is_relative_to(root) or directory == root:
                            raise ValueError('workspace outside frozen storage root')
                        current = directory
                        while current != root:
                            safe_dir(current)
                            current = current.parent
                    storage_lock = root / '.storage.lock'
                    fd = _private_file(storage_lock)
                    stack.callback(os.close, fd)
                    fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    if not same_json(jsonfile(root / '.storage-policy.json', 'storage_policy_unavailable'), storage):
                        error('storage_policy_mismatch')
                if not same_json(rebuilt, c):
                    error('expected_context_invalid_or_implementation_changed')
                if not isinstance(state, dict):
                    raise ValueError('state missing or invalid')
                result['evidence_hashes'].update(state_canonical_sha256=rules.digest(state), packet_canonical_sha256=rules.digest(packet))
                if seal != {'sha256': rules.digest(state)}:
                    error('state_seal_mismatch')
                rules.validate_state(state, c)
                if not same_json(state['context'], c):
                    error('frozen_context_mismatch')
                if not same_json(packet, rules.packet(state, c)):
                    error('packet_mismatch')
            except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
                error('state_context_validation_failed', exc)
            policy = jsonfile(http / 'http-policy.private.json', 'http_policy_unavailable')
            capture = jsonfile(http / 'http-capture-policy.private.json', 'capture_policy_unavailable')
            try:
                expected_context_digest = rules.digest(expected_context) if isinstance(expected_context, dict) else None
            except (ValueError, TypeError):
                expected_context_digest = None
            if (not isinstance(expected_http_policy, dict) or set(expected_http_policy) != {'schema_version', 'max_requests', 'context_sha256'} or
                expected_http_policy.get('schema_version') != 'controlled-model-http-1' or
                type(expected_http_policy.get('max_requests')) is not int or expected_http_policy['max_requests'] < 1 or
                not isinstance(expected_context, dict) or expected_http_policy.get('context_sha256') != expected_context_digest or
                not same_json(policy, expected_http_policy)):
                error('http_policy_mismatch_or_old')
            if (not isinstance(expected_capture_policy, dict) or set(expected_capture_policy) != {'capture_format', 'max_request_bytes', 'max_response_bytes'} or
                expected_capture_policy.get('capture_format') != 'controlled-model-capture-3' or
                any(type(expected_capture_policy.get(k)) is not int or expected_capture_policy[k] < 1 for k in ('max_request_bytes', 'max_response_bytes')) or
                not same_json(capture, expected_capture_policy)):
                error('capture_policy_mismatch_or_old')
            try:
                raw = read(http / 'http-attempts.private.jsonl')
                if raw and not raw.endswith(b'\n'):
                    error('journal_partial_line')
                for i, line in enumerate(raw.splitlines()):
                    try:
                        row = strict_json(line)
                        if not isinstance(row, dict):
                            raise ValueError('event is not an object')
                        rows.append((i + 1, row))
                    except (ValueError, UnicodeError) as exc:
                        error('journal_line_invalid', f'{i + 1}: {exc}')
            except (OSError, ValueError) as exc:
                error('journal_unavailable', exc)

        # Parse every readable event even if the surrounding evidence is invalid.
        reservations, terminals = {}, {}
        reservation_fields = {'capture_format','request_capture_complete','wire_request_sha256','wire_request_bytes','request_body_file','request_descriptor_sha256','logical_invocation_id','response_capacity_bytes','response_pending_file','journal_reservation_file','state','attempt_id','method','scheme','host','port','observed_at'}
        response_fields = {'state','attempt_id','capture_format','response_capture_complete','wire_response_sha256','wire_response_bytes','response_body_file','status','observed_at'}
        for line, row in rows:
            ident, kind = row.get('attempt_id'), row.get('state')
            if row.get('capture_format') != 'controlled-model-capture-3':
                error('old_or_unknown_capture', line)
            if not ishex(ident, 32):
                error('invalid_http_id', line)
                result['http_attempts'].append(dict(attempt_id=ident, line=line, disposition='invalid_event', linkage='unknown'))
                continue
            if kind == 'reserved':
                if ident in reservations:
                    error('duplicate_http_reservation', ident)
                    result['http_attempts'].append(dict(attempt_id=ident, line=line, disposition='duplicate_reservation', linkage='unknown'))
                    continue
                if any(k not in terminals for k in reservations):
                    error('journal_order_invalid', line)
                reservations[ident] = row
                mr = expected_capture_policy.get('max_request_bytes') if isinstance(expected_capture_policy, dict) else None
                ms = expected_capture_policy.get('max_response_bytes') if isinstance(expected_capture_policy, dict) else None
                if (set(row) != reservation_fields or row.get('request_capture_complete') is not True or
                    type(row.get('wire_request_bytes')) is not int or type(mr) is not int or not 0 <= row['wire_request_bytes'] <= mr or
                    row.get('response_capacity_bytes') != ms or not ishex(row.get('wire_request_sha256'),64) or
                    (row.get('logical_invocation_id') is not None and not ishex(row['logical_invocation_id'],32)) or
                    (row.get('request_descriptor_sha256') is not None and not ishex(row['request_descriptor_sha256'],64)) or
                    not isinstance(row.get('method'),str) or not row['method'].isascii() or not row['method'].isalpha() or not 1 <= len(row['method']) <= 32 or
                    row.get('scheme') not in ('http','https') or not isinstance(row.get('host'),str) or not row['host'].isascii() or not 1 <= len(row['host']) <= 253 or
                    (row.get('port') is not None and (type(row['port']) is not int or not 1 <= row['port'] <= 65535)) or not isinstance(row.get('observed_at'),str)):
                    error('reservation_invalid', ident)
                for key, suffix in [('request_body_file','-request.private.body'),('response_pending_file','-response.pending.private.body'),('journal_reservation_file','-journal-reservation.private.bytes')]:
                    if row.get(key) != ident + suffix: error('artifact_name_invalid', ident + suffix)
                name = ident + '-request.private.body'; expected_artifacts.add(name)
                artifact(http, row.get('request_body_file'), name, row.get('wire_request_bytes'), row.get('wire_request_sha256'))
            elif kind == 'response':
                if ident not in reservations or ident in terminals:
                    error('orphan_or_duplicate_response', ident)
                    result['http_attempts'].append(dict(attempt_id=ident, line=line, disposition='orphan_or_duplicate_response', linkage='unknown'))
                    continue
                terminals[ident] = row
                ms = expected_capture_policy.get('max_response_bytes') if isinstance(expected_capture_policy,dict) else None
                if (set(row) != response_fields or type(row.get('response_capture_complete')) is not bool or
                    type(row.get('wire_response_bytes')) is not int or type(ms) is not int or not 0 <= row['wire_response_bytes'] <= ms or
                    not ishex(row.get('wire_response_sha256'),64) or type(row.get('status')) is not int or not 100 <= row['status'] <= 999 or not isinstance(row.get('observed_at'),str)):
                    error('response_event_invalid', ident)
                name = ident + '-response.private.body'; expected_artifacts.add(name)
                artifact(http, row.get('response_body_file'), name, row.get('wire_response_bytes'), row.get('wire_response_sha256'))
                if row.get('response_capture_complete') is not True: error('response_capture_incomplete', ident)
            else:
                error('unknown_journal_event', line)
                result['http_attempts'].append(dict(attempt_id=ident, line=line, disposition='unknown_event', linkage='unknown'))
        if isinstance(expected_http_policy,dict) and type(expected_http_policy.get('max_requests')) is int and len(reservations) > expected_http_policy['max_requests']:
            error('http_cap_exceeded')
        for ident, row in reservations.items():
            terminal = terminals.get(ident)
            slot = ident + '-journal-reservation.private.bytes'; expected_artifacts.add(slot)
            if terminal is None:
                error('response_missing', ident)
                pending = ident + '-response.pending.private.body'
                if (http / pending).exists(): expected_artifacts.add(pending)
                # A pending buffer contains reserved capacity, not proven response bytes.
                if (http / pending).exists(): artifact(http, row.get('response_pending_file'), pending)
                artifact(http, row.get('journal_reservation_file'), slot)
            else:
                try:
                    bound = {'state':'response','attempt_id':ident,'capture_format':'controlled-model-capture-3', 'response_capture_complete':False,'wire_response_sha256':'f'*64,'wire_response_bytes':expected_capture_policy['max_response_bytes'], 'response_body_file':ident+'-response.private.body','status':999,'observed_at':'9999-12-31T23:59:59.999999+00:00'}
                    remaining = len(Transport._encoded(bound)) + expected_capture_policy['max_response_bytes'] - terminal['wire_response_bytes'] - len(Transport._encoded(terminal))
                    data = artifact(http, row.get('journal_reservation_file'), slot, remaining)
                    if data is not None and any(data): error('journal_capacity_altered', ident)
                except (KeyError, TypeError, ValueError) as exc: error('journal_capacity_unverified', exc)
        if http is not None:
            try:
                for p in sorted(http.iterdir()):
                    if p.name.endswith(('-journal-reservation.private.bytes','-request.private.body','-response.private.body','-response.pending.private.body')) and p.name not in expected_artifacts:
                        result['unjournaled_artifacts'].append(p.name)
                        error('unjournaled_artifact', p.name)
            except OSError as exc: error('artifact_inventory_unavailable', exc)

        attempts = state.get('attempts', []) if isinstance(state,dict) and isinstance(state.get('attempts'),list) else []
        successes = state.get('successes', {}) if isinstance(state,dict) and isinstance(state.get('successes'),dict) else {}
        logical_by_id = {}
        for index, a in enumerate(attempts):
            if not isinstance(a,dict):
                error('logical_event_invalid', index); continue
            ident = a.get('logical_invocation_id')
            if not ishex(ident, 32):
                error('invalid_logical_id', index)
                ident = None
            else:
                logical_by_id.setdefault(ident, []).append(a)
            linked = [key for key, row in reservations.items() if row.get('logical_invocation_id') == ident and ident is not None]
            result['logical_invocations'].append(dict(index=index, logical_invocation_id=ident, unit_id=a.get('unit_id'), status=a.get('status'), error_type=a.get('error_type'), reserved_usd=a.get('reserved_usd'), charged_usd=a.get('charged_usd',a.get('reserved_usd')), http_attempt_ids=linked, observed_http_reservations=len(linked), http_cardinality='at_least_'+str(len(linked)), dispatch='observed' if linked else 'unproven', output_comparison='unknown'))
        for ident, row in reservations.items():
            lid = row.get('logical_invocation_id'); matches = logical_by_id.get(lid, []) if ishex(lid, 32) else []
            linkage = 'bound' if len(matches) == 1 and row.get('request_descriptor_sha256') == matches[0].get('request_sha256') else ('unbound' if lid is None else 'orphan' if not matches else 'ambiguous_or_descriptor_mismatch')
            if linkage != 'bound': error('http_linkage_'+linkage, ident)
            t = terminals.get(ident)
            disposition = 'no_response' if t is None else 'partial_response' if t.get('response_capture_complete') is not True else 'http_response'
            output_state = 'unknown_no_complete_response'
            if t and t.get('response_capture_complete') is True:
                try:
                    raw = read(http / (ident + '-response.private.body'))
                    if len(raw) != t.get('wire_response_bytes') or hashlib.sha256(raw).hexdigest() != t.get('wire_response_sha256'):
                        raise ValueError('response integrity mismatch')
                    if type(t.get('status')) is int and 200 <= t['status'] < 300:
                        raw_output(raw)
                        output_state = 'structured_output_observed'
                    else:
                        output_state = 'non_success_http_output_unknown'
                except (OSError, ValueError, TypeError):
                    output_state = 'malformed_ambiguous_or_unverified'
            result['http_attempts'].append(dict(attempt_id=ident, logical_invocation_id=lid, request_descriptor_sha256=row.get('request_descriptor_sha256'), linkage=linkage, disposition=disposition, status=t.get('status') if t else None, raw_output_state=output_state))
        for logical in result['logical_invocations']:
            ids = logical['http_attempt_ids']; uid = logical['unit_id']
            if logical['status'] == 'succeeded':
                if len(ids) != 1:
                    logical['output_comparison'] = 'unknown_multiple_or_zero_http_attempts'; error('successful_output_ambiguous', logical['logical_invocation_id']); continue
                ident = ids[0]; t = terminals.get(ident); entry = successes.get(uid) if isinstance(uid, str) else None
                http_record = next((h for h in result['http_attempts'] if h.get('attempt_id') == ident and h.get('linkage') == 'bound'), None)
                if http_record is None:
                    logical['output_comparison'] = 'unknown_unverified_linkage'; error('successful_output_linkage_unverified', ident); continue
                if not t or t.get('response_capture_complete') is not True or type(t.get('status')) is not int or not 200 <= t['status'] < 300 or not isinstance(entry,dict):
                    logical['output_comparison'] = 'unknown_response_unavailable'; error('successful_output_unavailable', ident); continue
                try:
                    data = read(http / (ident + '-response.private.body'))
                    if len(data) != t.get('wire_response_bytes') or hashlib.sha256(data).hexdigest() != t.get('wire_response_sha256'): raise ValueError('response integrity mismatch')
                    value = raw_output(data)
                    if not same_json(value, entry['output']):
                        logical['output_comparison'] = 'mismatch'; error('raw_boundary_mismatch', ident)
                    else: logical['output_comparison'] = 'equal'
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    logical['output_comparison'] = 'unparseable_or_ambiguous'; error('raw_output_unverified', f'{ident}: {exc}')
            elif not ids:
                logical['output_comparison'] = 'unknown_no_observed_http'
        units = expected_context.get('plan',{}).get('units',[]) if isinstance(expected_context,dict) and isinstance(expected_context.get('plan'),dict) else []
        if not isinstance(units,list): units=[]
        for unit in units:
            if not isinstance(unit,dict): continue
            uid = unit.get('unit_id'); linked = [x for x in result['logical_invocations'] if x['unit_id'] == uid]
            entry = successes.get(uid) if isinstance(uid, str) else None
            generated = (isinstance(entry,dict) and isinstance(entry.get('output'),dict) and entry['output'].get('clause') is not None and any(x['status'] == 'succeeded' and x['output_comparison'] == 'equal' for x in linked))
            result['known_generated_lower_bound'] += int(generated)
            result['plans'].append(dict(unit_id=uid, logical_invocation_ids=[x['logical_invocation_id'] for x in linked], http_attempt_ids=[i for x in linked for i in x['http_attempt_ids']], disposition='succeeded' if entry else 'attempted' if linked else 'not_observed', dispatch='observed' if any(x['dispatch'] == 'observed' for x in linked) else 'unproven', generated_clause_observed=generated, accepted=False))
        if not result['plans']: error('planned_population_unavailable')
        if any(x['dispatch'] == 'unproven' for x in result['logical_invocations']): error('logical_dispatch_unproven')
        result['counts'] = dict(planned_units=len(result['plans']), logical_invocations=len(result['logical_invocations']), http_reservations=len(reservations), http_responses=len(terminals), unbound_http=sum(x.get('linkage')=='unbound' for x in result['http_attempts']), orphan_http=sum(x.get('linkage')=='orphan' for x in result['http_attempts']), no_response=sum(x.get('disposition')=='no_response' for x in result['http_attempts']), partial_response=sum(x.get('disposition')=='partial_response' for x in result['http_attempts']), unattempted_units=sum(x['disposition']=='not_observed' for x in result['plans']), failed_logical=sum(x['status']=='failed' for x in result['logical_invocations']), reserved_logical=sum(x['status']=='reserved' for x in result['logical_invocations']), succeeded_logical=sum(x['status']=='succeeded' for x in result['logical_invocations']))
        result['counts'].update(
            retries_observed=sum(max(0, len(x['http_attempt_ids']) - 1) for x in result['logical_invocations']),
            dispatch_unproven=sum(x['dispatch'] == 'unproven' for x in result['logical_invocations']),
            raw_output_equal=sum(x['output_comparison'] == 'equal' for x in result['logical_invocations']),
            raw_output_mismatch=sum(x['output_comparison'] == 'mismatch' for x in result['logical_invocations']),
            raw_output_unknown=sum(x['output_comparison'] not in ('equal', 'mismatch') for x in result['logical_invocations']),
            malformed_or_unverified_http_outputs=sum(x.get('raw_output_state') == 'malformed_ambiguous_or_unverified' for x in result['http_attempts']))
        history_errors = {'workspace_or_lock_unavailable', 'journal_unavailable', 'journal_partial_line',
                          'journal_line_invalid', 'old_or_unknown_capture', 'duplicate_http_reservation',
                          'invalid_http_id', 'unknown_journal_event'}
        result['http_history_cardinality'] = 'unknown_lower_bound'
        result['logical_history_cardinality'] = 'unknown_lower_bound'
        result['observed_http_reservation_lower_bound'] = len(reservations)
        result['observed_logical_record_count'] = len(result['logical_invocations'])
        result['http_journal_parse_consistent'] = not any(e['code'] in history_errors for e in errors)
        result['retained_records_consistent'] = not errors
        result['counts']['planned_dispatch_unproven'] = sum(x['dispatch'] == 'unproven' for x in result['plans'])
        if result['counts']['unattempted_units']:
            error('planned_units_unobserved', result['counts']['unattempted_units'])
        if result['counts']['planned_dispatch_unproven']:
            error('planned_dispatch_unproven', result['counts']['planned_dispatch_unproven'])
        # No independently anchored complete inventory is available. Even a
        # coherent retained trace cannot establish the full actual history.
        error('complete_history_unattested')
        result['status'] = 'incomplete'
    return result


def main(argv=None):
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description='Read-only private rule-unit journal reconciliation')
    for arg in ('run-dir','http-dir','source-body','expected-context','expected-http-policy','expected-capture-policy'):
        parser.add_argument('--'+arg, required=True)
    args = parser.parse_args(argv)
    try:
        # Expectations must also be private; use no mutating controller.
        def expectation(path):
            return strict_json(_read_private(path))
        result = reconcile(run_dir=args.run_dir,http_dir=args.http_dir,source_body=args.source_body,
            expected_context=expectation(args.expected_context),expected_http_policy=expectation(args.expected_http_policy),expected_capture_policy=expectation(args.expected_capture_policy))
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result = dict(schema_version=RECONCILIATION_VERSION,status='incomplete',errors=[dict(code='expectation_unavailable',detail=str(exc))])
    print(json.dumps(result,sort_keys=True,ensure_ascii=False,allow_nan=False))
    # Endpoint and wire contract remain open even for structurally complete evidence.
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
