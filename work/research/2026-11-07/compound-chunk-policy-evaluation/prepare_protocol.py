"""Prepare a comparison freeze from inspected sources/settings; sends no requests."""
import dataclasses,datetime as dt,hashlib,importlib.metadata,inspect,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];PACKET=Path(__file__).resolve().parent
PATHS=['/home/mjbommar/projects/bc/bc-modules-evidence-chunk-policy/bc-evidence/python','/home/mjbommar/projects/bc/bc-modules-sdk-retries/bc-llm/python']
sys.path[:0]=PATHS+[str(ROOT/'scripts')]
from bc_llm import BcLlmSettings,ModelSpec,PydanticAIBackend
from bc_content.chunk import chunk_text
import bc_evidence.extract as extractor
import extract_domain_candidates as domain
import runtime_file_pins
from pydantic_ai.models.openai import OpenAIResponsesModel
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
encode=lambda v:json.dumps(v,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()
private=Path('/data0/moratorium-refresh-2026/frozen-domain-evaluation/compound-chunk-policy-evaluation')
assert private.is_dir() and not (private/'provider').exists()
source_root=Path('/data0/moratorium-refresh-2026/discovery/ballot-nd-001')
snapshot=(ROOT/'data/expanded').resolve();claims={r['claim_id']:r for r in map(json.loads,(snapshot/'claims.jsonl').read_text().splitlines())}
review=ROOT/'work/research/2026-11-06/compound-clause-source-review'
bindings=json.loads((review/'claim-bindings.json').read_text());selection=json.loads((review/'selection.json').read_text())
criteria={
'mandan-data-center':'Principal/primary digital infrastructure definition and accessory/incidental equipment exclusion; no blanket inclusion of every business server.',
'mandan-large-scale':'Defined Data Center predicate AND aggregate capacity>=25MW; retain greatest documented metric/aggregation context and unresolved interaction with capacity-or-demand measurement language.',
'mandan-prohibition':'Separately defined Large-Scale predicate AND capacity OR demand>=25MW; lawful city/extraterritorial scope and existing-operation/vested-right qualifications; do not reduce to unconditional demand-only prohibition or current law.',
'mandan-below':'Data Center predicate AND aggregate capacity<25MW AND demand<25MW; source-qualified measures, not an approval entitlement.',
'mandan-no-entitlement':'Below-threshold status creates no approval/operation entitlement; other applicable laws remain applicable.',
'mandan-aggregation':'At least two Data Center facilities, objective evidence of common/affiliated control or common/coordinated development; retain written-findings/nondeterminative ordinary infrastructure limits without automatic adjacency inference.',
'mandan-anti-evasion':'Primary-purpose avoidance arrangements are prohibited as proposed; preserve source purpose and nonexclusive nature, not generic project prohibition.',
'harwood-major':'Industrial Development and discretionary City approval gates AND any ONE of all FIVE major alternatives: peak>=100MW, area>=100acres, full water comparison, generation>=100MW, qualifying major/TitleV/equivalent air authorization. Preserve foreseeable/cumulative/common-plan bases; no resource cap.',
'harwood-moderate':'Industrial Development and discretionary City approval gates AND AT LEAST TWO of all SIX moderate criteria: peak>=50MW, area>=50acres, water>=25000gallons/day, generation>=50MW, qualifying operational air permit, additional consistent uniformly applicable ordinance threshold. No one-moderate sufficiency.',
'harwood-common-plan':'At least two related components with source-defined relationships, considered collectively; no single unconnected parcel inference.',
'harwood-substantial-modification':'Existing Industrial Development expansion/change that materially increases or creates foreseeable impacts, with existing-plus-proposed cumulative applicability.',
'harwood-effective-applicability':'Proposed effect under charter-amendment provisions, applicable to nonfinal discretionary approvals and preserving vested rights; no inferred adoption/operative date.'}
families={'mandan':[],'harwood':[]}
for item in selection['clauses']:
 cid=item['clause_id'];binding=next(b for b in bindings if b['clause_id']==cid);claim=claims[binding['claim_id']]
 family='mandan' if cid.startswith('mandan-') else 'harwood'
 families[family].append(dict(slot_id=cid,canonical_claim_id=binding['claim_id'],canonical_value_sha256=hashlib.sha256(encode(claim['value'])).hexdigest(),criteria=criteria[cid],source_spans=item['source_spans'],supporting_spans=item['supporting_spans'],interpretive_limits=claim['value']['interpretive_limits'],target_table='measure_provisions',target_field='condition_clauses'))
slots=dict(schema_version='compound-semantic-slots-1',canonical_snapshot=snapshot.name,families=families,matching='Manual complete-group semantic review; exact equality is diagnostic only. Each covered slot requires one supported candidate and exactly one complete clause, with no joining of partial groups. Other clauses may share the same candidate array.')
(PACKET/'required-slots.json').write_text(json.dumps(slots,indent=2)+'\n')
settings=BcLlmSettings();spec=ModelSpec(model='openai:gpt-6-sol',reasoning_effort='low',output_mode='native',max_tokens=14000,timeout_s=120)
price=dataclasses.asdict(settings.pricing().get(spec.model))
proxy={'proxy':settings.proxy_url(),**{key:os.environ.get(key) for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY','OPENAI_BASE_URL','OPENAI_ORG_ID','OPENAI_PROJECT_ID')}}
sources={
 'mandan':dict(source_document_id='b042897c-dd19-4727-a318-4b01de972dad',title='Mandan proposed ordinance: retained petition legal text',subject_label='City of Mandan proposed data-center ordinance',body_path=str(source_root/'9f3fe75c1cff47e7ad99dbadf6e1b5f4.private.body'),text_path=str(source_root/'mandan-normative-layout.private.txt')),
 'harwood':dict(source_document_id='cb89ae87-9ad7-4bb2-94b5-cc1acc3cee64',title='Harwood proposed Home Rule Charter Article X',subject_label='City of Harwood proposed Article X',body_path=str(source_root/'cfa4727409bd4a8ba9e1f9aac3736126.private.body'),text_path=str(source_root/'cfa4727409bd4a8ba9e1f9aac3736126.private.txt'))}
sdocs={r['source_document_id']:r for r in map(json.loads,(snapshot/'source_documents.jsonl').read_text().splitlines())}
cases=[]
for family,policy,cap in [('mandan','default',4),('harwood','default',8),('mandan','whole',2),('harwood','whole',2)]:
 source=sources[family];doc=sdocs[source['source_document_id']]
 assert H(source['body_path'])==doc['body_sha256'] and H(source['text_path'])==doc['text_sha256']
 cases.append(dict(case_id=family+'-'+policy,family=family,policy=policy,**source,url=doc['url'],body_sha256=doc['body_sha256'],text_sha256=doc['text_sha256'],chunk_size=7000 if policy=='default' else 42000,chunk_overlap=400,max_calls=cap,max_usd=cap*.75,reservation_usd=.75))
admission_path=PACKET/'storage-admission.json'
admission=json.loads(admission_path.read_text())
layout=(ROOT/admission['layout']).resolve()
guard=Path('/home/mjbommar/projects/bc/bc-modules/scripts/check-storage-layout.py')
code=[ROOT/'scripts/runtime_file_pins.py',ROOT/'scripts/private_run_storage.py',admission_path,layout,guard,PACKET/'run.py',PACKET/'audit.py',Path(__file__).resolve(),ROOT/'scripts/extract_document_resumable.py',ROOT/'scripts/extract_domain_candidates.py',ROOT/'scripts/condition_expression.py',ROOT/'scripts/condition_scoring.py',ROOT/'scripts/controlled_model_transport.py',ROOT/'scripts/audit_domain_evaluation.py',domain.SCHEMA,ROOT/'work/schemas/extraction/1.2.0.json',Path(extractor.__file__).resolve(),Path(inspect.getfile(chunk_text)).resolve(),Path(inspect.getfile(PydanticAIBackend)).resolve(),Path(inspect.getfile(ModelSpec)).resolve(),Path(inspect.getfile(BcLlmSettings)).resolve(),Path(inspect.getfile(OpenAIResponsesModel)).resolve(),*sorted((Path(extractor.__file__).resolve().parent/'prompts').glob('extract*'))]
# Pin full pure-Python runtime packages, including the newer SDK worktree's price overlay.
for directory in PATHS:
    code.extend(sorted(Path(directory).glob('*/*.py')))
code=list(dict.fromkeys(code))
assert all(p.is_file() for p in code),'Implementation incomplete; no protocol can be prepared'
canonical=[*sorted(snapshot.glob('*.jsonl')),snapshot/'publication.json',ROOT/'data/moratorium_inventory.csv',ROOT/'data/state_legislation.csv',ROOT/'data/identities/expanded.jsonl',PACKET/'required-slots.json',review/'selection.json',review/'claim-bindings.json']
runtime_manifest=PACKET/'runtime-files.json'
runtime_manifest_sha256=runtime_file_pins.write_manifest(runtime_manifest)
protocol=dict(runtime_files_path=str(runtime_manifest),runtime_files_sha256=runtime_manifest_sha256,runtime_files_boundary=runtime_file_pins.BOUNDARY,pricing_basis='Locally pinned SDK-worktree overlay, not provider invoice or independently current price verification. Different from original installed genai-prices table.',schema_version='compound-chunk-comparison-1',prepared_at=dt.datetime.now(dt.timezone.utc).isoformat(),scope='Matched development comparison on two known source-reviewed documents. Not unseen holdout, general accuracy, complete discovery recall or overall P4 acceptance.',private_root=str(private),max_private_bytes=67108864,runtime_import_paths=PATHS,code_sha256={str(p):H(p) for p in code},canonical_inputs_sha256={str(p):H(p) for p in canonical},canonical_snapshot=snapshot.name,source_cohort_date='2026-11-05',model_spec=spec.model_dump(mode='json'),pricing=price,routing_fingerprint=hashlib.sha256(encode(proxy)).hexdigest(),dependency_versions={n:importlib.metadata.version(n) for n in ['openai','pydantic-ai-slim','pydantic','httpx2','bc-evidence','bc-llm','bc-content']},max_http_requests=16,question='Extract source-qualified fields relevant to the named proposed legal text. Preserve definitions, applicability, complete compound conditions, source scope and proposed versus operative status. Do not derive actual adoption, current legal force, election results, denominators or certification beyond explicit source support.',execution_order=[c['case_id'] for c in cases],cases=cases,required_slots_sha256=H(PACKET/'required-slots.json'),thresholds=dict(supported_fraction=.95,critical_unsupported_or_ambiguous=0,all_required_slots=True,full_supplied_text_coverage=True,source_quote_integrity=True),criticality='Every non-title field is high-impact; title may also be high-impact for identity errors.',scoring='Coordinator source review with two independently generated AI review populations. Agreement is not human ground truth. Policy gates are descriptive development gates only; overall P4 remains open regardless of outcome.',retry_accounting=dict(backend_max_attempts=1,sdk_max_retries=0,agent_retries=0,max_model_requests=1,native_chunk_attempts=extractor.CHUNK_ATTEMPTS,flex_fallback=False,estimated_reservations_usd=12,invoice_ceiling_verified=False),limitations=['Fixed default-first execution order; cache/latency/cost effects are not randomized or independently attributable.','One sample per document/policy; generation randomness and twelve-claim-per-chunk opportunity differ with policy.','Selected support windows are not a proven minimal necessary evidence set.','All selected primary quotes fit default chunks; the joint supporting context differs.','Mandan input is registered normative pages4-8, not personal petition pages; supplied-text processing does not prove PDF/OCR completeness.'])
(PACKET/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
print(json.dumps(dict(cases=len(cases),slots=sum(map(len,families.values())),expected_success_calls=12,http_cap=16,estimated_reservation_usd=12,protocol_sha256=H(PACKET/'protocol.json'),provider_executed=False),indent=2))
