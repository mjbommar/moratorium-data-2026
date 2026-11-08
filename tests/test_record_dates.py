import contextlib
import csv
import io
import sys
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


    def test_clearing_an_unsupported_date_invalidates_chart_without_check_rewriting(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "inventory.csv"
            output = Path(directory) / "timeline.svg"
            def write_rows(dates):
                with source.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=["date_enacted_iso", "sectors"])
                    writer.writeheader()
                    writer.writerows({"date_enacted_iso": value, "sectors": '["data_center"]'} for value in dates)
            write_rows(["2026-08-11", "2026-08-12"])
            with patch.object(make_timeline, "INV", source), patch.object(make_timeline, "OUT", output), contextlib.redirect_stdout(io.StringIO()):
                with patch.object(sys, "argv", ["make_timeline.py"]):
                    self.assertEqual(make_timeline.main(), 0)
                previous = output.read_bytes()
                self.assertIn(b"2 dated records; 0 without a usable month", previous)
                write_rows(["", "2026-08-12"])
                with patch.object(sys, "argv", ["make_timeline.py", "--check"]):
                    self.assertEqual(make_timeline.main(), 1)
                self.assertEqual(output.read_bytes(), previous)
                with patch.object(sys, "argv", ["make_timeline.py"]):
                    self.assertEqual(make_timeline.main(), 0)
                with patch.object(sys, "argv", ["make_timeline.py", "--check"]):
                    self.assertEqual(make_timeline.main(), 0)
                self.assertIn(b"1 dated records; 1 without a usable month", output.read_bytes())


if __name__ == "__main__":
    unittest.main()
