import datetime as dt
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
apply=module('apply_research');worklist=module('build_worklist')


class CalendarTerms(unittest.TestCase):
    def test_unknown_extension_endpoint_does_not_reuse_original_expiry(self):
        row={'enacted_status':'extended','duration_kind':'fixed_days','duration_days':'45',
             'date_enacted_iso':'2026-08-26','current_end_date_iso':''}
        self.assertIsNone(worklist.computed_expiry(row))
        row['current_end_date_iso']='2028-09-16'
        self.assertEqual(worklist.computed_expiry(row),dt.date(2028,9,16))

    def test_calendar_year_does_not_become_730_days(self):
        row={'duration_kind':'calendar_term','duration_days':'730','duration':'Two calendar years from signature',
             'date_enacted_iso':'2026-10-08','current_end_date_iso':''}
        self.assertIsNone(worklist.computed_expiry(row))
        apply.enforce_duration_invariant(row)
        self.assertEqual(row['duration_kind'],'calendar_term');self.assertEqual(row['duration_days'],'')
        self.assertIsNone(worklist.computed_expiry(row))

    def test_explicit_end_can_be_used_without_invented_anchor(self):
        row={'duration_kind':'calendar_term','duration_days':'','date_enacted_iso':'2026-10-08','current_end_date_iso':'2028-10-14'}
        self.assertEqual(worklist.computed_expiry(row),dt.date(2028,10,14))


if __name__=='__main__':unittest.main()
