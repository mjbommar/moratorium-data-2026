#!/usr/bin/env python3
"""Version pending prompts to use source-qualified hosts; preserve started jobs.

Run while the dispatcher is stopped, then hand off to the returned queue. Research
worker processes remain alive and are never relaunched by this operation.
"""
import argparse
import hashlib
import json
from pathlib import Path


def revise(queue_path,runs,output):
    queue=json.loads(queue_path.read_text());changes=[]
    instruction='''\nSOURCE-HOST RECOVERY UPDATE (coordinator, 2026-11-05):
Before using a site: filter, consult work/audit/source-host-leads-2026-11-05.json
for each assigned moratorium_id. Read only records for your IDs with a small Python
lookup, not the whole registry. These are source-qualified retrieval leads, not
accepted current claims. Use the actual host/portal URL and jurisdiction context.
Never invent a government domain from the town's name. If no existing lead applies,
use an unfiltered query to discover the real official site before domain fencing;
record unresolved host identity rather than spending a query on a guessed domain.
Preserve original client text files: write OCR/conversion output to NEW private files
and record the originating attempt ID, body SHA256, tool/version, page coverage and
derived text SHA256 in derivations.json. Do not overwrite hashed retrieval text.
Schema/polarity validation must pass before returning expanded ledgers. Do not fill
an outcome direction when the counted outcome or yes-vote meaning remains unknown.
'''
    for job in queue['jobs']:
        if (runs/job['id']/'status.json').exists():continue
        original_spec=Path(job['spec']);spec=json.loads(original_spec.read_text())
        original_prompt=Path(spec['prompt_file']);before=original_prompt.read_bytes()
        prompt=original_prompt.with_name(original_prompt.stem+'.v2.txt')
        new_spec=original_spec.with_name(original_spec.stem+'.v2.json')
        after=before.decode()+instruction
        if prompt.exists() or new_spec.exists():raise ValueError('Refusing to overwrite prompt revision')
        prompt.write_text(after)
        spec['prompt_file']=str(prompt.resolve())
        spec['prior_spec']=str(original_spec.resolve())
        new_spec.write_text(json.dumps(spec,indent=2)+'\n')
        job['spec']=str(new_spec.resolve())
        changes.append({'job_id':job['id'],'old_spec':str(original_spec),'new_spec':str(new_spec),
            'old_prompt_sha256':hashlib.sha256(before).hexdigest(),
            'new_prompt_sha256':hashlib.sha256(after.encode()).hexdigest()})
    queue['prompt_revision']={'reason':'Use existing source hosts; preserve text hashes and explicit OCR derivations.',
                              'started_jobs_unchanged':True,'changes':changes}
    output.write_text(json.dumps(queue,indent=2)+'\n')
    return len(changes)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('queue',type=Path);p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print('Revised pending prompts:',revise(a.queue,a.runs,a.output))
