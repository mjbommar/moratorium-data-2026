#!/usr/bin/env python3
"""Add frozen ballot-census and all-state/sector discovery lanes to the legacy queue."""
import argparse
import json
from pathlib import Path
from build_distributed_refresh import write

ROOT=Path(__file__).resolve().parents[1]


def build(legacy, seeds_path, specs, outputs):
    initial=json.loads(legacy.read_text())
    as_of=initial['as_of']
    seeds=[json.loads(x) for x in seeds_path.read_text().splitlines() if x.strip()]
    prompt_base=f'''You are a distributed Codex CLI worker, gpt-6.1-terra. Cutoff {as_of}.
Read docs/research-and-ballot-expansion-plan.md and work/research/2026-11-05/pilot-review.md.
Edit ONLY your assigned output directory. No canonical CSV edits, commits/pushes,
external LLM calls, more jobs, or changes to other workers' files. Network access
ONLY through ~/projects/bc/bc-modules/.venv/bin/python scripts/research_client.py
--directory OUTPUT search QUERY --backend exa|serpapi|googlenews|gdelt, or fetch URL
--mode auto|browser. Read client-config.json. Do not use built-in search, curl,
requests or direct library calls to bypass persistent caps. Existing archived
evidence can be read, including the Maine/Ohio pilot and work/sources. Reuse it
where the same source observation already settles a claim. Keep raw responses and
bodies private. No conclusions from snippets alone. Exact substantive quotes >=12
chars need text artifact/hash/span or explicit page/visual proof. Preserve gaps,
unsuccessful searches, publication vs event dates, original units and distinct
same-name governments. Do not infer legal force, certification, project cancellation
or a citywide ban from sentiment or a defeated pro-development vote. Record calls,
unpriced SerpAPI costs, failures, source dates and per-record dispositions in run.json.
Stop within25minutes; explicitly identify unattempted work rather than calling it
researched. Write a concise report.md, not full copyrighted article text.
'''
    jobs=[]
    def add(job, payload, caps, instructions):
        directory=outputs/job;directory.mkdir(parents=True,exist_ok=False)
        write(directory/'packet.json',payload);write(directory/'client-config.json',{'caps':caps})
        prompt=specs/(job+'.txt');prompt.parent.mkdir(parents=True,exist_ok=True)
        prompt.write_text(prompt_base.replace('OUTPUT',str(directory))+'\n'+instructions+f'\nOwned output: {directory}\nPacket: {directory}/packet.json\n')
        spec=specs/(job+'.json');write(spec,{'id':job,'prompt_file':str(prompt.resolve()),'owned_paths':[str(directory)],'reasoning_effort':'medium'})
        jobs.append({'id':job,'spec':str(spec.resolve()),'records':len(payload) if isinstance(payload,list) else 1,'caps':caps})
    for state in sorted({r['state_abbrev_reported'] for r in seeds}):
        rows=[r for r in seeds if r['state_abbrev_reported']==state]
        for i in range(0,len(rows),4):
            part=rows[i:i+4];n=len(part)
            add(f'ballot-{state.lower()}-{i//4+1:03}',part,
                {'search_total':2*n,'exa':n,'serpapi':n,'fetch':5*n},
                '''Research each ballot seed (discovery source is not canonical evidence). Confirm
actual jurisdiction/government type, election, designation, exact wording, bindingness,
yes-vote direction, mechanism, threshold/exemptions/calendar duration and result.
Seek official ballot/warrant, referral/petition qualification, original returns,
certification and adopted legal text. Keep unofficial figures and pending future
elections distinct. Compare full current inventory for predecessor/same-instrument
candidates; do not duplicate instruments. Reconcile source-list omissions discovered
along the way. Write candidates.json (JSON array with seed_id, fields and field-level
source/evidence/status), PLUS expanded/*.jsonl using named contracts in
work/schemas/expanded/1.0.0.json. Use seed IDs as provisional measure IDs until identity
review; every ID reference must resolve. Preserve supported observations even when
legal effect remains unresolved. Use explicit unknown/null for missing fields, but
do not blank known supported values merely to pass a validator. Source records must
hash original payload bytes and exact text, retain actual retrieval time, and label
authority/access. Claims are source-qualified; don't invent accepted legal reviews.
Validate expanded/ with scripts/expanded_data.py and legacy CSV reference options.
If validation cannot be met, report exact schema gaps without false acceptance.''')
    scope=json.loads((ROOT/'work/audit/refresh-scope-2026-11-05.json').read_text())
    for row in scope['packets']:
        state=row['state']
        add(f'discovery-{state.lower()}',{'state_abbrev':state,'as_of':as_of,
            'sectors':['data_center','battery_storage','solar','wind','cryptocurrency_mining'],
            'since':'2026-08-01'},
            {'search_total':14,'exa':5,'serpapi':7,'googlenews':1,'gdelt':1,'fetch':15},
            '''Discover missing instruments and ballot initiatives across ALL5 assigned sectors
in this state, including actions since August1 and older missed instruments. Compare
the existing full state inventory and policy tracker before proposing additions.
Use one semantic Exa and one keyword/official-domain Google query per sector, plus
ballot qualification/referral discovery. Try Google News RSS and GDELT for independent
leads within caps; distinguish index-window decline from no results. Publication
date filtering can hide undated official documents: recover them with unfiltered
domain/identifier searches. Chase cited ordinance numbers and original records.
Write candidates.json with local/state/ballot objects, field-level evidence, exact
source excerpts and unresolved legal/identity issues. For local moratorium additions,
also produce answers.json with decisions:[] and new_candidates matching the existing
research_decision schema. Do not force permanent bans or advisory ballots into that
schema: keep those in typed candidates for the expanded model. Record every query's
actual scope and all5 sector dispositions in coverage.json, sources attempted/read,
and any additional measures omitted by the seed list. This bounded discovery is NOT
a complete census of all local governments. An empty sector requires documented
attempts; inability to search is not a negative finding.''')
    combined={**initial,'jobs':jobs+initial['jobs'], 'added_lanes':{'ballot_jobs':sum(x['id'].startswith('ballot-') for x in jobs),'state_discovery_jobs':50},
        'scope_note':'Legacy full-ID refresh plus50 ballot seeds and50-state/all5-sector bounded discovery; review and publication remain separate.'}
    combined['max_search_attempts']=sum(x['caps']['search_total'] for x in combined['jobs'])
    combined['max_fetch_attempts']=sum(x['caps']['fetch'] for x in combined['jobs'])
    write(specs/'complete-queue.json',combined)
    return combined


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--legacy-queue',type=Path,required=True);p.add_argument('--seeds',type=Path,required=True)
    p.add_argument('--specs',type=Path,required=True);p.add_argument('--outputs',type=Path,required=True)
    a=p.parse_args();m=build(a.legacy_queue,a.seeds,a.specs.resolve(),a.outputs.resolve())
    print(json.dumps({'jobs':len(m['jobs']),'added_lanes':m['added_lanes'],'max_search_attempts':m['max_search_attempts'],'max_fetch_attempts':m['max_fetch_attempts']},indent=2))
