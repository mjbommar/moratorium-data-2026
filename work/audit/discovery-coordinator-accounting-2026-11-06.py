import json,hashlib,collections
from pathlib import Path
root=Path.cwd();h=lambda b:hashlib.sha256(b).hexdigest();lp=Path('work/audit/discovery-candidate-review-2026-11-06.json');raw=lp.read_bytes();l=json.loads(raw);packets={};rows=[];proofs={};buckets=collections.Counter();keys=[]
for c in l['candidates']:
 key=c['candidate_key'];keys.append(key);status=c['disposition']
 if status=='unreviewed':bucket='awaiting_coordinator_review'
 elif status.startswith('held_') or status=='unresolved_historical_proposal':bucket='reviewed_withheld'
 elif status=='covered_by_existing_reviewed_instrument':bucket='covered_existing'
 elif status in {'reviewed_pending_proposal_added','reviewed_historical_instrument_added','reviewed_historical_addition','reviewed_later_solar_instrument_added_earlier_act_held','reviewed_reported_active_added','reviewed_city_reported_adoption_added','reviewed_adopted_instrument_added'}:bucket='reviewed_addition'
 else:raise ValueError('Unrecognized coordinator disposition: '+status)
 buckets[bucket]+=1
 if bucket=='awaiting_coordinator_review':continue
 p=Path(c['review_packet']);assert p.is_file();x=json.loads(p.read_bytes());packets[str(p)]=h(p.read_bytes());matched=[v for v in x.get('candidates',[]) if v.get('candidate_key')==key] if isinstance(x.get('candidates'),list) else []
 if matched:
  assert len(matched)==1;review=matched[0];assert review['candidate_sha256']==c['candidate_sha256'];assert review.get('rationale');sourcechecks=review.get('source_checks',review.get('retained_source_versions',[]));assert sourcechecks
  for s in sourcechecks:
   assert all(s.get(f) for f in ['body_sha256','text_sha256','attempt_id','url']);proofs[(s['attempt_id'],s['body_sha256'],s['text_sha256'])]=s
  scope='Explicit candidate fingerprint and nonempty source-version references checked; substantive rationale not re-reviewed by this byte audit.'
 else:scope='Historical alternate packet layout: existence/hash checked only; no candidate-fingerprint or source verification asserted here.'
 rows.append(dict(candidate_key=key,bucket=bucket,disposition=status,review_packet=str(p),review_packet_sha256=packets[str(p)],check_scope=scope))
assert len(keys)==len(set(keys))==l['candidate_count']==185;assert buckets['awaiting_coordinator_review']==l['unreviewed_count'];assert buckets['reviewed_withheld']==l['reviewed_withheld_cases'];assert h(Path('data/moratorium_inventory.csv').read_bytes())==l['current_inventory_sha256']
# Verify review source bodies/text from original acquisition artifacts when their exact
# IDs occur in the original discovery directories or the explicit Illinois followup.
# Other source directories stay explicit rather than being guessed.
verified=[];unverified=[]
for (aid,bsha,tsha),s in sorted(proofs.items()):
 candidates=[]
 for folder in [*sorted(Path('/data0/moratorium-refresh-2026/discovery').glob('discovery-*')), Path('/data0/moratorium-refresh-2026/illinois-action-followup')]:
  p=folder/(aid+'.private.body')
  if p.exists():candidates.append(p)
 if not candidates:
  unverified.append(dict(attempt_id=aid,body_sha256=bsha,text_sha256=tsha,reason='Followup acquisition outside original-discovery directory; refer to packet-specific verified receipt.'));continue
 assert len(candidates)==1;bp=candidates[0];assert h(bp.read_bytes())==bsha;folder=bp.parent;matches=[p for p in folder.glob(aid+'*txt') if h(p.read_bytes())==tsha];assert matches
 verified.append(dict(attempt_id=aid,body_sha256=bsha,text_sha256=tsha,review_text_kind='original extraction' if matches[0].name==aid+'.private.txt' else 'separate retained derivation',acquisition_scope='original discovery' if bp.parent.name.startswith('discovery-') else 'explicit Illinois followup',scope='Exact body/review-text bytes; no renewed factual or legal acceptance.'))
report=dict(state='consistent_with_explicit_scope_limits',ledger_sha256=h(raw),inventory_sha256=l['current_inventory_sha256'],candidate_count=185,buckets=dict(buckets),reviewed_count=len(rows),packet_count=len(packets),packet_sha256=packets,explicit_candidate_fingerprint_checks=sum('Explicit candidate' in r['check_scope'] for r in rows),alternate_packet_layout_checks=sum('Historical alternate' in r['check_scope'] for r in rows),distinct_review_source_versions=len(proofs),source_versions_reverified=len(verified),original_discovery_source_versions_reverified=sum(v['acquisition_scope']=='original discovery' for v in verified),followup_source_versions_reverified=sum(v['acquisition_scope']=='explicit Illinois followup' for v in verified),source_versions_deferred_to_specific_receipts=len(unverified),verified_original_versions=verified,followup_source_scope_limits=unverified,candidates=rows,scope='Read-only mechanical coordinator-ledger/packet/source-byte accounting. Review completion is not substantive resolution or current-force verification. This audit does not close full record freshness, alternate packet evidence review, source extraction/migration or release gates.')
out=Path('work/audit/discovery-coordinator-accounting-2026-11-06.json');out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['packet_sha256','verified_original_versions','followup_source_scope_limits','candidates']},indent=2))
