import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot_adapter', ROOT / 'scripts/normalize_ballot_pilot.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def rows(out, name):
    return [json.loads(x) for x in (out / (name + '.jsonl')).read_text().splitlines()]


class PilotReplayTests(unittest.TestCase):
    def test_replay_values_provenance_and_determinism(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'expected-inputs.json').write_bytes((adapter.OUT / 'expected-inputs.json').read_bytes())
            with patch.object(adapter, 'OUT', out):
                adapter.main()
                first = {p.name: p.read_bytes() for p in out.iterdir()}
                adapter.main()
                self.assertEqual(first, {p.name: p.read_bytes() for p in out.iterdir()})
                measures = {x['measure_id']: x for x in rows(out, 'ballot_measures')}
                self.assertEqual(len(measures), 9)
                self.assertTrue(all(x['bindingness'] == 'unresolved' for x in measures.values()))
                self.assertIn('Retroactive Moratorium', measures['pilot-me-wells']['wording'])
                claims = rows(out, 'claims')
                for claim in claims:
                    path = claim['extraction_provenance'].split('; ')[1]
                    source = (adapter.BASE / path).read_text()
                    _, start, end = claim['span'].split(':')
                    self.assertGreaterEqual(len(claim['quote']), 12)
                    self.assertEqual(claim['quote'], source[int(start):int(end)])
                wells_claim = next(c for c in claims if c['predicate'] == 'source_excerpt:certificate_result')
                self.assertEqual(wells_claim['value']['blank'], 459)
                self.assertIn('visually reviewed', wells_claim['extraction_provenance'])
                results = {x['measure_id']: x for x in rows(out, 'measure_results')}
                self.assertEqual(len(results), 9)
                wells = results['pilot-me-wells']
                self.assertEqual((wells['yes_votes'], wells['no_votes'], wells['certification_status'], wells['certification_date']), (5818, 1282, 'certified', '2026-11-04'))
                self.assertIsNone(wells['ballots_cast'])
                self.assertIsNone(wells['overvotes'])
                self.assertEqual(wells['blank_votes'], 459)
                self.assertEqual(wells['yes_no_votes'], 7100)
                self.assertEqual(wells['value_methods']['certification_date']['method'], 'visual')
                wisc = results['pilot-me-wiscasset']
                self.assertEqual((wisc['yes_votes'], wisc['no_votes'], wisc['ballots_cast']), (1363, 712, 2155))
                self.assertIsNone(wisc['undervotes'])
                for key, counts in [('pilot-me-peru', (578, 182)), ('pilot-piqua-charter-2026', (4061, 2027))]:
                    self.assertEqual((results[key]['yes_votes'], results[key]['no_votes']), counts)
                    self.assertEqual(results[key]['certification_status'], 'unknown')
                grove = results['pilot-grove-city-issue-28-2026']
                self.assertEqual(grove['source_yes_percent'], 54.61)
                self.assertIsNone(grove['yes_votes'])
                for n, counts in enumerate([(739,2885),(732,2886),(724,2887),(716,2909)], 4):
                    mid = f'pilot-wilmington-o-26-0{n}-2026'
                    self.assertEqual((results[mid]['yes_votes'], results[mid]['no_votes']), counts)
                    self.assertEqual(measures[mid]['referendum_yes_effect'], 'unresolved')
                    self.assertTrue(any(c['subject']['id'] == mid and c['predicate'] == 'source_excerpt:reported_yes_meaning' and 'approved the zoning change' in c['quote'] for c in claims))
                provisions = {x['measure_id']: x for x in rows(out, 'measure_provisions')}
                self.assertEqual(provisions['pilot-me-wells']['thresholds'][0]['value'], 100000)
                self.assertIn('six calendar months', provisions['pilot-me-wiscasset']['implementation_requirements'])
                self.assertEqual(provisions['pilot-me-wiscasset']['duration']['unit'], 'calendar_months')
                self.assertIsNone(provisions['pilot-me-wiscasset']['duration']['anchor_date'])
                self.assertEqual(provisions['pilot-me-wells']['duration']['anchor_date']['earliest'], '2026-06-16')

    def test_manifest_tampering_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'expected-inputs.json').write_text('{}')
            with patch.object(adapter, 'OUT', out), self.assertRaisesRegex(ValueError, 'manifest drift'):
                adapter.main()
            self.assertEqual([p.name for p in out.iterdir()], ['expected-inputs.json'])

    def test_artifact_drift_fails(self):
        with patch.object(adapter, 'digest', return_value=adapter.MANIFEST_SHA256):
            with self.assertRaisesRegex(ValueError, 'input drift'):
                adapter.verify_inputs()


if __name__ == '__main__':
    unittest.main()
