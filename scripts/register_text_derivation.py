#!/usr/bin/env python3
"""Register a separately reviewed extraction without altering retrieval artifacts."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


def register(directory,attempt_id,text,method,pages,reviewer):
    directory=directory.resolve();text=text.resolve()
    if not text.is_relative_to(directory):raise ValueError('Derived text must stay inside job directory')
    events=[json.loads(x) for x in (directory/'attempts.private.jsonl').read_text().splitlines()]
    event=next(x for x in events if x['attempt_id']==attempt_id and x['state']=='finished' and x['kind']=='fetch')
    if not event.get('ok'):raise ValueError('Cannot derive evidence from a failed acquisition')
    # Use the exact client naming contract, independent of an OCR helper's names.
    stem=Path(event['artifact']).with_suffix('');body=stem.with_suffix(stem.suffix+'.body')
    if hashlib.sha256(body.read_bytes()).hexdigest()!=event['body_sha256']:raise ValueError('Original body drift')
    raw=text.read_bytes();raw.decode('utf-8')
    row={'attempt_id':attempt_id,'source_body_sha256':event['body_sha256'],
         'source_text_sha256':event['text_sha256'],'text_artifact':str(text),
         'derived_text_sha256':hashlib.sha256(raw).hexdigest(),'method':method,'pages':pages,
         'reviewer':reviewer,'review_status':'accepted_derivation',
         'reviewed_at':dt.datetime.now(dt.timezone.utc).isoformat(),
         'scope':'Extraction lineage only; no substantive claim or legal-effect acceptance.'}
    manifest=directory/'reviewed-derivations.json'
    old=json.loads(manifest.read_text()) if manifest.exists() else []
    if any(x['attempt_id']==attempt_id for x in old):raise ValueError('Derivation already registered; supersede explicitly')
    manifest.write_text(json.dumps(old+[row],indent=2)+'\n')
    return row


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path)
    p.add_argument('--attempt-id',required=True);p.add_argument('--text',type=Path,required=True)
    p.add_argument('--method',required=True);p.add_argument('--pages',nargs='+',type=int,required=True)
    p.add_argument('--reviewer',required=True)
    a=p.parse_args();print(json.dumps(register(a.directory,a.attempt_id,a.text,a.method,a.pages,a.reviewer),indent=2))
