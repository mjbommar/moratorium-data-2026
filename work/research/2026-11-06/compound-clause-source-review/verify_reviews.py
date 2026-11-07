"""Verify retained reviewer artifacts and exact source bindings; never promotes."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'scripts'))
from condition_expression import validate_condition_clauses
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[4]

def verify(path):
    data=json.loads(path.read_text());counts=[]
    schema=json.loads((ROOT/'work/schemas/expanded/1.0.3.json').read_text())
    validator=Draft202012Validator({'$defs':schema['$defs'],**schema['$defs']['measure_provisions']['properties']['condition_clauses']})
    seen=set()
    for case in data['cases']:
        source=Path(case['source_path']);raw=source.read_bytes();text=raw.decode()
        assert hashlib.sha256(raw).hexdigest()==case['text_sha256'],'Source hash drift'
        for item in case['clauses']:
            assert item['clause_id'] not in seen;seen.add(item['clause_id'])
            clause=item['contract'];assert not validate_condition_clauses([clause]),item['clause_id']
            assert validator.is_valid([clause]),item['clause_id']
            assert item['source_spans']
            for start,end in item['source_spans']:
                assert type(start) is int and type(end) is int and 0<=start<end<=len(text)
                assert text[start:end]==clause['source_text'],item['clause_id']
            for span in item['supporting_spans']:
                assert type(span['start']) is int and type(span['end']) is int
                assert 0<=span['start']<span['end']<=len(text)
                assert span['role']
        counts.append(dict(case_id=case['case_id'],text_sha256=case['text_sha256'],clauses=len(case['clauses'])))
    return dict(artifact_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),cases=counts,source_quote_and_support_bounds_verified=True,condition_contracts_valid=True,scope='Mechanical source location/schema checks, not independent source entailment or legal interpretation.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('review',type=Path);a=p.parse_args();print(json.dumps(verify(a.review),indent=2))
