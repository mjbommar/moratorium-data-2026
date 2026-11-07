import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.moratorium_maps.dates import recorded_month
from scripts import make_timeline


class RecordMonthTests(unittest.TestCase):
    def test_normalized_date_takes_precedence_over_legacy_range(self):
        row = {"date_enacted": "2020-2026 [VERIFY]", "date_enacted_iso": "2026-04-02"}
        self.assertEqual(recorded_month(row), "2026-04")
        row["date_enacted_iso"] = ""
        self.assertIsNone(recorded_month(row))

    def test_month_precision_is_retained_but_invalid_calendar_dates_are_not(self):
        self.assertEqual(recorded_month({"date_enacted_iso": "2026-04"}), "2026-04")
        for value in ["2026", "2026-28", "2026-00", "2026-02-30", "2026-04 reported"]:
            with self.subTest(value=value):
                self.assertIsNone(recorded_month({"date_enacted_iso": value}))

    def test_collection_does_not_truncate_earlier_valid_records_or_count_invalid_ones(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "inventory.csv"
            with source.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["date_enacted_iso", "sectors"])
                writer.writeheader()
                for value in ["2017-12-31", "2018-01", "2018-01-02", "2018-28", "2018"]:
                    writer.writerow({"date_enacted_iso": value, "sectors": '["solar"]'})
            with patch.object(make_timeline, "INV", source):
                months, monthly, cumulative = make_timeline.collect()
            self.assertEqual(months, ["2017-12", "2018-01"])
            self.assertEqual(monthly["2018-01"]["solar"], 2)
            self.assertEqual(cumulative, [1, 3])


if __name__ == "__main__":
    unittest.main()
