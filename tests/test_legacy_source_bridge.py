import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from bridge_legacy_sources import inventory, migrate, report


class LegacySourceBridgeTests(unittest.TestCase):
    def fixture(self, root, **changes):
        folder = root / 'work/sources/XX'
        folder.mkdir(parents=True, exist_ok=True)
        body = b'%PDF-test body'
        text = b'Retained text'
        (folder / 'source.pdf').write_bytes(body)
        (folder / 'source.txt').write_bytes(text)
        row = {'url': 'https://example.gov/record', 'fetched_at': '2026-11-05T12:00:00Z',
               'ok': True, 'status': 200, 'published': False, 'key': 'historical-key',
               'sha256': hashlib.sha256(body).hexdigest(),
               'text_sha256': hashlib.sha256(text).hexdigest(),
               'files': ['work/sources/XX/source.pdf', 'work/sources/XX/source.txt']}
        row.update(changes)
        manifest = folder / 'manifest.jsonl'
        manifest.write_text(json.dumps(row) + '\n')
        return manifest, row

    def test_exact_metadata_payload_and_idempotent_replay(self):
        from bc_store import Store
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, row = self.fixture(root)
            records, inputs = inventory(root, [manifest])
            original = manifest.read_bytes()
            self.assertEqual(migrate(root, records, root / 'store'), 1)
            self.assertEqual(migrate(root, records, root / 'store'), 1)
            with Store(root / 'store') as store:
                observations = store.observations()
                self.assertEqual(len(observations), 1)
                self.assertEqual(store.payload(observations[0]), b'%PDF-test body')
                derived = store.derivations(observation_id=observations[0].id)
                metadata = next(d for d in derived if d.kind == 'metadata')
                self.assertEqual(store.blobs.get(metadata.sha256), original)
                self.assertIs(json.loads(store.blobs.get(metadata.sha256))['published'], False)
            self.assertEqual(manifest.read_bytes(), original)
            self.assertEqual(report(records, inputs)['gap_records'], 0)

    def test_missing_body_is_gap_not_hash_only_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, row = self.fixture(root)
            (root / row['files'][0]).unlink()
            records, _ = inventory(root, [manifest])
            self.assertIn('original_body_not_retained_or_hash_not_matched', records[0]['issues'])
            self.assertEqual(migrate(root, records, root / 'store'), 0)

    def test_text_hash_drift_blocks_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, row = self.fixture(root)
            (root / row['files'][1]).write_text('changed extraction')
            records, _ = inventory(root, [manifest])
            self.assertIn('asserted_text_hash_not_matched', records[0]['issues'])

    def test_same_native_identity_different_bodies_stays_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, row = self.fixture(root)
            other = dict(row, sha256='0' * 64)
            with manifest.open('a') as out:
                out.write(json.dumps(other) + '\n')
            records, _ = inventory(root, [manifest])
            self.assertTrue(all('native_observation_identity_body_conflict' in r['issues'] for r in records))

    def test_changed_bytes_between_plan_and_apply_reject_before_observations(self):
        from bc_store import Store
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, row = self.fixture(root)
            records, _ = inventory(root, [manifest])
            (root / row['files'][0]).write_bytes(b'drift')
            with self.assertRaisesRegex(ValueError, 'changed after inventory'):
                migrate(root, records, root / 'store')
            with Store(root / 'store') as store:
                self.assertEqual(store.observations(), [])
