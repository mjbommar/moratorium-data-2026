#!/usr/bin/env python3
"""Index existing residual review questions; never infer factual acceptance."""
import argparse,csv,hashlib,json,re
from pathlib import Path

def digest(b): return hashlib.sha256(b).hexdigest()
def residual_values(value):
    if isinstance(value,str): return [value.strip()] if value.strip() else []
    if isinstance(value,list): return [s for item in value for s in residual_values(item)]
    if isinstance(value,dict):
        return [s for key,item in value.items() if key not in ('prior_review','prior_primary_disposition','prior_row_and_identity_guard','followup_class') for s in residual_values(item)]
    return []
def questions(value):
    found=[]
    if isinstance(value,dict):
        for key,item in value.items():
            if any(term in key.lower() for term in ('unperformed','precise_gap','outstanding_question','remaining_question')):
                found.extend(residual_values(item))
            elif isinstance(item,(dict,list)): found.extend(questions(item))
    elif isinstance(value,list):
        for item in value: found.extend(questions(item))
    return list(dict.fromkeys(found))
def public_text(s):
    s=re.sub(r'/(?:home|data0|nas[0-9]+|tmp)/[^\s`\"<>]+','[private review locator retained]',s)
    return s

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--review-ledger',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    root=Path.cwd();fpath=root/'work/research/2026-11-08/full-record-dispositions/funnel.json';f=json.loads(fpath.read_text())
    raw=args.review_ledger.read_bytes();history={(r['dataset'],r['id']):r for r in map(json.loads,raw.decode().splitlines())}
    current={}
    for dataset,path,key in [('local_inventory','data/moratorium_inventory.csv','moratorium_id'),('state_policy','data/state_legislation.csv','policy_action_id')]:
        for row in csv.DictReader((root/path).open(newline='')):current[dataset,row[key]]=row
    overlays={
      'tx-lavon-2026':['Obtain official vote minutes/final ordinance establishing action date and instrument identity; reconcile the recovered report chronology and establish any operative interval. November 17 remains scheduled, not an observed action.'],
      'ky-ashland-2026':['Obtain original ordinance/effective-date anchor and controlling term (six months versus 180 days); establish any explicit termination or intervening action. February 26 is now an attributed unverified news inference.'],
      'nd-oliver-county-2025-p2':['Obtain executed Resolution 2025-02 and amendments plus recording/publication proof; reconcile the 90-day motion with the standards-dependent operative text. The later general zoning compilation does not resolve these issues.'],
    }
    maine=args.output/'maine-terminal-dispositions.json'
    if maine.exists():
        for record in json.loads(maine.read_text())['records']:
            if record['recommendation']=='unresolved':
                overlays[record['id']]=[gap['field']+': '+gap['gap'] for gap in record['specific_remaining_gaps']]
    rows=[]
    for entry in f['records']:
        if entry['disposition']!='unresolved':continue
        key=entry['dataset'],entry['id'];assert key in current and key in history
        old=history[key];reviews=[old['accepted_record']] if old.get('accepted_record') else [e['record'] for e in old['original_independent']]
        qs=list(dict.fromkeys(public_text(q) for r in reviews for q in questions(r)))
        if entry['id'] in overlays:qs=overlays[entry['id']]
        row=current[key]
        rows.append({'dataset':key[0],'id':key[1],'current_row_sha256':digest(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),'route':'source_specific_followup' if qs else 'disposition_reconciliation_required','questions':qs,'basis':'post-release adjudication overlay' if entry['id'] in overlays else ('accepted independent review residuals' if old.get('accepted_record') else 'earlier-cohort independent review residuals'),'post_release_overlay':entry['id'] in overlays,'published_evidence_pointer':entry['public_receipt_pointer']})
    expected={(r['dataset'],r['id']) for r in f['records'] if r['disposition']=='unresolved'}
    assert {(r['dataset'],r['id']) for r in rows}==expected and len(rows)==len(expected)==f['counts']['unresolved']
    args.output.mkdir(parents=True,exist_ok=True);body=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in sorted(rows,key=lambda r:(r['dataset'],r['id']))).encode();(args.output/'outstanding-record-questions.jsonl').write_bytes(body)
    summary={'active_unresolved_records':len(rows),'records_with_explicit_questions':sum(bool(r['questions']) for r in rows),'records_requiring_disposition_reconciliation':[r['id'] for r in rows if not r['questions']],'local_records':sum(r['dataset']=='local_inventory' for r in rows),'state_policy_records':sum(r['dataset']=='state_policy' for r in rows),'funnel_sha256':digest(fpath.read_bytes()),'review_ledger_sha256':digest(raw),'queue_sha256':digest(body),'post_release_overlay_records':sum(r['post_release_overlay'] for r in rows),'overlay_review_sha256':digest(maine.read_bytes()) if maine.exists() else None,'scope':'Mechanical index of previously recorded residual questions, with explicit published post-release overlays. Not a new source review, factual classification, prioritization or admission of new searches. Retired IDs remain in the identity/disposition history. Held ballot payloads are separately accounted; do not add them as distinct canonical measures.'}
    (args.output/'outstanding-queue-verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
