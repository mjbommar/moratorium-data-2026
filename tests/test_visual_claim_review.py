import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from visual_claim_review import verify, audit_render_cache
from audit_refresh_returns import audit_expanded_evidence
try:
    import bc_core.text
    NATIVE_TEXT = True
except ImportError:
    NATIVE_TEXT = False


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


class AdditionalPdfPages(unittest.TestCase):
    setUp=VisualReview.setUp

    def test_every_additional_page_is_reproduced(self):
        self.review['additional_pdf_pages']=[dict(page=3,dpi=150,render_sha256='a'*64)]
        with patch('visual_claim_review.render_hash',side_effect=['approved-image-hash','a'*64]) as render:
            self.assertTrue(verify(self.claim,self.source,self.index,self.review))
            self.assertEqual(render.call_args_list[-1].args,(self.body,3,150))
        with patch('visual_claim_review.render_hash',side_effect=['approved-image-hash','b'*64]):
            with self.assertRaisesRegex(ValueError,'Additional reviewed rendering'):
                verify(self.claim,self.source,self.index,self.review)

    def test_duplicate_primary_page_cannot_hide_missing_continuation(self):
        self.review['additional_pdf_pages']=[dict(page=2,dpi=150,render_sha256='a'*64)]
        with patch('visual_claim_review.render_hash') as render:
            with self.assertRaisesRegex(ValueError,'additional PDF page'):
                verify(self.claim,self.source,self.index,self.review)
            render.assert_not_called()


class RenderReuse(unittest.TestCase):
    setUp=VisualReview.setUp

    def second(self):
        claim=copy.deepcopy(self.claim);claim['claim_id']='c2';claim['value']={'yes':20}
        review=copy.deepcopy(self.review);review['claim_id']='c2';review['values']=copy.deepcopy(claim['value'])
        review['claim_sha256']=hashlib.sha256(json.dumps(claim,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        return claim,review

    def audit(self,claim,review):
        source=dict(self.source,text_sha256=None)
        return audit_expanded_evidence({'source_documents':[source],'claims':[self.claim,claim]},
            self.index,{'c':self.review,'c2':review})

    @unittest.skipUnless(NATIVE_TEXT, 'requires native bc-core text audit')
    def test_audit_reuses_render_but_checks_each_receipt_and_starts_fresh(self):
        claim,review=self.second()
        with patch('visual_claim_review.render_hash',return_value='approved-image-hash') as render:
            issues,proofs=self.audit(claim,review)
            self.assertFalse(issues);self.assertTrue(all(p['visual_verified'] for p in proofs))
            self.assertEqual(render.call_count,1)
            self.audit(claim,review);self.assertEqual(render.call_count,2)
            review['render_sha256']='tampered'
            with self.assertRaisesRegex(ValueError,'could not be reproduced'):self.audit(claim,review)
            self.assertEqual(render.call_count,3)
            review['render_sha256']='approved-image-hash';review['values']={'yes':21}
            with self.assertRaisesRegex(ValueError,'claim drift'):self.audit(claim,review)

    def test_body_is_rehashed_on_cache_hit(self):
        claim,review=self.second()
        with audit_render_cache(), patch('visual_claim_review.render_hash',return_value='approved-image-hash') as render:
            verify(self.claim,self.source,self.index,self.review)
            self.body.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'unavailable or drifted'):
                verify(claim,self.source,self.index,review)
            self.assertEqual(render.call_count,1)

    def test_new_verified_body_renders_again(self):
        with audit_render_cache(), patch('visual_claim_review.render_hash',return_value='approved-image-hash') as render:
            verify(self.claim,self.source,self.index,self.review)
            self.body.write_bytes(b'new retained source')
            body_hash=hashlib.sha256(self.body.read_bytes()).hexdigest()
            self.source['body_sha256']=body_hash
            self.index[self.source['url']][0]['body_sha256']=body_hash
            self.review['source_body_sha256']=body_hash
            verify(self.claim,self.source,self.index,self.review)
            self.assertEqual(render.call_count,2)

    def test_page_dpi_and_executable_contents_and_path_invalidate(self):
        exe=Path(self.tmp.name)/'renderer';exe.write_bytes(b'version one')
        other=Path(self.tmp.name)/'renderer2';other.write_bytes(b'version two')
        with audit_render_cache(), patch('visual_claim_review.shutil.which',return_value=str(exe)) as which, \
             patch('visual_claim_review.render_hash',return_value='approved-image-hash') as render:
            verify(self.claim,self.source,self.index,self.review)
            verify(self.claim,self.source,self.index,self.review)
            self.review['pdf_page']=3;self.review['render_parameters']['page']=3
            verify(self.claim,self.source,self.index,self.review)
            self.review['render_parameters']['dpi']=150
            verify(self.claim,self.source,self.index,self.review)
            exe.write_bytes(b'version two');verify(self.claim,self.source,self.index,self.review)
            which.return_value=str(other);verify(self.claim,self.source,self.index,self.review)
            self.assertEqual(render.call_count,5)

    def test_cached_additional_page_still_checks_expected_hash(self):
        claim,review=self.second()
        self.review['additional_pdf_pages']=[dict(page=3,dpi=150,render_sha256='a'*64)]
        review['additional_pdf_pages']=[dict(page=3,dpi=150,render_sha256='b'*64)]
        with audit_render_cache(), patch('visual_claim_review.render_hash',side_effect=['approved-image-hash','a'*64]) as render:
            verify(self.claim,self.source,self.index,self.review)
            with self.assertRaisesRegex(ValueError,'Additional reviewed rendering'):
                verify(claim,self.source,self.index,review)
            self.assertEqual(render.call_count,2)

    def test_nested_and_exception_reset_and_standalone_uncached(self):
        with patch('visual_claim_review.render_hash',return_value='approved-image-hash') as render:
            with audit_render_cache():
                verify(self.claim,self.source,self.index,self.review)
                with self.assertRaisesRegex(RuntimeError,'abort'):
                    with audit_render_cache():
                        verify(self.claim,self.source,self.index,self.review)
                        raise RuntimeError('abort')
                verify(self.claim,self.source,self.index,self.review)
                self.assertEqual(render.call_count,2)
            verify(self.claim,self.source,self.index,self.review)
            verify(self.claim,self.source,self.index,self.review)
            self.assertEqual(render.call_count,4)


class NativePngReview(VisualReview):
    def setUp(self):
        super().setUp()
        import struct
        import zlib
        def chunk(kind,payload):
            return (struct.pack('>I',len(payload))+kind+payload+
                    struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff))
        raw=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,1,8,2,0,0,0))+
             chunk(b'IDAT',zlib.compress(b'\x00\xff\x00\x00\x00\xff\x00'))+chunk(b'IEND',b''))
        self.bind_body(raw)
        self.review.update(pdf_page=None,render_sha256=self.source['body_sha256'],
            render_parameters={'renderer':'native-png','width':2,'height':1})

    def bind_body(self,raw):
        self.body.write_bytes(raw);h=hashlib.sha256(raw).hexdigest()
        self.source['body_sha256']=h;self.index[self.source['url']][0]['body_sha256']=h
        self.review['source_body_sha256']=h

    # Parent cases exercise PDF rendering; native cases below exercise its own path.
    def test_reproduces_reviewed_page_parameters(self):
        with patch('visual_claim_review.render_hash') as render:
            self.assertTrue(verify(self.claim,self.source,self.index,self.review))
            render.assert_not_called()

    def test_different_render_is_not_accepted(self):
        self.review['render_sha256']='a transformed image hash'
        with self.assertRaisesRegex(ValueError,'original untransformed'):
            verify(self.claim,self.source,self.index,self.review)

    def test_crop_or_pdf_page_is_not_accepted(self):
        self.review['render_parameters']['crop']=[0,0,1,1]
        with self.assertRaisesRegex(ValueError,'parameters'):
            verify(self.claim,self.source,self.index,self.review)
        del self.review['render_parameters']['crop'];self.review['pdf_page']=1
        with self.assertRaisesRegex(ValueError,'parameters'):
            verify(self.claim,self.source,self.index,self.review)

    def test_dimension_drift_is_not_accepted(self):
        self.review['render_parameters']['width']=3
        with self.assertRaisesRegex(ValueError,'dimensions differ'):
            verify(self.claim,self.source,self.index,self.review)

    def test_non_png_bytes_are_not_accepted_even_with_matching_hashes(self):
        self.bind_body(b'%PDF not a native PNG')
        self.review['render_sha256']=self.source['body_sha256']
        with self.assertRaisesRegex(ValueError,'not PNG'):
            verify(self.claim,self.source,self.index,self.review)

    def test_corrupt_container_is_not_accepted_even_with_matching_hashes(self):
        raw=bytearray(self.body.read_bytes());raw[20]^=1;self.bind_body(raw)
        self.review['render_sha256']=self.source['body_sha256']
        with self.assertRaisesRegex(ValueError,'checksum'):
            verify(self.claim,self.source,self.index,self.review)


class NativeJpegReview(VisualReview):
    def setUp(self):
        super().setUp()
        import io
        from PIL import Image
        image=Image.new('RGB',(3,2),(20,40,60));exif=Image.Exif();exif[274]=8
        buf=io.BytesIO();image.save(buf,format='JPEG',exif=exif,progressive=True)
        self.bind_body(buf.getvalue())
        self.review.update(pdf_page=None,render_sha256=self.source['body_sha256'],
            render_parameters={'renderer':'native-jpeg','width':3,'height':2,'exif_orientation':8})

    def bind_body(self,raw):
        self.body.write_bytes(raw);h=hashlib.sha256(raw).hexdigest()
        self.source['body_sha256']=h;self.index[self.source['url']][0]['body_sha256']=h
        self.review['source_body_sha256']=h

    def test_reproduces_reviewed_page_parameters(self):
        with patch('visual_claim_review.render_hash') as render:
            self.assertTrue(verify(self.claim,self.source,self.index,self.review))
            render.assert_not_called()

    def test_different_render_is_not_accepted(self):
        self.review['render_sha256']='converted-image-hash'
        with self.assertRaisesRegex(ValueError,'original untransformed'):
            verify(self.claim,self.source,self.index,self.review)

    def test_wrong_orientation_or_dimensions_rejected(self):
        for field,bad in [('exif_orientation',1),('width',2),('height',3)]:
            original=self.review['render_parameters'][field]
            self.review['render_parameters'][field]=bad
            with self.assertRaisesRegex(ValueError,'dimensions/orientation differ'):
                verify(self.claim,self.source,self.index,self.review)
            self.review['render_parameters'][field]=original

    def test_orientation_required_and_crop_rejected(self):
        del self.review['render_parameters']['exif_orientation']
        with self.assertRaisesRegex(ValueError,'parameters'):
            verify(self.claim,self.source,self.index,self.review)
        self.review['render_parameters'].update(exif_orientation=8,crop=[0,0,1,1])
        with self.assertRaisesRegex(ValueError,'parameters'):
            verify(self.claim,self.source,self.index,self.review)

    def test_truncation_rejected_even_with_matching_hashes(self):
        self.bind_body(self.body.read_bytes()[:-2])
        self.review['render_sha256']=self.source['body_sha256']
        with self.assertRaisesRegex(ValueError,'complete JPEG'):
            verify(self.claim,self.source,self.index,self.review)

    def test_non_jpeg_rejected_even_with_matching_hashes(self):
        self.bind_body(b'\xff\xd8not an image\xff\xd9')
        self.review['render_sha256']=self.source['body_sha256']
        with self.assertRaisesRegex(ValueError,'Invalid native JPEG'):
            verify(self.claim,self.source,self.index,self.review)

    def test_lenient_decoder_mode_rejected(self):
        with patch('PIL.ImageFile.LOAD_TRUNCATED_IMAGES',True):
            with self.assertRaisesRegex(ValueError,'Strict native JPEG'):
                verify(self.claim,self.source,self.index,self.review)
