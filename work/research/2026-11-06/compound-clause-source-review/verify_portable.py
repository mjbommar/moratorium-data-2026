"""Verify a trusted manifest, restore its public tree and test offline readers.

The expected manifest hash must come from an independently trusted build receipt.
No bundled code is imported until the archive/member hashes have been checked.
"""
import argparse,builtins,hashlib,io,json,os
from pathlib import Path
import subprocess,sys,tarfile

p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--restore',type=Path,required=True);p.add_argument('--expected-manifest-sha256',required=True);a=p.parse_args()
raw=(a.directory/'manifest.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==a.expected_manifest_sha256
manifest=json.loads(raw);archive=a.directory/manifest['archive']['name']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archive']['sha256']
required=['work/research/2026-11-06/compound-clause-source-review/selection.json','work/research/2026-11-06/compound-clause-source-review/claim-bindings.json','work/schemas/expanded/1.0.3.json','scripts/condition_expression.py']
a.restore.mkdir(parents=True,exist_ok=False)
with tarfile.open(archive) as tar:
    assert set(tar.getnames())=={f['path'] for f in manifest['files']}
    assert set(required)<=set(tar.getnames())
    for f in manifest['files']:
        member=tar.getmember(f['path']);content=member.linkname.encode() if member.issym() else tar.extractfile(member).read()
        assert len(content)==f['bytes'] and hashlib.sha256(content).hexdigest()==f['sha256'],f['path']
    tar.extractall(a.restore,filter='data')
root=a.restore.resolve();assert not (root/'.git').exists()
original_builtin=builtins.open;original_io=io.open;original_popen=subprocess.Popen
blocked=[]
def guarded(function):
    def opened(file,*args,**kwargs):
        if not isinstance(file,int):
            resolved=Path(os.fsdecode(file)).resolve()
            if resolved==Path('/data0') or Path('/data0') in resolved.parents:
                blocked.append(str(resolved));raise AssertionError('Private source access forbidden in portable replay')
        return function(file,*args,**kwargs)
    return opened

def forbid_process(*args,**kwargs):
    raise AssertionError('Subprocess/Git forbidden in portable replay')

try:
    builtins.open=guarded(original_builtin);io.open=guarded(original_io);subprocess.Popen=forbid_process
    os.chdir(root);sys.path.insert(0,str(root/'scripts'))
    import expanded_promotion as promotion
    import check_expanded_publication as publication
    import build_expanded_csv as projection
    assert Path(promotion.__file__).resolve().is_relative_to(root)
    destination=root/'data/expanded';registry=root/'data/identities/expanded.jsonl'
    checked=publication.check(destination,registry,root/'data/moratorium_inventory.csv',root/'data/state_legislation.csv')
    plan=json.loads((root/'work/research/2026-11-06/compound-clause-source-review/publication-plan.json').read_text())
    replay=promotion.publish(destination,destination,registry,plan,[],apply=True,moratoria=root/'data/moratorium_inventory.csv',state_actions=root/'data/state_legislation.csv')
    assert replay['state']=='already_applied'
    generation,outputs=projection.build_outputs(destination.resolve())
    assert len(outputs)==19
    projection.verify_generation((root/'data/expanded-csv').resolve(),outputs)
    assert json.loads(outputs['manifest.json'])['validation_profile']['name']=='1.0.3'
    assert not blocked
finally:
    builtins.open=original_builtin;io.open=original_io;subprocess.Popen=original_popen
for f in manifest['files']:
    file=root/f['path'];content=os.readlink(file).encode() if file.is_symlink() else file.read_bytes()
    assert hashlib.sha256(content).hexdigest()==f['sha256'],f['path']
print(json.dumps(dict(schema_version='compound-portable-replay-1',source_commit=manifest['source_commit'],archive=manifest['archive'],manifest_sha256=a.expected_manifest_sha256,verified_members=len(manifest['files']),required_new_members=required,restored_without_git=True,private_source_access_denied=True,subprocesses_denied=True,publication=checked,replay=replay,csv_views=18,csv_generation=generation,all_public_members_unchanged=True,release_status='Local working-candidate verification; not final release/tag/deployment'),indent=2))
