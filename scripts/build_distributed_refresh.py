#!/usr/bin/env python3
"""Prepare the complete legacy refresh queue without executing network/model calls."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def prepare(as_of, specs, outputs, size):
    common = f'''You are a distributed Codex CLI research worker, model gpt-6.1-terra.
Research cutoff {as_of}. Read docs/research-and-ballot-expansion-plan.md and the assigned
packet. Preserve the shared workspace. Edit ONLY the assigned output directory.
No commits/pushes, canonical CSV writes, additional jobs, or external LLM API calls.
Use ~/projects/bc/bc-modules/.venv/bin/python and scripts/research_client.py for ALL
network access: --directory OUTPUT search QUERY --backend exa|serpapi, or fetch URL
--mode auto|browser. Read client-config.json; persistent caps cannot be reset. Do NOT
use curl, requests, built-in web tools, direct Searcher/Retriever, or bypass the client.
Read retained artifacts locally; don't repeat paid queries on a script error. Fetch
official legal/legislative sources; use browser pydoll for difficult portals if needed.
Review every assigned ID, using state/name/sector context and source identifiers.
At least one Exa and one official-domain Google search per record unless already-read
official sources settle it; state any query coverage shortfall. Read the documents,
not snippets. Distinguish adoption/effect/applicability/expiry, calendar-month terms,
pending proposals, advisory ballots, bans and temporary pauses. An empty search does
not establish expiry or current force. Do not map tax incentives to moratoria or
incentive restrictions merely because the legacy vocabulary/classifier did so.
Do not present archived original observations as fresh legal-status confirmation.
Use exact baseline from-values for local changes; policy records retain stable IDs.
Write answers.json conforming to the assigned legacy schema, a report.md with direct
source links, and run.json with exact IDs/dispositions, attempts, limits, costs known/
unknown, retrieval failures and unresolved claims. Every evidence item needs an exact
substantive short quotation located in the retained text (not a page title alone).
Record original source date and observation separately. No invented certification,
instrument number, expiry, project impact or missing vote count. If not supportable,
return unresolvable with useful attempts, not false confirmation. Existing public
work/sources archives may be read; never alter them. No force-merging. Stop within25
minutes, explicitly identify unfinished IDs, and report evidence limitations.
'''
    queue = []
    reservations = {'ca-status-wave1', 'me-policy-wave1'}
    already = {'inventory': set(), 'state_policy': set()}
    for lane in reservations:
        p = ROOT / 'work/research' / as_of / lane / 'packet.json'
        if p.exists():
            table = 'inventory' if lane.startswith('ca') else 'state_policy'
            key = 'moratorium_id' if table == 'inventory' else 'policy_action_id'
            already[table].update(r[key] for r in json.loads(p.read_text()))
    sources = {}
    for table, name, key in [('inventory', 'moratorium_inventory.csv', 'moratorium_id'),
                              ('state_policy', 'state_legislation.csv', 'policy_action_id')]:
        source = ROOT / 'data' / name
        with source.open(newline='', encoding='utf-8') as f: rows = list(csv.DictReader(f))
        sources[table] = {'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'rows': len(rows)}
        states = sorted({r['state_abbrev'] for r in rows})
        for state in states:
            selected = [r for r in rows if r['state_abbrev'] == state and r[key] not in already[table]]
            # Preserve records exactly; overdue/unresolved cases lead without dropping others.
            if table == 'inventory':
                selected.sort(key=lambda r: (not (r['enacted_status'] in ['active','extended','pending']), r['jurisdiction']))
            for index in range(0, len(selected), size):
                batch = selected[index:index+size]
                job = f'{state.lower()}-{table.replace("_", "-")}-{index//size+1:03}'
                directory = outputs / job; directory.mkdir(parents=True, exist_ok=True)
                write(directory / 'packet.json', batch)
                caps = {'search_total': 2*len(batch), 'exa': len(batch), 'serpapi': len(batch), 'fetch': 3*len(batch)}
                write(directory / 'client-config.json', {'caps': caps, 'price_note':'SerpAPI unpriced; bounded calls, no claimed total dollar cap'})
                schema = 'research_decision.schema.json' if table == 'inventory' else 'legislation_decision.schema.json'
                prompt = common.replace('OUTPUT', str(directory)) + f'\nOwned output: {directory}\nPacket: {directory}/packet.json\nSchema: work/schemas/{schema}\n'
                prompt_path = specs / (job+'.txt'); prompt_path.parent.mkdir(parents=True,exist_ok=True); prompt_path.write_text(prompt)
                spec_path = specs / (job+'.json')
                write(spec_path, {'id':job,'prompt_file':str(prompt_path.resolve()),'owned_paths':[str(directory)],
                                 'table':table,'state':state,'record_ids':[r[key] for r in batch], 'reasoning_effort':'medium'})
                queue.append({'id':job,'spec':str(spec_path.resolve()),'records':len(batch),'caps':caps})
    manifest = {'as_of':as_of,'sources':sources,'completed_pilot_ids':{k:sorted(v) for k,v in already.items()},
                'jobs':queue, 'model':'gpt-6.1-terra','reasoning_effort':'medium',
                'max_search_attempts':sum(x['caps']['search_total'] for x in queue),
                'max_fetch_attempts':sum(x['caps']['fetch'] for x in queue),
                'scope_note':'Full legacy-ID refresh queue only; independent all-state discovery and complete ballot census remain separate required lanes.'}
    write(specs/'queue.json',manifest)
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--as-of',required=True);p.add_argument('--specs',type=Path,required=True)
    p.add_argument('--outputs',type=Path,required=True);p.add_argument('--batch-size',type=int,default=8)
    a=p.parse_args()
    if not 1<=a.batch_size<=12:p.error('batch-size must be1..12')
    m=prepare(a.as_of,a.specs.resolve(),a.outputs.resolve(),a.batch_size)
    print(json.dumps({k:v for k,v in m.items() if k not in ['jobs','completed_pilot_ids']},indent=2))
    print('Prepared jobs:',len(m['jobs']))
