#!/usr/bin/env python3
"""Score a frozen prospective rule-unit population; see rule-unit-trial-scoring.md."""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


EXPOSED_VA = set('cdd0f5f52f700c0a354f8bbecaaf2efe4a19c45ce3b2f85690901f2a0ac74fa7 d3c3d980a2b54005cfd1ad44f4bfeaa6c13a212b874e9ac984a103ead3c5ab29 c6b5ca75cafd1f4934d0c706b5c048c486f7560f8bf2b825cb761df3e5bb5434 174856a626bb17d4b85d466dd5be8d516617f5e208360a4990128a5d69024230 63929cbcb6d9faff95b2eef84beacdb5a6ab24aac502a100067e83793f7daea1 dadd36cac8fa18822c45daf73457c66e6562e7d65e5d90ca7df88225878c31c3'.split())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()


def text_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def unique(pairs):
    d = {}
    for k, v in pairs:
        if k in d: raise ValueError('duplicate JSON key: ' + k)
        d[k] = v
    return d


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique)


def timestamp(s):
    d = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if d.tzinfo is None: raise ValueError('timestamp must include timezone')
    return d


def keys(items, field):
    values = [x[field] for x in items]
    if any(not isinstance(x, str) or not x for x in values) or len(values) != len(set(values)):
        raise ValueError('empty or duplicate ' + field)
    return set(values)


def ratio(n, d):
    return {'numerator': n, 'denominator': d, 'pass': d > 0 and 100*n >= 95*d}


def score(protocol, anchor, cases, judgments, judgment_anchor):
    gaps = []
    def need(ok, why):
        if not ok and why not in gaps: gaps.append(why)
    if digest(protocol) != anchor or digest(judgments) != judgment_anchor:
        raise ValueError('protocol or judgments anchor mismatch')
    if protocol.get('schema_version') != 'rule-unit-scoring-protocol-1' or judgments.get('schema_version') != 'rule-unit-scoring-judgments-1':
        raise ValueError('unsupported contract')
    # The frozen protocol contains no threshold overrides. Thresholds are fixed in code.
    if not {'schema_version','freeze_time','first_dispatch_time','reference_provenance','exposure_provenance','cases'} <= set(protocol) or set(protocol) - {'schema_version','freeze_time','first_dispatch_time','reference_provenance','exposure_provenance','calibration_complete_time','cases'}:
        raise ValueError('invalid protocol fields')
    freeze, dispatch = map(timestamp, (protocol['freeze_time'], protocol['first_dispatch_time']))
    if protocol.get('calibration_complete_time'): timestamp(protocol['calibration_complete_time'])
    need(freeze < dispatch, 'freeze chronology invalid')
    for k in ('reference_provenance', 'exposure_provenance'):
        v = protocol[k]
        need(isinstance(v, str) and bool(v.strip()), 'missing ' + k)
    pcases = protocol['cases']; case_ids = keys(pcases, 'case_id')
    need(keys(cases, 'case_id') <= case_ids, 'extra case data')
    need(all(x.get('split') in ('calibration','holdout') for x in pcases) and any(x.get('split') == 'holdout' for x in pcases), 'invalid split or missing holdout')
    jrows = judgments.get('cases', [])
    need(keys(jrows, 'case_id') <= case_ids, 'extra judgment cases')
    results = {}
    methods = []
    global_gaps = list(gaps)
    bycase = {x['case_id']:x for x in cases}; byj = {x['case_id']:x for x in jrows}
    for split in ('calibration', 'holdout'):
        totals = dict(generated=0, supported=0, change_units=0, complete_change_units=0, change_slots=0, covered_change_slots=0, required_slots=0, covered_required_slots=0, high_impact=0, unresolved=0)
        start_gaps = len(gaps)
        unit_reports = []
        for spec in [c for c in pcases if c.get('split') == split]:
            cid = spec['case_id']; data = bycase.get(cid); j = byj.get(cid)
            if not data:
                need(False, 'missing case data: ' + cid)
                for unit in spec['units']:
                    n = len(unit['slots']); kind = unit['kind']
                    totals['required_slots'] += n
                    if kind == 'change': totals['change_units'] += 1; totals['change_slots'] += n
                    unit_reports.append(dict(case_id=cid,family=spec['family'],unit_id=unit['unit_id'],kind=kind,slots=n,covered_slots=0,complete=False,scorable=False))
                continue
            if not j: need(False, 'missing judgments: ' + cid)
            j = j or {}
            expected_fields = {'case_id','split','family','source_text_sha256','source_body_sha256','context_sha256','plan_sha256','reference_sha256','role','exposure','units'}
            if set(spec) != expected_fields: raise ValueError('invalid case specification: ' + cid)
            need(isinstance(spec['exposure'], str) and bool(spec['exposure'].strip()), 'missing exposure disclosure: ' + cid)
            need(isinstance(spec['family'], str) and bool(spec['family']), 'missing family: ' + cid)
            audit, packet, document, reference, context = (data[k] for k in ('audit','packet','document','reference','context'))
            need(digest(context) == spec['context_sha256'] and context.get('document') == document and digest(context.get('plan')) == spec['plan_sha256'], 'frozen context mismatch: ' + cid)
            method_keys = ('model_identity','settings','schema','system','role')
            need(all(k in context for k in method_keys), 'method context missing: ' + cid)
            if split == 'holdout': methods.append({k:context.get(k) for k in method_keys})
            hashes = audit.get('evidence_hashes', {})
            need(digest(audit) == j.get('audit_sha256'), 'audit hash mismatch: ' + cid)
            need(audit.get('schema_version') == 'native-rule-unit-reconciliation-1' and audit.get('status') == 'complete' and not audit.get('errors') and all(audit.get(k) is True for k in ('response_accounting_complete','structural_evidence_complete','planned_trace_complete','prospective_anchor_verified','wire_contract_complete','endpoint_identity_complete')), 'incomplete audit: ' + cid)
            for k in ('source_text_sha256','source_body_sha256','context_sha256','plan_sha256'):
                need(hashes.get(k) == spec[k], 'audit ' + k + ' mismatch: ' + cid)
            need(digest(packet) == j.get('packet_sha256') == hashes.get('packet_canonical_sha256'), 'packet hash mismatch: ' + cid)
            need(digest(reference) == spec['reference_sha256'], 'reference hash mismatch: ' + cid)
            need(reference.get('source_text_sha256') == spec['source_text_sha256'] and reference.get('source_body_sha256') == spec['source_body_sha256'] and reference.get('role') == spec['role'] and isinstance(reference.get('provenance'), str) and bool(reference['provenance'].strip()), 'reference source or provenance mismatch: ' + cid)
            need(text_hash(document['text']) == spec['source_text_sha256'] and document.get('body_sha256') == spec['source_body_sha256'] and document.get('reviewed_source_role') == spec['role'] and packet.get('provenance', {}).get('reviewed_source_role') == spec['role'], 'source or role mismatch: ' + cid)
            uidset = keys(spec['units'], 'unit_id')
            need(keys(context.get('plan', {}).get('units', []), 'unit_id') == uidset and context['plan'].get('source_text_sha256') == spec['source_text_sha256'], 'plan population mismatch: ' + cid)
            packetids = keys(packet['units'], 'unit_id')
            need(uidset == packetids == keys(audit.get('plans', []), 'unit_id') == keys(reference['units'], 'unit_id') == (keys(j.get('units', []), 'unit_id') if j.get('units') else set()), 'unit population mismatch: ' + cid)
            need(packet.get('context_sha256') == spec['context_sha256'] and packet.get('plan_sha256') == spec['plan_sha256'] and packet.get('source_text_sha256') == spec['source_text_sha256'] and packet.get('source_body_sha256') == spec['source_body_sha256'], 'packet identity mismatch: ' + cid)
            for extra in (x for x in packet['units'] if x['unit_id'] not in uidset):
                extra_raw = extra.get('original_output')
                extra_enumerable = isinstance(extra_raw, dict) and 'clause' in extra_raw and (extra_raw['clause'] is None or isinstance(extra_raw['clause'], dict))
                need(extra_enumerable, 'unscorable clause enumeration: ' + cid + '/' + extra['unit_id'])
                if extra_enumerable and extra_raw['clause'] is not None: totals['generated'] += 1
            pu = {x['unit_id']:x for x in packet['units']}; ru = {x['unit_id']:x for x in reference['units']}; ju = {x['unit_id']:x for x in j.get('units', [])}
            for unit in spec['units']:
                unit_gap_start = len(gaps)
                uid = unit['unit_id']; p = pu.get(uid); ref = ru.get(uid); review = ju.get(uid)
                if unit.get('kind') not in ('change','control'): raise ValueError('invalid unit kind')
                slots = unit['slots']; slotids = keys(slots, 'slot_id')
                need(bool(slotids), 'empty slot inventory: ' + cid + '/' + uid)
                if unit['kind'] == 'change': totals['change_units'] += 1; totals['change_slots'] += len(slotids)
                totals['required_slots'] += len(slotids)
                raw = p.get('original_output') if p else None
                enumerable = isinstance(raw, dict) and 'clause' in raw and (raw['clause'] is None or isinstance(raw['clause'], dict))
                need(enumerable, 'unscorable clause enumeration: ' + cid + '/' + uid)
                clause = raw.get('clause') if enumerable else None
                if clause is not None: totals['generated'] += 1
                report = dict(case_id=cid,family=spec['family'],unit_id=uid,kind=unit['kind'],slots=len(slotids),covered_slots=0,complete=False,scorable=False,quote_locations=[],nonextractable_issues=[],errors=[],disagreements=[])
                unit_reports.append(report)
                if isinstance(clause, dict):
                    citations = []
                    def visit_early(x):
                        if isinstance(x, dict):
                            for k, v in x.items():
                                if k == 'source_text': citations.append(v)
                                visit_early(v)
                        elif isinstance(x, list):
                            for v in x: visit_early(v)
                    visit_early(clause)
                    quotes = raw.get('supporting_quotes')
                    quotes_valid = isinstance(quotes, list) and bool(quotes) and all(isinstance(q, str) and q for q in quotes)
                    need(quotes_valid, 'invalid supporting quote container: ' + cid + '/' + uid)
                    if quotes_valid: citations += quotes
                    for q in citations:
                        offsets = [i for i in range(len(document['text'])) if isinstance(q, str) and q and document['text'].startswith(q, i)]
                        report['quote_locations'].append({'quote':q,'source_text_sha256':spec['source_text_sha256'],'occurrences':[{'start':i,'end':i+len(q)} for i in offsets]})
                if not p or not ref or not review:
                    need(False, 'missing unit data: ' + cid + '/' + uid); continue
                def safe_slots(value, label):
                    if not isinstance(value, list):
                        need(False, 'invalid ' + label + ' slots: ' + cid + '/' + uid); return []
                    valid = []
                    seen = set()
                    for item in value:
                        sid = item.get('slot_id') if isinstance(item, dict) else None
                        if not isinstance(sid, str) or not sid or sid in seen:
                            need(False, 'invalid ' + label + ' slots: ' + cid + '/' + uid); continue
                        seen.add(sid); valid.append(item)
                    return valid
                refslots = safe_slots(ref.get('slots'), 'reference')
                reviewslots = safe_slots(review.get('slots'), 'review')
                need(keys(refslots, 'slot_id') == slotids and all(isinstance(x.get('evidence'), str) and x['evidence'].strip() for x in refslots), 'reference slots or evidence missing: ' + cid + '/' + uid)
                need(keys(reviewslots, 'slot_id') == slotids, 'judged slot population mismatch: ' + cid + '/' + uid)
                raw = p.get('original_output'); clause = raw.get('clause') if isinstance(raw, dict) else None
                need(isinstance(raw, dict) and p.get('output_sha256') == digest(raw), 'unscorable output pin: ' + cid + '/' + uid)
                # A reviewer supplies source-grounded decisions and provenance; IDs alone are insufficient.
                provenance = review.get('provenance', {})
                need(all(isinstance(provenance.get(k), str) and provenance[k].strip() for k in ('reviewer','independence_basis','source_evidence','adjudication')), 'review provenance missing: ' + cid + '/' + uid)
                need(review.get('output_sha256') == p.get('output_sha256') and review.get('reference_sha256') == spec['reference_sha256'], 'judgment pin mismatch: ' + cid + '/' + uid)
                high = review.get('high_impact'); support = review.get('support')
                need(high in ('yes','no','uncertain') and support in ('supported','unsupported','uncertain','no_clause'), 'invalid judgment: ' + cid + '/' + uid)
                if high == 'yes': totals['high_impact'] += 1
                if high == 'uncertain' or support == 'uncertain': totals['unresolved'] += 1; need(False, 'unresolved judgment: ' + cid + '/' + uid)
                need((clause is None) == (support == 'no_clause'), 'clause judgment mismatch: ' + cid + '/' + uid)
                literal = False
                if isinstance(clause, dict):
                    literal = quotes_valid and bool(report['quote_locations']) and all(len(x['occurrences']) == 1 for x in report['quote_locations'])
                    need(bool(clause.get('source_text')), 'clause source_text missing: ' + cid + '/' + uid)
                    if spec['role'] == 'proposed' and clause.get('assertion_context') == 'enacted_text': need(False, 'source role conflict: ' + cid + '/' + uid)
                valid = literal and support == 'supported'
                if clause is not None and valid: totals['supported'] += 1
                def locators_ok(locators):
                    return isinstance(locators, list) and bool(locators) and all(isinstance(x, dict) and isinstance(x.get('quote'), str) and bool(x['quote']) and type(x.get('start')) is int and type(x.get('end')) is int and 0 <= x['start'] < x['end'] <= len(document['text']) and document['text'][x['start']:x['end']] == x['quote'] and sum(document['text'].startswith(x['quote'], i) for i in range(len(document['text']))) == 1 for x in locators)
                issues = ref.get('nonextractable_issues')
                need(isinstance(issues, list) and all(isinstance(x, dict) and all(isinstance(x.get(k), str) and x[k].strip() for k in ('field','issue')) and locators_ok(x.get('source_locators')) for x in issues), 'invalid nonextractable inventory: ' + cid + '/' + uid)
                issue_reviews = review.get('nonextractable_reviews')
                need(isinstance(issue_reviews, list) and isinstance(issues, list) and len(issue_reviews) == len(issues) and all(isinstance(x, dict) and isinstance(x.get('field'), str) and isinstance(x.get('assessment'), str) and x['assessment'].strip() and locators_ok(x.get('source_locators')) for x in issue_reviews) and all(isinstance(x, dict) and isinstance(x.get('field'), str) for x in issues) and sorted(x['field'] for x in issue_reviews) == sorted(x['field'] for x in issues), 'invalid nonextractable review: ' + cid + '/' + uid)
                errors = review.get('errors'); disagreements = review.get('disagreements')
                need(isinstance(errors, list) and all(isinstance(x, dict) and x.get('category') in ('polarity_modal_reversal','scope_actor_misbinding','missing_exception_condition','incorrect_threshold_date','unsupported_legal_status','invented_consequential_fact') and isinstance(x.get('description'), str) and x['description'].strip() and locators_ok(x.get('source_locators')) for x in errors) and (high == 'yes') == bool(errors), 'invalid high-impact error evidence: ' + cid + '/' + uid)
                need(isinstance(disagreements, list) and all(isinstance(x, dict) and all(isinstance(x.get(k), str) and x[k].strip() for k in ('issue','resolution','adjudicator','independence_basis')) and x.get('status') == 'resolved' and x.get('adjudicator') != provenance.get('reviewer') and locators_ok(x.get('source_locators')) for x in disagreements), 'invalid disagreement adjudication: ' + cid + '/' + uid)
                if high == 'yes' and isinstance(errors, list): totals['high_impact'] += max(0, len(errors) - 1)
                report.update(nonextractable_issues=issues,nonextractable_reviews=issue_reviews,errors=errors,disagreements=disagreements)
                slotmap = {x['slot_id']:x for x in reviewslots}; refmap = {x['slot_id']:x for x in refslots}; covered = 0
                for sid in slotids:
                    s = slotmap.get(sid, {}); decision = s.get('decision')
                    need(decision in ('covered','uncovered','uncertain') and isinstance(s.get('evidence'), str) and bool(s['evidence'].strip()), 'missing slot judgment or evidence: ' + cid + '/' + uid + '/' + sid)
                    if decision == 'uncertain': totals['unresolved'] += 1; need(False, 'unresolved slot: ' + cid + '/' + uid + '/' + sid)
                    rs = refmap.get(sid, {})
                    structured = (isinstance(rs.get('proposition'), str) and bool(rs['proposition'].strip()) and isinstance(rs.get('qualifications'), list) and all(isinstance(q, str) and q.strip() for q in rs['qualifications']) and locators_ok(rs.get('source_locators')) and isinstance(s.get('rationale'), str) and bool(s['rationale'].strip()) and locators_ok(s.get('source_locators')))
                    need(structured, 'invalid structured slot support: ' + cid + '/' + uid + '/' + sid)
                    evidence = s.get('clause_evidence')
                    matched = isinstance(evidence, str) and bool(evidence.strip()) and isinstance(clause, dict) and evidence in json.dumps(clause, ensure_ascii=False)
                    if decision == 'covered': need(matched, 'slot clause evidence mismatch: ' + cid + '/' + uid + '/' + sid)
                    covered += int(decision == 'covered' and structured and matched)
                report.update(covered_slots=covered, complete=covered == len(slotids), scorable=len(gaps) == unit_gap_start, slot_judgments=reviewslots)
                totals['covered_required_slots'] += covered
                if unit['kind'] == 'change':
                    totals['covered_change_slots'] += covered
                    totals['complete_change_units'] += int(covered == len(slotids))
        metrics = {'support':ratio(totals['supported'],totals['generated']), 'change_unit_coverage':ratio(totals['complete_change_units'],totals['change_units']), 'change_slot_coverage':ratio(totals['covered_change_slots'],totals['change_slots']), 'required_slot_coverage':ratio(totals['covered_required_slots'],totals['required_slots'])}
        metrics['required_slot_coverage'].pop('pass')
        split_gaps = gaps[start_gaps:]
        incomplete = bool(global_gaps or split_gaps)
        if incomplete:
            for name, m in metrics.items():
                if name != 'required_slot_coverage': m['pass'] = None
        metrics['support']['denominator_complete'] = not any('unscorable clause enumeration' in g or 'missing case data' in g for g in split_gaps)
        totals['high_impact_complete'] = not incomplete
        def aggregate(rows):
            out = {}
            for label in ('pooled','change','control'):
                group = [u for u in rows if label == 'pooled' or u['kind'] == label]
                out[label] = {'units':len(group), 'complete_units':sum(u['complete'] for u in group), 'slots':sum(u['slots'] for u in group), 'covered_slots':sum(u['covered_slots'] for u in group)}
                out[label]['unit_rate'] = out[label]['complete_units'] / len(group) if group else None
                out[label]['slot_rate'] = out[label]['covered_slots'] / out[label]['slots'] if out[label]['slots'] else None
            return out
        families = {family:aggregate([u for u in unit_reports if u['family'] == family]) for family in sorted({u['family'] for u in unit_reports})}
        results[split] = {'counts':totals, 'metrics':metrics, 'coverage':aggregate(unit_reports), 'families':families, 'units':unit_reports, 'review_complete':not incomplete, 'gaps':split_gaps, 'thresholds_pass': None if incomplete else all(metrics[k]['pass'] for k in ('support','change_unit_coverage','change_slot_coverage')) and totals['high_impact'] == 0 and totals['unresolved'] == 0}
    need(bool(methods) and all(m == methods[0] for m in methods), 'holdout method mismatch')
    method_gap = 'holdout method mismatch' in gaps
    if method_gap:
        results['holdout']['thresholds_pass'] = None
        results['holdout']['review_complete'] = False
        for name, metric in results['holdout']['metrics'].items():
            if name != 'required_slot_coverage': metric['pass'] = None
    threshold_result = 'not_scored' if global_gaps or results['holdout']['gaps'] or method_gap else ('pass' if results['holdout']['thresholds_pass'] else 'fail')
    acceptance = 'fail' if threshold_result == 'fail' else 'not_scored'
    return {'schema_version':'rule-unit-trial-score-1','acceptance':acceptance,'threshold_result':threshold_result,'gaps':gaps,'splits':results,'p4_acceptance':'not_scored','p4_prerequisite':'The broader explicitly required P4 discovery, source recovery, behavioral and other gates are not established.', 'limitations':['Anchors and provenance are externally supplied; hashes do not authenticate history or prove independence.','Exposure labels and hashes are disclosures, not evidence of independent holdout status; the historical VA trial remains failed and spent.','Original terms and source roles do not establish current legal force.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('protocol','protocol-anchor','cases','judgments','judgment-anchor'): p.add_argument('--'+name, required=True)
    a = p.parse_args()
    try:
        result = score(load(a.protocol), a.protocol_anchor, load(a.cases), load(a.judgments), a.judgment_anchor)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        p.exit(2, 'Invalid scoring input: ' + str(exc) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
