import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
archive=module('archive_research_attempts');derivation=module('register_text_derivation')


class DerivationTests(unittest.TestCase):
    def test_ocr_keeps_retrieval_text_and_checks_derived_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=root/'job';job.mkdir()
            body=b'%PDF-scanned-original';(job/'abc.private.body').write_bytes(body)
            (job/'abc.private.txt').write_bytes(b'');(job/'abc.private.json').write_text('{}')
            e={'attempt_id':'abc','kind':'fetch','state':'finished','ok':True,'chars':0,
               'artifact':str(job/'abc.private.json'),'url':'https://example.gov/ordinance',
               'final_url':'https://example.gov/ordinance','status':200,'finished_at':'2026-11-05T12:00:00Z',
               'body_sha256':hashlib.sha256(body).hexdigest(),'text_sha256':hashlib.sha256(b'').hexdigest()}
            (job/'attempts.private.jsonl').write_text(json.dumps(e)+'\n')
            text=job/'derived.private.txt';text.write_text('A separately extracted legal document.\r\n')
            derivation.register(job,'abc',text,'synthetic extraction',[1],'test reviewer')
            with patch.object(archive,'ROOT',root):
                result=archive.import_attempts(job,'AK',apply=True)
                self.assertEqual(result['new_sources'],1)
                self.assertEqual((job/'abc.private.txt').read_bytes(),b'')
                self.assertEqual(result['sources'][0]['text_sha256'],hashlib.sha256(text.read_bytes()).hexdigest())
                text.write_text('Changed after review')
                with self.assertRaisesRegex(ValueError,'Derived text drift'):
                    archive.import_attempts(job,'AK')

    def test_unreviewed_text_replacement_is_not_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=root/'job';job.mkdir();raw=b'payload'
            (job/'abc.private.body').write_bytes(raw);(job/'abc.private.txt').write_text('unreviewed OCR')
            (job/'abc.private.json').write_text('{}')
            e={'attempt_id':'abc','kind':'fetch','state':'finished','ok':True,'chars':0,'artifact':str(job/'abc.private.json'),
               'body_sha256':hashlib.sha256(raw).hexdigest(),'text_sha256':hashlib.sha256(b'').hexdigest()}
            (job/'attempts.private.jsonl').write_text(json.dumps(e)+'\n')
            with patch.object(archive,'ROOT',root),self.assertRaisesRegex(ValueError,'without reviewed derivation'):
                archive.import_attempts(job,'AK')


if __name__=='__main__':unittest.main()
