"""A conditional fetch preserves body provenance and existing archive versions."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import archive_research_attempts as archive
from audit_refresh_returns import evidence_index, audit_expanded_evidence
from bridge_legacy_sources import inventory, migrate


class ArchiveCacheTests(unittest.TestCase):
    def add_event(self,directory,ident,cached,url='https://example.invalid/source',raw=None,
                  finished_at='2026-11-06T12:00:00Z',body_observed_at='2026-11-05T12:00:00Z'):
        stem=directory/(ident+'.private')
        if raw is None: raw=b'Retained synthetic source text; no legal facts.'
        Path(str(stem)+'.body').write_bytes(raw);Path(str(stem)+'.txt').write_bytes(raw)
        event=dict(state='finished',kind='fetch',attempt_id=ident,ok=True,status=200,
                   artifact=str(stem)+'.json',body_sha256=hashlib.sha256(raw).hexdigest(),
                   text_sha256=hashlib.sha256(raw).hexdigest(),url=url,
                   final_url=url,finished_at=finished_at,
                   from_cache=cached,revalidated=cached,body_observed_at=body_observed_at,
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

    def test_explicit_cross_state_selection_preserves_original_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=root/'job';job.mkdir()
            self.add_event(job,'kent',False,'https://kent.example.invalid/ordinance')
            self.add_event(job,'boone',False,'https://boone.example.invalid/ordinance')
            before=(job/'attempts.private.jsonl').read_bytes()
            with patch.object(archive,'ROOT',root):
                result=archive.import_attempts(job,'DE',True,attempt_ids=['kent'])
            self.assertEqual(result['new_sources'],1)
            self.assertEqual(result['sources'][0]['url'],'https://kent.example.invalid/ordinance')
            self.assertEqual(result['sources'][0]['attempt_id'],'kent')
            self.assertEqual((job/'attempts.private.jsonl').read_bytes(),before)

    def test_unknown_selected_attempt_rejected_before_archive_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=root/'job';job.mkdir();self.add_event(job,'kent',False)
            with patch.object(archive,'ROOT',root):
                with self.assertRaises(ValueError):
                    archive.import_attempts(job,'DE',True,attempt_ids=['not-recorded'])
            self.assertFalse((root/'work/sources').exists())

    def test_changed_url_body_preserves_versions_and_each_claim_binding(self):
        """A replacement web page cannot silently supply an old claim's quote."""
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=root/'job';job.mkdir()
            url='https://example.invalid/source'
            old=b'Original synthetic text: amber river.'
            new=b'Revised synthetic text: violet meadow.'
            self.add_event(job,'old',False,url,old,body_observed_at='2026-11-06T12:00:00Z')
            with patch.object(archive,'ROOT',root):
                first=archive.import_attempts(job,'ZZ',True)['sources'][0]
                manifest=root/'work/sources/ZZ/manifest.jsonl'
                prefix=manifest.read_bytes()
                original_files={p:(root/p).read_bytes() for p in first['files']}
                self.add_event(job,'new',False,url,new,finished_at='2026-11-07T12:00:00Z',
                               body_observed_at='2026-11-07T12:00:00Z')
                second=archive.import_attempts(job,'ZZ',True)['sources'][0]
                self.assertNotEqual(first['key'],second['key'])
                self.assertTrue(manifest.read_bytes().startswith(prefix))
                self.assertEqual(len(manifest.read_text().splitlines()),2)
                self.assertEqual(archive.import_attempts(job,'ZZ',True)['new_sources'],0)
                for path,body in original_files.items():
                    self.assertEqual((root/path).read_bytes(),body)
            index,issues,_=evidence_index(job)
            self.assertEqual(issues,[])
            records={'source_documents':[], 'claims':[]}
            for ident,row,quote in [('old',first,'text: amber river.'),('new',second,'text: violet meadow.')]:
                records['source_documents'].append({'source_document_id':ident,'url':url,
                    'body_sha256':row['sha256'],'text_sha256':row['text_sha256']})
                records['claims'].append({'claim_id':ident,'source_document_id':ident,'quote':quote})
            issues,proofs=audit_expanded_evidence(records,index)
            self.assertEqual(issues,[])
            self.assertTrue(all(p['evidence_verified'] for p in proofs))
            self.assertNotEqual(proofs[0]['verified_text_artifact'],proofs[1]['verified_text_artifact'])
            # Exercise the actual native-store boundary, not just archive keys.
            from bc_store import Store
            archived,_=inventory(root,[manifest])
            self.assertTrue(all(not r['issues'] for r in archived))
            self.assertEqual(migrate(root,archived,root/'native'),2)
            self.assertEqual(migrate(root,archived,root/'native'),2)
            native_index={url:[]}
            with Store(root/'native') as store:
                observations=store.observations()
                self.assertEqual(len(observations),2)
                self.assertEqual({store.payload(o) for o in observations},{old,new})
                for observation in observations:
                    body=store.payload(observation)
                    self.assertEqual(hashlib.sha256(body).hexdigest(),observation.payload_sha256)
                    texts=[d for d in store.derivations(observation_id=observation.id) if d.kind=='text']
                    self.assertEqual(len(texts),1)
                    text=store.blobs.get(texts[0].sha256)
                    self.assertEqual(text,body)
                    native_index[url].append(dict(body_sha256=observation.payload_sha256,
                        text_sha256=hashlib.sha256(text).hexdigest(),text=text.decode(),
                        text_artifact='native:'+texts[0].sha256))
            native_issues,native_proofs=audit_expanded_evidence(records,native_index)
            self.assertEqual(native_issues,[])
            self.assertTrue(all(p['evidence_verified'] for p in native_proofs))
            crossed=deepcopy(records)
            crossed['claims'][0]['quote']='violet meadow'
            self.assertFalse(audit_expanded_evidence(crossed,index)[1][0]['evidence_verified'])
            crossed=deepcopy(records)
            crossed['source_documents'][0]['body_sha256']=second['sha256']
            self.assertTrue(audit_expanded_evidence(crossed,index)[0])
            (job/'old.private.body').write_bytes(b'changed after collection')
            tampered,issues,_=evidence_index(job)
            self.assertTrue(issues)
            self.assertFalse(audit_expanded_evidence(records,tampered)[1][0]['evidence_verified'])
            self.assertTrue(all(p['evidence_verified'] for p in
                                audit_expanded_evidence(records,native_index)[1]))
            with patch.object(archive,'ROOT',root):
                with self.assertRaises(ValueError):archive.import_attempts(job,'ZZ',True)


if __name__=='__main__':unittest.main()
