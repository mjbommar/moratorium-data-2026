"""Legal forms must not silently change bill ranking denominators."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_summary_stats as stats

class PolicyFormStatisticsTests(unittest.TestCase):
    def test_bill_and_all_policy_rankings_use_their_own_populations(self):
        inventory=[dict(state='Alabama',state_abbrev='AL',activity_level='Low',enacted_status='pending')]
        policies=[]
        for state,kind,count in [('Alabama','bill',1),('Alabama','legislative_resolution',3),('Alaska','bill',2),('Alaska','legislative_precursor',1),('Alaska','legislative_amendment',2)]:
            policies.extend(dict(state=state,state_abbrev='AL' if state=='Alabama' else 'AK',activity_level='Low',policy_instrument_type=kind,policy_action_id=f"{('al' if state=='Alabama' else 'ak')}-{kind.replace('_','-')}-{i}") for i in range(count))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with patch.object(stats,'load',side_effect=lambda path: inventory if path==stats.INV else policies),patch.object(stats,'STATS',root/'stats.json'),patch.object(stats,'SWEEP',root/'sweep.json'),patch.object(stats,'STATES_DIR',root/'states'),patch.object(stats,'SCOPE_REGISTRY',root/'missing-registry.jsonl'):
                result=stats.build()
        self.assertEqual(result['total_state_bills'],3)
        self.assertEqual(result['total_state_policy_actions'],9)
        self.assertEqual(result['top_states_by_bills'],[['Alaska',2],['Alabama',1]])
        self.assertEqual(result['top_states_by_policy_actions'],[['Alaska',5],['Alabama',4]])
        self.assertEqual(result['state_policy_instrument_type_counts'],{'bill':3,'legislative_precursor':1,'legislative_resolution':3,'legislative_amendment':2})
        self.assertEqual(result['state_details']['Alabama']['state_bills_count'],1)
        self.assertEqual(result['state_details']['Alabama']['state_policy_actions_count'],4)

if __name__=='__main__':unittest.main()
