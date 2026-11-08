import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
try:
    import bc_spec
    import bc_web
    import build_sparse_refresh_worklist as work
    NATIVE=True
except ImportError:
    NATIVE=False


@unittest.skipUnless(NATIVE,'requires native bc-spec and bc-web')
class SparseWorklistTests(unittest.TestCase):
    def test_unknown_sector_measure_is_retained_for_neutral_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            path = root / 'data/expanded/ballot_measures.jsonl'
            measures = [json.loads(line) for line in path.read_text().splitlines()]
            measures[1]['sectors'] = []
            path.write_text(''.join(json.dumps(row) + '\n' for row in measures))
            result = work.build(root, '2026-11-07')
            task = next(row for row in result['worklist']['items'] if row['id'] == 'measure:m-2')
            self.assertEqual(result['summary']['object_counts']['measure'], 2)
            self.assertEqual(task['planning_status'], 'sector_neutral_search_sector_review_open')
            self.assertEqual(task['sectors'], [])
            self.assertEqual({cell['sector'] for cell in result['plan']['cells']
                              if cell['known_id'] == 'measure:m-2'}, {'sector_unresolved'})
            self.assertEqual(task['freshness_disposition'], 'not_attempted_by_this_worklist')

    def fixture(self,root):
        def csvfile(path,rows):
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        local={'moratorium_id':'local-me','state_abbrev':'ME','state':'Maine','jurisdiction_type':'Town',
               'jurisdiction':'Example','sectors':'["cryptocurrency_mining"]','enacted_status':'active',
               'legal_basis':'Ordinance 12 with a long description','date_enacted_iso':'2026-01-01','current_end_date_iso':''}
        locals=[local,{**local,'moratorium_id':'local-wi','state_abbrev':'WI','state':'Wisconsin'},
                {**local,'moratorium_id':'local-city','jurisdiction_type':'City'}]
        csvfile(Path('data/moratorium_inventory.csv'),locals)
        csvfile(Path('data/state_legislation.csv'),[{'policy_action_id':'state-1','state_abbrev':'ME','bill':'HB 1','bill_status_category':'pending'}])
        expanded=root/'data/expanded';expanded.mkdir()
        tables={'jurisdictions':[{'jurisdiction_id':'j-1','name':'Example','state':'ME','aliases':['Town of Example'],
                                  'government_type':'town','county':'County'}],
                'elections':[{'election_id':'e-1','jurisdiction_id':'j-1','election_date':{'original_text':'November 2026'},
                              'official_result_urls':['https://unreviewed.example/results']}],
                'ballot_measures':[{'measure_id':'m-1','jurisdiction_id':'j-1','election_id':'e-1','sectors':['general','data_center'],
                                    'designation':'Question 1','title':'Example vote','lifecycle':'voted','bindingness':'unresolved'},
                                   {'measure_id':'m-2','jurisdiction_id':'j-1','election_id':'e-1','sectors':['general'],
                                    'designation':None,'title':'Other vote','lifecycle':'proposed','bindingness':'unresolved'}],
                'source_documents':[]}
        for table,rows in tables.items():
            (expanded/(table+'.jsonl')).write_text(''.join(json.dumps(r)+'\n' for r in rows))
        return locals

    def test_full_object_accounting_keeps_ambiguity_and_no_freshness_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);r=work.build(root,'2026-11-06')
            tasks=r['worklist']['items'];by_id={t['id']:t for t in tasks}
            self.assertEqual(len(tasks),506)
            self.assertEqual(r['summary']['object_counts'],{'moratorium':3,'state_action':1,'measure':2})
            self.assertEqual(by_id['state_action:state-1']['planning_status'],'sector_neutral_search_sector_review_open')
            self.assertEqual(by_id['measure:m-2']['planning_status'],'partial_sector_review')
            self.assertEqual(by_id['measure:m-1']['unresolved_sector_terms'],['general'])
            self.assertEqual(by_id['moratorium:local-me']['sectors'],['cryptocurrency'])
            self.assertEqual(len({by_id['moratorium:'+k]['jurisdiction_id'] for k in ['local-me','local-wi','local-city']}),3)
            self.assertNotEqual(by_id['moratorium:local-me']['jurisdiction_id'],by_id['measure:m-1']['jurisdiction_id'])
            self.assertTrue(all(t['freshness_disposition']=='not_attempted_by_this_worklist' for t in tasks))
            self.assertFalse(r['plan']['allow_unpriced'])
            self.assertEqual(len(r['preview']['selected_cells']),507)
            self.assertEqual(len(r['preview']['excluded_cell_ids']),0)
            small=work.build(root,'2026-11-06',per_lane=1)
            self.assertEqual(len(small['preview']['selected_cells']),3)
            self.assertEqual(len(small['preview']['excluded_cell_ids']),504)
            self.assertEqual(r,work.build(root,'2026-11-06'))
            self.assertEqual({c['sector'] for c in r['plan']['cells']},set(work.SECTOR_WORDS)|{'sector_unresolved'})
            self.assertTrue(all('start_date' not in v and 'end_date' not in v for c in r['plan']['cells'] for v in c['variants']))

    def test_reviewed_host_requires_retained_body_and_candidates_are_not_filters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);first=work.build(root,'2026-11-06')
            self.assertTrue(all(not v.get('include_domains') for c in first['plan']['cells'] for v in c['variants']))
            raw=b'Fixture source body';folder=root/'work/sources/ME';folder.mkdir(parents=True)
            (folder/'source.pdf').write_bytes(raw);sha=hashlib.sha256(raw).hexdigest()
            url='https://official.example/source.pdf'
            (folder/'manifest.jsonl').write_text(json.dumps({'url':url,'sha256':sha,'ok':True,'files':['work/sources/ME/source.pdf']})+'\n')
            binding={'schema_version':'refresh-host-bindings-1','bindings':[{'jurisdiction_id':'expanded:j-1',
                     'host':'official.example','source_url':url,'body_sha256':sha,'locator':'Fixture document heading',
                     'role':'election','reviewer':'fixture','manifest':'work/sources/ME/manifest.jsonl'}]}
            review={k:binding['bindings'][0][k] for k in ['jurisdiction_id','host','role','source_url','body_sha256','reviewer']}
            review.update(authority_basis='Fixture-only jurisdiction/role evidence, not an actual authority assertion.',reviewed_at='2026-11-06T12:00:00+00:00')
            review_path=root/'work/research/fixture/host-review.json';review_path.parent.mkdir(parents=True);review_path.write_text(json.dumps(review))
            binding['bindings'][0].update(authority_review='work/research/fixture/host-review.json',authority_review_sha256=hashlib.sha256(review_path.read_bytes()).hexdigest())
            result=work.build(root,'2026-11-06',bindings=binding)
            filtered=[v for c in result['plan']['cells'] for v in c['variants'] if v.get('include_domains')]
            self.assertTrue(filtered);self.assertTrue(all(v['include_domains']==['official.example'] for v in filtered))
            self.assertEqual(result['summary']['reviewed_host_coordinates'],1)
            emitted=next(x for x in result['plan']['registry'] if x['id']=='expanded:j-1')['official_hosts'][0]['authority_review']
            self.assertEqual(emitted['path'],'work/research/fixture/host-review.json')
            self.assertEqual(emitted['sha256'],binding['bindings'][0]['authority_review_sha256'])
            review['path']='spoofed';review_path.write_text(json.dumps(review))
            binding['bindings'][0]['authority_review_sha256']=hashlib.sha256(review_path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError,'Reserved authority'):work.build(root,'2026-11-06',bindings=binding)
            del review['path'];review_path.write_text(json.dumps(review))
            binding['bindings'][0]['authority_review_sha256']=hashlib.sha256(review_path.read_bytes()).hexdigest()
            (folder/'source.pdf').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'unavailable or drifted'):work.build(root,'2026-11-06',bindings=binding)

    def test_unknown_binding_and_duplicate_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            binding={'schema_version':'refresh-host-bindings-1','bindings':[{'jurisdiction_id':'invented',
                     'host':'official.example','source_url':'https://official.example/source','body_sha256':'a'*64,
                     'locator':'heading','role':'government','reviewer':'fixture','manifest':'work/sources/ME/manifest.jsonl','authority_review':'work/research/fixture/host-review.json','authority_review_sha256':'a'*64}]}
            with self.assertRaisesRegex(ValueError,'Unknown binding'):work.build(root,'2026-11-06',bindings=binding)
            path=root/'data/expanded/ballot_measures.jsonl';path.write_text(path.read_text()+path.read_text().splitlines()[0]+'\n')
            with self.assertRaisesRegex(ValueError,'Duplicate or blank input'):work.build(root,'2026-11-06')
