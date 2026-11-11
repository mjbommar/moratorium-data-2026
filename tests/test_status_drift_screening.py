import copy
import csv
import datetime as dt
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_dataset import Report, check_inventory
from build_worklist import classify, build_item


class StatusDriftScreeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(Path(__file__).resolve().parents[1] / 'data/moratorium_inventory.csv', newline='') as stream:
            reader = csv.DictReader(stream)
            cls.fields = reader.fieldnames
            cls.lodi = next(r for r in reader if r['moratorium_id'] == 'mi-lodi-township-2026')

    def warnings(self, row, today):
        report = Report()
        check_inventory([row], self.fields, today, report)
        return [message for kind, message in report.warnings if kind == 'status.drift']

    def test_successor_endpoint_prevents_old_term_false_positive(self):
        today = dt.date(2026, 11, 11)
        self.assertEqual(self.warnings(self.lodi, today), [])
        self.assertNotIn('expired_in_force', classify(self.lodi, today, 60))

    def test_past_recorded_endpoint_still_flags_extended_record(self):
        row = copy.deepcopy(self.lodi)
        row.update(enacted_status='extended', current_end_date_iso='2026-11-01')
        warnings = self.warnings(row, dt.date(2026, 11, 11))
        self.assertEqual(len(warnings), 1)
        self.assertIn('recorded current endpoint 2026-11-01', warnings[0])
        self.assertIn('not proof of legal expiry', warnings[0])
        item = build_item(row, ['expired_in_force'], dt.date(2026, 11, 11))
        self.assertIn('does not prove legal expiry', item['questions'][0])
        self.assertNotIn('original term ran out', item['questions'][0])

    def test_original_arithmetic_is_screening_not_legal_conclusion(self):
        row = copy.deepcopy(self.lodi)
        row['current_end_date_iso'] = ''
        warnings = self.warnings(row, dt.date(2026, 11, 11))
        self.assertEqual(len(warnings), 1)
        self.assertIn('screening date', warnings[0])
        self.assertNotIn('computed expiry', warnings[0])

    def test_invalid_current_endpoint_does_not_fall_back_to_old_term(self):
        row = copy.deepcopy(self.lodi)
        row['current_end_date_iso'] = 'bad-date'
        report = Report()
        check_inventory([row], self.fields, dt.date(2026, 11, 11), report)
        self.assertTrue(any(kind == 'date.current_end_format' for kind, _ in report.errors))
        self.assertFalse(any(kind == 'status.drift' for kind, _ in report.warnings))


if __name__ == '__main__':
    unittest.main()
