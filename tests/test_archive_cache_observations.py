"""A conditional fetch preserves body provenance and existing archive versions."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import archive_research_attempts as archive


class ArchiveCacheTests(unittest.TestCase):
    def add_event(self,directory,ident,cached):
        stem=directory/(ident+'.private');raw=b'Retained synthetic source text; no legal facts.'
        Path(str(stem)+'.body').write_bytes(raw);Path(str(stem)+'.txt').write_bytes(raw)
        event=dict(state='finished',kind='fetch',attempt_id=ident,ok=True,status=200,
                   artifact=str(stem)+'.json',body_sha256=hashlib.sha256(raw).hexdigest(),
                   text_sha256=hashlib.sha256(raw).hexdigest(),url='https://example.invalid/source',
                   final_url='https://example.invalid/source',finished_at='2026-11-06T12:00:00Z',
                   from_cache=cached,revalidated=cached,body_observed_at='2026-11-05T12:00:00Z',
                   origin_attempt_statuses=[304] if cached else [200])
        with (directory/'attempts.private.jsonl').open('a') as stream:stream.write(json.dumps(event)+'\n')
    def test_revalidation_does_not_rewrite_existing_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=root/'job';job.mkdir();self.add_event(job,'first',False)
            with patch.object(archive,'ROOT',root):
                archive.import_attempts(job,'ZZ',True)
                manifest=root/'work/sources/ZZ/manifest.jsonl';before=manifest.read_bytes()
                self.add_event(job,'second',True)
                result=archive.import_attempts(job,'ZZ',True)
                self.assertEqual(result['new_sources'],0);self.assertEqual(manifest.read_bytes(),before)
            self.assertEqual(len((job/'attempts.private.jsonl').read_text().splitlines()),2)
    def test_new_cached_version_records_original_body_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=root/'job';job.mkdir();self.add_event(job,'cached',True)
            with patch.object(archive,'ROOT',root):result=archive.import_attempts(job,'ZZ',True)
            row=result['sources'][0];observed=row['retrieval_observation']
            self.assertTrue(observed['from_cache']);self.assertTrue(observed['origin_revalidated'])
            self.assertEqual(observed['origin_attempt_statuses'],[304])
            self.assertEqual(observed['body_observed_at'],'2026-11-05T12:00:00Z')
            self.assertNotEqual(row['fetched_at'],observed['body_observed_at'])


if __name__=='__main__':unittest.main()
