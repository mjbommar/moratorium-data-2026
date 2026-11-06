import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_adaptive_revisit_plan import plan


class AdaptiveRevisitTests(unittest.TestCase):
    def rows(self):
        return [{'url':'https://example.invalid/source','variant':'http','at':t,
                 'attempt_id':str(t),'sha256':'same'} for t in [1000,2000]]
    def test_past_asof_does_not_learn_from_future_observations(self):
        row=plan(self.rows(),1500)[0]
        self.assertEqual(row['visits'],1)
        self.assertIsNone(row['native_rate_per_s'])
        self.assertEqual(row['attempt_ids'],['1000'])
    def test_signed_download_url_stays_private_and_public_event_priority_applies(self):
        import json
        rows=self.rows()
        for row in rows:row['url']='https://files.blob.core.windows.net/doc.pdf?sig=secret&sp=r'
        result=plan(rows,3000,{'https://files.blob.core.windows.net/doc.pdf':2500})
        self.assertNotIn('secret',json.dumps(result))
        self.assertEqual(result[0]['url'],'https://files.blob.core.windows.net/doc.pdf')
        self.assertEqual(result[0]['effective_due'],2500)
        self.assertIn('retrieval_url_sha256',result[0])
    def test_event_review_cannot_be_postponed_by_unchanged_content(self):
        row=plan(self.rows(),3000,{'https://example.invalid/source':2500})[0]
        self.assertTrue(row['due_now']);self.assertEqual(row['effective_due'],2500)
        self.assertGreater(row['adaptive_due'],row['event_review_due'])
    def test_later_event_review_cannot_postpone_native_due(self):
        row=plan(self.rows(),3000,{'https://example.invalid/source':10**10})[0]
        self.assertEqual(row['effective_due'],row['adaptive_due'])
    def test_http_and_rendered_observations_are_not_mixed(self):
        rows=self.rows();rows[1]['variant']='browser'
        result=plan(rows,3000)
        self.assertEqual(len(result),2);self.assertTrue(all(r['visits']==1 for r in result))
        self.assertTrue(all(r['native_rate_per_s'] is None for r in result))


if __name__=='__main__':unittest.main()
