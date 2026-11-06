import copy
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import legacy_moratorium_identity as identity
from preview_legacy_identity import row_hash, sha


class LegacyMoratoriumIdentityTests(unittest.TestCase):
    def fixture(self, root):
        raw = b'moratorium_id,enacted_status,note\r\na,active,canonical\r\nb,active,older observation\r\nc,pending,other act\r\n'
        inventory = root/'moratorium_inventory.csv'
        inventory.write_bytes(raw)
        rows = list(csv.DictReader(io.StringIO(raw.decode())))
        retired = rows[1]
        output = io.StringIO(newline='')
        writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator='\r\n')
        writer.writeheader(); writer.writerows([rows[0], rows[2]])
        plan = dict(schema_version='legacy-moratorium-retirement-1',
                    preview_plan=dict(schema_version='legacy-identity-preview-1', inventory_sha256=sha(raw),
                        reviewer='reviewer', reviewed_at='2026-11-06T00:00:00Z', merges=[dict(
                            canonical_id='a', alias_ids=['b'], record_sha256={r['moratorium_id']:row_hash(r) for r in rows[:2]},
                            evidence=[dict(url='https://example.gov/act', body_sha256='0'*64, locator='Act title')],
                            rationale='Explicit duplicate identity review')]),
                    event_id='76a227d3-4bc4-40b8-96f6-5c1af3ec3b34', expected_registry_sha256=sha(b''),
                    inventory_after_sha256=sha(output.getvalue().encode()), retired_record=retired)
        return inventory, identity.registry_path(inventory), plan, raw

    def test_explicit_retirement_preserves_every_survivor_and_legacy_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory, registry, plan, original = self.fixture(Path(tmp))
            self.assertEqual(identity.retire(inventory, registry, plan)['state'], 'ready')
            self.assertEqual(inventory.read_bytes(), original)
            self.assertFalse(registry.exists())
            self.assertEqual(identity.retire(inventory, registry, plan, True)['state'], 'applied')
            result = identity.lookup(inventory, 'b')
            self.assertEqual(result['canonical_id'], 'a')
            self.assertEqual(result['record']['note'], 'canonical')
            event = json.loads(registry.read_text())
            self.assertEqual(event['retired_record']['note'], 'older observation')
            state = inventory.read_bytes(), registry.read_bytes()
            self.assertEqual(identity.retire(inventory, registry, plan, True)['state'], 'already_applied')
            self.assertEqual(state, (inventory.read_bytes(), registry.read_bytes()))

    def test_interruption_after_csv_replacement_can_resume_exact_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory, registry, plan, _ = self.fixture(Path(tmp))
            original_write = identity.atomic_write
            def failing(path, raw):
                if path == registry: raise OSError('injected registry write failure')
                original_write(path, raw)
            with patch.object(identity, 'atomic_write', side_effect=failing):
                with self.assertRaises(OSError): identity.retire(inventory, registry, plan, True)
            self.assertEqual(identity.retire(inventory, registry, plan)['state'], 'resume_registry')
            identity.retire(inventory, registry, plan, True)
            self.assertEqual(identity.lookup(inventory, 'b')['canonical_id'], 'a')

    def test_stale_input_and_retired_preimage_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory, registry, plan, raw = self.fixture(Path(tmp))
            wrong = copy.deepcopy(plan)
            wrong['retired_record']['note'] = 'unreviewed'
            with self.assertRaisesRegex(ValueError, 'preimage differs'):
                identity.retire(inventory, registry, wrong, True)
            inventory.write_bytes(raw.replace(b'canonical', b'changed'))
            with self.assertRaisesRegex(ValueError, 'differs from review|Inventory changed'):
                identity.retire(inventory, registry, plan, True)
            self.assertFalse(registry.exists())

    def test_identity_replay_preserves_later_survivor_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory, registry, plan, _ = self.fixture(Path(tmp))
            identity.retire(inventory, registry, plan, True)
            inventory.write_bytes(inventory.read_bytes().replace(b'canonical', b'later reviewed value'))
            current = inventory.read_bytes()
            self.assertEqual(identity.retire(inventory, registry, plan, True)['state'], 'already_applied')
            self.assertEqual(inventory.read_bytes(), current)
            self.assertEqual(identity.lookup(inventory, 'b')['record']['note'], 'later reviewed value')

    def test_registry_target_and_retired_history_drift_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            inventory, registry, plan, _ = self.fixture(Path(tmp))
            identity.retire(inventory, registry, plan, True)
            with self.assertRaisesRegex(ValueError, 'no surviving'):
                identity.load_aliases(inventory, {'c'})
            event = json.loads(registry.read_text())
            event['retired_record']['note'] = 'changed'
            registry.write_text(json.dumps(event)+'\n')
            with self.assertRaisesRegex(ValueError, 'observation changed'):
                identity.lookup(inventory, 'b')
