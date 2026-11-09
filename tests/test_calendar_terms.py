import csv
import datetime as dt
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
apply=module('apply_research');worklist=module('build_worklist')
validate=module('validate_dataset');state_pages=module('update_state_counts')


class CalendarTerms(unittest.TestCase):
    def test_calendar_conversion_keeps_unknown_current_end_visible(self):
        with (ROOT/'data/moratorium_inventory.csv').open() as f:
            reader=csv.DictReader(f);fields=reader.fieldnames
            row=next(reader)
        row.update(duration_kind='calendar_term',duration_days='',current_end_date_iso='')
        for status in ('active','extended','replaced','expired','rescinded','pending','rejected'):
            row['enacted_status']=status
            report=validate.Report()
            validate.check_inventory([row],fields,dt.date(2026,11,5),report)
            flagged=any(code=='duration.calendar_end_unverified' for code,_ in report.warnings)
            self.assertEqual(flagged,status in {'active','extended'})
        row.update(enacted_status='active',current_end_date_iso='2027-09-22')
        report=validate.Report()
        validate.check_inventory([row],fields,dt.date(2026,11,5),report)
        self.assertFalse(any(code=='duration.calendar_end_unverified' for code,_ in report.warnings))

    def test_rejected_proposal_is_valid_without_adoption_date(self):
        with (ROOT/'data/moratorium_inventory.csv').open() as f:
            reader=csv.DictReader(f);fields=reader.fieldnames;row=next(reader)
        row.update(enacted_status='rejected',date_enacted_iso='',
                   date_enacted_uncertainty='unverified',current_end_date_iso='')
        report=validate.Report()
        validate.check_inventory([row],fields,dt.date(2026,11,5),report)
        self.assertFalse(any(code=='vocab.enacted_status' for code,_ in report.errors))
        self.assertFalse(any(code=='date.missing' for code,_ in report.warnings))

    def test_rejected_proposal_is_separate_in_state_counts(self):
        rows=[{'enacted_status':s}for s in validate.ENACTED_STATUSES]
        counts=state_pages.counts_for(rows)
        self.assertEqual(counts,dict(in_force=2,pending=1,past=3,rejected=1,total=7))

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
