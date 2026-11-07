"""Offline contract tests for source-reviewed policy instrument forms."""
import contextlib
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import apply_legislation as apply
import validate_dataset as validate

FORMS = ('legislative_precursor', 'legislative_resolution')
EVIDENCE = [{'url': 'https://example.invalid/source', 'source_type': 'journal',
             'supports': 'Synthetic source-reviewed instrument form'}]
SCHEMA = json.loads((ROOT / 'work/schemas/legislation_decision.schema.json').read_text())


def decision(form):
    return {'state_abbrev': 'CA', 'researched_as_of': '2026-11-07',
            'decisions': [{'bill_key': 'CA:S1', 'outcome': 'corrected',
                           'fields': {'policy_instrument_type': form}, 'evidence': EVIDENCE}]}


def new_row_decision(form):
    return {'state_abbrev': 'CA', 'researched_as_of': '2026-11-07', 'decisions': [],
            'new_bills': [{'state': 'California', 'bill': 'S2', 'key_provisions': 'Synthetic',
                           'policy_instrument_type': form, 'evidence': EVIDENCE}]}


class PolicyInstrumentFormsTests(unittest.TestCase):
    def test_schema_accepts_both_forms_in_both_locations_and_rejects_unknown(self):
        for make in (decision, new_row_decision):
            for form in FORMS:
                with self.subTest(location=make.__name__, form=form):
                    jsonschema.validate(make(form), SCHEMA)
            with self.subTest(location=make.__name__, form='unknown'):
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(make('not_a_form'), SCHEMA)

    def exercise_apply(self, form, stale=False, new=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'data').mkdir()
            path = root / 'data/state_legislation.csv'
            columns = apply.BASE_COLUMNS + apply.NEW_COLUMNS
            row = dict.fromkeys(columns, '')
            row.update(state='California', state_abbrev='CA', bill='S1', activity_level='Low',
                       policy_action_id='ca-s1', policy_instrument_type='bill',
                       legal_effect_status='unknown')
            with path.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=columns)
                writer.writeheader()
                writer.writerow(row)
            baseline = root / 'baseline.json'
            baseline.write_text(json.dumps([row]))
            if stale:
                row['sponsors'] = 'Concurrent edit'
                with path.open('w', newline='') as stream:
                    writer = csv.DictWriter(stream, fieldnames=columns)
                    writer.writeheader()
                    writer.writerow(row)
            before = path.read_bytes()
            answers = root / 'answers.json'
            answers.write_text(json.dumps(new_row_decision(form) if new else decision(form)))
            output = io.StringIO()
            with patch.object(apply, 'REPO', root), patch.object(apply, 'LEG', path), \
                 patch.object(apply, 'AUDIT_DIR', root / 'audit'), \
                 patch.object(sys, 'argv', ['apply_legislation', '--answers', str(answers),
                                            '--baseline', str(baseline)]), \
                 contextlib.redirect_stdout(output):
                result = apply.main()
            if stale or form == 'not_a_form':
                self.assertEqual(result, 1, output.getvalue())
                self.assertEqual(path.read_bytes(), before)
                self.assertFalse((root / 'audit').exists())
                if stale:
                    self.assertIn('stale or missing baseline', output.getvalue())
                return
            self.assertEqual(result, 0, output.getvalue())
            with path.open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            if new:
                self.assertEqual(rows[0], row)
                self.assertEqual(rows[1]['policy_instrument_type'], form)
                self.assertEqual(rows[1]['policy_action_id'], 'ca-s2')
            else:
                self.assertEqual(rows, [{**row, 'policy_instrument_type': form}])
                receipt = json.loads(next((root / 'audit').glob('*.json')).read_text())
                self.assertEqual([change['column'] for change in receipt['changes']],
                                 ['policy_instrument_type'])

    def test_source_reviewed_change_preserves_whole_row_and_id(self):
        for form in FORMS:
            with self.subTest(form=form):
                self.exercise_apply(form)

    def test_stale_whole_row_blocks_form_change(self):
        for form in FORMS:
            with self.subTest(form=form):
                self.exercise_apply(form, stale=True)

    def test_new_rows_accept_forms(self):
        for form in FORMS:
            with self.subTest(form=form):
                self.exercise_apply(form, new=True)

    def test_apply_rejects_unknown_form(self):
        for new in (False, True):
            with self.subTest(new=new):
                self.exercise_apply('not_a_form', new=new)

    def test_dataset_accepts_forms_and_rejects_unknown(self):
        columns = apply.BASE_COLUMNS + apply.NEW_COLUMNS
        row = dict.fromkeys(columns, '')
        row.update(state='California', state_abbrev='CA', bill='S1', activity_level='Low',
                   policy_action_id='ca-s1')
        for form in (*FORMS, 'not_a_form'):
            with self.subTest(form=form):
                report = validate.Report()
                validate.check_legislation([{**row, 'policy_instrument_type': form}], columns, report)
                if form in FORMS:
                    self.assertEqual(report.errors, [])
                else:
                    self.assertEqual([code for code, _ in report.errors],
                                     ['legislation.policy_instrument_type'])


if __name__ == '__main__':
    unittest.main()
