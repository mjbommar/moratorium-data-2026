import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_duration_review import row_hash, sha, validate_return


class DurationReviewTests(unittest.TestCase):
    def fixture(self, root):
        text, body = root/'a.private.txt', root/'a.private.body'
        text.write_text('Original 45 days; later extension ten months.')
        body.write_bytes(b'retained original body')
        proof = dict(url='https://example.gov/act', body_sha256=sha(body.read_bytes()),
                     text_sha256=sha(text.read_bytes()), text_artifact=str(text), attempt_id='a')
        row = dict(moratorium_id='x', duration='45 days; extended ten months', duration_days='45')
        packet = [dict(record=row, record_sha256=row_hash(row), retained_worker_evidence_proofs=[proof])]
        evidence = {k: v for k, v in proof.items() if k != 'attempt_id'}
        evidence.update(locator='Original term paragraph', support_scope='Original explicit day count only')
        decision = dict(moratorium_id='x', record_sha256=row_hash(row), original_duration_text=row['duration'],
                        recommendation='keep_fixed_days', proposed_duration_kind='fixed_days',
                        proposed_duration_days='45', rationale='Original days differ from extension months',
                        evidence=[evidence], limitations=['Current force unresolved'])
        return packet, dict(job_id='job', inventory_sha256='snapshot', decisions=[decision])

    def test_original_day_term_survives_calendar_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet, answers = self.fixture(Path(tmp))
            result = validate_return(packet, answers, 'job', 'snapshot')
            self.assertEqual(result[0]['recommendation'], 'keep_fixed_days')
            self.assertIn('not_assessed', result[0]['substantive_acceptance'])

    def test_proposed_day_counts_cannot_change_or_be_guessed(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet, answers = self.fixture(Path(tmp))
            answers['decisions'][0]['proposed_duration_days'] = '180'
            with self.assertRaisesRegex(ValueError, 'unsupported fields or day count'):
                validate_return(packet, answers, 'job', 'snapshot')

    def test_source_bytes_and_record_association_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet, answers = self.fixture(root)
            wrong = copy.deepcopy(answers)
            wrong['decisions'][0]['evidence'][0]['url'] = 'https://other.gov'
            with self.assertRaisesRegex(ValueError, 'not tied to this record'):
                validate_return(packet, wrong, 'job', 'snapshot')
            (root/'a.private.body').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'body hash drift'):
                validate_return(packet, answers, 'job', 'snapshot')

    def test_withholding_does_not_require_invented_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet, answers = self.fixture(Path(tmp))
            d = answers['decisions'][0]
            d.update(recommendation='withhold', proposed_duration_kind=None, proposed_duration_days=None, evidence=[])
            self.assertEqual(validate_return(packet, answers, 'job', 'snapshot')[0]['recommendation'], 'withhold')
            d.update(recommendation='calendar_term', proposed_duration_kind='calendar_term', proposed_duration_days='')
            with self.assertRaisesRegex(ValueError, 'needs inspected evidence'):
                validate_return(packet, answers, 'job', 'snapshot')

    def test_missing_duplicate_and_stale_decisions_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet, answers = self.fixture(Path(tmp))
            for mutation in ('missing', 'duplicate', 'stale'):
                value = copy.deepcopy(answers)
                if mutation == 'missing': value['decisions'] = []
                elif mutation == 'duplicate': value['decisions'] *= 2
                else: value['decisions'][0]['record_sha256'] = 'changed'
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    validate_return(packet, value, 'job', 'snapshot')
