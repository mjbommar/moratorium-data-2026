import asyncio
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
try:
    import httpx
    from bc_web.settings import BcWebSettings
    import bc_spec
    NATIVE = True
except ImportError:
    NATIVE = False
import search_refresh_batch as batch


def plan():
    return {'schema_version':'refresh-search-plan-1',
            'registry':[{'id':'seattle-wa','label':'Seattle, Washington','aliases':['City of Seattle'],
                         'official_hosts':[{'host':'clerk.seattle.gov','source_url':'https://clerk.seattle.gov/act',
                                            'body_sha256':'a'*64,'locator':'Original official record'}]}],
            'cells':[{'id':'seattle-history','lane':'inventory_refresh','jurisdiction_id':'seattle-wa',
                      'sector':'data_center','period':'through-2026-11-05','intent':'later-operative-history',
                      'known_id':'wa-seattle-2026','variants':[
                          {'name':'exa-semantic','backend':'exa','query':'Seattle ordinance 127447 later amendment extension repeal','max_results':3},
                          {'name':'google-exact','backend':'serpapi','query':'"Seattle" "127447" extension repeal','max_results':3}]}],
            'sample':{'strategy':'full','seed':42},
            'caps':{'exa':1,'serpapi':1,'googlenews':0,'gdelt':0,'search_total':2},'allow_unpriced':True}


@unittest.skipUnless(NATIVE, 'bc-modules native environment required')
class SearchBatchTests(unittest.IsolatedAsyncioTestCase):
    def test_preview_is_deterministic_sparse_and_budgeted(self):
        p=plan(); first=batch.preview(p)
        self.assertEqual(first,batch.preview(copy.deepcopy(p)))
        self.assertEqual(first['estimated_calls'],2)
        self.assertIsNone(first['estimated_total_usd'])
        self.assertEqual(first['explicit_cells'],1)
        p['caps']['search_total']=1
        with self.assertRaisesRegex(ValueError,'exceed'):batch.preview(p)

    def test_unknown_registry_host_and_duplicate_coordinates_rejected(self):
        p=plan();p['cells'][0]['variants'][0]['include_domains']=['invented.gov']
        with self.assertRaisesRegex(ValueError,'reviewed host'):batch.preview(p)
        p=plan();p['cells'].append({**copy.deepcopy(p['cells'][0]),'id':'duplicate'})
        with self.assertRaisesRegex(ValueError,'Duplicate sparse'):batch.preview(p)

    def test_seeded_three_lane_frame_records_exclusions(self):
        p=plan()
        p['cells']=[{**copy.deepcopy(p['cells'][0]),'id':lane+str(i),'lane':lane,'intent':'gap-'+str(i)}
                    for lane in sorted(batch.LANES) for i in range(2)]
        p['sample']={'strategy':'stratified','dimension':'lane','per':1,'seed':17}
        p['caps']={'exa':3,'serpapi':3,'googlenews':0,'gdelt':0,'search_total':6}
        result=batch.preview(p)
        self.assertEqual(len(result['selected_cells']),3)
        self.assertEqual(len(result['excluded_cell_ids']),3)
        self.assertEqual({c['lane'] for c in result['selected_cells']},batch.LANES)
        self.assertEqual(result,batch.preview(p))

    async def test_native_search_many_fusion_sightings_redaction_and_cached_replay(self):
        calls=[]
        def handler(request):
            calls.append(request)
            if request.url.host=='api.exa.ai':
                return httpx.Response(200,json={'results':[{'url':'https://clerk.seattle.gov/shared','title':'Exa','highlights':['test-secret-exa']},
                                                          {'url':'https://example.gov/exa-only','title':'Unique'}],
                                               'costDollars':{'total':0.007}})
            return httpx.Response(200,json={'organic_results':[{'link':'https://clerk.seattle.gov/shared','title':'Google','position':1},
                                                               {'link':'https://example.gov/google-only','title':'Unique','position':2}]})
        settings=BcWebSettings(exa_api_key='test-secret-exa',serpapi_api_key='test-secret-serp')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            result=await batch.execute(plan(),root,settings=settings,transport=httpx.MockTransport(handler))
            self.assertEqual(len(calls),2)
            self.assertEqual(result['cells'][0]['sightings'],4)
            payload=json.loads((root/result['cells'][0]['artifact']).read_text())
            self.assertEqual(payload['hits'][0]['ranks'],{'exa-semantic':1,'google-exact':1})
            from normalize_search_provenance import normalize
            normalized=normalize(root)
            self.assertEqual(normalized['summary']['search_attempts'],2)
            self.assertEqual(len(normalized['sightings']),4)
            for path in root.iterdir():
                self.assertNotIn(b'test-secret-exa',path.read_bytes())
                self.assertNotIn(b'test-secret-serp',path.read_bytes())
            replay=await batch.execute(plan(),root,settings=settings,transport=httpx.MockTransport(handler))
            self.assertTrue(replay['replay']); self.assertEqual(len(calls),2)
            (root/result['cells'][0]['artifact']).write_text('{}')
            with self.assertRaisesRegex(ValueError,'artifact drift'):
                await batch.execute(plan(),root,settings=settings,transport=httpx.MockTransport(handler))

    async def test_failure_and_zero_hits_preserve_attempts_without_retry(self):
        calls=[]
        def handler(request):
            calls.append(request)
            if request.url.host=='api.exa.ai':return httpx.Response(503,text='error test-secret-exa')
            return httpx.Response(200,json={'organic_results':[]})
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            result=await batch.execute(plan(),root,settings=BcWebSettings(exa_api_key='test-secret-exa',serpapi_api_key='test-secret-serp'),transport=httpx.MockTransport(handler))
            self.assertEqual(len(calls),2)
            states=result['cells'][0]['coverage']
            self.assertEqual(states['status'],'partial')
            self.assertEqual(states['variants'],{'exa-semantic':'error','google-exact':'zero_hits'})
            events=[json.loads(s) for s in (root/'attempts.private.jsonl').read_text().splitlines()]
            self.assertEqual(sum(e['state']=='reserved' for e in events),2)
            self.assertEqual(sum(e['state']=='finished' for e in events),2)
            self.assertEqual(len(json.loads((root/'exchanges.private.json').read_text())),2)

    async def test_concurrent_same_provider_variants_keep_exchange_attribution(self):
        p=plan();p['cells'][0]['variants']=[{'name':name,'backend':'serpapi','query':query,'max_results':3}
                                           for name,query in [('first','alpha'),('second','beta')]]
        p['caps'].update(exa=0,serpapi=2)
        def handler(request):
            return httpx.Response(200,json={'marker':request.url.params['q'],'organic_results':[]})
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            await batch.execute(p,root,settings=BcWebSettings(serpapi_api_key='test-secret-serp'),transport=httpx.MockTransport(handler))
            exchanges=json.loads((root/'exchanges.private.json').read_text())
            self.assertEqual({e['variant']:json.loads((root/e['artifact']).read_text())['marker'] for e in exchanges},
                             {'first':'alpha','second':'beta'})

    async def test_domain_scope_diagnostic_does_not_hide_outside_hits(self):
        from bc_web.fusion import FusedResponse
        from bc_web.search import SearchQuery, SearchResponse, SearchHit
        response=FusedResponse(query='scope',responses={'google':SearchResponse(query='scope',backend='serpapi',hits=[
            SearchHit(position=1,title='Unrelated',url='https://unrelated.example/act',source='serpapi')])})
        diagnostics=batch.domain_diagnostics(response,{'google':SearchQuery(query='scope',backend='serpapi',include_domains=['example.gov'])})
        self.assertEqual(diagnostics['google']['nonmatching_hits'],1)
        self.assertEqual(len(response.responses['google'].hits),1)

    async def test_unpriced_stop_precedes_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=plan();p['allow_unpriced']=False;root=Path(tmp)
            with self.assertRaisesRegex(ValueError,'unpriced-call authorization'):
                await batch.execute(p,root)
            self.assertEqual(list(root.iterdir()),[])

    async def test_decline_is_not_zero_hits_and_incomplete_run_never_restarts(self):
        from bc_web.fusion import FusedResponse
        from bc_web.search import SearchResponse
        response=FusedResponse(query='old',responses={'gdelt':SearchResponse(query='old',backend='gdelt',hits=[],declined='outside index window')})
        self.assertEqual(batch.coverage(response,['gdelt'])['variants']['gdelt'],'declined')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=plan()
            (root/'run.private.json').write_text(json.dumps({'plan_sha256':batch.preview(p)['plan_sha256'], 'runtime':batch.runtime_fingerprint()}))
            with self.assertRaisesRegex(ValueError,'unfinished'):
                await batch.execute(p,root)
