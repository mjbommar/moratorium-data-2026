#!/usr/bin/env python3
"""Export committed public inputs plus authenticated replay history, never joins."""
import argparse
import csv
import ctypes
import errno
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[1]
VERSION='2.0.0'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def encode(value):return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
def relative(value):
    require(isinstance(value,str) and value and '\\' not in value,'Invalid handoff path')
    path=PurePosixPath(value)
    require(not path.is_absolute() and '..' not in path.parts and str(path)==value,'Unsafe handoff path')
    return path


def inventory(root,*,source_tree=False):
    records=[]
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            allowed={'data/expanded','data/expanded-csv'} if source_tree else {'source/data/expanded','source/data/expanded-csv'}
            require(path.relative_to(root).as_posix() in allowed,'Unexpected handoff symlink')
            target=os.readlink(path)
            require(not Path(target).is_absolute() and path.resolve(strict=True).is_relative_to(root.resolve()),'Handoff symlink escapes root')
            raw=target.encode();kind='symlink'
        elif path.is_file():raw=path.read_bytes();kind='file'
        elif path.is_dir() and not source_tree:raw=b'';kind='directory'
        else:continue
        name=path.relative_to(root).as_posix()
        if name=='manifest.json':continue
        records.append({'path':name,'kind':kind,'bytes':len(raw),'sha256':sha(raw)})
    # Git/archive manifests sort full POSIX paths. Keep the established
    # directory-inclusive handoff order unchanged for historical snapshots.
    return sorted(records,key=lambda r:r['path']) if source_tree else records


def verify_tree(root,records):
    require(root.is_dir() and not root.is_symlink(),'Handoff root must be a directory')
    for record in records:relative(record['path'])
    require(len({r['path'] for r in records})==len(records),'Duplicate handoff manifest path')
    require(inventory(root)==records,'Handoff file set, kind, size or hash differs')


def run_source_checks(root):
    source=root/'source'
    results=[]
    commands=[['scripts/check_expanded_publication.py'],['scripts/build_expanded_csv.py','--check']]
    if (source/'scripts/build_policy_scope_exports.py').exists():
        commands.append(['scripts/build_policy_scope_exports.py','--check'])
    for args in commands:
        result=subprocess.run([sys.executable,'-B',*args],cwd=source,capture_output=True,text=True)
        require(result.returncode==0,'Restored source check failed: '+args[0]+'\n'+result.stdout+result.stderr)
        results.append({'command':args,'exit_code':0,'result':result.stdout.strip() if args[0].endswith('build_policy_scope_exports.py') else json.loads(result.stdout)})
    return results


def alias_specs(source):
    source=source.resolve(strict=True)
    snapshot=(source/'data/expanded').resolve(strict=True);projection=(source/'data/expanded-csv').resolve(strict=True)
    require(snapshot.is_relative_to(source.resolve()) and projection.is_relative_to(source.resolve()),'Source pointer escapes replay tree')
    aliases=[]
    if (source/'scripts/build_policy_scope_exports.py').exists():
        required=['data/state_policy_scope_reviews.jsonl','docs/policy-scope-exports.md',
                  'data/policy-scope/all-annotated.csv','data/policy-scope/reviewed-included.csv',
                  'data/policy-scope/not-explicitly-excluded-candidates.csv','data/policy-scope/receipt.json']
        require(all((source/name).is_file() for name in required),'Incomplete policy-scope handoff')
    def add(name,origin):aliases.append({'path':name,'source_path':'source/'+origin.relative_to(source).as_posix()})
    for name in ['moratorium_inventory.csv','state_legislation.csv','summary_stats.json']:add('data/'+name,source/'data'/name)
    for name in ['state_policy_scope_reviews.jsonl']:
        if (source/'data'/name).exists():add('data/'+name,source/'data'/name)
    for name in ['all-annotated.csv','reviewed-included.csv','not-explicitly-excluded-candidates.csv','receipt.json']:
        if (source/'data/policy-scope'/name).exists():add('data/policy-scope/'+name,source/'data/policy-scope'/name)
    for name in ['expanded.jsonl','legacy-moratoria.jsonl']:
        if (source/'data/identities'/name).exists():add('data/identities/'+name,source/'data/identities'/name)
    for path in sorted(snapshot.glob('*.jsonl')):add('expanded/'+path.name,path)
    add('expanded/publication.json',snapshot/'publication.json')
    for path in sorted(projection.iterdir()):add('expanded-csv/'+path.name,path)
    for path in sorted((source/'work/schemas/expanded').glob('*.json')):add('schemas/expanded/'+path.name,path)
    for name in ['expanded-data-contracts.md','ballot-measures.md','known-gaps.md','instrument-events.md','event-validity-publication.md','policy-scope-exports.md']:
        if (source/'docs'/name).exists():add('docs/'+name,source/'docs'/name)
    gap=source/'work/audit/ballot-release-dispositions-2026-11-06.json'
    if gap.exists():add('work/audit/'+gap.name,gap)
    return aliases


def current_metadata(source):
    source=source.resolve(strict=True)
    snapshot=(source/'data/expanded').resolve(strict=True);projection=(source/'data/expanded-csv').resolve(strict=True)
    require(snapshot.is_relative_to(source.resolve()) and projection.is_relative_to(source.resolve()),'Source pointer escapes replay tree')
    publication=json.loads((snapshot/'publication.json').read_text());csv_manifest=json.loads((projection/'manifest.json').read_text())
    if publication['plan'].get('validation_profile',{}).get('name') in ('1.0.2','1.0.3','1.0.4'):
        require((projection/'instrument_events_current.csv').is_file() and (projection/'instrument_event_status.csv').is_file(),'Profile 1.0.2 requires current/status event views')
    def csv_count(path):return len(list(csv.DictReader(io.StringIO(path.read_text()))))
    def jsonl_count(path):return sum(1 for l in path.read_text().splitlines() if json.loads(l))
    counts={'moratorium_records':csv_count(source/'data/moratorium_inventory.csv'),'state_policy_records':csv_count(source/'data/state_legislation.csv'),
            'ballot_measures':jsonl_count(snapshot/'ballot_measures.jsonl'),'retained_results':jsonl_count(snapshot/'measure_results.jsonl'),
            'current_results':csv_count(projection/'measure_results_current.csv'),'retained_events':jsonl_count(snapshot/'instrument_events.jsonl'),
            'current_accepted_historical_events':csv_count(projection/'instrument_events_current.csv') if (projection/'instrument_events_current.csv').exists() else None,
            'restriction_records':jsonl_count(snapshot/'local_restrictions.jsonl'),'measure_instrument_link_records':jsonl_count(snapshot/'measure_instrument_links.jsonl')}
    return {'source_publication_reviewed_at':publication['plan']['reviewed_at'],'expanded_snapshot':snapshot.name,
            'expanded_table_snapshot_sha256':publication['sha256'],'source_publication_sha256':sha((snapshot/'publication.json').read_bytes()),
            'validation_profile':publication['plan'].get('validation_profile',{'name':'1.0.0'}),
            'csv_projection':projection.name,'csv_views':len(csv_manifest['files']),'current_counts':counts}


def verify_handoff(destination,expected_manifest_sha256,*,run_checks=True):
    require(isinstance(expected_manifest_sha256,str) and len(expected_manifest_sha256)==64,'Externally pinned manifest SHA-256 required')
    destination=destination.absolute()
    require(not destination.is_symlink() and not (destination/'manifest.json').is_symlink(),'Handoff root/manifest cannot be symlinks')
    raw=(destination/'manifest.json').read_bytes();require(sha(raw)==expected_manifest_sha256,'Handoff manifest fingerprint differs')
    manifest=json.loads(raw);require(manifest['schema_version']==VERSION,'Unsupported handoff format')
    require(manifest['exporter_source_commit']==manifest['source_commit'],'Exporter revision differs from source revision')
    require(sha((destination/'verify_handoff.py').read_bytes())==manifest['source_exporter_sha256'],'Packaged verifier differs from pinned exporter bytes')
    verify_tree(destination,manifest['files'])
    upstream_raw=(destination/'upstream-manifest.json').read_bytes()
    require(sha(upstream_raw)==manifest['upstream_manifest_sha256'],'Upstream manifest fingerprint differs')
    upstream=json.loads(upstream_raw)
    require(upstream['source_commit']==manifest['source_commit'],'Source revision mismatch')
    expected=[]
    for item in upstream['files']:
        relative(item['path'])
        expected.append({'path':'source/'+item['path'],'kind':item['kind'],'bytes':item['bytes'],'sha256':item['sha256']})
    actual=[r for r in manifest['files'] if r['path'].startswith('source/') and r['kind']!='directory']
    require(sorted(expected,key=lambda r:r['path'])==sorted(actual,key=lambda r:r['path']),
            'Source replay tree differs from upstream manifest')
    require(manifest['compatibility_aliases']==alias_specs(destination/'source'),'Compatibility alias coverage differs')
    metadata=current_metadata(destination/'source')
    require(all(json.dumps(manifest[k],sort_keys=True)==json.dumps(v,sort_keys=True) for k,v in metadata.items()),'Current metadata/profile/counts differ from pinned source')
    for alias in manifest['compatibility_aliases']:
        path=destination/relative(alias['path']);origin=destination/relative(alias['source_path'])
        require(alias['source_path'].startswith('source/'),'Compatibility alias must reference replay tree')
        require(path.is_file() and not path.is_symlink() and path.read_bytes()==origin.read_bytes(),'Compatibility alias differs from pinned source')
    # Matching the caller's trusted hash precedes execution of packaged source code.
    checks=run_source_checks(destination) if run_checks else []
    verify_tree(destination,manifest['files'])
    return {'state':'verified','source_commit':manifest['source_commit'],'manifest_sha256':expected_manifest_sha256,
            'expanded_snapshot':manifest['expanded_snapshot'],'files':sum(r['kind']!='directory' for r in manifest['files']),'entries':len(manifest['files']),
            'checks':checks,'checks_run':run_checks,'scope':('Pinned input integrity and offline publication consistency, not source reacquisition or downstream join acceptance.' if run_checks else 'Pinned file integrity only; source publication checkers skipped.')}


def rename_noreplace(source,destination):
    """Linux atomic no-replace; no check/rename fallback on unsupported hosts."""
    library=ctypes.CDLL(None,use_errno=True);operation=getattr(library,'renameat2',None)
    require(operation is not None,'Atomic renameat2 is required for handoff publication')
    operation.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    operation.restype=ctypes.c_int
    if operation(-100,os.fsencode(source),-100,os.fsencode(destination),1)!=0:
        error=ctypes.get_errno()
        if error==errno.EEXIST:raise FileExistsError(error,os.strerror(error),str(destination))
        raise OSError(error,os.strerror(error),str(destination))


def publish_tree(stage,destination):
    def existing():
        require(not destination.is_symlink() and destination.is_dir(),'Destination cannot be a symlink or non-directory')
        require((destination/'manifest.json').is_file() and not (destination/'manifest.json').is_symlink(),'Refusing to replace existing directory without handoff manifest')
        expected=(stage/'manifest.json').read_bytes()
        require((destination/'manifest.json').read_bytes()==expected,'Refusing to replace a different handoff')
        verify_tree(destination,json.loads(expected)['files'])
        return 'already_present'
    require(not destination.is_symlink(),'Destination cannot be a symlink')
    if destination.exists():return existing()
    try:rename_noreplace(stage,destination)
    except FileExistsError:return existing()
    return 'created'


def _populate(source_bundle,stage,exporter_raw):
    upstream_raw=(source_bundle/'manifest.json').read_bytes();upstream=json.loads(upstream_raw)
    archive=source_bundle/upstream['archive']['name']
    require(archive.name==upstream['archive']['name'] and archive.stat().st_size==upstream['archive']['bytes'] and sha(archive.read_bytes())==upstream['archive']['sha256'],'Source archive fingerprint differs')
    source=stage/'source';source.mkdir()
    with tarfile.open(archive) as tar:
        members=tar.getmembers();require([m.name for m in members]==[r['path'] for r in upstream['files']],'Archive member list differs')
        for m in members:relative(m.name)
        tar.extractall(source,filter='data')
    expected=[{k:item[k] for k in ('path','kind','bytes','sha256')} for item in upstream['files']]
    require(inventory(source,source_tree=True)==sorted(expected,key=lambda r:r['path']),'Restored upstream bytes differ')
    aliases=alias_specs(source)
    for alias in aliases:
        target=stage/alias['path'];target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((stage/alias['source_path']).read_bytes())
    (stage/'upstream-manifest.json').write_bytes(upstream_raw)
    (stage/'verify_handoff.py').write_bytes(exporter_raw)
    metadata=current_metadata(source)
    (stage/'README.md').write_text('''# Reviewed moratorium and ballot working inputs

This additive input handoff preserves separate local, state-policy and ballot denominators. See manifest.json for the pinned source revision, profile, publication/CSV identities, record counts and every file hash. Read source/ for the complete public replay tree; expanded/ and data/ preserve compatibility paths and are exact copies, not independent authorities.

instrument_events.csv retains history. instrument_events_current.csv and instrument_event_status.csv distinguish current review acceptance from retained history when provided by the selected profile. Acceptance of a historical event does not establish current instrument force. Restriction and measure-instrument link records preserve their reviewed scope/status and do not establish project applicability or causation.

Use an independently trusted copy of scripts/export_reviewed_handoff.py (or the source-identical integration verifier) with --verify DIRECTORY --manifest-sha256 HASH. Obtain the manifest pin and verifier SHA-256 from the separately trusted delivery receipt/repository revision. The packaged verify_handoff.py is not a trust bootstrap: authenticate its bytes independently before execution. The tested environment is Linux with a symlink-capable filesystem and Python/jsonschema. Private source bodies and Git are unnecessary for verification. Trusted hash verification precedes execution of packaged source checkers; internal consistency does not authenticate an untrusted tip.

This is a working input transfer, not a final release or rebuilt bridge/collaborator packet. Historical project/disclosure snapshots and their cutoffs remain unchanged. Stable IDs and reviewed relations are transferred without accepting RDF assertions, proximity exposure, legal applicability, market outcomes or causal joins. Unknown implementation/current-force facts and unresolved ballot groups remain unknown.
''')
    manifest={'schema_version':VERSION,'source_repository':'moratorium-data-2026','source_commit':upstream['source_commit'],
              'exporter_source_commit':upstream['source_commit'],'source_exporter_sha256':sha(exporter_raw),'upstream_manifest_sha256':sha(upstream_raw),
              'working_cohort_cutoff':upstream['working_cohort_cutoff'],**metadata,
              'compatibility_aliases':aliases,'files':inventory(stage),
              'scope':'Additive pinned public working inputs and complete replay tree; no downstream join or renewed legal-force acceptance.',
              'limits':['Raw source bodies and private model/network payloads are excluded.','The source working cohort is not inventory-wide freshness or complete election coverage.',
                        'Historical bridge, collaborator, project/disclosure and market outputs remain at their documented cutoffs.','RDF/assertion/project applicability review is a separate downstream gate.']}
    (stage/'manifest.json').write_bytes(encode(manifest))
    return manifest


def export(destination,revision='HEAD'):
    commit=subprocess.check_output(['git','rev-parse',revision+'^{commit}'],cwd=ROOT,text=True).strip()
    exporter_raw=Path(__file__).read_bytes()
    require(subprocess.check_output(['git','show',commit+':scripts/export_reviewed_handoff.py'],cwd=ROOT)==exporter_raw,'Commit the exact exporter before delivery')
    builder=ROOT/'scripts/build_release_candidate.py'
    require(subprocess.check_output(['git','show',commit+':scripts/build_release_candidate.py'],cwd=ROOT)==builder.read_bytes(),'Bundle builder differs from selected commit')
    destination=destination.absolute();require(not destination.is_symlink(),'Destination cannot be a symlink')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='moratorium-handoff-source-') as temp:
        source_bundle=Path(temp)/'bundle'
        result=subprocess.run([sys.executable,str(builder),str(source_bundle),'--revision',commit],cwd=ROOT,capture_output=True,text=True)
        require(result.returncode==0,'Source bundle build failed: '+result.stdout+result.stderr)
        with tempfile.TemporaryDirectory(prefix='.moratorium-handoff-',dir=destination.parent) as staging:
            stage=Path(staging)/'snapshot';stage.mkdir();manifest=_populate(source_bundle,stage,exporter_raw)
            pin=sha((stage/'manifest.json').read_bytes());verify_handoff(stage,pin)
            state=publish_tree(stage,destination)
    return {'state':state,'source_commit':commit,'manifest_sha256':pin,'expanded_snapshot':manifest['expanded_snapshot'],
            'files':sum(r['kind']!='directory' for r in manifest['files']),'entries':len(manifest['files']),'current_counts':manifest['current_counts'],'destination':str(destination)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('destination',type=Path,nargs='?')
    parser.add_argument('--revision',default='HEAD');parser.add_argument('--verify',type=Path);parser.add_argument('--manifest-sha256')
    args=parser.parse_args()
    if args.verify:
        require(args.destination is None,'Choose export or verification, not both')
        result=verify_handoff(args.verify,args.manifest_sha256)
    else:
        require(args.destination is not None,'Export destination required');result=export(args.destination,args.revision)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
