import sys
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_refresh_returns import audit_expanded_evidence, candidate_id_coverage, pinned_evidence_index


class ExpandedEvidenceAudit(unittest.TestCase):
    def test_reused_source_requires_retained_hash_verified_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);body=b'%PDF original';text=b'The measure was approved.'
            sha=lambda value:hashlib.sha256(value).hexdigest()
            (base/'body').write_bytes(body);(base/'text').write_bytes(text)
            manifest=base/'manifest.json';manifest.write_text(json.dumps({'body':sha(body),'text':sha(text)}))
            pin=sha(manifest.read_bytes())
            source={'source_document_id':'prior','url':'https://example.gov/prior',
                    'body_sha256':sha(body),'text_sha256':sha(text)}
            index,issues=pinned_evidence_index(base,manifest,pin,[source])
            self.assertEqual(issues,[]);self.assertIn(source['url'],index)
            (base/'text').write_bytes(text+b'\r\n')
            manifest.write_text(json.dumps({'body':sha(body),'text':sha(text+b'\r\n')}))
            # The documented pilot text transform is bound to the pinned raw file.
            source['text_sha256']=sha(text+b'\n')
            (base/'text.txt').write_bytes((base/'text').read_bytes())
            manifest.write_text(json.dumps({'body':sha(body),'text.txt':sha(text+b'\r\n')}))
            pin=sha(manifest.read_bytes())
            index,issues=pinned_evidence_index(base,manifest,pin,[source])
            self.assertEqual(issues,[])
            self.assertEqual(index[source['url']][0]['text'],text.decode()+'\n')
            (base/'body').write_bytes(b'changed')
            index,issues=pinned_evidence_index(base,manifest,pin,[source])
            self.assertEqual(dict(index),{});self.assertEqual(len(issues),1)
            manifest.write_text('{}')
            with self.assertRaisesRegex(ValueError,'manifest drift'):
                pinned_evidence_index(base,manifest,pin,[source])

    def test_returned_count_alone_cannot_prove_seed_coverage(self):
        coverage=candidate_id_coverage(['a','b','c'],[{'seed_id':'a'},{'seed_id':'a'},{'seed_id':'x'}])
        self.assertEqual(coverage,{'missing_seed_ids':['b','c'],'extra_seed_ids':['x'],'duplicate_seed_ids':['a']})

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

    def test_payload_only_source_does_not_prove_a_text_claim(self):
        records,index=self.fixture()
        records['source_documents'][0]['text_sha256']=None
        issues,proofs=audit_expanded_evidence(records,index)
        self.assertEqual(issues,[])
        self.assertFalse(proofs[0]['quote_located'])
