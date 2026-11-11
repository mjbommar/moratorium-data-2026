"""New-source admission must stop reuse before network or budget reservation."""
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research_client as client


class SourceNoveltyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.job = self.root / 'job'
        self.job.mkdir()
        (self.job / 'client-config.json').write_text(json.dumps({'caps': {'fetch': 3}}))
        self.sources = self.root / 'sources'
        (self.sources / 'WI').mkdir(parents=True)
        self.source_patch = patch.object(client, 'SOURCE_ROOT', self.sources)
        self.source_patch.start()
        self.addCleanup(self.source_patch.stop)

    def manifest(self, **row):
        (self.sources / 'WI/manifest.jsonl').write_text(json.dumps(row) + '\n')

    def reservations(self):
        path = self.job / 'attempts.private.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_redirect_fragment_and_default_port_block_before_execute(self):
        self.manifest(url='http://example.invalid/old',
                      final_url='https://EXAMPLE.invalid:443/results?year=2026', key='old')
        args = argparse.Namespace(directory=self.job, action='fetch', mode='http',
                                  url='https://example.invalid/results?year=2026#top',
                                  new_source_only=True)
        with self.assertRaisesRegex(ValueError, 'Retained source URL'):
            asyncio.run(client.execute(args))
        self.assertEqual(self.reservations(), [])
        denial = json.loads((self.job / 'source-novelty-denials.private.jsonl').read_text())
        self.assertEqual(denial['outcome'], 'blocked_before_reservation_and_network')

    def test_distinct_functional_query_is_admitted(self):
        self.manifest(url='https://example.invalid/document?id=1', key='one')
        result = client.reserve(self.job, 'fetch', intent={
            'url': 'https://example.invalid/document?id=2',
            'source_novelty_policy': 'reject_retained_request_or_redirect_url'})
        self.assertEqual(self.reservations()[0]['attempt_id'], result['attempt_id'])

    def test_concurrent_same_url_reserves_only_once(self):
        barrier = threading.Barrier(2)

        def attempt():
            barrier.wait(timeout=5)
            try:
                client.reserve(self.job, 'fetch', intent={
                    'url': 'https://example.invalid/new',
                    'source_novelty_policy': 'reject_retained_request_or_redirect_url'})
                return 'reserved'
            except ValueError as error:
                self.assertIn('Retained source URL', str(error))
                return 'denied'

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(), range(2)))
        self.assertCountEqual(results, ['reserved', 'denied'])
        self.assertEqual(len(self.reservations()), 1)

    def test_explicit_refresh_without_flag_remains_available(self):
        self.manifest(url='https://example.invalid/results', key='old')
        client.reserve(self.job, 'fetch', intent={'url': 'https://example.invalid/results'})
        self.assertEqual(len(self.reservations()), 1)

    def test_corrupt_manifest_fails_closed_without_reservation(self):
        (self.sources / 'WI/manifest.jsonl').write_text('{broken\n')
        with self.assertRaises(json.JSONDecodeError):
            client.reserve(self.job, 'fetch', intent={
                'url': 'https://example.invalid/new',
                'source_novelty_policy': 'reject_retained_request_or_redirect_url'})
        self.assertEqual(self.reservations(), [])


if __name__ == '__main__':
    unittest.main()
