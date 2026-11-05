import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from visual_claim_review import verify


class VisualReview(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.body=Path(self.tmp.name)/'body.pdf';self.body.write_bytes(b'%PDF retained source bytes')
        digest=lambda raw:hashlib.sha256(raw).hexdigest()
        self.claim={'claim_id':'c','source_document_id':'s','value':{'yes':10,'no':2},'quote':None}
        self.source={'source_document_id':'s','url':'https://example.gov/canvass','body_sha256':digest(self.body.read_bytes())}
        self.index={self.source['url']:[{'body_sha256':self.source['body_sha256'],'body_artifact':str(self.body)}]}
        self.review={'claim_id':'c','source_document_id':'s','claim_sha256':digest(json.dumps(self.claim,sort_keys=True,separators=(',',':')).encode()),
            'values':copy.deepcopy(self.claim['value']),'source_body_sha256':self.source['body_sha256'],
            'disposition':'accepted_visual_values','reviewer':'coordinator','pdf_page':2,
            'render_parameters':{'renderer':'pdftoppm','page':2,'dpi':120},'render_sha256':'approved-image-hash'}

    def test_reproduces_reviewed_page_parameters(self):
        with patch('visual_claim_review.render_hash',return_value='approved-image-hash') as render:
            self.assertTrue(verify(self.claim,self.source,self.index,self.review))
            render.assert_called_once_with(self.body,2,120)

    def test_changed_claim_fails_before_rendering(self):
        self.claim['value']['yes']=11
        with patch('visual_claim_review.render_hash') as render:
            with self.assertRaisesRegex(ValueError,'claim drift'):
                verify(self.claim,self.source,self.index,self.review)
            render.assert_not_called()

    def test_changed_retained_body_is_not_accepted(self):
        self.body.write_bytes(b'different source')
        with patch('visual_claim_review.render_hash') as render:
            with self.assertRaisesRegex(ValueError,'unavailable or drifted'):
                verify(self.claim,self.source,self.index,self.review)
            render.assert_not_called()

    def test_different_render_is_not_accepted(self):
        with patch('visual_claim_review.render_hash',return_value='different-image-hash'):
            with self.assertRaisesRegex(ValueError,'could not be reproduced'):
                verify(self.claim,self.source,self.index,self.review)
