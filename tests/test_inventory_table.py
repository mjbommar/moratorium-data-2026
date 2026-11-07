import unittest
from unittest.mock import patch

from scripts.generate_tables._common import InventoryRow
from scripts.generate_tables.inventory_clean import infer_status, original_duration, recorded_sectors, render, short_date


def row(**values):
    return InventoryRow.from_csv_dict(values)


class InventoryTableTests(unittest.TestCase):
    def test_place_name_and_incidental_prose_do_not_add_sectors(self):
        sample = row(jurisdiction='Irwindale', trigger='Battery impacts discussed',
                     sectors='["data_center"]')
        self.assertEqual(recorded_sectors(sample), ['Data Center'])
        self.assertEqual(recorded_sectors(row(sectors='["battery_storage", "solar", "general"]')),
                         ['BESS', 'Solar', 'Other'])

    def test_missing_or_invalid_sector_metadata_stays_unknown(self):
        for value in ('', '[]', '"wind"', '["unsupported_sector"]', '[null]'):
            with self.subTest(value=value):
                self.assertEqual(recorded_sectors(row(trigger='data center', sectors=value)), ['Unknown'])

    def test_original_term_does_not_select_extension_days(self):
        sample = row(duration='Initial 45-day pause; extended ten months and 15 days',
                     duration_kind='fixed_days', duration_days='45')
        self.assertEqual(original_duration(sample), '45d')

    def test_duration_metadata_preserves_units_and_uncertainty(self):
        for kind, days, expected in [
            ('calendar_term', '', 'Calendar term'),
            ('unknown', '', 'Unknown'),
            ('fixed_days', '', 'Unknown'),
            ('fixed_days', '45.5', 'Unknown'),
            ('until_date', '', 'Date-limited'),
            ('until_event', '', 'Event-based'),
        ]:
            with self.subTest(kind=kind, days=days):
                self.assertEqual(original_duration(row(duration='180 days then another year',
                    duration_kind=kind, duration_days=days)), expected)

    def test_dates_use_normalized_field_only(self):
        self.assertEqual(short_date(row(date_enacted='Ordinance 2026-47', date_enacted_iso='2026-06-15', date_enacted_uncertainty='exact')), '2026-06')
        self.assertEqual(short_date(row(date_enacted='Ordinance 2026-13', date_enacted_uncertainty='unverified')), '')
        for value in ('2026-13', '2026-02-30', '2026-83', 'prose 2026-04'):
            with self.subTest(value=value):
                self.assertEqual(short_date(row(date_enacted_iso=value, date_enacted_uncertainty='unverified')), '')

    def test_precision_and_uncertainty(self):
        for value, uncertainty, expected in [
            ('2026-03', 'month_only', '2026-03'), ('2025', 'year_only', '2025'),
            ('', 'unverified', ''), ('2026-03-04', 'unverified', '2026-03?'),
            ('2026-05-13', 'range', 'Range'), ('2026-04-01', 'month_only', ''),
            ('2026-04', '', ''),
        ]:
            with self.subTest(value=value, uncertainty=uncertainty):
                self.assertEqual(short_date(row(date_enacted_iso=value, date_enacted_uncertainty=uncertainty)), expected)

    def test_recorded_status_only(self):
        self.assertEqual(infer_status(row(current_status='No replacement adopted; not active', outcome='extension denied', enacted_status='active')), 'Active')
        self.assertEqual(infer_status(row(current_status='Not active', outcome='extension denied')), '')
        self.assertEqual(infer_status(row(enacted_status='pending')), 'Pending')

    def test_inventory_keeps_names_containing_federal(self):
        sample = [row(state='Maryland', state_abbrev='MD', jurisdiction='Federalsburg'),
                  row(state='Washington', state_abbrev='WA', jurisdiction='Federal Way')]
        with patch('scripts.generate_tables.inventory_clean.load_inventory', return_value=sample):
            output = render()
        self.assertIn('Federalsburg & MD', output)
        self.assertIn('Federal Way & WA', output)
        self.assertIn('Population: all canonical inventory records', output)

    def test_committed_artifact_matches_renderer(self):
        from pathlib import Path
        artifact = Path(__file__).resolve().parents[1] / 'tables/moratorium-inventory-clean.tex'
        self.assertEqual(artifact.read_text(), render())

    def test_render_metadata_deterministic(self):
        sample = row(state='Alabama', state_abbrev='AL', jurisdiction='Example', date_enacted_iso='2026-03', date_enacted_uncertainty='unverified', enacted_status='pending')
        with patch('scripts.generate_tables.inventory_clean.load_inventory', return_value=[sample]):
            first = render()
            self.assertEqual(first, render())
        self.assertIn('% Source: data/moratorium_inventory.csv', first)
        self.assertIn('working snapshot, November 5, 2026', first)
        self.assertIn('Record-level source and status dates vary', first)
        self.assertIn('2026-03?', first)
        self.assertIn('\\\\\n\\endlastfoot', first)
        self.assertNotIn('Data current through April', first)


if __name__ == '__main__':
    unittest.main()
