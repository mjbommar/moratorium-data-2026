import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from bc_core.budget import BudgetExceeded
from bc_llm.backend import ScriptedBackend
from pydantic import ValidationError, TypeAdapter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import extract_domain_candidates as domain


class DomainTests(unittest.IsolatedAsyncioTestCase):
    def inputs(self, text='This proposal expires 180 days from the effective date.'):
        return dict(doc=dict(doc_id='fixture', text=text, title='Proposal', final_url=None,
                             url='https://example.invalid/proposal', published=None, language='en',
                             body_sha256='0'*64, text_sha256=hashlib.sha256(text.encode()).hexdigest()),
                    cells=[dict(cell_id='fixture-cell',subject_label='Fixture',topic_label='Clauses',
                                prospective=False,window_start='2026-01-01',window_end='2026-11-05')],
                    question='Extract source candidates only.',today=dt.date(2026,11,5),
                    max_calls=5,model_identity={'model':'scripted:fake'})

    def fact(self, field='duration', value=None, quote='180 days from the effective date',
             table='measure_provisions'):
        if value is None:
            value=dict(value=180,unit='days',anchor='effective_date',anchor_date=None,
                       original_text=quote)
        return dict(target_table=table,target_field=field,subject_label='Fixture proposal',
                    value=value,quote=quote,assertion_context='proposed')

    def backend(self, facts, unresolved=None):
        return ScriptedBackend({'*':lambda *a:dict(relevance=1,summary='',
            unresolved_fields=unresolved or [],claims=[dict(text='Fixture proposed clauses.',
                quote='180 days from the effective date',cells=[0],facts=facts)])})

    async def test_typed_duration_and_real_pipeline_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend=self.backend([self.fact()],['actual_effective_date','certification_status'])
            result=await domain.run(tmp,backend=backend,**self.inputs())
            self.assertTrue(result['full_text_chunk_coverage'])
            candidate=result['candidates'][0]
            self.assertFalse(candidate['field_schema_errors'])
            self.assertEqual(candidate['value']['anchor_date'],None)
            self.assertTrue(candidate['exact_quote_spans'])
            self.assertFalse(candidate['accepted'])
            self.assertEqual(result['canonical_records_written'],0)
            self.assertIn('certification_status',result['unresolved_fields'])
            replay=await domain.run(tmp,backend=backend,**self.inputs())
            self.assertEqual(result,replay)
            self.assertEqual(len(backend.calls),1)

    async def test_invalid_field_value_and_unlocated_quote_stay_visible(self):
        facts=[self.fact('yes_votes',-180,table='measure_results'),
               self.fact('no_votes',180,table='measure_provisions'),
               self.fact(quote='invented quotation')]
        with tempfile.TemporaryDirectory() as tmp:
            result=await domain.run(tmp,backend=self.backend(facts),**self.inputs())
            self.assertEqual(len(result['candidates']),3)
            self.assertIn('field_schema_invalid',result['candidates'][0]['review_flags'])
            self.assertIn('field_schema_invalid',result['candidates'][1]['review_flags'])
            self.assertIn('quote_unlocated',result['candidates'][2]['review_flags'])
            self.assertTrue(all(not c['accepted'] for c in result['candidates']))

    async def test_conflicts_and_duplicate_candidates_are_not_silently_merged(self):
        first=self.fact(); second=self.fact();second['value']['value']=90
        with tempfile.TemporaryDirectory() as tmp:
            result=await domain.run(tmp,backend=self.backend([first,first,second]),**self.inputs())
            self.assertEqual(len(result['candidates']),2)
            self.assertTrue(all('conflicting_field_candidates' in c['review_flags']
                                for c in result['candidates']))

    async def test_ambiguous_quote_and_bad_calendar_date_are_flagged(self):
        inputs=self.inputs('180 days from the effective date; 180 days from the effective date')
        facts=[self.fact(), self.fact('certification_date','2026-02-31',table='measure_results')]
        with tempfile.TemporaryDirectory() as tmp:
            result=await domain.run(tmp,backend=self.backend(facts),**inputs)
            self.assertIn('quote_location_ambiguous',result['candidates'][0]['review_flags'])
            self.assertTrue(result['candidates'][1]['field_schema_errors'])

    async def test_vote_counts_do_not_create_denominators_or_outcomes(self):
        facts=[self.fact('yes_votes',578,quote='YES 578',table='measure_results'),
               self.fact('no_votes',182,quote='NO 182',table='measure_results')]
        with tempfile.TemporaryDirectory() as tmp:
            result=await domain.run(tmp,backend=self.backend(facts),
                                    **self.inputs('YES 578 NO 182. Total voters 774.'))
            self.assertEqual({c['target_field'] for c in result['candidates']},{'yes_votes','no_votes'})
            self.assertTrue(all(not c['field_schema_errors'] for c in result['candidates']))

    async def test_payload_text_hash_and_strict_numeric_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            inputs=self.inputs();inputs['doc']['text_sha256']='wrong'
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                await domain.run(tmp,backend=self.backend([]),**inputs)
        with self.assertRaises(ValidationError):
            TypeAdapter(domain.TypedDomainFact).validate_python(self.fact('yes_votes',True,table='measure_results'))

    async def test_provider_schema_requires_field_specific_values(self):
        parser=TypeAdapter(domain.TypedDomainFact)
        for fact in [self.fact('covered_uses','A string cannot replace a list.'),
                     self.fact('mechanism','A prose description.'),
                     self.fact('calculated_outcome','approved',table='measure_results')]:
            with self.assertRaises(ValidationError):
                parser.validate_python(fact)
        valid=parser.validate_python(self.fact('exemptions',['Routine existing upgrades']))
        self.assertEqual(valid.value,['Routine existing upgrades'])

    async def test_thresholds_preserve_units_operators_and_basis(self):
        threshold=dict(operator='lt',value=250,unit='kW',measurement_basis='computing load',
                       aggregation_rule='Must also meet the separate total-service condition',
                       scope='Accessory exemption')
        with tempfile.TemporaryDirectory() as tmp:
            text='Accessory facilities must use less than 250 kW of computing load.'
            fact=self.fact('thresholds',[threshold],quote='less than 250 kW of computing load')
            result=await domain.run(tmp,backend=self.backend([fact]),**self.inputs(text))
            candidate=result['candidates'][0]
            self.assertEqual(candidate['value'],[threshold])
            self.assertFalse(candidate['field_schema_errors'])
            self.assertFalse(candidate['accepted'])

    async def test_proposal_cannot_establish_voter_polarity(self):
        with tempfile.TemporaryDirectory() as tmp:
            fact=self.fact('yes_direction','restricts',table='ballot_measures')
            result=await domain.run(tmp,backend=self.backend([fact]),**self.inputs())
            candidate=result['candidates'][0]
            self.assertFalse(candidate['field_schema_errors'])
            self.assertTrue(candidate['exact_quote_spans'])
            self.assertIn('election_specific_evidence_required',candidate['review_flags'])
            self.assertFalse(candidate['accepted'])

    async def test_transport_schema_snapshot_matches_models(self):
        snapshot=json.loads((ROOT/'work/schemas/extraction/1.0.0.json').read_text())
        generated=domain.DomainChunk.model_json_schema()
        for key,value in generated.items():
            self.assertEqual(snapshot[key],value)

    async def test_failed_rerun_does_not_leave_stale_domain_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            await domain.run(tmp,backend=self.backend([self.fact()]),**self.inputs())
            path=Path(tmp)/'state.private.json';state=json.loads(path.read_text())
            state['budget_stop']='Synthetic stop';path.write_text(json.dumps(state))
            with self.assertRaises(BudgetExceeded):
                await domain.run(tmp,backend=self.backend([]),**self.inputs())
            self.assertFalse((Path(tmp)/'domain-candidates.private.json').exists())
