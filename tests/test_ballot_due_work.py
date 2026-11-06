import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from build_ballot_due_work import tasks


class DueWorkTest(unittest.TestCase):
    def run_tasks(self, day, results=(), bindingness='binding', precision='day'):
        return tasks([{'measure_id':'m','election_id':'e','bindingness':bindingness}],
                     {'e':{'election_date':{'earliest':day,'latest':day,'precision':precision}}},
                     list(results),dt.date(2026,11,6))

    def test_scheduled_does_not_request_early_certification(self):
        result=self.run_tasks('2026-12-15')
        self.assertEqual({r['kind'] for r in result},{'qualification_and_ballot','election_results'})
        self.assertTrue(all(not r['due_now'] for r in result))

    def test_certified_successor_removes_old_uncertified_task(self):
        old={'result_observation_id':'old','measure_id':'m','certification_status':'unknown'}
        new={'result_observation_id':'new','measure_id':'m','certification_status':'certified','supersedes_id':'old'}
        self.assertEqual([r['kind'] for r in self.run_tasks('2026-11-03',[old,new])],['implementation_review'])

    def test_advisory_certification_still_needed_without_law_task(self):
        result=self.run_tasks('2026-11-03',[{'result_observation_id':'r','measure_id':'m','certification_status':'unknown'}],'advisory')
        self.assertEqual([r['kind'] for r in result],['certification_or_recount'])

    def test_partial_date_is_not_assigned_a_day(self):
        result=self.run_tasks('2026-11-01',precision='month')
        self.assertEqual(result[0]['kind'],'election_date_review')
        self.assertIsNone(result[0]['due_on'])


if __name__=='__main__':
    unittest.main()
