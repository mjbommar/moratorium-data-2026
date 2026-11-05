#!/usr/bin/env python3
"""Run an explicit frozen CLI-job queue at bounded concurrency; never auto-retry.

Terminal failures remain in the receipt for coordinator review. Missing process
handles are recorded as orphaned, not restarted. Results are not auto-promoted.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def alive(pid):
    try:
        os.kill(pid,0)
        return True
    except (ProcessLookupError,TypeError):
        return False


def dispatch(queue_path, runs, concurrency):
    queue=json.loads(queue_path.read_text())
    runs.mkdir(parents=True,exist_ok=True)
    receipt_path=runs/'dispatch.json'
    receipt={'queue':str(queue_path),'queue_model':queue['model'],'pid':os.getpid(),
             'started_at':dt.datetime.now(dt.timezone.utc).isoformat(),'state':'running','jobs':{}}
    # The queue itself is immutable after launch, and rerun uses existing statuses.
    while True:
        active=[];pending=[]
        for job in queue['jobs']:
            path=runs/job['id']/'status.json'
            if not path.exists():
                pending.append(job);continue
            status=json.loads(path.read_text())
            state=status['state']
            if state in ('running','starting'):
                if state=='starting' or alive(status.get('child_pid')) or alive(status.get('supervisor_pid')):
                    active.append(job)
                else:
                    state='orphaned_requires_review'
            receipt['jobs'][job['id']]={'state':state,'child_pid':status.get('child_pid'),
                                        'exit_code':status.get('exit_code')}
        for job in pending[:max(0,concurrency-len(active))]:
            launch=subprocess.run([sys.executable,str(Path(__file__).with_name('refresh_jobs.py')),
                'launch',job['spec'],'--runs',str(runs)],capture_output=True,text=True)
            if launch.returncode:
                receipt['state']='launch_failed';receipt['launch_error']=launch.stderr[-1000:]
                receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
                return 1
            print(launch.stdout.strip(),flush=True)
        receipt['updated_at']=dt.datetime.now(dt.timezone.utc).isoformat()
        receipt['counts']={'active':len(active),'pending':len(pending),
                           'terminal':len(queue['jobs'])-len(active)-len(pending)}
        if not active and not pending:
            receipt['state']='queue_terminal_pending_review'
            receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
            return 0
        temp=receipt_path.with_suffix('.tmp');temp.write_text(json.dumps(receipt,indent=2)+'\n');temp.replace(receipt_path)
        time.sleep(15)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('queue',type=Path);p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--concurrency',type=int,default=3)
    a=p.parse_args()
    if not 1<=a.concurrency<=3:p.error('concurrency must be1..3 for this run')
    raise SystemExit(dispatch(a.queue.resolve(),a.runs.resolve(),a.concurrency))
