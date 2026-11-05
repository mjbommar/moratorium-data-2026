"""Ensure a full refresh cannot silently omit IDs or conflate state-policy rows."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("scope", Path(__file__).resolve().parents[1] / "scripts/build_refresh_scope.py")
scope = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scope)


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_root = scope.ROOT
        scope.ROOT = self.root
        (self.root / "data").mkdir()

    def tearDown(self):
        scope.ROOT = self.old_root
        self.tmp.cleanup()

    def write(self, file, id_column, ids):
        with (self.root / "data" / file).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[id_column, "state_abbrev"])
            w.writeheader()
            w.writerows([{id_column: i, "state_abbrev": "ME"} for i in ids])

    def test_every_row_is_unattempted_and_inputs_unchanged(self):
        self.write("moratorium_inventory.csv", "moratorium_id", ["local-a", "local-b"])
        self.write("state_legislation.csv", "policy_action_id", ["policy-a"])
        before = {p.name: p.read_bytes() for p in (self.root / "data").iterdir()}
        result = scope.build("2026-11-05", self.root / "packets")
        packet = json.loads((self.root / "packets/ME.json").read_text())
        self.assertEqual([x["id"] for x in packet["inventory"]], ["local-a", "local-b"])
        self.assertEqual([x["id"] for x in packet["state_policy"]], ["policy-a"])
        self.assertEqual(result["freshness"]["inventory"]["confirmed"], 0)
        self.assertTrue(all(x["disposition"] == "not_attempted" for x in packet["inventory"]))
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.root / "data").iterdir()})

    def test_duplicate_ids_refused(self):
        self.write("moratorium_inventory.csv", "moratorium_id", ["duplicate", "duplicate"])
        self.write("state_legislation.csv", "policy_action_id", [])
        with self.assertRaises(ValueError):
            scope.build("2026-11-05", self.root / "packets")


if __name__ == "__main__":
    unittest.main()
