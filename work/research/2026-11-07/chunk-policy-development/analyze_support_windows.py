"""Measure joint support-window availability; never infers extraction quality."""
import argparse,hashlib,json
from pathlib import Path
from bc_content.chunk import chunk_text

ROOT=Path(__file__).resolve().parents[4]
CASES={
 'bp-f7852025abec20c9':('mandan-normative-layout.private.txt','56b5dde5b23ced1fa574d2e5ab9f4175d30fb39979cecf007585c90a69defd92'),
 'bp-e0efdc31b0b81e45':('cfa4727409bd4a8ba9e1f9aac3736126.private.txt','e820aa938e2dc1033ce6cc6fef2e6acf780abbd59a2869cda4f5137f09964514'),
}


def analyze(directory):
    selected=ROOT/'work/research/2026-11-06/compound-clause-source-review/selection.json'
    data=json.loads(selected.read_text());result=[]
    for case,(filename,expected) in CASES.items():
        source=directory/filename;raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
        text=raw.decode();policies={str(size):chunk_text(text,size=size,overlap=400) for size in (7000,42000)}
        clauses=[]
        for item in data['clauses']:
            if item['case_id']!=case:continue
            primary=item['source_spans']
            spans=primary+[[p['start'],p['end']] for p in item['supporting_spans']]
            assert all(type(a) is int and type(b) is int and 0<=a<b<=len(text) for a,b in spans)
            joint=lambda windows,points:any(all(c.start<=a and b<=c.end for a,b in points) for c in windows)
            clauses.append(dict(clause_id=item['clause_id'],primary_spans=primary,supporting_spans=spans[len(primary):],primary_joint_default=joint(policies['7000'],primary),all_support_joint_default=joint(policies['7000'],spans),all_support_joint_large=joint(policies['42000'],spans)))
        result.append(dict(case_id=case,text_sha256=expected,characters=len(text),policies={size:dict(size=int(size),overlap=400,chunks=[[c.start,c.end] for c in windows]) for size,windows in policies.items()},clauses=clauses))
    return dict(schema_version='source-support-window-analysis-1',selection_sha256=hashlib.sha256(selected.read_bytes()).hexdigest(),cases=result,limitations=['Both policies can read the complete text across all calls; this measures joint context within an individual prompt only.','Selected supporting spans are review inputs, not proof of a minimal necessary evidence set.','Two known development documents; no model extraction, measured quality improvement or unseen holdout.'],initial_hypothesis_correction='The Harwood moderate primary quote fits a default chunk. Its joint support set does not. The earlier split-list claim was corrected before provider execution.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source_directory',type=Path);a=p.parse_args();print(json.dumps(analyze(a.source_directory),indent=2))
