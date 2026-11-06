"""CSV views must preserve uncertainty and explicit observation lineage."""
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_expanded_csv import current_results, publish, render_table, sync_download_links
from expanded_data import SCHEMA

SCHEMAS = json.loads(SCHEMA.read_text())


class ExpandedCsvTests(unittest.TestCase):
    def read(self, records, table='measure_results'):
        raw, _ = render_table(table, records, SCHEMAS)
        return list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))

    def test_unknown_counts_are_not_zero(self):
        row = self.read([{'result_observation_id': 'one', 'yes_votes': 0, 'no_votes': None}])[0]
        self.assertEqual(row['yes_votes'], '0')
        self.assertEqual(row['no_votes'], '')
        self.assertEqual(row['blank_votes'], '')

    def test_structured_scope_and_source_categories_survive(self):
        scope = {'kind': 'county_part', 'description': 'One county only'}
        categories = [{'label': 'VOIDS', 'count': 24, 'claim_ids': ['claim']}]
        row = self.read([{'result_observation_id': 'one', 'reporting_scope': scope,
                          'source_vote_categories': categories}])[0]
        self.assertEqual(json.loads(row['reporting_scope']), scope)
        self.assertEqual(json.loads(row['source_vote_categories']), categories)

    def test_csv_quotes_multiline_text_without_altering_it(self):
        text = 'Question, with "quoted" text\nand a second line'
        row = self.read([{'measure_id': 'one', 'wording': text}], 'ballot_measures')[0]
        self.assertEqual(row['wording'], text)

    def test_current_view_retains_other_reporting_scopes(self):
        records = [{'result_observation_id': 'old-a', 'supersedes_id': None, 'measure_id': 'same'},
                   {'result_observation_id': 'new-a', 'supersedes_id': 'old-a', 'measure_id': 'same'},
                   {'result_observation_id': 'county-b', 'supersedes_id': None, 'measure_id': 'same'}]
        self.assertEqual({r['result_observation_id'] for r in current_results(records)}, {'new-a', 'county-b'})
        self.assertEqual(len(records), 3)

    def test_invalid_result_lineage_is_rejected(self):
        for records in [
            [{'result_observation_id': 'one', 'supersedes_id': 'missing'}],
            [{'result_observation_id': 'one', 'supersedes_id': 'two'},
             {'result_observation_id': 'two', 'supersedes_id': 'one'}],
            [{'result_observation_id': 'one', 'supersedes_id': None}] * 2,
        ]:
            with self.subTest(records=records), self.assertRaises(ValueError):
                current_results(records)

    def test_empty_tables_still_have_contract_headers(self):
        raw, columns = render_table('instrument_events', [], SCHEMAS)
        self.assertIn('event_id', columns)
        self.assertEqual(len(list(csv.reader(io.StringIO(raw.decode())))), 1)

    def test_missing_columns_are_not_silently_dropped(self):
        with self.assertRaises(ValueError):
            self.read([{'result_observation_id': 'one', 'new_unrecognized_field': 1}])

    def test_input_order_does_not_change_download_bytes(self):
        records = [{'result_observation_id': 'z', 'yes_votes': 1},
                   {'result_observation_id': 'a', 'yes_votes': None}]
        self.assertEqual(render_table('measure_results', records, SCHEMAS)[0],
                         render_table('measure_results', records[::-1], SCHEMAS)[0])

    def test_download_links_are_checked_without_rewriting_other_prose(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'README.md'
            path.write_text('Keep this prose.\n<!-- BEGIN EXPANDED CSV DOWNLOADS -->\n<!-- END EXPANDED CSV DOWNLOADS -->\nKeep the ending.\n')
            outputs = {'manifest.json': json.dumps({'files': {'measure_results.csv': {'rows': 56}}}).encode()}
            sync_download_links(path, 'generation', outputs)
            self.assertTrue(path.read_text().startswith('Keep this prose.\n'))
            self.assertTrue(path.read_text().endswith('Keep the ending.\n'))
            sync_download_links(path, 'generation', outputs, check=True)
            path.write_text(path.read_text().replace('| 56 |', '| 50 |'))
            with self.assertRaises(ValueError):
                sync_download_links(path, 'generation', outputs, check=True)

    def test_generation_replay_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = {'measure_results.csv': b'header\n', 'manifest.json': b'{}\n'}
            self.assertEqual(publish(root, 'generation', outputs), 'generated')
            first = (root / 'expanded-csv').readlink()
            self.assertFalse(first.is_absolute())
            self.assertEqual(publish(root, 'generation', outputs, check=True), 'matches')
            self.assertEqual(publish(root, 'generation', outputs), 'generated')
            self.assertEqual(first, (root / 'expanded-csv').readlink())
            (root / 'expanded-csv/measure_results.csv').write_bytes(b'changed\n')
            with self.assertRaises(ValueError):
                publish(root, 'generation', outputs, check=True)
            with self.assertRaises(ValueError):
                publish(root, 'generation', outputs)


if __name__ == '__main__':
    unittest.main()
