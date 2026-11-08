#!/usr/bin/env python3
"""Verify and replay a candidate against an independently obtained manifest digest."""
import argparse
import csv
import datetime as dt
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

HASH = re.compile(r'[0-9a-f]{64}\Z')
POINTERS = {'data/expanded': 'expanded-snapshots', 'data/expanded-csv': 'expanded-csv-snapshots'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name):
    require(isinstance(name, str) and name and '\\' not in name and '\x00' not in name, 'Invalid path')
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')),
            'Unsafe path: ' + name)
    return path


def verify_archive(directory, expected):
    require(isinstance(expected, str) and HASH.fullmatch(expected), 'Expected manifest SHA256 required')
    raw = (directory / 'manifest.json').read_bytes()
    require(digest(raw) == expected, 'Manifest SHA256 mismatch')
    manifest = json.loads(raw)
    archive = manifest['archive']
    name = archive['name']
    require(len(safe_path(name).parts) == 1, 'Invalid archive name')
    require(type(archive['bytes']) is int and archive['bytes'] >= 0 and
            isinstance(archive['sha256'], str) and HASH.fullmatch(archive['sha256']), 'Invalid archive metadata')
    archive_path = directory / name
    with archive_path.open('rb') as f:
        h = hashlib.file_digest(f, 'sha256').hexdigest()
    require(archive_path.stat().st_size == archive['bytes'] and h == archive['sha256'], 'Archive size or SHA256 mismatch')
    records = manifest['files']
    require(isinstance(records, list), 'Invalid file inventory')
    by_name = {}
    for record in records:
        path = record['path']; safe_path(path)
        require('.git' not in PurePosixPath(path).parts, 'Git metadata forbidden')
        require(path not in by_name, 'Duplicate manifest member: ' + path)
        require(record['kind'] in ('file', 'symlink') and type(record['bytes']) is int and record['bytes'] >= 0
                and isinstance(record['sha256'], str) and HASH.fullmatch(record['sha256']), 'Invalid member metadata')
        require((path in POINTERS) == (record['kind'] == 'symlink'), 'Unexpected member kind or pointer')
        by_name[path] = record
    require(set(POINTERS) <= by_name.keys(), 'Missing data pointers')
    for name in by_name:
        require(not any('/'.join(name.split('/')[:i]) in by_name for i in range(1, len(name.split('/')))), 'Member path collision')
    contents = {}
    with tarfile.open(archive_path, 'r:*') as tar:
        members = tar.getmembers()
        names = [m.name for m in members]
        require(len(names) == len(set(names)), 'Duplicate archive member')
        require(set(names) == set(by_name), 'Archive inventory mismatch')
        for m in members:
            safe_path(m.name)
            record = by_name[m.name]
            require((m.isfile() if record['kind'] == 'file' else m.issym()), 'Archive member type mismatch: ' + m.name)
            if m.issym():
                target = m.linkname
                safe_path(target)
                require(re.fullmatch(re.escape(POINTERS[m.name]) + r'/[0-9a-f]{64}', target), 'Invalid pointer target')
                data = target.encode('utf-8')
                require(any(n.startswith('data/' + target + '/') for n in by_name), 'Pointer target absent')
            else:
                stream = tar.extractfile(m)
                require(stream is not None, 'Unreadable member')
                data = stream.read()
            require(len(data) == record['bytes'] and digest(data) == record['sha256'], 'Member digest mismatch: ' + m.name)
            contents[m.name] = data
    return manifest, contents


def restore_tree(restore, manifest, contents):
    restore.mkdir(parents=True, exist_ok=False)
    root = restore.resolve()
    for record in manifest['files']:
        if record['kind'] == 'file':
            path = root / record['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents[record['path']])
    for record in manifest['files']:
        if record['kind'] == 'symlink':
            (root / record['path']).symlink_to(contents[record['path']].decode('utf-8'))
    return root


def replay(root):
    # Audit hooks also cover os.open and pathlib's io.open, unlike an open() wrapper.
    active = [True]
    def audit(event, args):
        if not active[0]:
            return
        if event.startswith(('subprocess.', 'socket.')) or event in ('os.system', 'os.posix_spawn', 'os.fork', 'os.forkpty', 'os.exec', 'os.spawn'):
            raise PermissionError('Process and network access forbidden during replay')
        if event in ('open', 'os.listdir', 'os.scandir') and args and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if path.is_relative_to('/data0') and not path.is_relative_to(root):
                raise PermissionError('Private /data0 access forbidden during replay')
    sys.addaudithook(audit)
    old_cwd, old_path = Path.cwd(), sys.path[:]
    try:
        os.chdir(root)
        sys.path.insert(0, str(root / 'scripts'))
        promotion = importlib.import_module('expanded_promotion')
        publication = importlib.import_module('check_expanded_publication')
        projection = importlib.import_module('build_expanded_csv')
        for module in (promotion, publication, projection):
            require(Path(module.__file__).resolve().is_relative_to(root), 'Validator imported outside restore')
        destination = root / 'data/expanded'; registry = root / 'data/identities/expanded.jsonl'
        moratoria = root / 'data/moratorium_inventory.csv'; state = root / 'data/state_legislation.csv'
        checked = publication.check(destination, registry, moratoria, state)
        plan = json.loads((destination / 'publication.json').read_text())['plan']
        result = promotion.publish(destination, destination, registry, plan, [], apply=True, moratoria=moratoria, state_actions=state)
        require(result['state'] == 'already_applied', 'Publication replay was not already applied')
        generation, outputs = projection.build_outputs(destination.resolve())
        projection.verify_generation((root / 'data/expanded-csv').resolve(), outputs)
        legacy = None
        if (root / 'scripts/legacy_moratorium_identity.py').is_file():
            require((root / 'data/identities/legacy-moratoria.jsonl').is_file(), 'Legacy registry missing')
            module = importlib.import_module('legacy_moratorium_identity')
            require(Path(module.__file__).resolve().is_relative_to(root), 'Legacy validator imported outside restore')
            with moratoria.open(newline='', encoding='utf-8-sig') as f:
                ids = {row['moratorium_id'] for row in csv.DictReader(f)}
            legacy = len(module.load_aliases(moratoria, ids))
        legacy_validation = None
        policy_scope_reviews = None
        if (root / 'scripts/validate_dataset.py').is_file():
            validator = importlib.import_module('validate_dataset')
            require(Path(validator.__file__).resolve().is_relative_to(root), 'Dataset validator imported outside restore')
            report = validator.Report()
            inv, inv_cols = validator.read_csv(validator.INV)
            leg, leg_cols = validator.read_csv(validator.LEG)
            stats = json.loads(validator.STATS.read_text(encoding='utf-8'))
            today = dt.date.today()
            validator.check_inventory(inv, inv_cols, today, report)
            validator.check_legislation(leg, leg_cols, report)
            scope_path = root / 'data/state_policy_scope_reviews.jsonl'
            if scope_path.is_file():
                require((root / 'scripts/policy_scope_reviews.py').is_file(), 'Policy scope validator missing')
                scope_validator = importlib.import_module('policy_scope_reviews')
                require(Path(scope_validator.__file__).resolve().is_relative_to(root), 'Policy scope validator imported outside restore')
                policy_scope_reviews = len(scope_validator.load_reviews(scope_path, leg))
            validator.check_summary_stats(inv, leg, stats, report)
            require(report.ok, 'Restored legacy dataset failed validation: ' + repr(report.errors))
            legacy_validation = {'as_of': today.isoformat(), 'errors': len(report.errors), 'warnings': len(report.warnings)}
        return {'publication': checked, 'replay': result, 'csv_generation': generation, 'csv_outputs': len(outputs), 'legacy_aliases': legacy, 'legacy_validation': legacy_validation, 'policy_scope_reviews': policy_scope_reviews}
    finally:
        active[0] = False
        os.chdir(old_cwd)
        sys.path[:] = old_path


def verify(directory, restore, expected):
    manifest, contents = verify_archive(directory, expected)
    root = restore_tree(restore, manifest, contents)
    result = replay(root)
    for record in manifest['files']:
        path = root / record['path']
        require(path.is_symlink() if record['kind'] == 'symlink' else path.is_file() and not path.is_symlink(), 'Member type changed')
        data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
        require(len(data) == record['bytes'] and digest(data) == record['sha256'], 'Member changed: ' + record['path'])
    return {'manifest_sha256': expected, 'verified_members': len(contents), 'checks': result,
            'scope': 'Internal portable consistency only; no source acceptance, freshness or release determination.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--restore', required=True, type=Path)
    parser.add_argument('--expected-manifest-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory, args.restore, args.expected_manifest_sha256), indent=2))


if __name__ == '__main__':
    main()
