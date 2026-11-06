#!/usr/bin/env python3
"""Check the explicitly frozen retrospective section-11 pilot; never publish facts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from expanded_data import IDS, validate, certified_result_count
from expanded_promotion import fingerprint, read_snapshot

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'peru','wells','bloomington','piqua','grove-city','harwood','wilmington','el-dorado',
            'earlier-election','december-pending','council-only','portal-failure',
            'failed-qualification','amended-certification','mixed-polarity','predecessor-replacement','december-shape'}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value,message):
    if not value: raise ValueError(message)
def row_sha(row): return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def local(root,value):
    path=(root/value).resolve(strict=True)
    require(path.is_relative_to(root.resolve()),'Fixture escapes repository')
    return path


def audit(manifest_path, root=ROOT):
    manifest=json.loads(manifest_path.read_text())
    require(manifest['schema_version']=='pilot-contract-review-1','Unsupported pilot manifest')
    cases=manifest['cases'];require(len(cases)==len(REQUIRED) and {c['case_id'] for c in cases}==REQUIRED,'Incomplete/duplicate pilot cases')
    require('Retrospective' in manifest['chronology'] and 'not' in manifest['chronology'].lower(),'Pilot chronology must retain prior-tuning limitation')
    require(sha(root/'work/schemas/expanded/1.0.0.json')==manifest['schema_sha256'],'Schema drift')
    snapshot=local(root,manifest['snapshot'])
    require(fingerprint(read_snapshot(snapshot))==manifest['snapshot_sha256'],'Snapshot drift')
    for name,digest in manifest['table_sha256'].items():require(sha(snapshot/name)==digest,'Snapshot table drift')
    references={}
    for kind,fixture in manifest['legacy_reference_fixtures'].items():
        path=local(root,fixture['path']);require(sha(path)==fixture['sha256'],'Frozen legacy reference drift')
        references[kind]=path
    # Historical fixtures must survive legitimate future inventory updates.
    # Original full-CSV hashes remain provenance; immutable ID-only fixtures
    # supply validation context, rather than today's changing inventory rows.
    errors,rows=validate(snapshot,references['moratoria'],references['state_actions'])
    require(not errors,'Frozen canonical contracts invalid: '+str(errors[:3]))
    reports=[];measures=set();assertions=0;source_files={}
    for case in cases:
        require(case['limits'].strip(),'Missing case qualification')
        for evidence in case['evidence_files']:
            path=local(root,evidence['path']);require(sha(path)==evidence['sha256'],'Review evidence drift: '+evidence['path']);source_files[evidence['path']]=evidence['sha256']
        for table,records in case['records'].items():
            require(table in IDS,'Unknown pilot table')
            for ident,digest in records.items():
                require(ident in rows[table] and row_sha(rows[table][ident])==digest,'Frozen case record drift')
                if table=='ballot_measures':measures.add(ident)
        for assertion in case['assertions']:
            value=rows[assertion['table']][assertion['id']]
            for key in assertion['path']:value=value[key]
            require(value==assertion['equals'],'Case expectation differs: '+case['case_id']+'/'+str(assertion['path']));assertions+=1
        if case['kind']=='synthetic_schema_example':
            fixture=local(root,case['fixture'])
            require({p.name for p in fixture.iterdir() if p.is_file()}==set(case['fixture_sha256']),'Synthetic fixture membership drift')
            for name,digest in case['fixture_sha256'].items():require(sha(fixture/name)==digest,'Synthetic fixture drift')
            errors,example=validate(fixture,fixture/'legacy.csv' if (fixture/'legacy.csv').exists() else None)
            require(not errors,'Synthetic example invalid: '+case['case_id']+': '+str(errors[:3]))
            if case['case_id']=='amended-certification':require(len(example['measure_results'])==2 and certified_result_count(example)==1,'Amended result double-counted')
            if case['case_id'] in ('failed-qualification','december-shape'):require(not example['measure_results'],'Unvoted synthetic case acquired results')
            if case['case_id']=='predecessor-replacement':require(len(example['instrument_events'])==2 and len(example['local_restrictions'])==1,'Distinct predecessor/replacement identities lost')
        else:require(bool(case['evidence_files']),'Source-backed case lacks reviewed source metadata')
        reports.append({'case_id':case['case_id'],'kind':case['kind'],'checked_record_count':sum(len(v) for v in case['records'].values()),'limits':case['limits']})
    wilm=next(c for c in cases if c['case_id']=='wilmington')['records']['ballot_measures']
    require(len(wilm)==4 and len({rows['ballot_measures'][m]['election_id'] for m in wilm})==1
            and len({rows['ballot_measures'][m]['jurisdiction_id'] for m in wilm})==1,'Wilmington measure/election grain drift')
    months=Counter(rows['elections'][rows['ballot_measures'][m]['election_id']]['election_date']['earliest'][:7] for m in measures)
    require(months=={'2026-11':11,'2026-03':1},'Election-cohort denominator drift')
    return {'schema_version':'pilot-contract-validation-1','manifest_sha256':sha(manifest_path),'snapshot_sha256':manifest['snapshot_sha256'],
            'cases':reports,'case_kind_counts':dict(Counter(c['kind'] for c in cases)),'unique_review_evidence_files':len(source_files),
            'explicit_field_expectations':assertions,'selected_canonical_measures':len(measures),'selected_measure_months':dict(months),
            'quality_gate_status':'not_assessed','chronology':manifest['chronology'],
            'calibration_findings':manifest.get('calibration_findings',[]),
            'validation_errors':0,'scope':'Retrospective schema/example review and pinned-source-receipt integrity. Not a discovery/extraction accuracy metric, new legal acceptance, independent holdout, source reacquisition or P4 quality-gate completion.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=audit(args.manifest)
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    else:print(text,end='')
