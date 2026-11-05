import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_ballot_census import namespace
from expanded_data import validate


class CensusNamespaces(unittest.TestCase):
    def test_independent_packets_with_identical_ids_keep_separate_graphs(self):
        fixture=ROOT/'work/schemas/expanded/fixtures/synthetic'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            for path in fixture.glob('*.jsonl'):
                rows=[json.loads(l) for l in path.read_text().splitlines()]
                merged=[namespace(path.stem,row,prefix) for prefix in ('job-a','job-b') for row in rows]
                (out/path.name).write_text(''.join(json.dumps(r)+'\n' for r in merged))
            errors,tables=validate(out)
            self.assertEqual(errors,[])
            self.assertEqual(len(tables['ballot_measures']),2)
            for result in tables['measure_results'].values():
                prefix=result['result_observation_id'].split('::')[0]
                self.assertTrue(result['measure_id'].startswith(prefix+'::'))

    def test_external_instruments_and_source_values_are_preserved(self):
        row={'event_id':'e','instrument':{'kind':'moratorium','id':'ca-existing-2026'},'claim_ids':['c'],
             'value':{'measure_id':'literal source value'},'subject':{'table':'claims','id':'c'}}
        before=copy.deepcopy(row);new=namespace('instrument_events',row,'job')
        self.assertEqual(row,before)
        self.assertEqual(new['instrument'],row['instrument'])
        self.assertEqual(new['value'],row['value'])
        self.assertEqual(new['subject']['id'],'job::c')
        row['instrument']['kind']='restriction'
        self.assertEqual(namespace('instrument_events',row,'job')['instrument']['id'],'job::ca-existing-2026')

    def test_result_value_method_and_revision_references_are_namespaced(self):
        row={'result_observation_id':'r2','measure_id':'m','source_document_id':'s','supersedes_id':'r1',
             'value_methods':{'reported_outcome':{'claim_ids':['c'],'method':'source_reported','note':None}}}
        new=namespace('measure_results',row,'job')
        self.assertEqual(new['supersedes_id'],'job::r1')
        self.assertEqual(new['value_methods']['reported_outcome']['claim_ids'],['job::c'])
