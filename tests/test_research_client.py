"""Budget reservations survive errors/restarts and are enforced before paid calls."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("client", Path(__file__).resolve().parents[1] / "scripts/research_client.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class ClientTests(unittest.TestCase):
    def test_interrupted_reservation_cannot_reset_budget(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "client-config.json").write_text(json.dumps({"caps": {"search_total": 2, "exa": 1, "serpapi": 2}}))
            first = client.reserve(p, "exa")
            with self.assertRaises(RuntimeError):
                client.reserve(p, "exa")
            second = client.reserve(p, "serpapi")
            with self.assertRaises(RuntimeError):
                client.reserve(p, "serpapi")
            self.assertNotEqual(first["attempt_id"], second["attempt_id"])

    def test_failure_consumes_cap_and_does_not_erase_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "client-config.json").write_text(json.dumps({"caps": {"fetch": 1}}))
            a = client.reserve(p, "fetch")
            client.finish(p, a, outcome="error", error_type="TimeoutError")
            with self.assertRaises(RuntimeError):
                client.reserve(p, "fetch")
            events = [json.loads(x) for x in (p / "attempts.private.jsonl").read_text().splitlines()]
            self.assertEqual([x["state"] for x in events], ["reserved", "finished"])


if __name__ == "__main__":
    unittest.main()
