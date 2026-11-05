#!/usr/bin/env python3
"""Apply explicit identity decisions to an append-only registry, never domain facts.

Plan files pin the previous registry hash. Dry-run is the default. IDs are opaque
UUIDs supplied by a reviewer, never inferred from names, dates or question text.
"""
import argparse
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from datetime import datetime
from uuid import UUID

TABLES={'jurisdictions','elections','ballot_measures','measure_provisions','measure_results',
        'local_restrictions','instrument_events','measure_instrument_links','source_documents',
        'claims','review_decisions','search_runs','search_attempts','search_sightings','coverage_observations'}
HASH=re.compile(r'^[0-9a-f]{64}$')

def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def require(ok,message):
    if not ok:raise ValueError(message)
def keys(obj,expected,where):
    require(isinstance(obj,dict) and set(obj)==set(expected),where+': wrong fields')
def nonempty(value):return isinstance(value,str) and bool(value.strip())
def opaque(value):
    try:return isinstance(value,str) and str(UUID(value))==value
    except (ValueError,TypeError,AttributeError):return False

def alias_key(alias):
    keys(alias,{'namespace','source_id','record_sha256'},'alias')
    require(nonempty(alias['namespace']) and nonempty(alias['source_id']) and
            isinstance(alias['record_sha256'],str) and HASH.fullmatch(alias['record_sha256']), 'Invalid alias fingerprint')
    return tuple(alias[k] for k in ('namespace','source_id','record_sha256'))

class Registry:
    def __init__(self,events=()):
        self.events={};self.entities={};self.aliases={}
        for event in events:self.add(event)

    def resolve(self,canonical_id):
        require(canonical_id in self.entities,'Unknown canonical ID '+str(canonical_id))
        entity=self.entities[canonical_id]
        if not entity['successors']:return {canonical_id}
        result=set()
        for target in entity['successors']:result.update(self.resolve(target))
        return result

    def resolve_alias(self,table,alias):
        key=(table,)+alias_key(alias)
        require(key in self.aliases,'Unknown alias')
        return self.resolve(self.aliases[key])

    def add(self,event):
        # Validate on a copy: a conflict must not leave half-applied in-memory state.
        trial=copy.deepcopy(self)
        trial._add(event)
        self.events,self.entities,self.aliases=trial.events,trial.entities,trial.aliases

    def _add(self,e):
        common={'schema_version','event_id','action','table','inputs','outputs','aliases',
                'assignments','reviewer','reviewed_at','rationale','evidence'}
        keys(e,common,'identity event')
        require(e['schema_version']=='1.0.0' and opaque(e['event_id']),'Invalid identity event version or ID')
        require(e['event_id'] not in self.events,'Duplicate event ID')
        table=e['table'];action=e['action'];inputs=e['inputs'];outputs=e['outputs']
        require(isinstance(table,str) and table in TABLES and isinstance(action,str) and
                action in {'allocate','alias','merge','split'},'Invalid table or action')
        require(isinstance(inputs,list) and isinstance(outputs,list) and
                all(opaque(x) for x in inputs+outputs),'Canonical IDs must be opaque UUIDs')
        require(len(set(inputs))==len(inputs) and len(set(outputs))==len(outputs),'Repeated input/output ID')
        require(isinstance(e['aliases'],list) and isinstance(e['assignments'],list),'Invalid alias lists')
        require(nonempty(e['reviewer']) and nonempty(e['rationale']),'Explicit reviewer and rationale required')
        try:stamp=datetime.fromisoformat(e['reviewed_at'].replace('Z','+00:00'))
        except (ValueError,TypeError,AttributeError):raise ValueError('Invalid review timestamp')
        require(stamp.tzinfo is not None,'Review timestamp must include timezone')
        require(isinstance(e['evidence'],list) and e['evidence'],'Identity evidence required')
        for ev in e['evidence']:
            keys(ev,{'url','body_sha256','locator'},'identity evidence')
            require(nonempty(ev['url']) and ev['url'].startswith(('https://','http://')) and
                    isinstance(ev['body_sha256'],str) and HASH.fullmatch(ev['body_sha256']) and
                    nonempty(ev['locator']),'Invalid identity evidence reference')
        for key in inputs:
            require(key in self.entities and self.entities[key]['table']==table and
                    not self.entities[key]['successors'],'Input must be active and in the same table')
        if action=='allocate':
            require(not inputs and len(outputs)==1 and not e['assignments'],'Allocation requires one new ID')
        elif action=='alias':
            require(len(inputs)==1 and outputs==inputs and not e['assignments'],'Alias requires one active ID')
        elif action=='merge':
            require(len(inputs)>=2 and len(outputs)==1 and outputs[0] in inputs and not e['assignments'],
                    'Merge requires active inputs and one of them as survivor')
        else:
            require(len(inputs)==1 and len(outputs)>=2 and not (set(inputs)&set(outputs)) and not e['aliases'],
                    'Split requires one active input and new outputs')
        if action in {'allocate','split'}:
            require(not any(x in self.entities for x in outputs),'Canonical ID collision or reuse')
            for key in outputs:self.entities[key]={'table':table,'successors':[]}
        if action=='merge':
            for key in inputs:
                if key!=outputs[0]:self.entities[key]['successors']=outputs[:]
        elif action=='split':
            affected={key for key,value in self.aliases.items() if self.resolve(value)==set(inputs)}
            assignments={}
            for item in e['assignments']:
                keys(item,{'alias','canonical_id'},'split assignment');key=(table,)+alias_key(item['alias'])
                require(key not in assignments and key in affected,'Duplicate or unrelated split alias')
                require(item['canonical_id'] is None or item['canonical_id'] in outputs,'Split alias target outside outputs')
                assignments[key]=item['canonical_id']
            require(set(assignments)==affected,'Every affected alias needs an explicit split disposition')
            self.entities[inputs[0]]['successors']=outputs[:]
            for key,target in assignments.items():
                # Null retains the retired ID, so lookup returns all possible successors.
                if target is not None:self.aliases[key]=target
        for alias in e['aliases']:
            key=(table,)+alias_key(alias)
            require(key not in self.aliases,'Alias collision; use reviewed merge/split history')
            self.aliases[key]=outputs[0]
        if action in {'allocate','alias'}:require(e['aliases'],'Allocation/alias requires a pinned observation')
        self.events[e['event_id']]=copy.deepcopy(e)


def read_events(raw):
    return [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]

def apply_plan(path,plan,apply=False):
    keys(plan,{'schema_version','expected_sha256','events'},'identity plan')
    require(plan['schema_version']=='1.0.0' and isinstance(plan['events'],list) and plan['events'],'Invalid or empty identity plan')
    require(all(isinstance(e,dict) and opaque(e.get('event_id')) for e in plan['events']),
            'Every planned event needs an opaque event ID')
    expected=plan['expected_sha256']
    require(expected is None or isinstance(expected,str) and HASH.fullmatch(expected),'Invalid expected hash')
    # The same lock is used across replacements; never lock the replaceable inode.
    if apply:
        path.parent.mkdir(parents=True,exist_ok=True)
        lock=path.with_suffix(path.suffix+'.lock').open('a')
        fcntl.flock(lock,fcntl.LOCK_EX)
    else:lock=None
    try:
        raw=path.read_bytes() if path.exists() else b'';current=digest(raw) if path.exists() else None
        registry=Registry(read_events(raw))
        if current!=expected:
            same=all(isinstance(e,dict) and registry.events.get(e.get('event_id'))==e for e in plan['events'])
            require(same,'Registry changed since plan review; regenerate against current hash')
            return {'state':'already_applied','sha256':current,'events_added':0}
        for event in plan['events']:registry.add(event)
        suffix=''.join(encode(e)+'\n' for e in plan['events']).encode()
        require(not raw or raw.endswith(b'\n'),'Registry must end with a newline')
        result=raw+suffix
        if apply:
            fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
            try:
                with os.fdopen(fd,'wb') as f:f.write(result);f.flush();os.fsync(f.fileno())
                os.replace(tmp,path)
                directory=os.open(path.parent,os.O_DIRECTORY)
                try:os.fsync(directory)
                finally:os.close(directory)
            finally:
                if os.path.exists(tmp):os.unlink(tmp)
        return {'state':'applied' if apply else 'dry_run','sha256':digest(result),'events_added':len(plan['events'])}
    finally:
        if lock is not None:lock.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--registry',type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan',type=Path);mode.add_argument('--check',action='store_true')
    p.add_argument('--apply',action='store_true');a=p.parse_args()
    if a.check and a.apply:p.error('--apply requires --plan')
    try:
        if a.check:
            raw=a.registry.read_bytes();registry=Registry(read_events(raw))
            require(not raw or raw.endswith(b'\n'),'Registry must end with a newline')
            print(json.dumps({'state':'valid','sha256':digest(raw),'events':len(registry.events),
                              'identities':len(registry.entities),'aliases':len(registry.aliases)},indent=2))
        else:print(json.dumps(apply_plan(a.registry,json.loads(a.plan.read_text()),a.apply),indent=2))
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as exc:p.exit(1,str(exc)+'\n')
