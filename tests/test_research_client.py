"""Budget reservations survive errors/restarts and are enforced before paid calls."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

spec = importlib.util.spec_from_file_location("client", Path(__file__).resolve().parents[1] / "scripts/research_client.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class ClientTests(unittest.TestCase):
    def test_unsupported_controls_do_not_consume_a_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'client-config.json').write_text(json.dumps({'caps':{'fetch':1,'search_total':1,'gdelt':1}}))
            script=Path(__file__).resolve().parents[1]/'scripts/research_client.py'
            for args in (['fetch','https://example.invalid','--mode','http','--settle-ms','5000'],
                         ['fetch','https://example.invalid','--mode','http','--record-network'],
                         ['fetch','https://example.invalid','--mode','browser','--conditional-cache'],
                         ['fetch','https://example.invalid','--conditional-cache'],
                         ['search','query','--backend','gdelt','--domain','example.invalid']):
                result=subprocess.run([sys.executable,str(script),'--directory',str(p),*args],capture_output=True,text=True)
                self.assertEqual(result.returncode,2)
                self.assertFalse((p/'attempts.private.jsonl').exists())

    def test_site_diagnostic_uses_hostname_not_url_substrings(self):
        r=client.search_scope('site:example.gov moratorium',[
            {'url':'https://records.example.gov/ordinance'},
            {'url':'https://example.gov.evil.test/path/example.gov'}])
        self.assertEqual(r['status'],'partly_outside_declared_sites')
        self.assertEqual(r['matching_hits'],1)

    def test_site_diagnostic_does_not_treat_scope_failure_as_absence(self):
        r=client.search_scope('site:example.gov repeal',[{'url':'https://dictionary.test/repeal'}])
        self.assertEqual(r['status'],'no_returned_url_in_declared_sites')
        self.assertEqual(client.search_scope('site:example.gov repeal',[])['status'],'empty_result_set')
        self.assertEqual(client.search_scope('moratorium -site:example.gov',[])['status'],'not_evaluated')

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
