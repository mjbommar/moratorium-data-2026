#!/usr/bin/env python3
"""Replay the 2026-11-05 pilot into review-stage ledgers; no network or promotion."""
import hashlib
import json
from pathlib import Path
from bc_core.text import locate_quote

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'work/research/2026-11-05'
OUT = BASE / 'normalized-pilot'
MANIFEST_SHA256 = '6e02d209283cec13eb9d852bb50a0df08148cb996be24dba86dce12b437f1f67'
V = '1.0.0'
UNKNOWN_DATE = dict(earliest=None, latest=None, precision='unknown', original_text=None)


def digest(b):
    return hashlib.sha256(b).hexdigest()


def verify_inputs():
    raw = (OUT / 'expected-inputs.json').read_bytes()
    if digest(raw) != MANIFEST_SHA256:
        raise ValueError('expected-inputs manifest drift')
    manifest = json.loads(raw)
    for name, expected in manifest.items():
        path = BASE / name
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise ValueError(f'input drift: {name}')
    return manifest


def main():
    verify_inputs()
    tables = {k: [] for k in ('jurisdictions', 'elections', 'ballot_measures', 'source_documents', 'claims', 'review_decisions', 'measure_results', 'measure_provisions')}
    gaps, originals, sources = [], [], {}
    for pilot in ('maine-pilot', 'ohio-pilot'):
        folder = BASE / pilot

        for line in (folder / 'candidates.jsonl').read_text().splitlines():
            c = json.loads(line); originals.append({'pilot': pilot, 'candidate': c})
            if pilot == 'maine-pilot':
                town = c['measure'].split()[0]; state = 'ME'; key = town.lower(); name = town
                designation = c['designation'].get('value') if c['designation'].get('status') == 'supported_candidate' else None
            else:
                key = c['candidate_key']; state = 'OH'
                town = 'Wilmington' if key.startswith('wilmington') else 'Piqua' if key.startswith('piqua') else 'Grove City'
                name = town; designation = ('Issue 28' if key.startswith('grove') else 'Ordinance ' + key.split('-')[1].upper() + '-' + key.split('-')[2] + '-' + key.split('-')[3] if key.startswith('wilmington') else None)
            jid = f'pilot-{state.lower()}-{town.lower().replace(" ", "-")}'
            mid = 'pilot-' + (key if state == 'OH' else state.lower() + '-' + key)
            eid = jid + '-2026-11-03'
            if not any(r['jurisdiction_id'] == jid for r in tables['jurisdictions']):
                tables['jurisdictions'].append(dict(schema_version=V, jurisdiction_id=jid, name=name, state=state, government_type='unknown', county=None, authoritative_ids={}, aliases=[], boundary_reference=None, valid_from=None, valid_until=None))
                tables['elections'].append(dict(schema_version=V, election_id=eid, jurisdiction_id=jid, election_date=dict(earliest='2026-11-03',latest='2026-11-03',precision='day',original_text='2026-11-03'), administering_authority='unknown', election_type='unknown', official_result_urls=[]))
            title = (c.get('measure', {}).get('value') if state == 'OH' else {'Peru': 'Temporary Moratorium of the Development and Permitting of Data Centers', 'Wells': 'An Ordinance to Establish a Retroactive Moratorium on Data Centers', 'Wiscasset': 'Data Center Moratorium'}[town])
            wording = c.get('ballot_wording', {}).get('value')
            tables['ballot_measures'].append(dict(schema_version=V, measure_id=mid, jurisdiction_id=jid, election_id=eid, designation=designation, wording=wording, title=title, placement_method='unknown', lifecycle='voted', bindingness='unresolved', sectors=[], yes_direction='unresolved', referendum_yes_effect='unresolved', scope_note='Review-stage candidate; identity and legal effect require review.'))
            gaps.append({'measure_id':mid, 'gap':'Legal effect, administration, and any links to other instruments require separate review; see retained candidate for field-specific gaps.'})
            # Extra substantive excerpts tie results and interpretation to source artifacts.
            if town == 'Wells':
                c['certificate_result'] = {'value': {'yes':5818,'no':1282,'blank':459,'certification_date':'2026-11-04'}, 'evidence':[{'artifact':'wells-results.private.pdf','url':'https://www.wellstown.org/DocumentCenter/View/8559/November-3-2026-Official-Election-Results?bidId=','quote':'ARTICLE 5. Shall an ordinance entitled, “An Ordinance to Establish a Retroactive Moratorium on Data\nCenters” be enacted?\n\nYES: 5818\nNO: 1282\nBlank: 459','location':'page 2 OCR; coordinator visually reviewed pages 1 and 2 and handwritten certification date'}]}
            if town == 'Wiscasset':
                raw=(folder/'wiscasset-results.private.html').read_text()
                start=raw.index('2. Data Center Moratorium'); end=raw.index('</ul>',start)+5
                c['result_table']={'value':{'yes':1363,'no':712},'evidence':[{'artifact':'wiscasset-results.private.html','url':'https://www.wiscasset.gov/m/newsflash/Home/Detail/211','quote':raw[start:end],'location':'town unofficial results'}]}
                start=raw.index('Total Ballots Cast:'); end=raw.index('</span>',start)+7
                c['ballots_cast']={'value':2155,'evidence':[{'artifact':'wiscasset-results.private.html','url':'https://www.wiscasset.gov/m/newsflash/Home/Detail/211','quote':raw[start:end],'location':'town unofficial results'}]}
            if town == 'Wilmington':
                c['reported_yes_meaning']={'value':'A yes vote approved the zoning change, according to the newspaper; legal referendum effect unresolved','evidence':[{'artifact':'wilmington-news.private.txt','url':'https://www.wnewsj.com/2026/11/03/wilmington-voters-reject-four-rezoning-ordinances/','quote':'A yes vote approved the zoning change, while a no vote rejected it and retained the rural residential classification.','location':'newspaper report'}]}
            # Every excerpt is a source assertion, not an endorsement of its candidate value.
            for field, obj in c.items():
                if not isinstance(obj, dict): continue
                for evidence in obj.get('evidence', []):
                    artifact = evidence.get('artifact'); q = evidence.get('quote', evidence.get('exact_short_quote'))
                    if not artifact or not q: continue
                    if len(q.strip()) < 12:
                        gaps.append({'measure_id':mid,'field':field,'gap':'Short label omitted; substantive evidence required','artifact':artifact}); continue
                    body_path = folder / artifact
                    stem = artifact.split('.private')[0]
                    text_path = folder / (stem + '.private.txt')
                    if stem == 'wells-results': text_path = folder / 'wells-results-page.private-2.txt'
                    if not text_path.exists(): text_path = body_path
                    meta_path = folder / (stem + '.private.json')
                    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
                    if artifact.endswith('.txt'):
                        body_path = folder / (stem + '.private.body')
                    if not body_path.exists() or not text_path.exists():
                        gaps.append({'measure_id':mid,'field':field,'gap':'Source body or extracted text unavailable','artifact':artifact}); continue
                    text = text_path.read_text(encoding='utf-8')
                    span = locate_quote(text, q)
                    if span is None:
                        gaps.append({'measure_id':mid,'field':field,'gap':'Quote not located in stored text; visual/OCR review retained in original candidate','artifact':artifact,'source_scope':evidence.get('location')}); continue
                    a,b = span; exact = text[a:b]
                    # Reject approximate matches: emitted quote is always the exact source slice.
                    body_hash=digest(body_path.read_bytes()); text_hash=digest(text.encode('utf-8'))
                    expected_body = meta.get('body_sha256') or meta.get('content_sha256') or evidence.get('body_sha256') or evidence.get('sha256')
                    expected_text = meta.get('text_sha256') or evidence.get('text_sha256')
                    if expected_body and expected_body != body_hash: raise ValueError(f'sidecar body hash mismatch: {body_path}')
                    if expected_text and expected_text != text_hash: raise ValueError(f'sidecar text hash mismatch: {text_path}')
                    sid='pilot-source-'+body_hash[:20]+'-'+text_hash[:12]
                    if sid not in sources:
                        retrieved = meta.get('fetched_at')
                        if not retrieved:
                            gaps.append({'measure_id':mid,'field':field,'gap':'Retrieval timestamp unavailable','artifact':artifact}); continue
                        sources[sid]=dict(schema_version=V, source_document_id=sid,url=evidence['url'],body_sha256=body_hash,text_sha256=text_hash,retrieved_at=retrieved,published_date=None,retrieval_method=meta.get('engine') or 'pilot stored retrieval',extraction_version='stored text; no re-extraction',access_classification='private pending classification',publication_classification='private pending classification')
                    cid='pilot-claim-'+digest((mid+'\0'+field+'\0'+sid+'\0'+str(a)+'\0'+str(b)).encode())[:24]
                    if any(r['claim_id']==cid for r in tables['claims']): continue
                    tables['claims'].append(dict(schema_version=V,claim_id=cid,subject={'table':'ballot_measures','id':mid},predicate='source_excerpt:'+field,value=(obj.get('value') if field in ('certificate_result','result_table','ballots_cast','reported_yes_meaning') else exact),source_document_id=sid,quote=exact,span=f'utf8-text-codepoints:{a}:{b}',temporal_support=UNKNOWN_DATE,extraction_provenance=f'bc_core.text.locate_quote; {text_path.relative_to(BASE)}; source location: {evidence.get("location", "not specified")}'))
    # Emit the four Clinton observations only when the full table row and totals
    # are directly located in the pinned election-results text.
    text_path = BASE / 'ohio-pilot/clinton-results.private.txt'
    result_text = text_path.read_text(encoding='utf-8')
    import re
    for row in tables['ballot_measures']:
        mid = row['measure_id']
        match = re.search(r'wilmington-o-26-(0[4-7])-2026$', mid)
        if not match: continue
        label = 'Wilmington Referendum Ordinance O-26-' + match.group(1)
        pos = result_text.find(label)
        block = result_text[pos:result_text.find('\n\n', pos)] if pos >= 0 else ''
        counts = re.search(r'\n\s*YES\s+(\d+)[^\n]*\n\s*NO\s+(\d+)', block)
        span = locate_quote(result_text, block) if block else None
        sid = next((s['source_document_id'] for s in sources.values() if s['url'].endswith('/20261103results.pdf')), None)
        if not counts or not span or not sid:
            gaps.append({'measure_id':mid,'gap':'Could not locate result table and source'}); continue
        yes, no = map(int, counts.groups())
        cid = 'pilot-result-claim-' + match.group(1)
        tables['claims'].append(dict(schema_version=V,claim_id=cid,subject={'table':'ballot_measures','id':mid},predicate='source_result_table',value={'yes':yes,'no':no},source_document_id=sid,quote=block,span=f'utf8-text-codepoints:{span[0]}:{span[1]}',temporal_support=UNKNOWN_DATE,extraction_provenance='bc_core.text.locate_quote; ohio-pilot/clinton-results.private.txt; election return table'))
        tables['measure_results'].append(dict(schema_version=V,result_observation_id=mid+'-result',measure_id=mid,source_document_id=sid,observed_at=sources[sid]['retrieved_at'],published_at=None,yes_votes=yes,no_votes=no,other_votes=None,valid_votes=None,ballots_cast=None,registered_voters=None,undervotes=None,overvotes=None,precincts_reporting=None,precincts_total=None,source_yes_percent=None,percentage_denominator='unknown',passage_threshold=None,threshold_comparison='unknown',reported_outcome='unknown',calculated_outcome='unknown',outcome_direction='unresolved',reporting_status='unknown',certification_status='unofficial',certification_date=None,supersedes_id=None))
    # Results are source observations; totals and legal effect are independent.
    by_mid = {r['measure_id']: r for r in tables['ballot_measures']}
    def source_for(mid, field):
        claim = next((x for x in tables['claims'] if x['subject']['id'] == mid and x['predicate'] == 'source_excerpt:'+field), None)
        return sources.get(claim['source_document_id']) if claim else None
    for mid, field, yes, no, ballots, pct, cert, date in [
        ('pilot-me-peru','outcome',578,182,None,None,'unknown',None),
        ('pilot-me-wells','certificate_result',5818,1282,None,None,'certified','2026-11-04'),
        ('pilot-me-wiscasset','result_table',1363,712,2155,None,'unofficial',None),
        ('pilot-grove-city-issue-28-2026','result',None,None,None,54.61,'unofficial',None),
        ('pilot-piqua-charter-2026','yes_votes',4061,2027,None,None,'unknown',None),
    ]:
        src=source_for(mid,field)
        if not src:
            gaps.append({'measure_id':mid,'field':'result','gap':'Substantive source claim unavailable'}); continue
        tables['measure_results'].append(dict(schema_version=V,result_observation_id=mid+'-result',measure_id=mid,source_document_id=src['source_document_id'],observed_at=src['retrieved_at'],published_at=None,yes_votes=yes,no_votes=no,other_votes=None,valid_votes=None,ballots_cast=ballots,registered_voters=None,undervotes=None,overvotes=None,precincts_reporting=None,precincts_total=None,source_yes_percent=pct,percentage_denominator='unknown',passage_threshold=None,threshold_comparison='unknown',reported_outcome='unknown',calculated_outcome='unknown',outcome_direction='unresolved',reporting_status='unknown',certification_status=cert,certification_date=date,supersedes_id=None))
    for mid, row in by_mid.items():
        claims=[x for x in tables['claims'] if x['subject']['id']==mid]
        relevant=[x['claim_id'] for x in claims if x['predicate'] in ('source_excerpt:duration','source_excerpt:threshold','source_excerpt:scope','source_excerpt:mechanism','source_excerpt:reported_yes_meaning','source_excerpt:applicability_date')]
        if relevant:
            thresholds=[]
            if mid=='pilot-me-wells':
                thresholds=[dict(operator='ge',value=100000,unit='square feet',measurement_basis='Data Center Area as defined',aggregation_rule='aggregate',scope='definition of Data Center')]
            descriptions={'pilot-me-wells':'Warrant candidate: retroactive applicability on or after June 16, 2026; 180 days from Date of Applicability; immediate effect upon enactment. Legal force unresolved.', 'pilot-me-wiscasset':'Guide candidate: six calendar months after enactment, subject to earlier lifting or extension; applicability to applications filed on or after November 3, 2026.', 'pilot-me-peru':'Ordinance candidate: 180 days from effective date; effect upon passage.'}
            mechanism = ('temporary_permitting_pause' if mid in ('pilot-me-wells','pilot-me-wiscasset') else
                         'voter_approval_requirement' if 'grove-city' in mid else
                         'zoning_change' if 'wilmington' in mid else 'unresolved')
            tables['measure_provisions'].append(dict(schema_version=V,provision_id=mid+'-provision',measure_id=mid,mechanism=mechanism,bindingness='unresolved',covered_uses=[],thresholds=thresholds,exemptions=[],geography=None,implementation_requirements=descriptions.get(mid),claim_ids=relevant))
    for provision in tables['measure_provisions']:
        mid=provision['measure_id']
        if mid=='pilot-me-wells':
            provision['duration']=dict(value=180,unit='days',anchor='applicability_date',anchor_date=dict(earliest='2026-06-16',latest='2026-06-16',precision='day',original_text='June 16, 2026'),original_text='180 days from the Date of Applicability')
        elif mid=='pilot-me-wiscasset':
            provision['duration']=dict(value=6,unit='calendar_months',anchor='adoption',anchor_date=None,original_text='six months after enactment; subject to earlier lifting or extension')
    for result in tables['measure_results']:
        mid=result['measure_id']
        ids=[c['claim_id'] for c in tables['claims'] if c['subject']['id']==mid and ('result' in c['predicate'] or c['predicate'].endswith(('yes_votes','no_votes','outcome')))]
        y,n=result['yes_votes'],result['no_votes']
        result['yes_no_votes']=y+n if y is not None and n is not None else None
        result['blank_votes']=459 if mid=='pilot-me-wells' else None
        result['value_methods']={'yes_no_votes':dict(method='derived',claim_ids=ids,note='Arithmetic sum of yes/no observations; not election turnout or assumed total valid votes.')}
        if mid=='pilot-me-wells':
            result['value_methods'].update({field:dict(method='visual',claim_ids=ids,note='Coordinator inspected certificate pages1/2; see pilot-review.md. Handwritten date not represented as machine-located OCR.') for field in ('yes_votes','no_votes','blank_votes','certification_date')})
    gaps.extend([{'measure_id':'pilot-me-wells','gap':'Certificate date and blank count visually reviewed by coordinator; OCR text does not locate the handwritten date. Blank votes are separate; no overvote or election turnout established.'}, {'gap':'Schema requires retrieved_at and observed_at; sources missing actual retrieval time are omitted, never assigned run completion.'}, {'gap':'Review decisions require a precise decided_at timestamp; coordinator review records only a date, so no timestamp is fabricated. Legal effect, identity links, and adoption remain unresolved.'}])
    tables['source_documents'] = sorted(sources.values(),key=lambda x:x['source_document_id'])
    for name, rows in tables.items():
        (OUT / (name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    (OUT/'candidates.private.json').write_text(json.dumps(originals,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (OUT/'gaps.json').write_text(json.dumps(gaps,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f"{len(tables['ballot_measures'])} candidates; {len(tables['claims'])} located excerpts; {len(gaps)} gaps")

if __name__ == '__main__': main()
