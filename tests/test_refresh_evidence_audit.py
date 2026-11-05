import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_refresh_returns import audit_expanded_evidence


class ExpandedEvidenceAudit(unittest.TestCase):
    def fixture(self):
        source={'source_document_id':'s1','url':'https://example.gov/results',
                'body_sha256':'body','text_sha256':'text'}
        claim={'claim_id':'c1','source_document_id':'s1',
               'quote':'The measure was approved.'}
        version={'body_sha256':'body','text_sha256':'text',
                 'text':'Results: The measure was approved. End.',
                 'text_artifact':'retained.txt'}
        return {'source_documents':[source],'claims':[claim]}, {source['url']:[version]}

    def test_matching_url_does_not_substitute_for_matching_payload(self):
        records,index=self.fixture()
        records['source_documents'][0]['body_sha256']='different'
        issues,proofs=audit_expanded_evidence(records,index)
        self.assertEqual(len(issues),1)
        self.assertFalse(proofs[0]['quote_located'])

    def test_missing_quote_fails_even_when_source_hashes_match(self):
        records,index=self.fixture()
        records['claims'][0]['quote']='The measure was rejected.'
        issues,proofs=audit_expanded_evidence(records,index)
        self.assertEqual(issues,[])
        self.assertFalse(proofs[0]['quote_located'])

    def test_verified_location_is_recomputed(self):
        records,index=self.fixture()
        records['claims'][0]['span']='worker supplied unsupported offset'
        issues,proofs=audit_expanded_evidence(records,index)
        self.assertEqual(issues,[])
        self.assertEqual(proofs[0]['verified_span'],(9,34))
        self.assertEqual(proofs[0]['verified_text_artifact'],'retained.txt')

    def test_validator_id_indexed_tables(self):
        records,index=self.fixture()
        records={k:{'id':v[0]} for k,v in records.items()}
        issues,proofs=audit_expanded_evidence(records,index)
        self.assertEqual(issues,[])
        self.assertTrue(proofs[0]['quote_located'])
