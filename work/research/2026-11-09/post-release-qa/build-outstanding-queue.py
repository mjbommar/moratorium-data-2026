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
            if (key.lower() in ('source_followup', 'source_followup_required')
                or any(term in key.lower() for term in ('unperformed','precise_gap','outstanding_question','remaining_question'))):
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
    additions=args.output/'post-release-new-record-reviews.json'
    if additions.exists():
        for entry in json.loads(additions.read_text())['records']:
            key=(entry['dataset'],entry['id'])
            assert key not in history and entry['cohort']=='post_release_additions'
            history[key]=entry
    current={}
    for dataset,path,key in [('local_inventory','data/moratorium_inventory.csv','moratorium_id'),('state_policy','data/state_legislation.csv','policy_action_id')]:
        for row in csv.DictReader((root/path).open(newline='')):current[dataset,row[key]]=row
    overlays={
      'tx-lavon-2026':['Obtain official vote minutes/final ordinance establishing action date and instrument identity; reconcile the recovered report chronology and establish any operative interval. November 17 remains scheduled, not an observed action.'],
      'ky-ashland-2026':['Obtain original ordinance/effective-date anchor and controlling term (six months versus 180 days); establish any explicit termination or intervening action. February 26 is now an attributed unverified news inference.'],
      'wa-renton-2026':['Obtain full signed Ordinance 6200 and verify operative effective anchor, end date, exceptions and later actions/current force. Official August 17 minutes now establish adoption and October 5 minutes establish the data-center hearing/comments/closure.'],
      'nd-oliver-county-2025-p2':['Obtain executed Resolution 2025-02 and amendments plus recording/publication proof; reconcile the 90-day motion with the standards-dependent operative text. The later general zoning compilation does not resolve these issues.'],
    }
    remaining_links=args.output/'remaining-policy-source-links-adjudications.json'
    remaining_link_records={r['id']:r for r in json.loads(remaining_links.read_text())['records']} if remaining_links.exists() else {}
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
    cromwell_path=Path('work/research/2026-11-10/post-release-qa/cromwell-later-proposal-review.json')
    cromwell=json.loads(cromwell_path.read_text()) if cromwell_path.exists() else None
    local_reconciliation=args.output/'local-residual-reconciliation.json'
    if local_reconciliation.exists():
        for record in json.loads(local_reconciliation.read_text())['records']:
            if cromwell and record['id']==cromwell['id']:
                assert record['current_row_sha256']==cromwell['prior_row_sha256']
                assert not record['whole_record_closure_recommended']
                continue
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
    wy_code=args.output/'wyoming-current-tax-code-adjudications.json'
    wy_code_records={r['id']:r for r in json.loads(wy_code.read_text())['records']} if wy_code.exists() else {}
    wy_sponsors_path=Path('work/research/2026-11-10/post-release-qa/wyoming-hb325-sponsor-application.json')
    wy_sponsors=json.loads(wy_sponsors_path.read_text()) if wy_sponsors_path.exists() else None
    wy_retained=args.output/'wy-retained-adjudications.json'
    if wy_retained.exists():
        for record in json.loads(wy_retained.read_text())['records']:
            if wy_sponsors and record['id']==wy_sponsors['id']:
                assert record['current_row_sha256']==wy_sponsors['prior_row_sha256']
                assert record['recommendation']==wy_sponsors['prior_disposition']=='unresolved'
                continue
            if record['id'] in wy_code_records:
                later=wy_code_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record['recommendation']==later['prior_disposition']=='unresolved'
                continue  # Original guard is explicitly chained to the later guarded review below.
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
    lb613_introducer_path=Path('work/research/2026-11-10/post-release-qa/nebraska-lb613-introducer-review.json')
    lb613_introducer=json.loads(lb613_introducer_path.read_text()) if lb613_introducer_path.exists() else None
    lb613=args.output/'nebraska-lb613-adjudication.json'
    if lb613.exists():
        record=json.loads(lb613.read_text())
        key=('state_policy',record['id'])
        if lb613_introducer:
            assert record['current_row_sha256']==lb613_introducer['prior_row_sha256']
        else:
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    if lb613_introducer:
        record=lb613_introducer;key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
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
    ga34=args.output/'georgia-sb34-history-adjudication.json'
    ga34_records={r['id']:r for r in json.loads(ga34.read_text())['records']} if ga34.exists() else {}
    georgia=args.output/'georgia-residual-adjudications.json'
    if georgia.exists():
        for record in json.loads(georgia.read_text())['records']:
            if record['id'] in ga34_records:
                later=ga34_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record['recommendation']==later['prior_disposition']=='unresolved'
                continue  # Explicitly chained to the superseding guarded review below.
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
            if record['id'] in remaining_link_records:
                later=remaining_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']
                continue
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
            if record['id'] in remaining_link_records:
                later=remaining_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']
                continue
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
            if record['id'] in remaining_link_records:
                later=remaining_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']
                continue
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
    monterey=args.output/'monterey-park-adjudication.json'
    if monterey.exists():
        record=json.loads(monterey.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='unresolved' and record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    solano=args.output/'solano-adjudication.json'
    if solano.exists():
        record=json.loads(solano.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']=='corrected_resolved'
    local_minutes=args.output/'coachella-vacaville-adjudications.json'
    if local_minutes.exists():
        for record in json.loads(local_minutes.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='unresolved' and record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    washington=args.output/'washington-county-adjudication.json'
    if washington.exists():
        record=json.loads(washington.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']=='corrected_resolved'
    kentucky=args.output/'kentucky-adjudications.json'
    if kentucky.exists():
        for record in json.loads(kentucky.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']=='corrected_resolved'
    oklahoma=args.output/'oklahoma-adjudications.json'
    if oklahoma.exists():
        for record in json.loads(oklahoma.read_text())['records']:
            if record['id'] in remaining_link_records:
                later=remaining_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else:
                assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
    washington_session=args.output/'washington-session-adjudications.json'
    if washington_session.exists():
        for record in json.loads(washington_session.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation'] in ('corrected_resolved','confirmed_unchanged') and not record['remaining_questions']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
    txwv_links=args.output/'texas-wv-source-links-adjudications.json'
    txwv_link_records={r['id']:r for r in json.loads(txwv_links.read_text())['records']} if txwv_links.exists() else {}
    texas=args.output/'texas-session-adjudications.json'
    if texas.exists():
        for record in json.loads(texas.read_text())['records']:
            if record['id'] in txwv_link_records:
                later=txwv_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record['recommendation']==later['prior_disposition']
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else:
                assert record['recommendation']=='confirmed_unchanged' and not record['remaining_questions']
    pennsylvania=args.output/'pennsylvania-amendment-adjudications.json'
    if pennsylvania.exists():
        for record in json.loads(pennsylvania.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    pa_history=args.output/'pennsylvania-history-adjudications.json'
    if pa_history.exists():
        for record in json.loads(pa_history.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='confirmed_unchanged'
            assert not record['remaining_questions']
    pa_house_history=args.output/'pennsylvania-house-history-adjudications.json'
    if pa_house_history.exists():
        for record in json.loads(pa_house_history.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='confirmed_unchanged'
            assert not record['remaining_questions']
    ny_history=args.output/'new-york-history-adjudications.json'
    if ny_history.exists():
        for record in json.loads(ny_history.read_text())['records']:
            if record['id'] in remaining_link_records:
                later=remaining_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='confirmed_unchanged'
            assert not record['remaining_questions']
    ma_amendment=args.output/'massachusetts-amendment-adjudication.json'
    if ma_amendment.exists():
        for record in json.loads(ma_amendment.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    ma_proposal=args.output/'massachusetts-proposal-adjudications.json'
    if ma_proposal.exists():
        for record in json.loads(ma_proposal.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    pa939=args.output/'pennsylvania-sb939-adjudication.json'
    if pa939.exists():
        for record in json.loads(pa939.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='confirmed_unchanged'
            assert not record['remaining_questions']
    ct_rules=args.output/'connecticut-rules-adjudications.json'
    if ct_rules.exists():
        for record in json.loads(ct_rules.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['recommendation']=='unresolved'
            disposition=next(r for r in f['records'] if r['id']==record['id'])['disposition']
            if disposition!='unresolved':
                later=json.loads((args.output/'connecticut-session-outcome-adjudications.json').read_text())
                resolved=next(r for r in later['records'] if r['id']==record['id'])
                assert disposition==resolved['recommendation']=='corrected_resolved'
                assert resolved['current_row_sha256']==record['current_row_sha256'] and not resolved['remaining_questions']
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    nj_history=args.output/'new-jersey-history-adjudications.json'
    if nj_history.exists():
        for record in json.loads(nj_history.read_text())['records']:
            if record['id'] in remaining_link_records:
                later=remaining_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            assert record['recommendation'] in ('confirmed_unchanged','corrected_resolved') and not record['remaining_questions']
    nj_version=args.output/'new-jersey-version-adjudications.json'
    if nj_version.exists():
        for record in json.loads(nj_version.read_text())['records']:
            if record['id'] in remaining_link_records:
                later=remaining_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
    nj_a5462=args.output/'new-jersey-a5462-adjudication.json'
    if nj_a5462.exists():
        for record in json.loads(nj_a5462.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
    nj_bpu=args.output/'new-jersey-bpu-report-adjudication.json'
    if nj_bpu.exists():
        for record in json.loads(nj_bpu.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    nj_final_law=args.output/'new-jersey-final-law-adjudications.json'
    if nj_final_law.exists():
        for record in json.loads(nj_final_law.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    illinois=args.output/'illinois-adjudications.json'
    if illinois.exists():
        for record in json.loads(illinois.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else:
                assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
    south_carolina=args.output/'south-carolina-history-adjudications.json'
    if south_carolina.exists():
        for record in json.loads(south_carolina.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='confirmed_unchanged'
            assert not record['remaining_questions']
    ohio=args.output/'ohio-history-adjudications.json'
    if ohio.exists():
        for record in json.loads(ohio.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            assert record['recommendation'] in ('corrected_resolved','confirmed_unchanged') and not record['remaining_questions']
    wisconsin=args.output/'wisconsin-text-adjudications.json'
    if wisconsin.exists():
        for record in json.loads(wisconsin.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
    mn_links=args.output/'minnesota-source-links-adjudications.json'
    mn_link_records={r['id']:r for r in json.loads(mn_links.read_text())['records']} if mn_links.exists() else {}
    mn_authors=args.output/'minnesota-author-roster-adjudications.json'
    mn_author_records={r['id']:r for r in json.loads(mn_authors.read_text())['records']} if mn_authors.exists() else {}
    minnesota=args.output/'minnesota-session-adjudications.json'
    if minnesota.exists():
        for record in json.loads(minnesota.read_text())['records']:
            if record['id'] in mn_author_records:
                later=mn_author_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record['recommendation']==later['prior_disposition']=='corrected_resolved'
                continue
            if record['id'] in mn_link_records:
                later=mn_link_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record['recommendation']==later['prior_disposition']=='corrected_resolved'
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
    geography=args.output/'missing-geography-application.json'
    if geography.exists():
        for record in json.loads(geography.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert record['whole_record_disposition_unchanged'] and record['geography_question_resolved']
            if any(e['id']==record['id'] and e['disposition']=='unresolved' for e in f['records']):
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    az_context=args.output/'arizona-governing-context-adjudications.json'
    if az_context.exists():
        for record in json.loads(az_context.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
    ct_outcomes=args.output/'connecticut-session-outcome-adjudications.json'
    if ct_outcomes.exists():
        for record in json.loads(ct_outcomes.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
    wv_comparison=args.output/'west-virginia-comparison-adjudications.json'
    if wv_comparison.exists():
        for record in json.loads(wv_comparison.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']
            assert record['whole_record_disposition_unchanged']
            if record['existing_disposition']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    sedgwick=args.output/'sedgwick-followup-adjudications.json'
    if sedgwick.exists():
        for record in json.loads(sedgwick.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    sedgwick_publication=args.output/'sedgwick-publication-adjudication.json'
    if sedgwick_publication.exists():
        record=json.loads(sedgwick_publication.read_text());key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    oshtemo=args.output/'oshtemo-followup-adjudications.json'
    if oshtemo.exists():
        for record in json.loads(oshtemo.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    phillips=args.output/'phillips-followup-adjudications.json'
    if phillips.exists():
        for record in json.loads(phillips.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    coweta=args.output/'coweta-followup-adjudications.json'
    if coweta.exists():
        for record in json.loads(coweta.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    audubon=args.output/'audubon-followup-adjudications.json'
    if audubon.exists():
        for record in json.loads(audubon.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    lee=args.output/'lee-followup-adjudications.json'
    if lee.exists():
        for record in json.loads(lee.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    starke=args.output/'starke-followup-adjudications.json'
    if starke.exists():
        for record in json.loads(starke.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    boone=args.output/'boone-followup-adjudications.json'
    if boone.exists():
        for record in json.loads(boone.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    alaska_terminal=args.output/'alaska-terminal-adjudications.json'
    if alaska_terminal.exists():
        for record in json.loads(alaska_terminal.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    nonblank_geo=args.output/'nonblank-geography-application.json'
    if nonblank_geo.exists():
        for record in json.loads(nonblank_geo.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    committee_details=args.output/'committee-final-detail-adjudications.json'
    if committee_details.exists():
        for record in json.loads(committee_details.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            assert not record['remaining_questions']
    hawaii_outcomes=args.output/'hawaii-session-outcome-adjudications.json'
    if hawaii_outcomes.exists():
        for record in json.loads(hawaii_outcomes.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
            if record['recommendation']=='unresolved':
                assert record['remaining_questions']
                overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
            else: assert not record['remaining_questions']
    proposal_endpoints=args.output/'policy-proposal-endpoint-adjudications.json'
    if proposal_endpoints.exists():
        for record in json.loads(proposal_endpoints.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    idaho_signature=args.output/'idaho-signature-corroboration.json'
    if idaho_signature.exists():
        record=json.loads(idaho_signature.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    maryland_trigger=args.output/'maryland-trigger-adjudication.json'
    if maryland_trigger.exists():
        record=json.loads(maryland_trigger.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    utah_signature=args.output/'utah-hb507-retained-signature-review.json'
    if utah_signature.exists():
        record=json.loads(utah_signature.read_text())
        if record['id'] in remaining_link_records:
            later=remaining_link_records[record['id']]
            assert record['current_row_sha256']==later['prior_row_sha256']
            assert record.get('recommendation',record.get('existing_disposition'))==later['prior_disposition']=='unresolved'
        else:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    virginia_incorporation=args.output/'virginia-sb130-incorporation-review.json'
    if virginia_incorporation.exists():
        record=json.loads(virginia_incorporation.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
        assert not record['remaining_questions']
    virginia_numbering=args.output/'virginia-sb94-numbering-review.json'
    if virginia_numbering.exists():
        record=json.loads(virginia_numbering.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    utah_versions=args.output/'utah-sb231-version-adjudication.json'
    if utah_versions.exists():
        record=json.loads(utah_versions.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    alabama_instruments=args.output/'alabama-local-instrument-adjudications.json'
    if alabama_instruments.exists():
        for record in json.loads(alabama_instruments.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    homewood_minutes=args.output/'homewood-2979-minute-adjudication.json'
    if homewood_minutes.exists():
        record=json.loads(homewood_minutes.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    lodi_version=args.output/'lodi-effective-version-adjudication.json'
    if lodi_version.exists():
        record=json.loads(lodi_version.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    nashville_minutes=args.output/'nashville-meeting-minute-adjudication.json'
    if nashville_minutes.exists():
        record=json.loads(nashville_minutes.read_text())
        key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    montana_text=args.output/'montana-enrolled-text-adjudication.json'
    if montana_text.exists():
        record=json.loads(montana_text.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['existing_disposition']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    montana_hj46=args.output/'montana-hj46-text-adjudication.json'
    if montana_hj46.exists():
        record=json.loads(montana_hj46.read_text())
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
        assert not record['remaining_questions']
    for record in wy_code_records.values():
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
        if record['recommendation']=='unresolved':
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
        else:
            assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
    ohio_veto=args.output/'ohio-hb96-veto-adjudication.json'
    if ohio_veto.exists():
        for record in json.loads(ohio_veto.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    sc_terminal=args.output/'south-carolina-s902-terminal-review.json'
    if sc_terminal.exists():
        for record in json.loads(sc_terminal.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wy_scope_dispositions=args.output/'wyoming-scope-disposition-reconciliation.json'
    if wy_scope_dispositions.exists():
        for record in json.loads(wy_scope_dispositions.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
    indiana_fiscal=args.output/'indiana-sb234-fiscal-review.json'
    if indiana_fiscal.exists():
        for record in json.loads(indiana_fiscal.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    dover_minutes=args.output/'dover-october12-minutes-adjudication.json'
    if dover_minutes.exists():
        for record in json.loads(dover_minutes.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wv_carryover=args.output/'wv-senate-carryover-authority-review.json'
    if wv_carryover.exists():
        for record in json.loads(wv_carryover.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    monument_text=args.output/'monument-ordinance-adjudication.json'
    if monument_text.exists():
        for record in json.loads(monument_text.read_text())['records']:
            key=('local_inventory',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wy_sf193=args.output/'wyoming-sf193-disposition-reconciliation.json'
    if wy_sf193.exists():
        for record in json.loads(wy_sf193.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
            assert digest(Path(record['prior_adjudication']).read_bytes())==record['prior_adjudication_sha256']
            scope_events=[json.loads(line) for line in Path('data/state_policy_scope_reviews.jsonl').read_text().splitlines() if json.loads(line)['policy_action_id']==record['id']]
            assert scope_events[-1]['decision_id']==record['scope_decision_id'] and scope_events[-1]['decision']=='include'
            overlays.pop(record['id'],None)
    mo_final=args.output/'missouri-final-passage-adjudications.json'
    if mo_final.exists():
        for record in json.loads(mo_final.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
            overlays.pop(record['id'],None)
    mn3793=args.output/'minnesota-hf3793-terminal-adjudication.json'
    if mn3793.exists():
        for record in json.loads(mn3793.read_text())['records']:
            if record['id'] in mn_author_records:
                later=mn_author_records[record['id']]
                assert record['current_row_sha256']==later['prior_row_sha256']
                assert record['recommendation']==later['prior_disposition']=='unresolved'
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    va_returned=args.output/'virginia-returned-veto-adjudications.json'
    if va_returned.exists():
        for record in json.loads(va_returned.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
            assert not record['remaining_questions']
            overlays.pop(record['id'],None)
    for record in ga34_records.values():
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        assert record['remaining_questions']
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    for record in mn_author_records.values():
        if record['id'] in mn_link_records:
            later=mn_link_records[record['id']]
            assert record['current_row_sha256']==later['prior_row_sha256']
            assert record['recommendation']==later['prior_disposition']=='corrected_resolved'
            continue
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
        if record['recommendation']=='unresolved':
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
        else:
            assert record['recommendation']=='corrected_resolved' and not record['remaining_questions']
            overlays.pop(record['id'],None)
    for record in mn_link_records.values():
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='corrected_resolved'
        assert not record['remaining_questions']
        overlays.pop(record['id'],None)
    for record in txwv_link_records.values():
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
        if record['recommendation']=='unresolved':
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
        else:
            assert record['recommendation'] in ('corrected_resolved','confirmed_unchanged') and not record['remaining_questions']
            overlays.pop(record['id'],None)
    for record in remaining_link_records.values():
        key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']
        if record['recommendation']=='unresolved':
            assert record['remaining_questions']
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
        else:
            assert record['recommendation'] in ('corrected_resolved','confirmed_unchanged') and not record['remaining_questions']
            overlays.pop(record['id'],None)
    fairbanks_recovery=Path('work/research/2026-11-10/post-release-qa/fairbanks-ordinance-recovery.json')
    if fairbanks_recovery.exists():
        record=json.loads(fairbanks_recovery.read_text());key=('local_inventory',record['record_id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['record_id'])['disposition']=='unresolved'
        assert record['canonical_fields_changed']==record['whole_record_closures']==0
        overlays[record['record_id']]=['Recover full Ordinance2026-42 text and verify proposed term, subsequent action and adoption. '+record['next_action']+' Recovery receipt: '+str(fairbanks_recovery)]
    ma_conference_discovery=Path('work/research/2026-11-10/post-release-qa/massachusetts-conference-discovery.json')
    if ma_conference_discovery.exists():
        record=json.loads(ma_conference_discovery.read_text());key=('state_policy',record['record_id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['record_id'])['disposition']=='unresolved'
        assert not record['independent_review_completed'] and record['canonical_fields_changed']==record['whole_record_closures']==0
        overlays[record['record_id']]=[public_text(q) for q in record['remaining_questions']]
    if cromwell:
        key=('local_inventory',cromwell['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==cromwell['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==cromwell['id'])['disposition']==cromwell['recommendation']=='unresolved'
        overlays[cromwell['id']]=[public_text(q) for q in cromwell['remaining_questions']]
    morris_path=Path('work/research/2026-11-10/post-release-qa/morris-adopted-term-review.json')
    if morris_path.exists():
        morris=json.loads(morris_path.read_text());key=('local_inventory',morris['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==morris['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==morris['id'])['disposition']==morris['recommendation']=='unresolved'
        overlays[morris['id']]=[public_text(q) for q in morris['remaining_questions']]
    trumbull_path=Path('work/research/2026-11-10/post-release-qa/trumbull-retained-minutes-review.json')
    if trumbull_path.exists():
        record=json.loads(trumbull_path.read_text());key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    west_haven_path=Path('work/research/2026-11-10/post-release-qa/west-haven-adoption-text-review.json')
    if west_haven_path.exists():
        record=json.loads(west_haven_path.read_text());key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    new_haven_path=Path('work/research/2026-11-10/post-release-qa/new-haven-signature-review.json')
    if new_haven_path.exists():
        record=json.loads(new_haven_path.read_text());key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    new_haven_version_path=Path('work/research/2026-11-10/post-release-qa/new-haven-version-comparison.json')
    if new_haven_version_path.exists():
        record=json.loads(new_haven_version_path.read_text());key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']==record['prior_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        assert record['canonical_cells_changed']==record['whole_record_closures']==0
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    independence_later_path=Path('work/research/2026-11-10/post-release-qa/independence-ordinance19850-review.json')
    independence_later=json.loads(independence_later_path.read_text()) if independence_later_path.exists() else None
    independence_path=Path('work/research/2026-11-10/post-release-qa/independence-operative-term-review.json')
    if independence_path.exists():
        record=json.loads(independence_path.read_text());key=('local_inventory',record['id'])
        if independence_later:
            assert record['current_row_sha256']==independence_later['prior_row_sha256']
            assert record['recommendation']==independence_later['prior_disposition']=='unresolved'
        else:
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    if independence_later:
        record=independence_later;key=('local_inventory',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wy_session_path=Path('work/research/2026-11-10/post-release-qa/wyoming-session-identity-review.json')
    if wy_session_path.exists():
        for record in json.loads(wy_session_path.read_text())['records']:
            if wy_sponsors and record['id']==wy_sponsors['id']:
                assert record['current_row_sha256']==wy_sponsors['prior_row_sha256']
                assert record['recommendation']==wy_sponsors['prior_disposition']=='unresolved'
                continue
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            overlays[record['id']]=list(dict.fromkeys(overlays.get(record['id'],[])+[public_text(q) for q in record['remaining_questions']]))
    if wy_sponsors:
        record=wy_sponsors;key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    ky_code_path=Path('work/research/2026-11-10/post-release-qa/kentucky-current-incentive-code-review.json')
    if ky_code_path.exists():
        for record in json.loads(ky_code_path.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wy_api_path=Path('work/research/2026-11-10/post-release-qa/wyoming-sf91-sponsor-api-review.json')
    if wy_api_path.exists():
        record=json.loads(wy_api_path.read_text());key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    la_hcr61_path=Path('work/research/2026-11-10/post-release-qa/louisiana-hcr61-closing-window-review.json')
    if la_hcr61_path.exists():
        record=json.loads(la_hcr61_path.read_text());key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wy_fullname_path=Path('work/research/2026-11-10/post-release-qa/wyoming-sf91-full-name-review.json')
    if wy_fullname_path.exists():
        record=json.loads(wy_fullname_path.read_text());key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    ks_publication_path=Path('work/research/2026-11-10/post-release-qa/kansas-sb98-publication-review.json')
    if ks_publication_path.exists():
        record=json.loads(ks_publication_path.read_text());key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    ks_two_path=Path('work/research/2026-11-10/post-release-qa/kansas-sb51-sb92-publication-review.json')
    if ks_two_path.exists():
        for record in json.loads(ks_two_path.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    ks_order_path=Path('work/research/2026-11-10/post-release-qa/kansas-sb51-amendment-order-review.json')
    if ks_order_path.exists():
        record=json.loads(ks_order_path.read_text());key=('state_policy',record['id'])
        assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
        assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
        overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    wa_current_path=Path('work/research/2026-11-10/post-release-qa/washington-enacted-current-law-review.json')
    if wa_current_path.exists():
        for record in json.loads(wa_current_path.read_text())['records']:
            key=('state_policy',record['id'])
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==record['current_row_sha256']
            assert next(r for r in f['records'] if r['id']==record['id'])['disposition']==record['recommendation']=='unresolved'
            overlays[record['id']]=[public_text(q) for q in record['remaining_questions']]
    rows=[]
    for entry in f['records']:
        if entry['disposition']!='unresolved':continue
        key=entry['dataset'],entry['id'];assert key in current and key in history
        old=history[key]
        if old.get('direct_review'):
            assert digest(json.dumps(current[key],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==old['current_row_sha256']
        reviews=[old['direct_review']] if old.get('direct_review') else ([old['accepted_record']] if old.get('accepted_record') else [e['record'] for e in old['original_independent']])
        qs=list(dict.fromkeys(public_text(q) for r in reviews for q in questions(r)))
        if entry['id'] in overlays:qs=overlays[entry['id']]
        row=current[key]
        rows.append({'dataset':key[0],'id':key[1],'current_row_sha256':digest(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),'route':'source_specific_followup' if qs else 'disposition_reconciliation_required','questions':qs,'basis':'post-release adjudication overlay' if entry['id'] in overlays else ('post-release direct review; independent review pending' if old.get('direct_review') else ('accepted independent review residuals' if old.get('accepted_record') else 'earlier-cohort independent review residuals')),'post_release_overlay':entry['id'] in overlays,'published_evidence_pointer':entry['public_receipt_pointer']})
    expected={(r['dataset'],r['id']) for r in f['records'] if r['disposition']=='unresolved'}
    assert {(r['dataset'],r['id']) for r in rows}==expected and len(rows)==len(expected)==f['counts']['unresolved']
    args.output.mkdir(parents=True,exist_ok=True);body=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in sorted(rows,key=lambda r:(r['dataset'],r['id']))).encode();(args.output/'outstanding-record-questions.jsonl').write_bytes(body)
    summary={'active_unresolved_records':len(rows),'remaining_policy_source_links_sha256':digest(remaining_links.read_bytes()) if remaining_links.exists() else None,'texas_wv_source_links_sha256':digest(txwv_links.read_bytes()) if txwv_links.exists() else None,'minnesota_source_links_sha256':digest(mn_links.read_bytes()) if mn_links.exists() else None,'minnesota_author_roster_sha256':digest(mn_authors.read_bytes()) if mn_authors.exists() else None,'georgia_sb34_history_sha256':digest(ga34.read_bytes()) if ga34.exists() else None,'virginia_returned_veto_sha256':digest(va_returned.read_bytes()) if va_returned.exists() else None,'mn3793_terminal_sha256':digest(mn3793.read_bytes()) if mn3793.exists() else None,'missouri_final_passage_sha256':digest(mo_final.read_bytes()) if mo_final.exists() else None,'wy_sf193_disposition_sha256':digest(wy_sf193.read_bytes()) if wy_sf193.exists() else None,'monument_text_overlay_sha256':digest(monument_text.read_bytes()) if monument_text.exists() else None,'wv_carryover_authority_sha256':digest(wv_carryover.read_bytes()) if wv_carryover.exists() else None,'dover_minutes_overlay_sha256':digest(dover_minutes.read_bytes()) if dover_minutes.exists() else None,'indiana_fiscal_overlay_sha256':digest(indiana_fiscal.read_bytes()) if indiana_fiscal.exists() else None,'wyoming_scope_dispositions_sha256':digest(wy_scope_dispositions.read_bytes()) if wy_scope_dispositions.exists() else None,'south_carolina_terminal_overlay_sha256':digest(sc_terminal.read_bytes()) if sc_terminal.exists() else None,'ohio_veto_overlay_sha256':digest(ohio_veto.read_bytes()) if ohio_veto.exists() else None,'wyoming_current_code_overlay_sha256':digest(wy_code.read_bytes()) if wy_code.exists() else None,'montana_hj46_overlay_sha256':digest(montana_hj46.read_bytes()) if montana_hj46.exists() else None,'montana_text_overlay_sha256':digest(montana_text.read_bytes()) if montana_text.exists() else None,'nashville_minutes_overlay_sha256':digest(nashville_minutes.read_bytes()) if nashville_minutes.exists() else None,'lodi_version_overlay_sha256':digest(lodi_version.read_bytes()) if lodi_version.exists() else None,'homewood_minutes_overlay_sha256':digest(homewood_minutes.read_bytes()) if homewood_minutes.exists() else None,'alabama_instruments_overlay_sha256':digest(alabama_instruments.read_bytes()) if alabama_instruments.exists() else None,'utah_versions_overlay_sha256':digest(utah_versions.read_bytes()) if utah_versions.exists() else None,'virginia_numbering_overlay_sha256':digest(virginia_numbering.read_bytes()) if virginia_numbering.exists() else None,'virginia_incorporation_overlay_sha256':digest(virginia_incorporation.read_bytes()) if virginia_incorporation.exists() else None,'utah_signature_overlay_sha256':digest(utah_signature.read_bytes()) if utah_signature.exists() else None,'maryland_trigger_overlay_sha256':digest(maryland_trigger.read_bytes()) if maryland_trigger.exists() else None,'idaho_signature_overlay_sha256':digest(idaho_signature.read_bytes()) if idaho_signature.exists() else None,'proposal_endpoints_overlay_sha256':digest(proposal_endpoints.read_bytes()) if proposal_endpoints.exists() else None,'hawaii_outcome_overlay_sha256':digest(hawaii_outcomes.read_bytes()) if hawaii_outcomes.exists() else None,'committee_detail_overlay_sha256':digest(committee_details.read_bytes()) if committee_details.exists() else None,'nonblank_geography_overlay_sha256':digest(nonblank_geo.read_bytes()) if nonblank_geo.exists() else None,'alaska_terminal_overlay_sha256':digest(alaska_terminal.read_bytes()) if alaska_terminal.exists() else None,'boone_overlay_sha256':digest(boone.read_bytes()) if boone.exists() else None,'starke_overlay_sha256':digest(starke.read_bytes()) if starke.exists() else None,'lee_overlay_sha256':digest(lee.read_bytes()) if lee.exists() else None,'audubon_overlay_sha256':digest(audubon.read_bytes()) if audubon.exists() else None,'coweta_overlay_sha256':digest(coweta.read_bytes()) if coweta.exists() else None,'phillips_overlay_sha256':digest(phillips.read_bytes()) if phillips.exists() else None,'oshtemo_overlay_sha256':digest(oshtemo.read_bytes()) if oshtemo.exists() else None,'sedgwick_publication_overlay_sha256':digest(sedgwick_publication.read_bytes()) if sedgwick_publication.exists() else None,'sedgwick_overlay_sha256':digest(sedgwick.read_bytes()) if sedgwick.exists() else None,'wv_comparison_overlay_sha256':digest(wv_comparison.read_bytes()) if wv_comparison.exists() else None,'connecticut_outcome_overlay_sha256':digest(ct_outcomes.read_bytes()) if ct_outcomes.exists() else None,'arizona_context_overlay_sha256':digest(az_context.read_bytes()) if az_context.exists() else None,'geography_overlay_sha256':digest(geography.read_bytes()) if geography.exists() else None,'records_with_explicit_questions':sum(bool(r['questions']) for r in rows),'records_requiring_disposition_reconciliation':[r['id'] for r in rows if not r['questions']],'local_records':sum(r['dataset']=='local_inventory' for r in rows),'state_policy_records':sum(r['dataset']=='state_policy' for r in rows),'funnel_sha256':digest(fpath.read_bytes()),'review_ledger_sha256':digest(raw),'post_release_additions_sha256':digest(additions.read_bytes()) if additions.exists() else None,'queue_sha256':digest(body),'post_release_overlay_records':sum(r['post_release_overlay'] for r in rows),'overlay_review_sha256':digest(maine.read_bytes()) if maine.exists() else None,'terminal_overlay_sha256':digest(terminal.read_bytes()) if terminal.exists() else None,'procedure_overlay_sha256':digest(procedure.read_bytes()) if procedure.exists() else None,'sponsor_overlay_sha256':digest(sponsor.read_bytes()) if sponsor.exists() else None,'enacted_overlay_sha256':digest(enacted.read_bytes()) if enacted.exists() else None,'local_reconciliation_sha256':digest(local_reconciliation.read_bytes()) if local_reconciliation.exists() else None,'northport_overlay_sha256':digest(northport.read_bytes()) if northport.exists() else None,'pa_history_overlay_sha256':digest(pa_history.read_bytes()) if pa_history.exists() else None,'minnesota_overlay_sha256':digest(minnesota.read_bytes()) if minnesota.exists() else None,'wisconsin_overlay_sha256':digest(wisconsin.read_bytes()) if wisconsin.exists() else None,'ohio_overlay_sha256':digest(ohio.read_bytes()) if ohio.exists() else None,'south_carolina_overlay_sha256':digest(south_carolina.read_bytes()) if south_carolina.exists() else None,'illinois_overlay_sha256':digest(illinois.read_bytes()) if illinois.exists() else None,'nj_final_law_overlay_sha256':digest(nj_final_law.read_bytes()) if nj_final_law.exists() else None,'nj_bpu_report_overlay_sha256':digest(nj_bpu.read_bytes()) if nj_bpu.exists() else None,'nj_a5462_overlay_sha256':digest(nj_a5462.read_bytes()) if nj_a5462.exists() else None,'nj_version_overlay_sha256':digest(nj_version.read_bytes()) if nj_version.exists() else None,'nj_history_overlay_sha256':digest(nj_history.read_bytes()) if nj_history.exists() else None,'ct_rules_overlay_sha256':digest(ct_rules.read_bytes()) if ct_rules.exists() else None,'pa939_overlay_sha256':digest(pa939.read_bytes()) if pa939.exists() else None,'ma_proposal_overlay_sha256':digest(ma_proposal.read_bytes()) if ma_proposal.exists() else None,'ma_amendment_overlay_sha256':digest(ma_amendment.read_bytes()) if ma_amendment.exists() else None,'ny_history_overlay_sha256':digest(ny_history.read_bytes()) if ny_history.exists() else None,'pa_house_history_overlay_sha256':digest(pa_house_history.read_bytes()) if pa_house_history.exists() else None,'pennsylvania_overlay_sha256':digest(pennsylvania.read_bytes()) if pennsylvania.exists() else None,'texas_overlay_sha256':digest(texas.read_bytes()) if texas.exists() else None,'washington_session_overlay_sha256':digest(washington_session.read_bytes()) if washington_session.exists() else None,'oklahoma_overlay_sha256':digest(oklahoma.read_bytes()) if oklahoma.exists() else None,'kentucky_overlay_sha256':digest(kentucky.read_bytes()) if kentucky.exists() else None,'washington_county_overlay_sha256':digest(washington.read_bytes()) if washington.exists() else None,'local_minutes_overlay_sha256':digest(local_minutes.read_bytes()) if local_minutes.exists() else None,'solano_overlay_sha256':digest(solano.read_bytes()) if solano.exists() else None,'monterey_park_overlay_sha256':digest(monterey.read_bytes()) if monterey.exists() else None,'irwindale_overlay_sha256':digest(irwindale.read_bytes()) if irwindale.exists() else None,'covina_overlay_sha256':digest(covina.read_bytes()) if covina.exists() else None,'nh_version_overlay_sha256':digest(nh_version.read_bytes()) if nh_version.exists() else None,'nh_text_overlay_sha256':digest(nh_text.read_bytes()) if nh_text.exists() else None,'wv_authority_overlay_sha256':digest(wv_authority.read_bytes()) if wv_authority.exists() else None,'tennessee_overlay_sha256':digest(tennessee.read_bytes()) if tennessee.exists() else None,'georgia_overlay_sha256':digest(georgia.read_bytes()) if georgia.exists() else None,'ne_transfer_overlay_sha256':digest(ne_transfer.read_bytes()) if ne_transfer.exists() else None,'lb613_overlay_sha256':digest(lb613.read_bytes()) if lb613.exists() else None,'nebraska_overlay_sha256':digest(nebraska.read_bytes()) if nebraska.exists() else None,'wy_retained_overlay_sha256':digest(wy_retained.read_bytes()) if wy_retained.exists() else None,'foley_overlay_sha256':digest(foley.read_bytes()) if foley.exists() else None,'petersburg_overlay_sha256':digest(petersburg.read_bytes()) if petersburg.exists() else None,'alabama_overlay_sha256':digest(alabama.read_bytes()) if alabama.exists() else None,'arizona_overlay_sha256':digest(arizona.read_bytes()) if arizona.exists() else None,'va_wy_overlay_sha256':digest(va_wy.read_bytes()) if va_wy.exists() else None,'colorado_overlay_sha256':digest(colorado.read_bytes()) if colorado.exists() else None,'scope':'Mechanical index of previously recorded residual questions, with explicit published post-release overlays. Not a new source review, factual classification, prioritization or admission of new searches. Retired IDs remain in the identity/disposition history. Held ballot payloads are separately accounted; do not add them as distinct canonical measures.'}
    summary['lb613_introducer_sha256']=digest(lb613_introducer_path.read_bytes()) if lb613_introducer_path.exists() else None
    summary['ma_conference_discovery_sha256']=digest(ma_conference_discovery.read_bytes()) if ma_conference_discovery.exists() else None
    summary['cromwell_later_proposal_sha256']=digest(cromwell_path.read_bytes()) if cromwell_path.exists() else None
    summary['morris_term_review_sha256']=digest(morris_path.read_bytes()) if morris_path.exists() else None
    summary['trumbull_retained_minutes_sha256']=digest(trumbull_path.read_bytes()) if trumbull_path.exists() else None
    summary['west_haven_text_sha256']=digest(west_haven_path.read_bytes()) if west_haven_path.exists() else None
    summary['new_haven_signature_sha256']=digest(new_haven_path.read_bytes()) if new_haven_path.exists() else None
    summary['new_haven_version_comparison_sha256']=digest(new_haven_version_path.read_bytes()) if new_haven_version_path.exists() else None
    summary['independence_operative_term_sha256']=digest(independence_path.read_bytes()) if independence_path.exists() else None
    summary['independence_ordinance19850_sha256']=digest(independence_later_path.read_bytes()) if independence_later_path.exists() else None
    summary['louisiana_hcr61_closing_window_sha256']=digest(la_hcr61_path.read_bytes()) if la_hcr61_path.exists() else None
    summary['washington_enacted_current_law_sha256']=digest(wa_current_path.read_bytes()) if wa_current_path.exists() else None
    summary['kansas_sb51_amendment_order_sha256']=digest(ks_order_path.read_bytes()) if ks_order_path.exists() else None
    summary['kansas_sb51_sb92_publication_sha256']=digest(ks_two_path.read_bytes()) if ks_two_path.exists() else None
    summary['kansas_sb98_publication_sha256']=digest(ks_publication_path.read_bytes()) if ks_publication_path.exists() else None
    summary['wyoming_sf91_fullname_sha256']=digest(wy_fullname_path.read_bytes()) if wy_fullname_path.exists() else None
    summary['wyoming_sf91_api_sha256']=digest(wy_api_path.read_bytes()) if wy_api_path.exists() else None
    summary['kentucky_current_code_sha256']=digest(ky_code_path.read_bytes()) if ky_code_path.exists() else None
    summary['wyoming_hb325_sponsors_sha256']=digest(wy_sponsors_path.read_bytes()) if wy_sponsors_path.exists() else None
    summary['wyoming_session_identity_sha256']=digest(wy_session_path.read_bytes()) if wy_session_path.exists() else None
    summary['fairbanks_recovery_sha256']=digest(fairbanks_recovery.read_bytes()) if fairbanks_recovery.exists() else None
    (args.output/'outstanding-queue-verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
