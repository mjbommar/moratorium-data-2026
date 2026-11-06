#!/usr/bin/env python3
"""Offline source revisit proposals using bc-web's native rate/interval policy."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from bc_web.recrawl import estimate_rate, interval_for
import bc_web.recrawl as native_policy
from archive_research_attempts import public_source_url


def plan(observations, now, event_due=None):
    grouped=defaultdict(list)
    for row in observations:
        if row['at']<=now:grouped[(row['url'],row['variant'])].append(row)
    output=[]
    for (url,variant),entries in sorted(grouped.items()):
        entries=sorted(entries,key=lambda r:(r['at'],r['attempt_id']))
        changes=sum(a['sha256']!=b['sha256'] for a,b in zip(entries,entries[1:]))
        mean=(entries[-1]['at']-entries[0]['at'])/(len(entries)-1) if len(entries)>1 else 0
        rate=estimate_rate(len(entries),changes,mean)
        interval=interval_for(rate)
        adaptive_due=entries[-1]['at']+interval
        deadline=(event_due or {}).get(url,(event_due or {}).get(public_source_url(url)))
        effective_due=min(adaptive_due,deadline) if deadline is not None else adaptive_due
        output.append(dict(url=url,variant=variant,visits=len(entries),detected_body_changes=changes,
                           mean_interval_s=mean,native_rate_per_s=rate,native_interval_s=interval,
                           adaptive_due=adaptive_due,event_review_due=deadline,effective_due=effective_due,
                           due_now=now>=effective_due,attempt_ids=[r['attempt_id'] for r in entries]))
        public_url=public_source_url(url)
        if public_url!=url:
            output[-1]['url']=public_url
            output[-1]['retrieval_url_sha256']=hashlib.sha256(url.encode()).hexdigest()
            output[-1]['retrieval_note']='Refresh through the owning portal; full retrieval URL remains in the private attempt ledger.'
    return output


def load_observations(directories):
    rows={};hashes={};excluded=[]
    for directory in directories:
        directory=directory.resolve();ledger=directory/'attempts.private.jsonl'
        raw=ledger.read_bytes();hashes[str(ledger)]=hashlib.sha256(raw).hexdigest()
        for line in raw.decode().splitlines():
            event=json.loads(line)
            if event.get('state')!='finished' or event.get('kind')!='fetch':continue
            if not event.get('ok'):
                excluded.append({'attempt_id':event['attempt_id'],'reason':'Failed acquisition is not an unchanged source observation.'});continue
            artifact=Path(event['artifact']).resolve()
            if not artifact.is_relative_to(directory):raise ValueError('Artifact outside owned directory')
            stem=artifact.with_suffix('');body=stem.with_suffix(stem.suffix+'.body')
            raw=body.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=event['body_sha256']:raise ValueError('Retained body drift')
            metadata=artifact.read_bytes();hashes[str(artifact)]=hashlib.sha256(metadata).hexdigest()
            payload=json.loads(metadata)
            variant=json.dumps({'tier':payload.get('tier'),'engine':payload.get('engine'),
                                'browser_controls':event.get('browser_controls')},sort_keys=True,separators=(',',':'))
            at=datetime.fromisoformat(event['finished_at'].replace('Z','+00:00'))
            if at.tzinfo is None:raise ValueError('Observation time needs timezone')
            row={'url':event['url'],'variant':variant,'at':at.timestamp(),
                 'attempt_id':event['attempt_id'],'sha256':event['body_sha256']}
            if row['attempt_id'] in rows and rows[row['attempt_id']]!=row:raise ValueError('Conflicting duplicate attempt')
            rows[row['attempt_id']]=row
    return list(rows.values()),hashes,excluded


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,action='append',required=True)
    p.add_argument('--as-of',type=datetime.fromisoformat,required=True,help='ISO timestamp with timezone')
    p.add_argument('--event-due',type=Path,help='Optional explicit URL-to-ISO-review-time mapping; operator priorities, not legal deadlines')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.as_of.tzinfo is None:p.error('--as-of needs timezone')
    observations,hashes,excluded=load_observations(args.directory)
    due={}
    if args.event_due:
        values=json.loads(args.event_due.read_text());hashes['event_due']=hashlib.sha256(args.event_due.read_bytes()).hexdigest()
        for url,value in values.items():
            stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
            if stamp.tzinfo is None:raise ValueError('Event review time needs timezone')
            due[url]=stamp.timestamp()
    report={'as_of':args.as_of.isoformat(),'input_sha256':hashes,'sources':plan(observations,args.as_of.timestamp(),due),
            'excluded_failed_attempts':excluded,
            'excluded_future_attempt_ids':[r['attempt_id'] for r in observations if r['at']>args.as_of.timestamp()],
            'native_policy_module_sha256':hashlib.sha256(Path(native_policy.__file__).read_bytes()).hexdigest(),
            'scope':'Advisory source revisit proposals using native bc-web estimator; no fetches, installed schedules, factual acceptance, legal deadlines or current-force updates. Event review priorities can shorten but never postpone the native due time. Body changes are not semantic/legal changes.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'sources':len(report['sources']),'due_now':sum(r['due_now'] for r in report['sources']),'failed_attempts_excluded':len(excluded)},indent=2))
