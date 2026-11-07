"""Exercise the additive condition profile through real publication/CSV paths."""
import copy
import json
from pathlib import Path
import sys
import unittest
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_event_profile_publication as fixtures
from test_condition_expression import clause, group, threshold
from expanded_data import profile_path
from expanded_promotion import publish,digest,serialized,encode
from check_expanded_publication import check
from build_expanded_csv import build_outputs


def upgrade(plan):
    plan['schema_version']='1.0.3'
    plan['validation_profile']={'name':'1.0.3','schema_sha256':digest(profile_path('1.0.3').read_bytes()),'semantics':'event-validity-conditions-v1'}
    return plan


class ConditionPublicationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.EventProfilePublicationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_profile_preserves_legacy_record_and_rejects_incomplete_groups(self):
        schema=json.loads(profile_path('1.0.3').read_text())
        validator=Draft202012Validator({'$ref':'#/$defs/measure_provisions','$defs':schema['$defs']})
        base=json.loads((ROOT/'data/expanded/measure_provisions.jsonl').read_text().splitlines()[0])
        self.assertTrue(validator.is_valid(base))
        new=copy.deepcopy(base)
        new['condition_clauses']=[clause(group('any',threshold('capacity'),threshold('demand')))]
        self.assertTrue(validator.is_valid(new))
        old=json.loads(profile_path('1.0.2').read_text())
        self.assertFalse(Draft202012Validator({'$ref':'#/$defs/measure_provisions','$defs':old['$defs']}).is_valid(new))
        new['condition_clauses'][0]['expression']={'type':'at_least','count':3,'members':[threshold('capacity'),threshold('demand')]}
        self.assertFalse(validator.is_valid(new))

    def test_profile_upgrade_exact_replay_views_and_downgrade_rejection(self):
        f=self.fixture
        f.publish()
        original=f.destination.resolve()
        rows,candidate,plan=f.prepare('2026-11-02T13:00:00Z')
        upgrade(plan)
        result=publish(f.destination,candidate,f.registry,plan,[f.evidence],apply=True,moratoria=f.legacy)
        self.assertNotEqual(f.destination.resolve(),original)
        self.assertEqual(check(f.destination,f.registry,f.legacy)['generations_checked'],2)
        self.assertEqual(publish(f.destination,candidate,f.registry,plan,[f.evidence],apply=True,moratoria=f.legacy)['state'],'already_applied')
        _,outputs=build_outputs(f.destination.resolve())
        manifest=json.loads(outputs['manifest.json'])
        self.assertEqual(manifest['validation_profile']['name'],'1.0.3')
        self.assertIn('instrument_events_current.csv',outputs)
        self.assertIn('condition_clauses',outputs['measure_provisions.csv'].decode().splitlines()[0])
        f.previous=rows
        _,candidate,downgrade=f.prepare('2026-11-03T13:00:00Z')
        pointer=f.destination.resolve()
        with self.assertRaisesRegex(ValueError,'Cannot downgrade condition'):
            publish(f.destination,candidate,f.registry,downgrade,[f.evidence],apply=True,moratoria=f.legacy)
        self.assertEqual(f.destination.resolve(),pointer)
        # The new profile retains the event-validity withdrawal contract.
        fixtures.withdraw(f.raw,time='2026-11-03T12:00:00Z')
        rows,candidate,plan=f.prepare('2026-11-03T13:00:00Z')
        upgrade(plan)
        publish(f.destination,candidate,f.registry,plan,[f.evidence],apply=True,moratoria=f.legacy)
        self.assertEqual(check(f.destination,f.registry,f.legacy)['generations_checked'],3)
        _,outputs=build_outputs(f.destination.resolve())
        self.assertEqual(len(outputs['instrument_events_current.csv'].decode().splitlines()),1)

if __name__=='__main__':unittest.main()
