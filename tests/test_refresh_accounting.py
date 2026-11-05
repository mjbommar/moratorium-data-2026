import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_refresh_accounting import collection_stage


class RefreshAccountingTests(unittest.TestCase):
    def valid(self):
        return {'cli_state': 'finished', 'checks': [], 'schema_errors': [],
                'missing_ids': [], 'extra_ids': [], 'duplicate_ids': []}

    def test_unresolved_return_is_not_successful_verification(self):
        self.assertEqual(collection_stage(self.valid(), 'unresolvable'), 'returned_unresolved')
        self.assertEqual(collection_stage(self.valid(), 'confirmed_unchanged'),
                         'returned_other_outcome')

    def test_incomplete_or_invalid_batch_does_not_count_as_returned(self):
        for field in ('schema_errors', 'missing_ids', 'extra_ids', 'duplicate_ids', 'checks'):
            job = self.valid()
            job[field] = ['problem']
            self.assertEqual(collection_stage(job, 'corrected'), 'terminal_without_valid_complete_return')
        self.assertEqual(collection_stage(self.valid(), None), 'terminal_without_valid_complete_return')

    def test_nonterminal_or_unchecked_output_cannot_pass(self):
        job = self.valid()
        job['cli_state'] = 'running'
        self.assertEqual(collection_stage(job, 'corrected'), 'running')
        self.assertEqual(collection_stage(None, 'corrected'), 'queued')
        self.assertEqual(collection_stage({'cli_state': 'finished'}, 'corrected'),
                         'terminal_without_valid_complete_return')

    def test_both_ledger_formats_and_historical_exclusion(self):
        import json
        import tempfile
        from build_refresh_accounting import build
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data').mkdir()
            audits = root / 'work/audit'
            audits.mkdir(parents=True)
            (root / 'data/moratorium_inventory.csv').write_text(
                'moratorium_id,state_abbrev\nlocal-1,ME\nlocal-2,ME\n')
            (root / 'data/state_legislation.csv').write_text(
                'policy_action_id,state_abbrev,bill\npolicy-1,ME,LD 1\n')
            for filename, change in [
                ('apply-20261105T010101.json', {'moratorium_id': 'local-1'}),
                ('apply-20260731T010101.json', {'moratorium_id': 'local-2'}),
                ('apply-legislation-20261105T010101.json', {'bill_key': 'ME:LD 1'}),
            ]:
                (audits / filename).write_text(json.dumps({'changes': [change]}))
            queue, audit = root / 'queue.json', root / 'audit.json'
            queue.write_text(json.dumps({'jobs': [], 'completed_pilot_ids': {}}))
            audit.write_text(json.dumps({'jobs': [], 'observed_at': '2026-11-05',
                                         'job_states': {}, 'not_started_jobs': 0}))
            result = build(queue, audit, root)
            inventory = result['tables']['inventory']
            self.assertEqual(inventory['editorial_counts'],
                             {'has_refresh_apply_change': 1, 'no_refresh_apply_change': 1})
            self.assertEqual(result['tables']['state_policy']['editorial_counts'],
                             {'has_refresh_apply_change': 1})
            self.assertEqual(inventory['collection_counts'], {'not_assigned_in_this_queue': 2})
            self.assertTrue(all(r['legal_force_verification'] ==
                                'not_assessed_by_this_mechanical_accounting'
                                for r in inventory['records']))
