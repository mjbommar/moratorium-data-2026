#!/usr/bin/env python3
"""Build deterministic public data assets from one committed revision."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def build(destination, revision):
    commit = git('rev-parse', revision+'^{commit}').decode().strip()
    names = git('ls-tree', '-r', '--name-only', commit).decode().splitlines()
    exact = {'data/moratorium_inventory.csv', 'data/state_legislation.csv', 'data/summary_stats.json',
             'data/identities/expanded.jsonl', 'data/expanded', 'LICENSE-data', 'LICENSE-code', 'CITATION.cff',
             'docs/codebook.md', 'docs/expanded-data-contracts.md', 'docs/expanded-promotion.md',
             'docs/expanded-identity-registry.md', 'docs/ballot-results.md', 'docs/ballot-measures.md',
             'docs/known-gaps.md', 'docs/methodology.md', 'docs/refresh-operations.md',
             'work/audit/ohio-place-coordinate-postreview-2026-11-06.json',
             'work/research/2026-11-06/perry-geography-review/validation.json',
             'work/research/2026-11-06/ohio-municipal-geography-review/validation.json',
             'work/research/2026-11-06/edgewater-restriction-migration/validation.json',
             'work/audit/ballot-release-dispositions-2026-11-06.json',
             'work/audit/refresh-baseline-delta-2026-11-06.json',
             'work/audit/refresh-baseline-delta-2026-11-06.md',
             'work/schemas/expanded/1.0.0.json'}
    selected = sorted(n for n in names if n in exact or n.startswith('data/expanded-snapshots/'))
    assert exact <= set(selected), exact-set(selected)
    manifest = {'schema_version': '1.0.0', 'candidate_status': 'unreleased_preparation',
                'source_commit': commit, 'working_cohort_cutoff': '2026-11-05',
                'scope': 'Public data and retained expanded publication history. Not proof of completed factual freshness, legal force, sibling synchronization or remote publication.',
                'files': []}
    paper = git('show', commit+':paper/moratorium-nation-2026-04-30.pdf')
    manifest['historical_paper'] = {'path': 'paper/moratorium-nation-2026-04-30.pdf',
        'url': f'https://github.com/mjbommar/moratorium-data-2026/blob/{commit}/paper/moratorium-nation-2026-04-30.pdf',
        'sha256': hashlib.sha256(paper).hexdigest(), 'bytes': len(paper),
        'disposition': 'Historical April edition; not synchronized to November data; linked rather than bundled.'}
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination/'moratorium-data-working-candidate.tar.gz'
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode='w') as tar:
                for name in selected:
                    data = git('show', commit+':'+name)
                    info = tarfile.TarInfo(name)
                    info.uid = info.gid = info.mtime = 0
                    info.mode = 0o644
                    if name == 'data/expanded':
                        info.type = tarfile.SYMTYPE
                        info.linkname = data.decode()
                        tar.addfile(info)
                        kind = 'symlink'
                    else:
                        info.size = len(data)
                        tar.addfile(info, io.BytesIO(data))
                        kind = 'file'
                    manifest['files'].append({'path': name, 'kind': kind, 'bytes': len(data),
                        'sha256': hashlib.sha256(data).hexdigest()})
    # Read every member back, including symlink target text, before accepting the asset.
    with tarfile.open(archive) as tar:
        for record in manifest['files']:
            member = tar.getmember(record['path'])
            content = member.linkname.encode() if member.issym() else tar.extractfile(member).read()
            assert len(content) == record['bytes']
            assert hashlib.sha256(content).hexdigest() == record['sha256']
    manifest['archive'] = {'name': archive.name, 'bytes': archive.stat().st_size,
                          'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}
    target = destination/'manifest.json'
    target.write_text(json.dumps(manifest, indent=2)+'\n')
    checks = [manifest['archive']['sha256']+'  '+archive.name,
              hashlib.sha256(target.read_bytes()).hexdigest()+'  '+target.name]
    (destination/'SHA256SUMS').write_text('\n'.join(checks)+'\n')
    print(json.dumps({'source_commit': commit, 'files': len(selected), 'archive': manifest['archive']}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('destination', type=Path)
    p.add_argument('--revision', default='HEAD')
    a = p.parse_args()
    build(a.destination, a.revision)
