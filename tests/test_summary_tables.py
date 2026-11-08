import unittest
from unittest.mock import patch

from scripts.generate_tables._common import InventoryRow
from scripts.generate_tables.state_sector_counts import render
from scripts.generate_tables.temporal_distribution import recorded_year


class SummaryTableTests(unittest.TestCase):
    def test_sector_counts_ignore_incidental_prose_and_place_name(self):
        row = InventoryRow.from_csv_dict({'state':'California','jurisdiction':'Irwindale',
            'trigger':'Battery and solar impacts discussed', 'sectors':'["data_center"]'})
        with patch('scripts.generate_tables.state_sector_counts.load_inventory', return_value=[row]):
            result = render(min_total=1)
        self.assertIn('California     &  1 &  0 &  0 &  0 &  0 &  0 &  1', result)
        with patch('scripts.generate_tables.state_sector_counts.load_inventory', return_value=[InventoryRow.from_csv_dict({'state':'California','sectors':'[]'})]):
            with self.assertRaises(ValueError):
                render(min_total=1)

    def test_year_counts_use_normalized_date_and_preserve_unknown(self):
        cases = [
            ({'date_enacted':'Ordinance 2026-14'}, None),
            ({'date_enacted':'2026 (reported)', 'date_enacted_iso':'2024', 'date_enacted_uncertainty':'year_only'}, 2024),
            ({'date_enacted_iso':'2026-02-30','date_enacted_uncertainty':'exact'}, None),
            ({'date_enacted_iso':'2026-05-04','date_enacted_uncertainty':'range'}, None),
            ({'date_enacted_iso':'2026-05-04','date_enacted_uncertainty':'unverified'}, 2026),
        ]
        for values, expected in cases:
            with self.subTest(values=values):
                self.assertEqual(recorded_year(InventoryRow.from_csv_dict(values)), expected)
