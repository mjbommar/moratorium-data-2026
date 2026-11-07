#!/usr/bin/env python3
"""Event-validity contract for explicitly selected publication profile 1.0.2.

This checks review relationships, not source entailment, rights or legal force.
The publication adapter must still verify every source, identity and immutable
predecessor. No missing decision is interpreted as acceptance.
"""
from collections import defaultdict
from datetime import datetime
import json


EVENT_FIELDS = ('instrument','action','occurrence','observed_at','published_at')


def require(ok,message):
    if not ok: raise ValueError(message)


def instant(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    require(result.tzinfo is not None,'Review timestamp requires timezone')
    return result


class Decisions:
    """One connected, time-ordered chain for each exact target and scope."""
    def __init__(self, records):
        self.records=records;self.chains={}
        groups=defaultdict(dict)
        for key,d in records.items():
            require(key==d['decision_id'],'Decision identity differs from key')
            require(d['reviewer'].strip() and d['rationale'].strip() and d['method'].strip(),'Explicit review attribution required')
            require(d['disposition'] in ('accepted','rejected','unresolved'),'Unknown review disposition')
            group=(d['target']['table'],d['target']['id'],d['scope'])
            groups[group][key]=d
        for group,items in groups.items():
            roots=[];child={}
            for key,d in items.items():
                parent=d['supersedes_id'];instant(d['decided_at'])
                if parent is None: roots.append(key);continue
                require(parent in items,'Decision predecessor missing or changes target/scope')
                require(parent not in child,'Branched decision history')
                require(instant(items[parent]['decided_at'])<instant(d['decided_at']),'Decision predecessor must be strictly earlier')
                child[parent]=key
            require(len(roots)==1,'Decision history requires exactly one root')
            chain=[];cursor=roots[0]
            while cursor is not None:
                require(cursor not in chain,'Cyclic decision history')
                chain.append(cursor);cursor=child.get(cursor)
            require(len(chain)==len(items),'Disconnected decision history')
            self.chains[group]=[items[key] for key in chain]

    def chain(self,target,scope):
        return self.chains.get((target['table'],target['id'],scope),[])

    def head(self,target,scope):
        chain=self.chain(target,scope)
        return chain[-1] if chain else None

    def at(self,target,scope,when):
        # Equal timestamps on different scopes can be one atomic review batch.
        # Equal timestamps within the same chain are rejected above.
        found=[d for d in self.chain(target,scope) if instant(d['decided_at'])<=when]
        return found[-1] if found else None


def same(left,right):
    return json.dumps(left,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(right,sort_keys=True,separators=(',',':'),allow_nan=False)


def event_target(key): return {'table':'instrument_events','id':key}
def claim_target(key): return {'table':'claims','id':key}


def exact_claims(event, claims):
    expected={f:event[f] for f in ('instrument','action','occurrence')}
    return {cid for cid in event['claim_ids'] if cid in claims and
            claims[cid]['subject']==event_target(event['event_id']) and
            claims[cid]['predicate']=='instrument_event' and same(claims[cid]['value'],expected)}


def accepted_claim(index,claim,when=None):
    d=(index.at(claim_target(claim['claim_id']),claim['predicate'],when) if when else
       index.head(claim_target(claim['claim_id']),claim['predicate']))
    if d is not None and d['disposition']=='accepted':
        require(d['claim_ids']==[claim['claim_id']],'Claim acceptance must cite its exact source claim')
        return True
    return False


def accepted_event_evidence(event, claims, index, when=None):
    exact={cid for cid in exact_claims(event,claims) if accepted_claim(index,claims[cid],when)}
    require(exact,'Current event lacks accepted exact event claim')
    for field in EVENT_FIELDS:
        d=index.at(event_target(event['event_id']),field,when) if when else index.head(event_target(event['event_id']),field)
        if event.get(field) is None: continue
        require(d and d['disposition']=='accepted','Current event lacks field acceptance: '+field)
        require(d['claim_ids'] and all(cid in claims and accepted_claim(index,claims[cid],when) for cid in d['claim_ids']),'Field support lapsed at event review time')
        if field in ('instrument','action','occurrence'):
            require(bool(exact.intersection(d['claim_ids'])),'Current event field must cite exact claim: '+field)
    return exact


def inspect(rows):
    """Return status/current/correction views only if the entire contract passes."""
    events=rows['instrument_events'];claims=rows['claims']
    index=Decisions(rows['review_decisions']);statuses={};validities={}
    for key,event in events.items():
        require(key==event['event_id'],'Event identity differs from key')
        require(exact_claims(event,claims),'Retained event lacks original exact claim')
        validity=index.head(event_target(key),'event_validity')
        require(validity and validity['disposition'] in ('accepted','rejected'),'Event requires explicit accepted/rejected validity decision')
        validities[key]=validity
        if validity['disposition']=='accepted':
            exact=accepted_event_evidence(event,claims,index)
            require(bool(exact.intersection(validity['claim_ids'])),'Validity acceptance must cite accepted exact claim')
        else:
            for field in EVENT_FIELDS:
                d=index.head(event_target(key),field)
                if event.get(field) is None and d is None: continue
                require(d and d['disposition']=='rejected','Withdrawn event requires rejected field decision: '+field)
            basis=[]
            for cid in validity['claim_ids']:
                c=claims.get(cid,{})
                if (c.get('subject')==event_target(key) and c.get('predicate')=='event_validity'
                    and isinstance(c.get('value'),dict) and set(c['value'])=={'disposition','basis'}
                    and c['value']['disposition']=='rejected' and isinstance(c['value']['basis'],str)
                    and c['value']['basis'].strip() and accepted_claim(index,c)):
                    basis.append(cid)
            require(basis,'Withdrawal requires accepted, event-scoped validity-basis evidence')
        statuses[key]={'event_id':key,'review_state':'accepted' if validity['disposition']=='accepted' else 'withdrawn',
                       'decision_id':validity['decision_id'],'decided_at':validity['decided_at'],'replacement_event_ids':[]}
    # Superseded event decisions keep support at their decision time. A later
    # claim rejection cannot retroactively erase a formerly supported review.
    for d in index.records.values():
        if d['target']['table']!='instrument_events': continue
        require(d['target']['id'] in events,'Decision targets missing event')
        for cid in d['claim_ids']:
            require(cid in claims and claims[cid]['subject']==d['target'],'Event decision claim subject differs')
        if d['disposition']!='accepted': continue
        require(d['claim_ids'],'Accepted event decision needs evidence')
        live=index.head(d['target'],d['scope'])['decision_id']==d['decision_id']
        if d['scope'] in ('instrument','action','occurrence'):
            exact={cid for cid in exact_claims(events[d['target']['id']],claims) if accepted_claim(index,claims[cid],instant(d['decided_at']))}
            require(bool(exact.intersection(d['claim_ids'])),'Historical factual field lacks exact support at its own review time')
        for cid in d['claim_ids']:
            require(accepted_claim(index,claims[cid],instant(d['decided_at'])) and
                    (not live or accepted_claim(index,claims[cid])),
                    'Event decision lacks current or historical claim acceptance')
    # Validate each validity transition at its own time, including superseded
    # withdrawals. Later evidence cannot retroactively justify a recorded review.
    for key,event in events.items():
        for d in index.chain(event_target(key),'event_validity'):
            when=instant(d['decided_at'])
            if d['disposition']=='accepted':
                exact={cid for cid in exact_claims(event,claims) if accepted_claim(index,claims[cid],when)}
                require(bool(exact.intersection(d['claim_ids'])),'Historical validity lacks exact support at review time')
                for field in EVENT_FIELDS:
                    if event.get(field) is None:continue
                    f=index.at(event_target(key),field,when)
                    require(f and f['disposition']=='accepted','Historical validity lacks accepted field at review time')
                    if field in ('instrument','action','occurrence'):
                        require(bool(exact.intersection(f['claim_ids'])),'Historical event field must cite exact support')
            elif d['disposition']=='rejected':
                for field in EVENT_FIELDS:
                    if event.get(field) is None:continue
                    f=index.at(event_target(key),field,when)
                    require(f and f['disposition']=='rejected','Historical withdrawal has dangling field acceptance')
                basis=[claims[cid] for cid in d['claim_ids'] if cid in claims]
                require(any(c['subject']==event_target(key) and c['predicate']=='event_validity'
                            and isinstance(c['value'],dict) and set(c['value'])=={'disposition','basis'}
                            and c['value']['disposition']=='rejected' and isinstance(c['value']['basis'],str)
                            and c['value']['basis'].strip() and accepted_claim(index,c,when) for c in basis),
                        'Historical withdrawal lacks accepted basis at review time')
            else:
                raise ValueError('Published event validity history cannot contain unresolved transitions')
    # Check the combined timeline, not only event-validity transition instants.
    # Every relevant same-instant batch is evaluated atomically.
    for key,event in events.items():
        times={instant(d['decided_at']) for d in index.records.values()
               if d['target']==event_target(key) or
               (d['target']['table']=='claims' and d['target']['id'] in claims and
                claims[d['target']['id']]['subject']==event_target(key))}
        for when in sorted(times):
            validity=index.at(event_target(key),'event_validity',when)
            if validity is None:continue  # Legacy baseline is separately predecessor-bound.
            if validity['disposition']=='accepted':
                exact=accepted_event_evidence(event,claims,index,when)
                require(bool(exact.intersection(validity['claim_ids'])),'Validity support lapsed between transitions')
            else:
                for field in EVENT_FIELDS:
                    f=index.at(event_target(key),field,when)
                    if event.get(field) is None and f is None:continue
                    require(f and f['disposition']=='rejected','Withdrawn event has intermediate field acceptance')
    # An explicitly typed claim can record one-to-many correction relationships.
    # It is not an instrument merge or inference about current legal force.
    edges=defaultdict(set)
    for c in claims.values():
        if c['predicate']!='event_correction':continue
        require(c['subject']['table']=='instrument_events' and c['subject']['id'] in events,'Correction subject must be retained event')
        old=c['subject']['id'];value=c['value']
        require(isinstance(value,dict) and set(value)=={'replacement_event_ids'},'Wrong correction value fields')
        targets=value['replacement_event_ids']
        require(isinstance(targets,list) and targets and all(isinstance(t,str) for t in targets)
                and len(set(targets))==len(targets),'Unique replacement event IDs required')
        require(all(t in events and t!=old for t in targets),'Missing or self replacement event')
        for decision in index.chain(claim_target(c['claim_id']),'event_correction'):
            if decision['disposition']!='accepted':continue
            require(decision['claim_ids']==[c['claim_id']],'Correction acceptance must cite its exact source claim')
            when=instant(decision['decided_at'])
            original=index.at(event_target(old),'event_validity',when)
            require(original and original['disposition']=='rejected','Original was not withdrawn at correction review time')
            for target in targets:
                v=index.at(event_target(target),'event_validity',when)
                require(v and v['disposition']=='accepted','Replacement was not accepted at correction review time')
        if not accepted_claim(index,c):continue
        require(statuses[old]['review_state']=='withdrawn','Accepted correction requires withdrawn original event')
        edges[old].update(targets)
    def walk(key,path):
        require(key not in path,'Cyclic event corrections')
        for target in edges[key]:walk(target,path|{key})
    for key in list(edges):walk(key,set())
    for key,targets in edges.items():statuses[key]['replacement_event_ids']=sorted(targets)
    return {'statuses':[statuses[k] for k in sorted(statuses)],
            'current_events':[events[k] for k in sorted(events) if statuses[k]['review_state']=='accepted']}


def transition(rows, previous):
    """Check predecessor retention in addition to the current review contract.

    Full publication must independently validate the predecessor using its pinned
    profile and registry/evidence receipts. This function never supplies that proof.
    """
    result=inspect(rows)
    prior_events=previous['instrument_events']
    for key,event in prior_events.items():
        require(key in rows['instrument_events'] and same(rows['instrument_events'][key],event),'Historical event deleted or mutated')
    for table in ('claims','review_decisions'):
        for key,record in previous[table].items():
            require(key in rows[table] and same(rows[table][key],record),'Historical '+table+' deleted or mutated')
    prior_index=Decisions(previous['review_decisions']);current_index=Decisions(rows['review_decisions'])
    for status in result['statuses']:
        key=status['event_id']
        if key not in prior_events:
            require(status['review_state']=='accepted','New already-withdrawn events cannot bypass initial publication')
            chain=current_index.chain(event_target(key),'event_validity')
            require(all(d['disposition']=='accepted' for d in chain),'New event cannot invent a pre-publication withdrawal history')
            continue
        prior=prior_index.head(event_target(key),'event_validity')
        if prior is None:
            # Profile1.0.1 migration can establish its prior accepted baseline
            # from the already-published exact claim/field reviews, without
            # inventing a historical event-validity decision.
            accepted_event_evidence(prior_events[key],previous['claims'],prior_index)
    return result
