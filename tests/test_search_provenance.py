import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from normalize_search_provenance import normalize, digest


class SearchProvenanceTests(unittest.TestCase):
    def fixture(self, root, state='response', hits=None, declined=None):
        reserved = dict(attempt_id='a', kind='exa', state='reserved', reserved_at='2026-11-06T00:00:00Z',
                        client_sha256='client', config_sha256='config')
        events = [reserved]
        if state != 'interrupted':
            done = dict(reserved, state='finished', outcome=state, finished_at='2026-11-06T00:01:00Z')
            if state == 'response':
                body = root / 'response.body'
                body.write_text('private provider response')
                payload = root / 'response.json'
                payload.write_text(json.dumps(dict(backend='exa', query='q', hits=hits or [], declined=declined)))
                done.update(query='q', artifact=str(payload), hits=len(hits or []), cost_usd=None,
                            exchanges=[dict(artifact=str(body), status=200, original_body_sha256=digest(body),
                                            stored_body_sha256=digest(body), redacted=False)])
            else:
                done['error_type'] = 'TimeoutError'
            events.append(done)
        (root / 'attempts.private.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))

    def test_zero_failure_interruption_and_decline_are_distinct(self):
        for state, decline, expected in [('response', None, 'success'), ('error', None, 'error'),
                                         ('interrupted', None, 'interrupted'), ('response', 'window', 'partial')]:
            with self.subTest(state=state, decline=decline), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root, state, declined=decline)
                result = normalize(root)
                self.assertEqual(result['attempts'][0]['outcome'], expected)
                self.assertEqual(result['summary']['successful_zero_hit_attempts'], int(expected == 'success'))
                self.assertEqual(result['summary']['unpriced_attempts'], 1)

    def test_sightings_preserve_order_without_private_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, hits=[dict(url='https://example.org', position=7, snippet='private snippet')])
            result = normalize(root)
            self.assertEqual(result['sightings'][0]['provider_position'], 7)
            self.assertEqual(result['sightings'][0]['returned_order'], 1)
            self.assertNotIn('private snippet', json.dumps(result))
            (root / 'response.body').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                normalize(root)

    def test_duplicate_terminal_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, 'error')
            ledger = root / 'attempts.private.jsonl'
            ledger.write_text(ledger.read_text()+ledger.read_text().splitlines()[-1]+'\n')
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                normalize(root)

    def test_failed_reserved_intent_is_retained_and_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, 'error')
            ledger = root/'attempts.private.jsonl'
            events = [json.loads(line) for line in ledger.read_text().splitlines()]
            for event in events:
                event['intent'] = {'query': 'specific gap', 'publication_window': {'since': None, 'until': None}}
            ledger.write_text(''.join(json.dumps(event)+'\n' for event in events))
            self.assertEqual(normalize(root)['attempts'][0]['query'], 'specific gap')
            events[-1]['intent']['query'] = 'different gap'
            ledger.write_text(''.join(json.dumps(event)+'\n' for event in events))
            with self.assertRaisesRegex(ValueError, 'intent mismatch'):
                normalize(root)

    def test_error_and_interrupted_exchanges_survive_without_payload(self):
        for state in ('error', 'interrupted'):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root, state)
                body = root / 'failure.body'
                body.write_text('private rate-limit response')
                exchange = dict(attempt_id='a', artifact=str(body), status=429,
                                original_body_sha256=digest(body), stored_body_sha256=digest(body), redacted=False)
                (root / 'exchanges.private.jsonl').write_text(json.dumps(exchange)+'\n')
                result = normalize(root)
                self.assertEqual(result['attempts'][0]['exchanges'][0]['status'], 429)
                self.assertEqual(result['attempts'][0]['outcome'], state)
                self.assertNotIn('private rate-limit response', json.dumps(result))
                self.assertEqual(result['sightings'], [])

    def test_exchange_copies_must_agree_and_are_not_double_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            done = json.loads((root/'attempts.private.jsonl').read_text().splitlines()[-1])
            exchange = dict(done['exchanges'][0], attempt_id='a')
            ledger = root/'exchanges.private.jsonl'
            ledger.write_text(json.dumps(exchange)+'\n')
            self.assertEqual(len(normalize(root)['attempts'][0]['exchanges']), 1)
            exchange['status'] = 503
            ledger.write_text(json.dumps(exchange)+'\n')
            with self.assertRaisesRegex(ValueError, 'mismatch'):
                normalize(root)
