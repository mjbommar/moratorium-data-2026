#!/usr/bin/env python3
"""Export pinned public working inputs without accepting downstream joins or force."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def export(destination):
    snapshot = (ROOT / 'data/expanded').resolve(strict=True)
    sources = [ROOT / 'data' / n for n in
               ('moratorium_inventory.csv', 'state_legislation.csv', 'summary_stats.json')]
    sources += sorted(snapshot.glob('*.jsonl'))
    sources += [ROOT / 'data/identities/expanded.jsonl',
                ROOT / 'docs/expanded-data-contracts.md', ROOT / 'docs/ballot-measures.md',
                ROOT / 'docs/known-gaps.md',
                ROOT / 'work/audit/ballot-release-dispositions-2026-11-06.json']
    contents = {}
    files = []
    for source in sources:
        relative = ('expanded/' + source.name if source.parent == snapshot
                    else str(source.relative_to(ROOT)))
        raw = source.read_bytes()
        if source.suffix == '.jsonl':
            count = sum(1 for line in raw.splitlines() if json.loads(line))
        elif source.suffix == '.csv':
            count = len(list(csv.DictReader(io.StringIO(raw.decode()))))
        else:
            count = None
        contents[relative] = raw
        files.append(dict(path=relative, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                          records=count))
    manifest = dict(schema_version='1.0.0', source_repository='moratorium-data-2026',
                    source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    working_cohort_cutoff='2026-11-05', review_observation_date='2026-11-06',
                    expanded_snapshot=snapshot.name, files=files,
                    scope='Public current-table input export. Not a release, complete historical replay bundle, renewed legal-force finding or downstream join acceptance.',
                    limits=['Predecessor expanded generations and raw source bodies are not included.',
                            'Historical collaborator packets and project/disclosure cutoffs are unchanged.',
                            'No proximity, project applicability, instrument links or causal relationship is inferred.',
                            'Seven ballot candidate groups remain unresolved; current expanded instrument/link tables are empty.'])
    contents['manifest.json'] = (json.dumps(manifest, indent=2)+'\n').encode()
    contents['README.md'] = ('# November reviewed working inputs\n\n'
        'Use manifest.json for source revision, cohort cutoff, file hashes and record counts. '
        'The legacy local/state CSVs and expanded ballot tables have separate denominators. '
        'This additive input snapshot does not rebuild or supersede historical bridge outputs, '
        'collaborator packets, project/disclosure corpora or accepted legal-applicability joins. '
        'It is not a complete replay archive: obtain retained expanded generations from the source repository. '
        'Unknown implementation dates and unresolved candidates remain unknown.\n').encode()
    destination.mkdir(parents=True, exist_ok=True)
    for name, raw in contents.items():
        path = destination / name
        if path.exists() and path.read_bytes() != raw:
            raise ValueError(f'Refusing to overwrite different snapshot bytes: {path}')
    for name, raw in contents.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        assert path.read_bytes() == raw
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    result = export(args.destination)
    print(json.dumps({'files': len(result['files']), 'snapshot': result['expanded_snapshot'],
                      'destination': str(args.destination)}, indent=2))
