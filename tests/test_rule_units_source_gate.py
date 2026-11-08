"""Synthetic offline checks of source binding and retained production responses."""
import copy
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

from test_rule_unit_extraction import ext, DOC, PLAN, ARGS, candidate


class RawBackend:
    def __init__(self, values):
        self.values = iter(values)
        self.calls = 0

    async def generate(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(model='scripted:fake', priced=True, cost_usd=0,
                               input_tokens=0, output_tokens=0, output=next(self.values))


class SourceGateTests(unittest.IsolatedAsyncioTestCase):
    async def run_one(self, value, doc=DOC):
        plan = {**PLAN, 'units': PLAN['units'][:1]}
        with tempfile.TemporaryDirectory() as d:
            backend = RawBackend([value])
            first = await ext.run(d, doc, plan, backend=backend, **ARGS)
            self.assertEqual(first, await ext.run(d, doc, plan, backend=backend, **ARGS))
            self.assertEqual(backend.calls, 1)
            state = json.loads((Path(d) / 'rule-units-state.private.json').read_text())
            self.assertEqual(state['successes']['u1']['output'], value)
            self.assertEqual(first['units'][0]['output_sha256'], ext.digest(value))
            return first

    async def test_malformed_and_coerced_values_retained_and_unscorable(self):
        values = []
        bad = candidate('u1'); bad['supporting_quotes'] = 'not a list'; values.append(bad)
        bad = candidate('u1'); bad['clause']['expression'] = {'type': 'at_least', 'count': 1.0,
            'members': [{'type': 'text_predicate', 'text': 'site is small'}]}; values.append(bad)
        values.append(['not', 'an', 'object'])
        bad = candidate('u1'); bad['unit_id'] = 'wrong'; values.append(bad)
        for value in values:
            with self.subTest(value=value):
                packet = await self.run_one(value)
                unit = packet['units'][0]
                self.assertEqual(unit['original_output'], value)
                self.assertEqual(unit['outcome'], 'unresolved')
                self.assertIn('native_response_unscorable', unit['review_flags'])
                self.assertEqual(packet['unscorable_response_count'], 1)
                self.assertFalse(packet['response_accounting_complete'])
                self.assertEqual(packet['generated_clause_count'], int(isinstance(value, dict)))

    async def test_structural_unknown_nested_and_support_locations_fail_closed(self):
        cases = []
        bad = candidate('u1'); bad['clause']['expression'] = {'type': 'all', 'members': []}; cases.append((bad, 'condition_schema_invalid'))
        bad = candidate('u1'); bad['clause']['expression'] = {'type': 'unknown', 'source_text': 'not found'}; cases.append((bad, 'unknown_expression'))
        bad = candidate('u1'); bad['supporting_quotes'] = ['not found']; cases.append((bad, 'quote_unlocated_or_ambiguous'))
        bad = candidate('u1'); bad['supporting_quotes'] = ['Rule']; cases.append((bad, 'quote_unlocated_or_ambiguous'))
        bad = candidate('u1'); bad['clause']['source_text'] = 'Rule'; cases.append((bad, 'quote_unlocated_or_ambiguous'))
        for value, flag in cases:
            with self.subTest(flag=flag):
                p = await self.run_one(value)
                unit = p['units'][0]
                self.assertEqual(unit['outcome'], 'unresolved')
                self.assertIn(flag, unit['review_flags'])
                self.assertEqual(unit['clause'], value['clause'])
                self.assertEqual(p['generated_clause_count'], 1)

    async def test_exact_location_is_not_entailment(self):
        value = candidate('u1')
        value['clause']['expression']['text'] = 'A false unrelated claim'
        unit = (await self.run_one(value))['units'][0]
        self.assertEqual(unit['outcome'], 'candidate')
        self.assertFalse(unit['accepted'])
        self.assertTrue(unit['review_required'])

    def test_unicode_literal_and_overlapping_matches(self):
        self.assertEqual(ext.spans('é e\u0301 é', 'é'), [[0, 1], [5, 6]])
        self.assertEqual(ext.spans('aaaa', 'aa'), [[0, 2], [1, 3], [2, 4]])
        self.assertEqual(ext.spans('e\u0301', 'é'), [])


if __name__ == '__main__':
    unittest.main()
