import unittest
from scripts.archive_research_attempts import public_source_url

class PublicSourceURLTests(unittest.TestCase):
    def test_widen_signed_rendition_retains_only_resource_identifier(self):
        url='https://previews.us-east-1.widencdn.net/preview/50057123/assets/asset-view/example/pdf/bnVsbA==/document?sig.ver=1&sig.keyId=key&sig.expires=123&sig=private'
        self.assertEqual(public_source_url(url),url.split('?')[0])

    def test_azure_signed_download_still_redacted(self):
        url='https://example.blob.core.windows.net/documents/law.pdf?sv=1&sig=private'
        self.assertEqual(public_source_url(url),url.split('?')[0])

    def test_s3_signed_redirect_retains_only_resource_identifier(self):
        url='https://granicus-aasmp-peak-files.s3.amazonaws.com/uploads/attachment/pdf/1/law.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=private&X-Amz-Signature=private&X-Amz-Expires=3600'
        self.assertEqual(public_source_url(url),url.split('?')[0])

    def test_unsigned_s3_and_lookalike_queries_preserved(self):
        for url in ['https://example.s3.amazonaws.com/law.pdf?page=2',
                    'https://example.s3.amazonaws.com.evil.org/law.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=public&X-Amz-Signature=public',
                    'https://eureka.granicus.com/MetaViewer.php?view_id=3&clip_id=1914&meta_id=146588']:
            with self.subTest(url=url):
                self.assertEqual(public_source_url(url),url)

    def test_stable_viewer_and_unrelated_queries_preserved(self):
        for url in ['https://itswebny.widen.net/view/pdf/asset/law.pdf?u=public',
                    'https://example.org/law.pdf?sig=public&sig.keyId=key&sig.expires=123',
                    'https://previews.us-east-1.widencdn.net/law.pdf?page=2',
                    'https://widencdn.net.example.org/law.pdf?sig=private&sig.keyId=key&sig.expires=123']:
            with self.subTest(url=url):
                self.assertEqual(public_source_url(url),url)
