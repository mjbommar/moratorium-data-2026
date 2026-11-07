#!/usr/bin/env python3
"""Verify reviewed source inventories and create private adapter plans; no network.

This is preparation only. It intentionally does not create an executable protocol.
"""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
INPUT = Path('/data0/moratorium-refresh-2026/rule-unit-extraction-2026-11-07')
PRIVATE = Path('/data0/moratorium-refresh-2026/direct-rule-unit-evaluation-2026-11-07/preparation')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(x):
    if not x:
        raise ValueError('Inventory verification failed')

def main():
    audit = json.loads((ROOT/'work/audit/rule-unit-extraction-2026-11-07/audit.json').read_bytes())
    inventory_hashes = audit['source_inventory']['private_artifacts_sha256']
    for name, expected in inventory_hashes.items():
        require(sha((INPUT/name).read_bytes()) == expected)
    old = json.loads((ROOT/'work/research/2026-11-07/compound-contract-evaluation/protocol.json').read_bytes())
    summaries = []
    for family, filename, count in [('mandan','mandan-rule-plan-revised.private.json',20),('harwood','harwood-rule-plan-boundary-fixed.private.json',66)]:
        case = next(c for c in old['cases'] if c['family'] == family)
        src = Path(case['text_path']).read_bytes()
        require(sha(src) == case['text_sha256'] and sha(Path(case['body_path']).read_bytes()) == case['body_sha256'])
        text = src.decode('utf-8')
        inv = json.loads((INPUT/filename).read_bytes())
        require(inv['text_sha256'] == case['text_sha256'] and inv['body_sha256'] == case['body_sha256'] and inv['source_document_id'] == case['source_document_id'])
        units = inv['units']
        require(len(units) == count and len({u['unit_id'] for u in units}) == count)
        by_id = {u['unit_id']: u for u in units}
        locator_count = 0
        def check_locator(loc):
            a, b = loc['span']
            require(type(a) is int and type(b) is int and 0 <= a < b <= len(text))
            segment = text[a:b]
            require(sha(segment.encode()) == loc['text_sha256'])
            require(segment.startswith(loc['start_anchor']) and segment.endswith(loc['end_anchor']))
        plans = []
        for unit in units:
            a,b = unit['anchor_span']
            require(text[a:b] == unit['anchor_quote'] and text.count(unit['anchor_quote']) == 1)
            context = unit['boundary_context']
            loc = context['printed_source_span']
            check_locator(loc)
            for ref in context['context_locators']:
                require(ref['unit_id'] in by_id)
                check_locator(ref['locator'])
                require(ref['locator'] == by_id[ref['unit_id']]['boundary_context']['printed_source_span'])
                locator_count += 1
            # Numerical character offsets and source-printed start/end boundaries are
            # locators, not semantic criteria. Preserve source order and references.
            instruction = json.dumps({'printed_source_span':loc,
                'context_locators':[{'unit_id':r['unit_id'],'locator':r['locator']} for r in context['context_locators']],
                **({'layout_note':context['layout_note']} if 'layout_note' in context else {})},ensure_ascii=False,sort_keys=True)
            plans.append({k:unit[k] for k in ('unit_id','anchor_quote','label')} | {'instruction':instruction})
        plan = {'source_text_sha256':sha(src),'units':plans}
        payload=(json.dumps(plan,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
        target=PRIVATE/(family+'-adapter-plan.private.json')
        fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as f:
            f.write(payload);f.flush();os.fsync(f.fileno())
        summaries.append({'case_id':family+'-direct','units':count,'context_locators_verified':locator_count,'source_text_sha256':sha(src),'source_body_sha256':case['body_sha256'],'inventory_sha256':inventory_hashes[filename],'transformed_plan_sha256':sha(payload)})
    result={'status':'preparation_only_not_execution_authorized','inventory_review_sha256':{k:v for k,v in inventory_hashes.items() if 'review' in k},'cases':summaries,'conversion_code_sha256':sha(Path(__file__).read_bytes()),'provider_calls':0,'independent_conversion_review':'not performed'}
    (HERE/'inventory-validation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__ == '__main__':
    main()
