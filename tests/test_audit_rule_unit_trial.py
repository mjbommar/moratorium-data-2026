"""Public synthetic-only tests for prospective trial accounting."""
import copy
import base64
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('trial_audit', Path(__file__).parents[1] / 'scripts/audit_rule_unit_trial.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def fixture(n=27):
    text = 'Synthetic source.'
    sha = hashlib.sha256(text.encode()).hexdigest()
    units = [dict(unit_id=str(i), anchor_quote='synthetic', label='x', instruction='x') for i in range(n)]
    plan = dict(source_text_sha256=sha, units=units)
    doc = dict(text=text, text_sha256=sha, body_sha256=hashlib.sha256(b'synthetic body').hexdigest(), reviewed_source_role='proposed')
    ctx = dict(document=doc, plan=plan, role='extractor', system='system', schema={}, settings={})
    attempts, successes, packets = [], {}, []
    for u in units:
        uid = u['unit_id']
        dc = {'reviewed_source_role': 'proposed'}
        prompt = ('Document context (JSON):\n' + json.dumps(dc, ensure_ascii=False, sort_keys=True)
                  + '\nFull source:\n' + text + '\nLocal slot (JSON):\n' + json.dumps(u, ensure_ascii=False, sort_keys=True))
        rh = a.digest(dict(role='extractor', stage='rule_unit', prompt=prompt, system='system', schema={}, settings={}))
        raw = dict(unit_id=uid, outcome='candidate', clause={'source_text': text, 'assertion_context': 'proposed'}, supporting_quotes=[text], unresolved_reason=None)
        entry = dict(request_sha256=rh, output=raw, output_sha256=a.digest(raw))
        attempts.append(dict(unit_id=uid, status='succeeded', request_sha256=rh))
        successes[uid] = entry
        packets.append(dict(unit_id=uid, outcome='candidate' if uid == '0' else 'unresolved', clause=raw['clause'], original_output=raw, output_sha256=entry['output_sha256'], request_sha256=rh, review_flags=[] if uid == '0' else ['quote_unlocated_or_ambiguous']))
    state = dict(context=ctx, context_sha256=a.digest(ctx), attempts=attempts, successes=successes, budget_stop=None)
    packet = dict(context_sha256=state['context_sha256'], source_text_sha256=sha, source_body_sha256=hashlib.sha256(b'synthetic body').hexdigest(), plan_sha256=a.digest(plan), units=packets)
    return dict(schema_version='rule-unit-trial-bundle-1', state=state, state_sha256=a.digest(state), source_body_b64=base64.b64encode(b'synthetic body').decode(), packet=packet, captures=[], reviews=[], protocol=None)


def reseal(b):
    b['state_sha256'] = a.digest(b['state'])


class AccountingTests(unittest.TestCase):
    def test_all_generated_even_when_locally_unresolved(self):
        r = a.audit(fixture())
        self.assertEqual(r['counts']['generated_clauses_known'], 27)
        self.assertEqual(r['counts']['local_unresolved'], 26)
        self.assertEqual(r['quality'], 'not_scored')
        self.assertIn('missing independent semantic judgments', r['blockers'])
        self.assertIn('no frozen prospective protocol and reference contract', r['blockers'])

    def test_unscorable_and_unknown(self):
        b = fixture(1)
        entry = b['state']['successes']['0']
        entry['output'] = 'unparseable'; entry['output_sha256'] = a.digest(entry['output'])
        p = b['packet']['units'][0]; p.update(original_output=entry['output'], output_sha256=entry['output_sha256'], review_flags=['native_response_unscorable'])
        reseal(b)
        r = a.audit(b)
        self.assertEqual(r['counts']['unknown_cardinality_outputs'], 1)
        self.assertTrue(r['generated_clause_count_is_lower_bound'])
        self.assertFalse(r['response_accounting_complete'])

    def test_failed_interrupted_and_unattempted(self):
        b = fixture(3)
        b['state']['attempts'] = b['state']['attempts'][:2]
        b['state']['attempts'][0]['status'] = 'failed'
        b['state']['attempts'][1]['status'] = 'reserved'
        b['state']['successes'] = {}
        reseal(b)
        r = a.audit(b)
        self.assertEqual((r['counts']['failed_attempts'], r['counts']['interrupted_attempts'], r['counts']['unattempted_units']), (1, 1, 1))
        self.assertEqual(r['counts']['unknown_cardinality_attempts'], 2)
        self.assertTrue(r['generated_clause_count_is_lower_bound'])

    def test_role_conflict_and_drift(self):
        b = fixture(1)
        entry = b['state']['successes']['0']; entry['output']['clause']['assertion_context'] = 'enacted_text'
        entry['output_sha256'] = a.digest(entry['output'])
        b['packet']['units'][0]['output_sha256'] = entry['output_sha256']
        reseal(b)
        self.assertIn('reviewed source role conflict', a.audit(b)['blockers'])
        b['state']['context']['document']['text'] = 'changed'
        reseal(b)
        with self.assertRaisesRegex(ValueError, 'context hash mismatch'): a.audit(b)

    def test_wrong_review_target_and_duplicates_and_missing_population(self):
        b = fixture(1)
        b['reviews'] = [dict(unit_id='wrong', reviewer_id='x', source_text_sha256='', source_body_sha256='', context_sha256='', request_sha256='', output_sha256='', raw_request_sha256='', raw_response_sha256='', judgment='supported', dimensions={}, evidence='x')]
        with self.assertRaisesRegex(ValueError, 'review target'): a.audit(b)
        b['reviews'] = []; b['packet']['units'].append(copy.deepcopy(b['packet']['units'][0]))
        with self.assertRaisesRegex(ValueError, 'population'): a.audit(b)
        b['packet']['units'] = []
        with self.assertRaisesRegex(ValueError, 'population'): a.audit(b)

    def test_review_identity_disagreement_and_no_inferred_support(self):
        b = fixture(1)
        enc = base64.b64encode(b'bytes').decode()
        h = hashlib.sha256(b'bytes').hexdigest()
        b['captures'] = [dict(schema_version='normalized-http-capture-1', attempt_index=0, unit_id='0', request_b64=enc, request_sha256=h, response_b64=enc, response_sha256=h)]
        e = b['state']['successes']['0']; ctx = b['state']['context']
        dimensions = {x: 'supported' for x in ('relevance', 'assertions', 'actors', 'dates', 'polarity', 'conditions', 'consequences', 'qualifications', 'omissions', 'role', 'expression_binding')}
        review = dict(unit_id='0', reviewer_id='one', source_text_sha256=ctx['document']['text_sha256'], source_body_sha256=ctx['document']['body_sha256'], context_sha256=b['state']['context_sha256'], request_sha256=e['request_sha256'], output_sha256=e['output_sha256'], raw_request_sha256=h, raw_response_sha256=h, judgment='supported', dimensions=dimensions, evidence='synthetic judgment')
        b['reviews'] = [review, dict(review, reviewer_id='two', judgment='uncertain')]
        result = a.audit(b)
        self.assertIn('unresolved reviewer disagreement', result['blockers'])
        self.assertEqual(result['quality'], 'not_scored')
        b['reviews'][1]['raw_response_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'raw capture identity'): a.audit(b)
        b['reviews'][1] = copy.deepcopy(review)
        with self.assertRaisesRegex(ValueError, 'duplicate review'): a.audit(b)

    def test_no_override_and_capture_hash(self):
        b = fixture(1); b['captures'] = [dict(schema_version='normalized-http-capture-1', attempt_index=0, unit_id='0', request_b64='YQ==', request_sha256='0'*64, response_b64=None, response_sha256=None)]
        with self.assertRaisesRegex(ValueError, 'request capture hash mismatch'): a.audit(b)
        b = fixture(1); b['override'] = True
        with self.assertRaisesRegex(ValueError, 'bundle fields'): a.audit(b)


class CompletenessRegressionTests(unittest.TestCase):
    def test_missing_captures_never_claim_end_to_end_completion(self):
        r = a.audit(fixture(1))
        self.assertTrue(r['boundary_output_accounting_complete'])
        self.assertFalse(r['response_accounting_complete'])
        self.assertEqual(r['counts']['raw_requests_captured'], 0)
        self.assertEqual(r['units'][0]['attempts'][0]['capture_disposition'], 'missing')
        self.assertEqual(r['quality'], 'not_scored')
        self.assertIn('raw capture journal integration and raw-to-boundary response mapping not verified', r['blockers'])

    def test_unattempted_and_partial_evidence_are_explicit(self):
        b = fixture(2)
        b['state']['attempts'] = b['state']['attempts'][:1]
        del b['state']['successes']['1']
        enc = base64.b64encode(b'request').decode()
        b['captures'] = [dict(schema_version='normalized-http-capture-1', attempt_index=0, unit_id='0', request_b64=enc, request_sha256=hashlib.sha256(b'request').hexdigest(), response_b64=None, response_sha256=None)]
        reseal(b)
        r = a.audit(b)
        self.assertEqual(r['units'][0]['attempts'][0]['capture_disposition'], 'response_missing')
        self.assertEqual(r['units'][1]['planned_output_state'], 'unknown_not_observed')
        self.assertEqual(r['units'][1]['attempts'], [])
        self.assertEqual(r['counts']['planned_units_without_boundary_output'], 1)
        self.assertTrue(r['planned_output_cardinality_unknown'])
        self.assertTrue(r['generated_clause_count_is_lower_bound'])
        self.assertFalse(r['response_accounting_complete'])
        b = fixture(1); b['state']['attempts'] = []; b['state']['successes'] = {}; reseal(b)
        r = a.audit(b)
        self.assertEqual(r['counts']['generated_clauses_known'], 0)
        self.assertEqual(r['counts']['failed_attempts'], 0)
        self.assertTrue(r['planned_output_cardinality_unknown'])


class AuditCliTests(unittest.TestCase):
    def test_blocked_audit_has_json_evidence_and_nonzero_exit(self):
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / 'synthetic.json'
            bundle.write_text(json.dumps(fixture(1)))
            result = subprocess.run([sys.executable, str(Path(a.__file__)), str(bundle)],
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report['response_accounting_complete'])
        self.assertEqual(report['quality'], 'not_scored')
        self.assertTrue(report['blockers'])


if __name__ == '__main__':
    unittest.main()
