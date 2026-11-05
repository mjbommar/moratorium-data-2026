#!/usr/bin/env python3
"""Read-only census of job returns, schema/ID coverage and located evidence.

This is a mechanical pre-review gate, never a legal acceptance or promotion tool.
Client text and explicitly pinned reusable evidence are verified before locating
quotes; new OCR requires a separate explicit derivation record, not an untracked
text file with a plausible name.
"""
import argparse
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load_lines(path):
    if not path.exists(): return []
    rows=[]
    for line in path.read_text().splitlines():
        if line.strip(): rows.append(json.loads(line))
    return rows


def evidence_index(directory):
    index=defaultdict(list); issues=[]; totals=Counter()
    derivations_path=directory/'reviewed-derivations.json'
    derivations={x['attempt_id']:x for x in json.loads(derivations_path.read_text())} if derivations_path.exists() else {}
    for e in load_lines(directory/'attempts.private.jsonl'):
        if e['state']=='reserved': totals[e['kind']]+=1
        if e['state']!='finished' or e['kind']!='fetch' or not e.get('ok'): continue
        artifact=Path(e['artifact']).resolve()
        if not artifact.is_relative_to(directory.resolve()):
            issues.append({'attempt_id':e['attempt_id'],'error':'artifact outside owned directory'});continue
        stem=artifact.with_suffix('')
        body=stem.with_suffix(stem.suffix+'.body')
        text=stem.with_suffix(stem.suffix+'.txt')
        if not body.exists() or not text.exists():
            issues.append({'attempt_id':e['attempt_id'],'error':'missing body/text'});continue
        raw,txt=body.read_bytes(),text.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=e['body_sha256']:
            issues.append({'attempt_id':e['attempt_id'],'error':'body/text hash drift; explicit derivation required'});continue
        derivation=derivations.get(e['attempt_id'])
        if derivation:
            derived=Path(derivation['text_artifact']).resolve()
            if (not derived.is_relative_to(directory.resolve()) or derivation['review_status']!='accepted_derivation'
                or derivation['source_body_sha256']!=e['body_sha256']):
                issues.append({'attempt_id':e['attempt_id'],'error':'invalid derivation lineage'});continue
            txt=derived.read_bytes();text=derived
            if hashlib.sha256(txt).hexdigest()!=derivation['derived_text_sha256']:
                issues.append({'attempt_id':e['attempt_id'],'error':'derived text hash drift'});continue
        elif hashlib.sha256(txt).hexdigest()!=e['text_sha256']:
            issues.append({'attempt_id':e['attempt_id'],'error':'text hash drift; explicit derivation required'});continue
        entry={'attempt_id':e['attempt_id'],'text':txt.decode('utf-8'),'text_artifact':str(text),
               'body_artifact':str(body),
               'body_sha256':e['body_sha256'],'text_sha256':hashlib.sha256(txt).hexdigest()}
        for url in set([e['url'],e.get('final_url') or e['url']]):index[url].append(entry)
    return index,issues,dict(totals)


def audit_expanded_evidence(records, index, visual_reviews=None):
    """Match each declared source version and quote to retained, verified bytes.

    This deliberately does not accept a URL alone as proof of a source version.
    Free-form worker span labels are retained but are not trusted as offsets;
    locate_quote independently establishes a location in the verified text.
    """
    from bc_core.text import locate_quote
    issues=[]; verified={}; proofs=[]
    def values(table):
        rows=records.get(table, {})
        return rows.values() if isinstance(rows,dict) else rows
    for source in values('source_documents'):
        sid=source['source_document_id']
        matches=[v for v in index.get(source['url'], [])
                 if v['body_sha256']==source['body_sha256']
                 and (source['text_sha256'] is None or v['text_sha256']==source['text_sha256'])]
        if not matches:
            issues.append({'source_document_id':sid,'error':'declared source version not found in verified client evidence'})
        else:
            # A retained scanned payload can legitimately have no declared text
            # version. Its body is accounted for, but cannot prove a text quote.
            verified[sid]=matches if source['text_sha256'] is not None else []
    for claim in values('claims'):
        sid=claim['source_document_id'];quote=claim['quote']
        location=None; artifact=None; decoding=None
        for version in verified.get(sid, []):
            location=locate_quote(version['text'], quote)
            if location is not None:
                artifact=version['text_artifact'];decoding=version.get('text_decoding','exact UTF-8 extraction');break
        visual=False
        if visual_reviews and claim['claim_id'] in visual_reviews:
            from visual_claim_review import verify
            source=next(s for s in values('source_documents') if s['source_document_id']==sid)
            visual=verify(claim,source,index,visual_reviews[claim['claim_id']])
        proofs.append({'claim_id':claim['claim_id'],'source_document_id':sid,
                       'quote_located':location is not None,
                       'visual_verified':visual,'evidence_verified':location is not None or visual,
                       'verified_span':location,'verified_text_artifact':artifact,
                       'verified_text_decoding':decoding})
    return issues,proofs


def pinned_evidence_index(base, manifest, manifest_sha256, sources):
    """Resolve reusable source versions only through a pinned artifact manifest.

    A worker's copied source metadata is not proof that the original exists.
    Rehash both body and text at their retained paths before returning a version.
    """
    raw=manifest.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=manifest_sha256:
        raise ValueError('Reusable evidence manifest drift')
    paths=defaultdict(list)
    for name,digest in json.loads(raw).items():
        path=base/name
        if not path.absolute().is_relative_to(base.absolute()) or '..' in Path(name).parts:
            raise ValueError('Reusable artifact outside manifest base')
        paths[digest].append(path)
    index=defaultdict(list);issues=[]
    def resolve(digest):
        for path in paths.get(digest,[]):
            if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest:return path
        return None
    def resolve_text(digest):
        direct=resolve(digest)
        if direct is not None:return direct,direct.read_bytes().decode('utf-8'),'pinned UTF-8 text'
        # The original pilot hashes Python read_text() output, including universal
        # newline decoding of HTML fallback artifacts. Reproduce that documented
        # transform only after verifying the exact original file hash.
        for expected,candidates in paths.items():
            for path in candidates:
                if path.suffix not in ('.txt','.html') or not path.is_file():continue
                raw=path.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=expected:continue
                text=path.read_text(encoding='utf-8')
                if hashlib.sha256(text.encode('utf-8')).hexdigest()==digest:
                    return path,text,'pinned UTF-8 text with universal newline decoding'
        return None,None,None
    for source in sources:
        body=resolve(source['body_sha256']);text,decoded,method=resolve_text(source['text_sha256'])
        if body is None or text is None:
            issues.append({'source_document_id':source['source_document_id'],
                           'error':'Pinned reusable body/text missing or drifted'});continue
        index[source['url']].append({'attempt_id':'reused:'+source['source_document_id'],
            'body_sha256':source['body_sha256'],'text_sha256':source['text_sha256'],
            'text':decoded,'text_artifact':str(text),'text_decoding':method,
            'body_artifact':str(body),'evidence_origin':'pinned earlier pilot'})
    return index,issues


def seed_assignments(path):
    seeds=load_lines(path); result={}
    for state in sorted({s['state_abbrev_reported'] for s in seeds}):
        rows=[s for s in seeds if s['state_abbrev_reported']==state]
        for i in range(0,len(rows),4):
            result[f'ballot-{state.lower()}-{i//4+1:03}']=[s['seed_id'] for s in rows[i:i+4]]
    return result


def candidate_id_coverage(expected,candidates):
    returned=[c['seed_id'] for c in candidates]
    return {'missing_seed_ids':sorted(set(expected)-set(returned)),
            'extra_seed_ids':sorted(set(returned)-set(expected)),
            'duplicate_seed_ids':sorted(k for k,v in Counter(returned).items() if v>1)}


def audit(queue_path,runs):
    from jsonschema import Draft202012Validator,FormatChecker
    from bc_core.text import locate_quote
    from expanded_data import validate as expanded_validate
    queue=json.loads(queue_path.read_text());jobs=[]
    from normalize_ballot_pilot import MANIFEST_SHA256
    pilot=ROOT/'work/research/2026-11-05'
    reused,reuse_issues=pinned_evidence_index(pilot,pilot/'normalized-pilot/expected-inputs.json',
        MANIFEST_SHA256,load_lines(pilot/'normalized-pilot/source_documents.jsonl'))
    # Ballot recovery workers may reuse earlier workers' retained observations.
    # Shared availability does not erase integrity issues in the owning packet.
    for job in queue['jobs']:
        if not job['id'].startswith(('ballot-','recovery-ballot-')):continue
        status_path=runs/job['id']/'status.json'
        if not status_path.exists() or json.loads(status_path.read_text())['state'] not in ('finished','failed'):continue
        spec=json.loads(Path(job['spec']).read_text())
        shared,_,_=evidence_index(Path(spec['owned_paths'][0]))
        for url,versions in shared.items():reused[url].extend(versions)
    visual_registry=ROOT/'work/audit/visual-claim-reviews-2026-11-05.json'
    visual_reviews=defaultdict(dict)
    for rel in json.loads(visual_registry.read_text()) if visual_registry.exists() else []:
        review=json.loads((ROOT/rel).read_text())
        visual_reviews[review['job_id']][review['claim_id']]=review
    ballot_assignments=seed_assignments(ROOT/'work/research/2026-11-05/ballot-discovery/ballot-seeds.jsonl')
    schemas={name:json.loads((ROOT/'work/schemas'/file).read_text()) for name,file in
             [('inventory','research_decision.schema.json'),('state_policy','legislation_decision.schema.json')]}
    for job in queue['jobs']:
        status_path=runs/job['id']/'status.json'
        if not status_path.exists():continue
        status=json.loads(status_path.read_text())
        row={'job_id':job['id'],'cli_state':status['state'],'exit_code':status.get('exit_code'),
             'assigned_count':job['records'],'checks':[]}
        if status['state'] not in ('finished','failed'):
            row['child_pid']=status.get('child_pid');jobs.append(row);continue
        spec=json.loads(Path(job['spec']).read_text());directory=Path(spec['owned_paths'][0])
        row['directory']=str(directory)
        idx,issues,counts=evidence_index(directory)
        row.update(attempt_counts=counts,evidence_integrity_issues=issues,
                   successful_source_versions=len({v['attempt_id'] for versions in idx.values() for v in versions}))
        for url,versions in reused.items():idx[url].extend(versions)
        # A URL and final URL can point to the same observation; this is diagnostic,
        # never a denominator of independent supporting sources.
        table=spec.get('table')
        if table in schemas:
            answer=directory/'answers.json'
            if not answer.exists(): row['checks'].append('missing answers.json');jobs.append(row);continue
            try: data=json.loads(answer.read_text())
            except json.JSONDecodeError: row['checks'].append('invalid answer JSON');jobs.append(row);continue
            validator=Draft202012Validator(schemas[table],format_checker=FormatChecker())
            row['schema_errors']=[f"{'/'.join(map(str,e.absolute_path))}: {e.message}" for e in validator.iter_errors(data)]
            packet=json.loads((directory/'packet.json').read_text())
            if table=='inventory':
                expected={r['moratorium_id'] for r in packet};key='moratorium_id'
            else:
                expected={r['state_abbrev']+':'+r['bill'] for r in packet};key='bill_key'
            decisions=data.get('decisions',[]);returned=[r.get(key) for r in decisions]
            row['missing_ids']=sorted(expected-set(returned));row['extra_ids']=sorted(set(returned)-expected)
            row['duplicate_ids']=[k for k,v in Counter(returned).items() if v>1]
            row['outcomes']=dict(Counter(x.get('outcome','missing') for x in decisions))
            proofs=[]
            for d in decisions:
                for ev in d.get('evidence',[]):
                    quote=ev.get('quote') or ''; versions=idx.get(ev.get('url'),[])
                    proof={'record_id':d.get(key),'url':ev.get('url'),'quote_located':False,
                           'substantive_quote':len(quote.strip())>=12}
                    for version in versions:
                        span=locate_quote(version['text'],quote)
                        if span:
                            proof.update(quote_located=True,span=list(span),
                                text_artifact=version['text_artifact'],attempt_id=version['attempt_id'],
                                body_sha256=version['body_sha256'],text_sha256=version['text_sha256']);break
                    proofs.append(proof)
            row['evidence_proofs']=proofs
            row['mechanically_review_ready']=not (row['schema_errors'] or row['missing_ids'] or
                row['extra_ids'] or row['duplicate_ids'] or issues or any(not x['quote_located'] for x in proofs))
        elif job['id'].startswith(('ballot-','recovery-ballot-')):
            expected=spec['frozen_seed_ids'] if job['id'].startswith('recovery-ballot-') else ballot_assignments[job['id']]
            if job['id'].startswith('recovery-ballot-'):
                registry=ROOT/'work/research/2026-11-05/ballot-discovery/additional-ballot-leads.jsonl'
                if hashlib.sha256(registry.read_bytes()).hexdigest()!=spec['seed_registry_sha256']:
                    row['checks'].append('omission seed registry drift')
            candidate_path=directory/'candidates.json'
            coverage=candidate_id_coverage(expected,json.loads(candidate_path.read_text())) if candidate_path.exists() else candidate_id_coverage(expected,[])
            row['seed_coverage']=coverage
            if len(expected)!=job['records']:row['checks'].append('frozen seed assignment count disagrees with queue')
            path=directory/'expanded'
            if path.exists():
                try:
                    errors,records=expanded_validate(path,ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv')
                    row['expanded_schema_errors']=errors;row['expanded_counts']={k:len(v) for k,v in records.items()}
                    source_issues,proofs=audit_expanded_evidence(records,idx,visual_reviews.get(job['id']))
                    row['expanded_source_issues']=source_issues
                    row['expanded_evidence_proofs']=proofs
                    row['mechanically_review_ready']=not (errors or source_issues or issues or row['checks'] or any(coverage.values())
                        or any(not p['evidence_verified'] for p in proofs))
                except Exception as e:row['checks'].append('expanded validator: '+type(e).__name__+': '+str(e)[:200])
            else:row['checks'].append('missing expanded ledgers')
        jobs.append(row)
    return {'observed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'queue':str(queue_path),
            'job_states':dict(Counter(x['cli_state'] for x in jobs)),
            'not_started_jobs':len(queue['jobs'])-len(jobs),'jobs':jobs,
            'reusable_evidence_issues':reuse_issues,
            'scope':'Mechanical pre-review only. No source authority, legal-effect, field-support or substantive acceptance asserted.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--queue',type=Path,required=True);p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=audit(a.queue,a.runs);a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'states':r['job_states'],'not_started_jobs':r['not_started_jobs'],
                     'mechanically_review_ready':sum(x.get('mechanically_review_ready',False) for x in r['jobs'])},indent=2))
