#!/usr/bin/env python3
"""Index existing residual review questions; never infer factual acceptance."""
import argparse,csv,hashlib,json,re
from pathlib import Path

def digest(b): return hashlib.sha256(b).hexdigest()
def residual_values(value):
    if isinstance(value,str): return [value.strip()] if value.strip() else []
    if isinstance(value,list): return [s for item in value for s in residual_values(item)]
    if isinstance(value,dict):
        return [s for key,item in value.items() if key not in ('prior_review','prior_primary_disposition','prior_row_and_identity_guard','followup_class','retained_attempts','retained_search_attempts','mechanical_checks') for s in residual_values(item)]
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
      'wa-renton-2026':['Obtain full signed Ordinance 6200 and verify operative effective anchor, end date, exceptions and later actions/current force. Official August 17 minutes now establish adoption and October 5 minutes establish the data-center hearing/comments/closure.'],
      'nd-oliver-county-2025-p2':['Obtain executed Resolution 2025-02 and amendments plus recording/publication proof; reconcile the 90-day motion with the standards-dependent operative text. The later general zoning compilation does not resolve these issues.'],
    }
    maine=args.output/'maine-terminal-dispositions.json'
    if maine.exists():
        for record in json.loads(maine.read_text())['records']:
            if record['recommendation']=='unresolved':
                overlays[record['id']]=[gap['field']+': '+gap['gap'] for gap in record['specific_remaining_gaps']]
    terminal=args.output/'terminal-residual-audit.json'
    if terminal.exists():
        for record in json.loads(terminal.read_text())['records']:
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    procedure=args.output/'sd-procedure-adjudications.json'
    if procedure.exists():
        for record in json.loads(procedure.read_text())['records']:
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    sponsor=args.output/'sd-howard-independent-review.json'
    if sponsor.exists():
        record=json.loads(sponsor.read_text())
        assert record['conclusion']=='confirmed_match' and record['remaining_questions']
        key=('state_policy',record['record_id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['row_guard']['sha256']
        overlays[record['record_id']]=[public_text(q) for q in record['remaining_questions']]
    enacted=args.output/'sd-enacted-adjudications.json'
    if enacted.exists():
        for record in json.loads(enacted.read_text())['records']:
            assert record['recommendation']=='unresolved' and record['questions_open']
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            overlays[record['id']]=[public_text(q) for q in record['questions_open']]
    local_reconciliation=args.output/'local-residual-reconciliation.json'
    if local_reconciliation.exists():
        for record in json.loads(local_reconciliation.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['remaining_questions'] and not record['whole_record_closure_recommended']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    northport=args.output/'northport-adjudication.json'
    if northport.exists():
        record=json.loads(northport.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    colorado=args.output/'colorado-term-adjudications.json'
    if colorado.exists():
        for record in json.loads(colorado.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='unresolved' and record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    va_wy=args.output/'va-wy-adjudications.json'
    if va_wy.exists():
        for record in json.loads(va_wy.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='unresolved' and record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    arizona=args.output/'arizona-final-adjudications.json'
    if arizona.exists():
        for record in json.loads(arizona.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    alabama=args.output/'alabama-session-adjudications.json'
    if alabama.exists():
        for record in json.loads(alabama.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='unresolved' and record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    petersburg=args.output/'petersburg-followup.json'
    if petersburg.exists():
        record=json.loads(petersburg.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    foley=args.output/'foley-adjudication.json'
    if foley.exists():
        record=json.loads(foley.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wy_retained=args.output/'wy-retained-adjudications.json'
    if wy_retained.exists():
        for record in json.loads(wy_retained.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='unresolved' and record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    nebraska=args.output/'nebraska-retained-adjudication.json'
    if nebraska.exists():
        record=json.loads(nebraska.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    lb613=args.output/'nebraska-lb613-adjudication.json'
    if lb613.exists():
        record=json.loads(lb613.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    ne_transfer=args.output/'nebraska-transfer-adjudications.json'
    if ne_transfer.exists():
        for record in json.loads(ne_transfer.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation'] in ('unresolved','corrected_resolved')
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else:
                assert not record['remaining_questions']
                closure=json.loads((args.output/'nebraska-lb1111-closure.json').read_text())
                assert closure['id']==record['id'] and closure['current_row_sha256']==record['current_row_sha256']
                assert closure['recommendation']=='corrected_resolved'
                assert next(r for r in f['records'] if r['id']==record['id'])['disposition']=='corrected_resolved'
    georgia=args.output/'georgia-residual-adjudications.json'
    if georgia.exists():
        for record in json.loads(georgia.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation'] in ('unresolved','corrected_resolved','confirmed_unchanged')
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else:
                assert not record['remaining_questions']
                assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
    tennessee=args.output/'tennessee-session-adjudications.json'
    if tennessee.exists():
        for record in json.loads(tennessee.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation'] in ('unresolved','corrected_resolved','confirmed_unchanged')
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else:
                assert not record['remaining_questions']
    wv_authority=args.output/'wv-shared-authority-adjudications.json'
    if wv_authority.exists():
        for record in json.loads(wv_authority.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='unresolved' and record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    nh_text=args.output/'nh-text-adjudications.json'
    if nh_text.exists():
        for record in json.loads(nh_text.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation'] in ('unresolved','corrected_resolved')
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else:
                assert not record['remaining_questions']
    nh_version=args.output/'nh-version-journal-adjudications.json'
    if nh_version.exists():
        for record in json.loads(nh_version.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']=='corrected_resolved'
    covina=args.output/'covina-adjudication.json'
    if covina.exists():
        record=json.loads(covina.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    irwindale=args.output/'irwindale-adjudication.json'
    if irwindale.exists():
        record=json.loads(irwindale.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
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
    summary={'active_unresolved_records':len(rows),'records_with_explicit_questions':sum(bool(r['questions']) for r in rows),'records_requiring_disposition_reconciliation':[r['id'] for r in rows if not r['questions']],'local_records':sum(r['dataset']=='local_inventory' for r in rows),'state_policy_records':sum(r['dataset']=='state_policy' for r in rows),'funnel_sha256':digest(fpath.read_bytes()),'review_ledger_sha256':digest(raw),'queue_sha256':digest(body),'post_release_overlay_records':sum(r['post_release_overlay'] for r in rows),'overlay_review_sha256':digest(maine.read_bytes()) if maine.exists() else None,'terminal_overlay_sha256':digest(terminal.read_bytes()) if terminal.exists() else None,'procedure_overlay_sha256':digest(procedure.read_bytes()) if procedure.exists() else None,'sponsor_overlay_sha256':digest(sponsor.read_bytes()) if sponsor.exists() else None,'enacted_overlay_sha256':digest(enacted.read_bytes()) if enacted.exists() else None,'local_reconciliation_sha256':digest(local_reconciliation.read_bytes()) if local_reconciliation.exists() else None,'northport_overlay_sha256':digest(northport.read_bytes()) if northport.exists() else None,'irwindale_overlay_sha256':digest(irwindale.read_bytes()) if irwindale.exists() else None,'covina_overlay_sha256':digest(covina.read_bytes()) if covina.exists() else None,'nh_version_overlay_sha256':digest(nh_version.read_bytes()) if nh_version.exists() else None,'nh_text_overlay_sha256':digest(nh_text.read_bytes()) if nh_text.exists() else None,'wv_authority_overlay_sha256':digest(wv_authority.read_bytes()) if wv_authority.exists() else None,'tennessee_overlay_sha256':digest(tennessee.read_bytes()) if tennessee.exists() else None,'georgia_overlay_sha256':digest(georgia.read_bytes()) if georgia.exists() else None,'ne_transfer_overlay_sha256':digest(ne_transfer.read_bytes()) if ne_transfer.exists() else None,'lb613_overlay_sha256':digest(lb613.read_bytes()) if lb613.exists() else None,'nebraska_overlay_sha256':digest(nebraska.read_bytes()) if nebraska.exists() else None,'wy_retained_overlay_sha256':digest(wy_retained.read_bytes()) if wy_retained.exists() else None,'foley_overlay_sha256':digest(foley.read_bytes()) if foley.exists() else None,'petersburg_overlay_sha256':digest(petersburg.read_bytes()) if petersburg.exists() else None,'alabama_overlay_sha256':digest(alabama.read_bytes()) if alabama.exists() else None,'arizona_overlay_sha256':digest(arizona.read_bytes()) if arizona.exists() else None,'va_wy_overlay_sha256':digest(va_wy.read_bytes()) if va_wy.exists() else None,'colorado_overlay_sha256':digest(colorado.read_bytes()) if colorado.exists() else None,'scope':'Mechanical index of previously recorded residual questions, with explicit published post-release overlays. Not a new source review, factual classification, prioritization or admission of new searches. Retired IDs remain in the identity/disposition history. Held ballot payloads are separately accounted; do not add them as distinct canonical measures.'}
    (args.output/'outstanding-queue-verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
