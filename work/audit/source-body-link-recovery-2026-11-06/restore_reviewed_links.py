#!/usr/bin/env python3
"""Apply only the pinned, private-body compatibility-link recovery plan."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--plan',type=Path,required=True)
parser.add_argument('--receipt',type=Path,required=True)
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
raw=args.plan.read_bytes();plan=json.loads(raw);root=Path(plan['root']).resolve();cas=Path(plan['cas_root']).resolve()
assert root==Path.cwd().resolve()
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0'))
# Validate the entire plan before the first write. Never replace an existing link.
for name,expected in plan['manifest_sha256'].items():
    assert digest((root/name).read_bytes())==expected, 'Manifest drift'
for row in plan['entries']:
    relative=Path(row['destination']);destination=root/relative;target=Path(row['target'])
    assert not relative.is_absolute() and '..' not in relative.parts
    assert str(relative) not in tracked
    assert destination.parent==(root/row['manifest']).parent
    assert target.resolve().is_relative_to(cas)
    assert digest(target.read_bytes())==row['body_sha256']
    line=(root/row['manifest']).read_bytes().splitlines(keepends=True)[row['line']-1]
    assert digest(line)==row['manifest_row_sha256']
    assert json.loads(line).get('published')==row['original_published_value']
    if destination.is_symlink():
        assert os.readlink(destination)==str(target) and digest(destination.read_bytes())==row['body_sha256']
    else:
        assert not destination.exists(), 'Existing file preserved'
created=[];already=[];ignore_before={}
if args.apply:
    for row in plan['entries']:
        destination=root/row['destination'];target=Path(row['target']);ignore=destination.parent/'.gitignore'
        ignore_before.setdefault(str(ignore.relative_to(root)),ignore.read_bytes() if ignore.exists() else b'')
        with ignore.open('a+') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX);stream.seek(0);content=stream.read()
            if destination.name not in content.splitlines():
                stream.seek(0,2);stream.write(('\n' if content and not content.endswith('\n') else '')+destination.name+'\n');stream.flush();os.fsync(stream.fileno())
        if destination.is_symlink():already.append(row['destination'])
        else:destination.symlink_to(target);created.append(row['destination'])
        assert digest(destination.read_bytes())==row['body_sha256']
    names=[r['destination'] for r in plan['entries']]
    checked=subprocess.run(['git','check-ignore','--stdin','-z'],cwd=root,input=('\0'.join(names)+'\0').encode(),capture_output=True,check=True)
    assert set(checked.stdout.decode().split('\0'))- {''}==set(names)
    for name,before in ignore_before.items():assert (root/name).read_bytes().startswith(before)
for name,expected in plan['manifest_sha256'].items():assert digest((root/name).read_bytes())==expected
result={'apply':args.apply,'plan_sha256':digest(raw),'planned':len(plan['entries']),'created':created,'already_present':already,
        'manifest_hashes_unchanged':True,'publication_flags_unchanged':True,
        'all_restored_bodies_hash_verified':bool(args.apply),'all_restored_paths_git_ignored':bool(args.apply),
        'ignore_files_append_only':{name:{'before_sha256':digest(before),'after_sha256':digest((root/name).read_bytes())} for name,before in ignore_before.items()},
        'scope':'Only absent untracked body paths restored as ignored links to exact-hash existing private CAS bytes. No body copy, original-manifest edit, public content export, factual acceptance or source-date renewal.'}
args.receipt.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'planned':result['planned'],'created':len(created),'already_present':len(already),'apply':args.apply}))
