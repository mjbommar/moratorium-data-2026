"""Failed requests keep reservations even when bc-llm emits no result record."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('comparison_audit',ROOT/'work/research/2026-11-07/compound-chunk-policy-evaluation/audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
MODEL='openai:gpt-6-sol'


class ComparisonAccountingTests(unittest.TestCase):
    def data(self):
        key='a'*64
        failed=dict(request_sha256=key,status='failed',reserved_usd=.75,error_type='ModelHTTPError')
        success=dict(request_sha256=key,status='succeeded',reserved_usd=.75,charged_usd=.1,
                     accounting=dict(model=MODEL,priced=True,cost_usd=.1))
        cache={key:dict(output={},output_sha256=audit.digest({}))}
        ledger=[dict(attempts=1,cost_usd=.1)]
        case=dict(max_calls=4,reservation_usd=.75,max_usd=3)
        return failed,success,cache,ledger,case

    def test_failed_then_successful_same_key_has_only_one_result_record(self):
        failed,success,cache,ledger,case=self.data()
        result=audit.attempt_accounting([failed,success],ledger,cache,case,MODEL)
        self.assertAlmostEqual(result['accounted_usd'],.85)
        self.assertAlmostEqual(result['priced_cost_estimate_usd'],.1)
        self.assertEqual(result['unpriced_attempts'],1)
        self.assertEqual(result['held_unpriced_reservations_usd'],.75)
        self.assertFalse(result['estimated_accounting_complete'])
        self.assertEqual(result['successful_keys'],set(cache))

    def test_failed_after_priced_backend_return_consumes_its_result_record(self):
        failed,success,cache,ledger,case=self.data()
        failed.update(accounting=dict(model=MODEL,priced=True,cost_usd=.2),charged_usd=.2)
        result=audit.attempt_accounting([failed,success],[dict(attempts=1,cost_usd=.2),*ledger],cache,case,MODEL)
        self.assertAlmostEqual(result['accounted_usd'],.3)
        self.assertEqual(result['unpriced_attempts'],0)
        self.assertTrue(result['estimated_accounting_complete'])

    def test_missing_or_fabricated_result_records_and_changed_costs_fail(self):
        failed,success,cache,ledger,case=self.data()
        for rows in ([],[dict(attempts=1,cost_usd=0)],ledger*2):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                audit.attempt_accounting([failed,success],rows,cache,case,MODEL)
        with self.assertRaises(ValueError):
            audit.attempt_accounting([failed],ledger,{},case,MODEL)
        with self.assertRaises(ValueError):
            audit.attempt_accounting([success,failed],ledger,cache,case,MODEL)

    def test_caps_and_unpriced_returns_do_not_turn_unknown_cost_into_zero(self):
        failed,success,cache,ledger,case=self.data()
        with self.assertRaises(ValueError):
            audit.attempt_accounting([failed,failed,success],ledger,cache,dict(case,max_calls=2),MODEL)
        failed['accounting']=dict(model=MODEL,priced=False,cost_usd=None)
        result=audit.attempt_accounting([failed],[dict(attempts=1,cost_usd=None)],{},case,MODEL)
        self.assertEqual(result['accounted_usd'],.75)
        self.assertEqual(result['held_unpriced_reservations_usd'],.75)
        self.assertEqual(result['unpriced_attempts'],1)

if __name__=='__main__':unittest.main()
