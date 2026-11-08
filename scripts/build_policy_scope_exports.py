#!/usr/bin/env python3
"""Build deterministic policy-scope views; --check detects any directory drift."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile

from policy_scope_reviews import INFRASTRUCTURE_SCOPE, METADATA_FIELDS, OUTCOMES, partition_reviews

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/state_legislation.csv'
REGISTRY = ROOT / 'data/state_policy_scope_reviews.jsonl'
OUTPUT = ROOT / 'data/policy-scope'
ALL = 'all-annotated.csv'
INCLUDED = 'reviewed-included.csv'
CANDIDATES = 'not-explicitly-excluded-candidates.csv'
RECEIPT = 'receipt.json'
NAMES = frozenset((ALL, INCLUDED, CANDIDATES, RECEIPT))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def render(raw_path, registry_path, *, scope=INFRASTRUCTURE_SCOPE):
    raw = Path(raw_path).read_bytes()
    registry_path = Path(registry_path)
    try:
        registry_before = registry_path.read_bytes()
    except FileNotFoundError:
        registry_before = None
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True)
    fields = reader.fieldnames
    if not fields or any(not f or not f.strip() for f in fields) or len(fields) != len(set(fields)):
        raise ValueError('CSV headers must be present, nonblank and unique')
    if 'policy_action_id' not in fields:
        raise ValueError('CSV header must contain policy_action_id')
    if set(fields) & set(METADATA_FIELDS):
        raise ValueError('scope metadata collision in CSV header')
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError('CSV row has a different number of fields than header')
    partitions = partition_reviews(rows, registry_path, scope=scope)
    lookup = {row['policy_action_id']: (status, event) for status, items in partitions.items() for row, event in items}
    annotated = []
    for row in rows:
        status, event = lookup[row['policy_action_id']]
        annotated.append({**row, METADATA_FIELDS[0]: status, METADATA_FIELDS[1]: event['decision_id'] if event else ''})

    def csv_bytes(selected):
        buffer = io.StringIO(newline='')
        writer = csv.DictWriter(buffer, fieldnames=fields + list(METADATA_FIELDS), lineterminator='\n')
        writer.writeheader()
        writer.writerows(selected)
        return buffer.getvalue().encode('utf-8')

    artifacts = {
        ALL: csv_bytes(annotated),
        INCLUDED: csv_bytes(r for r in annotated if r[METADATA_FIELDS[0]] == 'reviewed_include'),
        CANDIDATES: csv_bytes(r for r in annotated if r[METADATA_FIELDS[0]] != 'reviewed_exclude'),
    }
    try:
        registry_after = registry_path.read_bytes()
    except FileNotFoundError:
        registry_after = None
    if registry_after != registry_before:
        raise ValueError('scope registry changed during export')
    registry_hash = digest(registry_after) if registry_after is not None else None
    receipt = {
        'schema_version': '1.0.0', 'analytical_scope': scope,
        'inputs': {'raw_csv_sha256': digest(raw), 'registry_sha256': registry_hash},
        'raw_observation_count': len(rows),
        'partitions': {status: {'count': len(partitions[status]), 'policy_action_ids': [r['policy_action_id'] for r, _ in partitions[status]]} for status in OUTCOMES},
        'candidate_pool_count': len(rows) - len(partitions['reviewed_exclude']),
        'artifacts_sha256': {name: digest(data) for name, data in artifacts.items()},
        'caveat': 'Rows are historical observations, not a unique instrument census. The candidate pool is not reviewed inclusion. Scope review does not establish freshness or current legal force.',
    }
    artifacts[RECEIPT] = (json.dumps(receipt, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    return artifacts


def sync(artifacts, output, *, check=False, boundary=ROOT):
    # The boundary itself may be a symlink (for example a checkout alias).
    # Every component below it must be a real directory.
    boundary = Path(os.path.abspath(boundary))
    output = Path(os.path.abspath(output))
    try:
        relative = output.relative_to(boundary)
    except ValueError:
        raise ValueError('output must be within trusted boundary') from None
    if not boundary.is_dir():
        raise ValueError('trusted boundary must be an existing directory')
    output = boundary.resolve()
    for part in relative.parts:
        output = output / part
        if output.is_symlink():
            raise ValueError('symlinked output path component')
        if output.exists() and not output.is_dir():
            raise ValueError('output path component must be a directory')
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError('output must be a real directory')
    existing = {p.name for p in output.iterdir()} if output.exists() else set()
    extra = existing - NAMES
    if extra:
        raise ValueError(f'unexpected policy-scope output entries: {sorted(extra)}')
    if check:
        return existing == NAMES and all((output / name).is_file() and not (output / name).is_symlink() and (output / name).read_bytes() == data for name, data in artifacts.items())
    if any((output / name).is_symlink() or ((output / name).exists() and not (output / name).is_file()) for name in NAMES):
        raise ValueError('output entries must be regular files')
    output.mkdir(parents=True, exist_ok=True)
    staged = []
    try:
        for name, data in artifacts.items():
            with tempfile.NamedTemporaryFile(dir=output, prefix='.scope-', delete=False) as f:
                staged.append(Path(f.name))
                f.write(data)
        for temp, name in zip(staged, artifacts):
            os.replace(temp, output / name)
    finally:
        for temp in staged:
            temp.unlink(missing_ok=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        ok = sync(render(RAW, REGISTRY), OUTPUT, check=args.check)
    except (ValueError, OSError, UnicodeError, csv.Error) as exc:
        parser.exit(1, f'policy-scope exports: {exc}\n')
    print('policy-scope exports ' + ('current' if args.check and ok else 'OUT OF DATE' if args.check else 'written'))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
