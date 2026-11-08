import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import score_rule_unit_trial as s


def fixture(n=1):
    specs, cases, js = [], [], []
    for split in ('calibration', 'holdout'):
        text = split + ' source'; source = s.text_hash(text); body = s.text_hash(split+' body')
        units, outputs, refs, reviews, plans = [], [], [], [], []
        for i in range(n):
            uid = str(i); slot = {'slot_id':'slot'}
            raw = dict(unit_id=uid, outcome='candidate', clause={'source_text':text,'assertion_context':'proposed'}, supporting_quotes=[text], unresolved_reason=None)
            units.append(dict(unit_id=uid,kind='change',slots=[slot]))
            outputs.append(dict(unit_id=uid,status='succeeded',outcome='candidate',review_flags=[],original_output=raw,output_sha256=s.digest(raw)))
            refs.append(dict(unit_id=uid,nonextractable_issues=[],slots=[dict(slot_id='slot',evidence='source passage',proposition='source proposition',qualifications=[],source_locators=[dict(quote=text,start=0,end=len(text))])]))
            reviews.append(dict(nonextractable_reviews=[],errors=[],disagreements=[],unit_id=uid,output_sha256=s.digest(raw),support='supported',high_impact='no',provenance=dict(reviewer='review',independence_basis='separate source reviewer',source_evidence='source passage',adjudication='no dispute'),slots=[dict(slot_id='slot',decision='covered',evidence='source passage',rationale='complete proposition',clause_evidence=text,source_locators=[dict(quote=text,start=0,end=len(text))])]))
            plans.append(dict(unit_id=uid))
        ref = {'units':refs,'source_text_sha256':source,'source_body_sha256':body,'role':'proposed','provenance':'independent full-source inventory'}; refhash = s.digest(ref)
        for j in reviews: j['reference_sha256'] = refhash
        document = dict(text=text,body_sha256=body,reviewed_source_role='proposed')
        plan_obj = dict(source_text_sha256=source,units=[dict(unit_id=str(i)) for i in range(n)])
        context_obj = dict(document=document,plan=plan_obj,model_identity={'model':'synthetic'},settings={},schema={},system='fixed',role='extractor')
        context, plan = s.digest(context_obj), s.digest(plan_obj)
        packet = dict(units=outputs,provenance={'reviewed_source_role':'proposed'},context_sha256=context,plan_sha256=plan,source_text_sha256=source,source_body_sha256=body)
        audit = dict(schema_version='native-rule-unit-reconciliation-1',status='complete',errors=[],plans=plans,evidence_hashes=dict(source_text_sha256=source,source_body_sha256=body,context_sha256=context,plan_sha256=plan,packet_canonical_sha256=s.digest(packet)),**{k:True for k in ('response_accounting_complete','structural_evidence_complete','planned_trace_complete','prospective_anchor_verified','wire_contract_complete','endpoint_identity_complete')})
        specs.append(dict(case_id=split,split=split,family=split,source_text_sha256=source,source_body_sha256=body,context_sha256=context,plan_sha256=plan,reference_sha256=refhash,role='proposed',exposure='unexposed',units=units))
        cases.append(dict(case_id=split,audit=audit,packet=packet,document=document,reference=ref,context=context_obj))
        js.append(dict(case_id=split,packet_sha256=s.digest(packet),audit_sha256=s.digest(audit),units=reviews))
    return dict(schema_version='rule-unit-scoring-protocol-1',freeze_time='2026-01-02T00:00:00Z',first_dispatch_time='2026-01-03T00:00:00Z',calibration_complete_time='2026-01-01T00:00:00Z',reference_provenance='independent source inventory',exposure_provenance='access records',cases=specs), cases, dict(schema_version='rule-unit-scoring-judgments-1',cases=js)


def run(f):
    p, c, j = f
    return s.score(p,s.digest(p),c,j,s.digest(j))


class ScoringTests(unittest.TestCase):
    def test_malformed_supporting_quote_container_cannot_pass(self):
        for quotes in ('invented quote', {'quote': 'holdout source'}, [], [None]):
            with self.subTest(quotes=quotes):
                f = fixture()
                case = f[1][1]
                output = case['packet']['units'][0]
                output['original_output']['supporting_quotes'] = quotes
                output['output_sha256'] = s.digest(output['original_output'])
                f[2]['cases'][1]['units'][0]['output_sha256'] = output['output_sha256']
                case['audit']['evidence_hashes']['packet_canonical_sha256'] = s.digest(case['packet'])
                f[2]['cases'][1]['packet_sha256'] = s.digest(case['packet'])
                f[2]['cases'][1]['audit_sha256'] = s.digest(case['audit'])
                result = run(f)
                self.assertEqual(result['threshold_result'], 'not_scored')
                self.assertEqual(result['splits']['holdout']['metrics']['support']['denominator'], 1)
                self.assertEqual(result['splits']['holdout']['metrics']['support']['numerator'], 0)
                self.assertTrue(any('invalid supporting quote container' in gap for gap in result['gaps']))

    def test_synthetic_mechanics_only(self):
        r=run(fixture()); self.assertEqual(r['threshold_result'],'pass'); self.assertEqual(r['acceptance'],'not_scored'); self.assertEqual(r['p4_acceptance'],'not_scored')
    def test_threshold_boundaries(self):
        self.assertTrue(s.ratio(19,20)['pass']); self.assertFalse(s.ratio(18,20)['pass']); self.assertFalse(s.ratio(0,0)['pass'])
        f=fixture(20); j=f[2]['cases'][1]['units']; j[0]['support']='unsupported'; j[0]['slots'][0]['decision']='uncovered'
        r=run(f); self.assertEqual(r['threshold_result'],'pass'); self.assertEqual(r['splits']['holdout']['metrics']['support']['denominator'],20)
        j[1]['support']='unsupported'; j[1]['slots'][0]['decision']='uncovered'; self.assertEqual(run(f)['acceptance'],'fail')
    def test_missing_and_incomplete(self):
        for mutate in (lambda f:f[1][1]['audit'].update(response_accounting_complete=False), lambda f:f[2]['cases'][1]['units'].clear(), lambda f:f[1][1]['reference']['units'].clear(), lambda f:f[1][1]['packet']['units'].clear()):
            f=fixture(); mutate(f)
            try: self.assertNotEqual(run(f)['acceptance'],'pass')
            except (ValueError, KeyError): pass
    def test_pins_and_role(self):
        f=fixture(); f[1][1]['document']['reviewed_source_role']='enacted_text'; self.assertEqual(run(f)['acceptance'],'not_scored')
        f=fixture(); f[1][1]['reference']['units'][0]['slots'][0]['evidence']='changed'; self.assertEqual(run(f)['acceptance'],'not_scored')
        f=fixture(); self.assertRaises(ValueError,s.score,f[0],'0'*64,f[1],f[2],s.digest(f[2]))
    def test_exposure_disclosed_and_chronology(self):
        f=fixture(); f[0]['cases'][1]['exposure']='exposed'; self.assertEqual(run(f)['threshold_result'],'pass')
        f=fixture(); f[0]['cases'][1]['exposure']=''; self.assertEqual(run(f)['threshold_result'],'not_scored')
        f=fixture(); f[0]['freeze_time']='2026-01-04T00:00:00Z'; self.assertEqual(run(f)['acceptance'],'not_scored')
        f=fixture(); f[0]['cases'][1]['source_body_sha256']=next(iter(s.EXPOSED_VA)); self.assertEqual(run(f)['acceptance'],'not_scored')  # Hash no longer matches the retained source.

    def test_uncertainty_and_high_impact(self):
        f=fixture(); f[2]['cases'][1]['units'][0]['slots'][0]['decision']='uncertain'; self.assertEqual(run(f)['acceptance'],'not_scored')
        f=fixture(); f[2]['cases'][1]['units'][0]['high_impact']='yes'; f[2]['cases'][1]['units'][0]['errors']=[dict(category='incorrect_threshold_date',description='wrong date',source_locators=[dict(quote='holdout source',start=0,end=14)])]; self.assertEqual(run(f)['acceptance'],'fail')
    def test_cli_pass_and_method_drift(self):
        import json, subprocess, tempfile
        f=fixture()
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for name, value in zip(('protocol','cases','judgments'),f):
                path=Path(d)/name; path.write_text(json.dumps(value)); paths.append(str(path))
            proc=subprocess.run([sys.executable,str(Path(s.__file__)), '--protocol',paths[0],'--protocol-anchor',s.digest(f[0]),'--cases',paths[1],'--judgments',paths[2],'--judgment-anchor',s.digest(f[2])],capture_output=True,text=True)
            self.assertEqual(proc.returncode,1,proc.stderr); self.assertEqual(json.loads(proc.stdout)['threshold_result'],'pass'); self.assertEqual(json.loads(proc.stdout)['p4_acceptance'],'not_scored')
        f[1][1]['context']['settings']={'temperature':1}
        self.assertEqual(run(f)['acceptance'],'not_scored')

    def test_missing_judgment_and_denominator(self):
        f=fixture(2); f[2]['cases'][1]['units'].pop(); r=run(f); self.assertEqual(r['acceptance'],'not_scored'); self.assertEqual(r['splits']['holdout']['counts']['change_units'],2)
    def test_adversarial_denominator_and_missing_case_review(self):
        for entire in (False, True):
            f=fixture(20)
            if entire: f[2]['cases'].pop()
            else: f[2]['cases'][1]['units'].pop()
            r=run(f); h=r['splits']['holdout']
            self.assertEqual(h['metrics']['support']['denominator'],20)
            self.assertIsNone(h['metrics']['support']['pass'])
            self.assertFalse(h['counts']['high_impact_complete'])
            self.assertEqual(r['threshold_result'],'not_scored')

    def test_controls_and_calibration_are_diagnostics(self):
        f=fixture(22)
        for i in (20,21):
            f[0]['cases'][1]['units'][i]['kind']='control'
            f[2]['cases'][1]['units'][i]['slots'][0]['decision']='uncovered'
        f[2]['cases'][0]['units'][0]['support']='unsupported'
        r=run(f); h=r['splits']['holdout']
        self.assertEqual(r['threshold_result'],'pass')
        self.assertEqual(h['metrics']['required_slot_coverage']['numerator'],20); self.assertNotIn('pass', h['metrics']['required_slot_coverage'])
        self.assertEqual(h['coverage']['control']['units'],2); self.assertEqual(h['coverage']['control']['covered_slots'],0)
        self.assertEqual(h['families']['holdout']['change']['complete_units'],20)

    def test_independent_slot_and_contradiction(self):
        f=fixture(); f[2]['cases'][1]['units'][0]['support']='unsupported'
        h=run(f)['splits']['holdout']
        self.assertEqual(h['metrics']['change_slot_coverage']['numerator'],1)
        f[2]['cases'][1]['units'][0]['support']='no_clause'
        r=run(f); self.assertEqual(r['threshold_result'],'not_scored')
        self.assertTrue(any('clause judgment mismatch' in g for g in r['gaps']))

    def test_unenumerable_and_invalid_slot_locators(self):
        f=fixture(); f[1][1]['packet']['units'][0]['original_output']=None
        h=run(f)['splits']['holdout']; self.assertFalse(h['metrics']['support']['denominator_complete']); self.assertIsNone(h['metrics']['support']['pass'])
        f=fixture(); f[2]['cases'][1]['units'][0]['slots'][0]['source_locators'][0]['end']=2
        r=run(f); self.assertEqual(r['threshold_result'],'not_scored'); self.assertEqual(r['splits']['holdout']['counts']['covered_change_slots'],0)
        f=fixture(); f[2]['cases'][1]['units'][0]['slots'][0]['clause_evidence']='invented'
        self.assertEqual(run(f)['threshold_result'],'not_scored')

    def test_evidence_and_disagreement(self):
        f=fixture(); r=run(f); u=r['splits']['holdout']['units'][0]
        self.assertEqual(u['quote_locations'][0]['occurrences'],[dict(start=0,end=14)])
        j=f[2]['cases'][1]['units'][0]
        j['disagreements']=[dict(issue='date',status='resolved',resolution='resolved',adjudicator='second',independence_basis='separate',source_locators=[dict(quote='holdout source',start=0,end=14)])]
        self.assertEqual(run(f)['threshold_result'],'pass')
        j['disagreements'][0]['adjudicator']='review'
        self.assertEqual(run(f)['threshold_result'],'not_scored')
        f=fixture(); f[2]['cases'][1]['units'][0]['high_impact']='yes'
        self.assertEqual(run(f)['threshold_result'],'not_scored')
        f=fixture(); del f[1][1]['reference']['units'][0]['nonextractable_issues']
        self.assertEqual(run(f)['threshold_result'],'not_scored')

    def test_invalid_split_and_missing_output(self):
        f=fixture(); f[0]['cases'][1]['split']='other'
        self.assertEqual(run(f)['threshold_result'],'not_scored')
        f=fixture(2); f[1][1]['packet']['units'].pop()
        h=run(f)['splits']['holdout']; self.assertEqual(h['counts']['change_units'],2); self.assertFalse(h['metrics']['support']['denominator_complete'])

    def test_extra_generated_clause_and_calibration_incomplete(self):
        f=fixture(); extra=copy.deepcopy(f[1][1]['packet']['units'][0]); extra['unit_id']='extra'; f[1][1]['packet']['units'].append(extra)
        h=run(f)['splits']['holdout']; self.assertEqual(h['counts']['generated'],2); self.assertIsNone(h['metrics']['support']['pass'])
        f=fixture(); f[2]['cases'][0]['units'].clear()
        r=run(f); self.assertEqual(r['threshold_result'],'pass'); self.assertIsNone(r['splits']['calibration']['metrics']['support']['pass'])

    def test_invalid_or_unresolved_clause_still_reviewed(self):
        f=fixture(); p=f[1][1]['packet']['units'][0]
        p['status']='invalid'; p['outcome']='unresolved'; p['review_flags']=['flag']
        c=f[1][1]; j=f[2]['cases'][1]; c['audit']['evidence_hashes']['packet_canonical_sha256']=s.digest(c['packet']); j['packet_sha256']=s.digest(c['packet']); j['audit_sha256']=s.digest(c['audit'])
        r=run(f); self.assertEqual(r['splits']['holdout']['metrics']['support']['numerator'],1)
        self.assertEqual(r['threshold_result'],'pass')

    def test_missing_slot_judgments_keep_denominators(self):
        f=fixture(2); del f[2]['cases'][1]['units'][0]['slots']
        r=run(f); self.assertEqual(r['splits']['holdout']['metrics']['support']['denominator'],2); self.assertIsNone(r['splits']['holdout']['metrics']['support']['pass'])
        f=fixture(2); f[2]['cases'][1]['units'][0]['slots']=[{}]
        r=run(f); self.assertEqual(r['splits']['holdout']['metrics']['support']['denominator'],2); self.assertIsNone(r['splits']['holdout']['metrics']['support']['pass'])

    def test_literal_not_entailment(self):
        f=fixture(); f[2]['cases'][1]['units'][0]['support']='unsupported'; self.assertEqual(run(f)['acceptance'],'fail')

if __name__ == '__main__': unittest.main()

class ExistingAuditChain(unittest.IsolatedAsyncioTestCase):
    async def test_offline_extractor_audit_to_scorer(self):
        # Exercise the real prospective audit fixture; its unresolved response cannot pass.
        from test_rule_unit_prospective_integration import ProspectiveTests
        native = ProspectiveTests(methodName='test_round_trip_and_tampering')
        await native.asyncSetUp()
        try:
            await native.extract()
            audit = await native.audit()
            packet = s.load(native.run_dir / 'rule-units-candidates.private.json')
            f = fixture(); spec = f[0]['cases'][1]; c = f[1][1]; j = f[2]['cases'][1]
            h = audit['evidence_hashes']
            for k in ('source_text_sha256','source_body_sha256','context_sha256','plan_sha256'): spec[k] = h[k]
            spec['units'][0]['unit_id'] = 'a'
            c.update(audit=audit,packet=packet,document=native.doc,context=native.ctx)
            # Compare against the same pinned method in the calibration fixture.
            for k in ('model_identity','settings','schema','system','role'): f[1][0]['context'][k] = native.ctx[k]
            f[0]['cases'][0]['context_sha256']=s.digest(f[1][0]['context'])
            cal=f[1][0]; cal['packet']['context_sha256']=f[0]['cases'][0]['context_sha256']; cal['audit']['evidence_hashes']['context_sha256']=f[0]['cases'][0]['context_sha256']; cal['audit']['evidence_hashes']['packet_canonical_sha256']=s.digest(cal['packet']); f[2]['cases'][0]['packet_sha256']=s.digest(cal['packet']); f[2]['cases'][0]['audit_sha256']=s.digest(cal['audit'])
            c['reference']['units'][0]['unit_id']='a'; c['reference'].update(source_text_sha256=spec['source_text_sha256'],source_body_sha256=spec['source_body_sha256']); spec['reference_sha256']=s.digest(c['reference'])
            j.update(audit_sha256=s.digest(audit),packet_sha256=s.digest(packet))
            j['units'][0].update(unit_id='a',output_sha256=packet['units'][0]['output_sha256'],reference_sha256=spec['reference_sha256'],support='no_clause')
            j['units'][0]['slots'][0]['decision']='uncovered'
            result=run(f)
            self.assertTrue(audit['response_accounting_complete'])
            self.assertNotEqual(result['acceptance'],'pass')
            self.assertEqual(result['splits']['holdout']['metrics']['change_unit_coverage']['denominator'],1)
        finally:
            await native.asyncTearDown()
