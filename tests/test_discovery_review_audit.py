import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_discovery_reviews import audit_candidate, digest


class DiscoveryReviewAuditTests(unittest.TestCase):
    def fixture(self):
        original = {'jurisdiction': 'Example', 'legal_basis': 'Ordinance 1'}
        fingerprint = digest(json.dumps(original, sort_keys=True, ensure_ascii=False,
                                        separators=(',', ':')).encode())
        check = {'url': 'https://example.gov', 'attempt_id': 'attempt',
                 'body_sha256': 'body', 'text_sha256': 'text',
                 'quote': 'actual proposal', 'quote_span': [0, 15]}
        candidate = {'candidate_key': 'state:0', 'candidate_sha256': fingerprint,
                     'disposition': 'unresolved', 'rationale': 'Proposal only; adoption not established.',
                     'source_checks': [check], 'proposed_candidate': None}
        assigned = {'state:0': {'candidate_sha256': fingerprint}}
        index = {'https://example.gov': [{**check, 'text': 'actual proposal, not adoption'}]}
        return candidate, assigned, {'state:0': original}, index, Draft202012Validator({})

    def test_good_hash_and_span_are_only_mechanical_proofs(self):
        issues, proofs = audit_candidate(*self.fixture())
        self.assertEqual(issues, [])
        self.assertTrue(proofs[0]['quote_span_verified'])
        self.assertNotIn('accepted', proofs[0])

    def test_different_source_version_cannot_reuse_quote(self):
        args = self.fixture()
        args[0]['source_checks'][0]['body_sha256'] = 'wrong body'
        issues, proofs = audit_candidate(*args)
        self.assertTrue(issues)
        self.assertFalse(proofs[0]['body_text_verified'])

    def test_wrong_span_and_changed_original_are_rejected(self):
        args = self.fixture()
        args[0]['source_checks'][0]['quote_span'] = [1, 16]
        args[2]['state:0']['legal_basis'] = 'Different ordinance'
        issues, proofs = audit_candidate(*args)
        self.assertEqual(len(issues), 2)
        self.assertFalse(proofs[0]['quote_span_verified'])

    def test_retained_failure_is_accounting_not_positive_evidence(self):
        args = self.fixture()
        check = args[0]['source_checks'][0]
        check.update(verified_success=False, quote='', quote_span=[0, 0])
        failed = {check['url']: [dict(check)]}
        args = (*args[:3], {}, args[4], failed)
        issues, proofs = audit_candidate(*args)
        self.assertEqual(issues, [])
        self.assertTrue(proofs[0]['failed_acquisition_verified'])
        self.assertFalse(proofs[0]['body_text_verified'])
        self.assertFalse(proofs[0]['quote_span_verified'])
