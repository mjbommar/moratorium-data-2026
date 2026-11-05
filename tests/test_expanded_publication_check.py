"""Public release checks detect inconsistent data/receipts without private sources."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from uuid import UUID

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check_expanded_publication as m

FIRST='0d3783df2c0d66dabd7c36163910b9dfd4d88a6ff056032735975f97bb7fa906'


class PublicSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.snapshots=self.root/'expanded-snapshots'
        self.snapshots.mkdir();self.generation=self.snapshots/FIRST
        shutil.copytree(ROOT/'data/expanded-snapshots'/FIRST,self.generation)
        self.destination=self.root/'expanded';self.destination.symlink_to('expanded-snapshots/'+FIRST)
        self.registry=self.root/'registry.jsonl';shutil.copyfile(ROOT/'data/identities/expanded.jsonl',self.registry)
        self.receipt_path=self.generation/'publication.json'
        self.receipt=json.loads(self.receipt_path.read_text())

    def check(self):return m.check(self.destination,self.registry)

    def save_receipt(self,rehash_plan=False):
        if rehash_plan:self.receipt['plan_sha256']=m.digest(m.encode(self.receipt['plan']).encode())
        self.receipt_path.write_text(json.dumps(self.receipt)+'\n')

    def test_real_first_batch_checks_without_private_source_files_or_writes(self):
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=self.check()
        self.assertEqual(result['records']['ballot_measures'],1)
        self.assertEqual(result['records']['claims'],15)
        self.assertEqual(result['snapshot_sha256'],FIRST)
        self.assertEqual(before,{p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_table_byte_drift_and_missing_table_fail(self):
        path=self.generation/'claims.jsonl';raw=path.read_bytes();path.write_bytes(raw+b'\n')
        with self.assertRaisesRegex(ValueError,'fingerprint'):self.check()
        path.unlink()
        with self.assertRaisesRegex(ValueError,'table set'):self.check()

    def test_changed_plan_and_rehashed_invalid_review_still_fail(self):
        self.receipt['plan']['rationale']='Changed after publication';self.save_receipt()
        with self.assertRaisesRegex(ValueError,'plan fingerprint'):self.check()
        self.receipt['plan']['record_reviews'][0]['accepted_fields']=[];self.save_receipt(True)
        with self.assertRaisesRegex(ValueError,'Every field'):self.check()

    def test_proof_coverage_wrong_source_and_false_support_fail(self):
        original=copy.deepcopy(self.receipt)
        self.receipt['evidence'].pop();self.save_receipt()
        with self.assertRaisesRegex(ValueError,'proof coverage'):self.check()
        self.receipt=copy.deepcopy(original)
        self.receipt['evidence'][0]['source_document_id']=str(UUID(int=999));self.save_receipt()
        with self.assertRaisesRegex(ValueError,'Proof source'):self.check()
        self.receipt=copy.deepcopy(original)
        self.receipt['evidence'][0]['evidence_verified']=False;self.save_receipt()
        with self.assertRaisesRegex(ValueError,'verified support'):self.check()

    def test_later_identity_allocations_preserve_historical_baseline(self):
        events=m.read_events(self.registry.read_bytes())
        event=copy.deepcopy(next(e for e in events if e['action']=='allocate'))
        event.update(event_id=str(UUID(int=9991)),outputs=[str(UUID(int=9992))],
            aliases=[{'namespace':'synthetic-later-event','source_id':'fixture-only','record_sha256':'a'*64}])
        with self.registry.open('a') as stream:stream.write(json.dumps(event)+'\n')
        self.assertEqual(self.check()['state'],'consistent')
        # Editing earlier history does not become a valid append-only baseline.
        raw=self.registry.read_text();self.registry.write_text(raw.replace('coordinator','changed-reviewer'))
        with self.assertRaisesRegex(ValueError,'baseline'):self.check()

    def test_external_absolute_and_redirected_generation_pointers_fail(self):
        self.destination.unlink();self.destination.symlink_to(self.generation)
        with self.assertRaisesRegex(ValueError,'relative'):self.check()
        self.destination.unlink();shutil.move(self.generation,self.root/FIRST)
        self.destination.symlink_to(FIRST)
        with self.assertRaisesRegex(ValueError,'escapes'):self.check()

    def test_cyclic_predecessor_and_unsupported_plan_version_fail(self):
        self.receipt['plan']['expected_sha256']=FIRST;self.save_receipt(True)
        with self.assertRaisesRegex(ValueError,'Cyclic'):self.check()
        self.receipt['plan']['expected_sha256']=None
        self.receipt['plan']['schema_version']='99';self.save_receipt(True)
        with self.assertRaisesRegex(ValueError,'Unsupported plan'):self.check()

    def test_receipt_and_table_symlinks_fail(self):
        external=self.root/'receipt.json';shutil.move(self.receipt_path,external)
        self.receipt_path.symlink_to(external)
        with self.assertRaisesRegex(ValueError,'receipt must be retained'):self.check()
        self.receipt_path.unlink();shutil.move(external,self.receipt_path)
        table=self.generation/'claims.jsonl';external=self.root/'claims.jsonl';shutil.move(table,external);table.symlink_to(external)
        with self.assertRaisesRegex(ValueError,'regular files'):self.check()


if __name__=='__main__':unittest.main()
