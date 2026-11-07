import json
import math
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from scripts.condition_expression import (
    ConditionClause, MAX_MEMBERS, condition_clauses_schema, validate_condition_clauses,
)

ROOT = Path(__file__).resolve().parents[1]


def threshold(basis, value=25, operator='ge'):
    return dict(type='threshold', operator=operator, value=value, unit='MW',
                measurement_basis=basis, aggregation_rule='aggregate', scope='facility')


def predicate(text):
    return dict(type='text_predicate', text=text)


def group(kind, *members, **extra):
    return dict(type=kind, members=list(members), **extra)


def clause(expression, purpose='prohibition_trigger'):
    return dict(purpose=purpose, assertion_context='proposed',
                source_text='Exact source quotation.', expression=expression)


class ConditionExpressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / 'work/schemas/condition-expression/1.0.0.json').read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def assert_equivalent(self, value, valid):
        self.assertEqual(not validate_condition_clauses(value), valid, value)
        self.assertEqual(self.validator.is_valid(value), valid, value)

    def test_mandan_compound_distinctions_round_trip(self):
        capacity, demand = threshold('capacity'), threshold('demand')
        proposed = clause(group('any', capacity, demand))
        below = clause(group('all', threshold('capacity', operator='lt'),
                             threshold('demand', operator='lt')), 'safe_harbor')
        self.assert_equivalent([proposed, below], True)
        result = ConditionClause.model_validate(proposed)
        self.assertEqual(result.model_dump(), proposed)
        self.assertNotEqual(proposed['expression']['type'], below['expression']['type'])
        self.assertEqual(json.loads(result.model_dump_json()), proposed)

    def test_harwood_nested_gates_and_unknown_water(self):
        water = predicate('50,000 gallons per day or exceeding 5% of available city water capacity, whichever threshold is less')
        major = group('any', threshold('peak demand', 100), water,
                      predicate('major-source air authorization'))
        moderate = group('at_least', threshold('peak demand', 50),
                         threshold('generation', 50), predicate('qualifying air permit'), count=2)
        expression = group('all', predicate('requires discretionary municipal approval'),
                           group('any', major, moderate))
        example = clause(expression, 'procedure_trigger')
        self.assert_equivalent([example], True)
        self.assertEqual(ConditionClause.model_validate(example).model_dump(), example)
        self.assert_equivalent([clause(dict(type='unknown', source_text='whichever is less'))], True)

    def test_invalid_shapes(self):
        a, b = threshold('capacity'), threshold('demand')
        cases = [group('all'), group('any', a, a), group('at_least', a, b, count=0),
                 group('at_least', a, b, count=3), group('at_least', a, count=True),
                 group('at_least', a, count=1.5), group('all', a, count=1),
                 group('at_least', a), dict(type='unknown', source_text=''),
                 dict(type='text_predicate', text=''), dict(type='missing'),
                 dict(a, value=True), dict(a, unit=''), dict(a, extra=1),
                 group('any', *[threshold(str(i)) for i in range(MAX_MEMBERS + 1)])]
        for expression in cases:
            with self.subTest(expression=expression):
                self.assert_equivalent([clause(expression)], False)
        self.assert_equivalent([dict(clause(a), extra=True)], False)
        self.assert_equivalent([dict(clause(a), source_text='')], False)
        self.assert_equivalent([dict(clause(a), assertion_context='adopted')], False)
        self.assert_equivalent({}, False)
        self.assert_equivalent([clause(group('at_least', a, b, count=2.0))], True)
        self.assert_equivalent([clause(group('any', a, dict(a, value=25.0)))], False)

    def test_nonfinite_python_values_rejected(self):
        for number in (math.nan, math.inf, -math.inf):
            with self.subTest(number=number):
                self.assertTrue(validate_condition_clauses([clause(threshold('capacity', number))]))
                with self.assertRaises(ValidationError):
                    ConditionClause.model_validate(clause(threshold('capacity', number)))

    def test_published_schema_is_generated_schema(self):
        self.assertEqual(self.schema, condition_clauses_schema())
        self.assertIn('$defs', self.schema)
        self.assertIn('$id', self.schema)
        self.assertEqual(self.schema['$schema'], 'https://json-schema.org/draft/2020-12/schema')


if __name__ == '__main__':
    unittest.main()
