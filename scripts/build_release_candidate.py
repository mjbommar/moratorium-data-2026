#!/usr/bin/env python3
"""Build deterministic public data assets from one committed revision."""
import argparse
import gzip
import hashlib
import io
import json
import re
from pathlib import Path
import subprocess
import tarfile
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]

# Reviewed public metadata only; raw evidence and other research files stay out.
PUBLIC_NOV7_METADATA = (
    'work/audit/refresh-field-accounting-2026-11-07.md',
    'work/audit/refresh-field-accounting-2026-11-07.json',
    'work/research/2026-11-07/wilmington-initiative-history/README.md',
    'work/research/2026-11-07/wilmington-initiative-history/validation.json',
    'work/research/2026-11-07/wilmington-initiative-history/publication-plan.json',
    'work/research/2026-11-07/wilmington-initiative-history/identity-plan.json',
    'work/research/2026-11-07/wilmington-initiative-history/apply.json',
    'work/research/2026-11-07/wilmington-initiative-history/replay.json',
    'work/research/2026-11-07/wilmington-initiative-history/identity-apply.json',
    'work/research/2026-11-07/wilmington-initiative-history/coordinator-corrections.json',
    'work/research/2026-11-07/wilmington-initiative-history/review-provenance.json',
    'work/research/2026-11-07/wilmington-initiative-history/worklist-comparison.json',
    'work/research/2026-11-07/wilmington-initiative-history/git-generation-byte-check.json',
    'work/research/2026-11-07/executive-force-review/README.md',
    'work/research/2026-11-07/executive-force-review/validation.json',
    'work/research/2026-11-07/executive-force-review/exact-diff.json',
    'work/research/2026-11-07/executive-force-review/review-provenance.json',
    'work/research/2026-11-07/executive-force-review/source-versions.json',
    'work/research/2026-11-07/executive-force-review/date-extraction-fidelity.json',
    'work/research/2026-11-07/executive-force-review/sb6-source-assessment.json',
    'work/research/2026-11-07/state-policy-forms/README.md',
    'work/research/2026-11-07/state-policy-forms/validation.json',
    'work/research/2026-11-07/state-policy-forms/exact-diff.json',
    'work/research/2026-11-07/state-policy-forms/native-migration-summary.json',
    'work/research/2026-11-07/state-policy-forms/source-review.json',
    'work/research/2026-11-07/state-policy-forms/visual-review.json',
)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def select_files(commit, names):
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
    # Include each retained top-level profile used by the selected validator;
    # the original schema remains required by frozen retrospective fixtures.
    exact.update(n for n in names if n.startswith('work/schemas/expanded/')
                 and len(Path(n).parts)==4 and n.endswith('.json'))
    exact.update(n for n in ['docs/compound-condition-development.md',
                              'work/schemas/condition-expression/1.0.0.json',
                              'work/schemas/extraction/1.2.0.json'] if n in names)
    exact.update(n for n in ['docs/instrument-events.md','docs/ballot-semantic-definitions.md','docs/event-validity-publication.md','docs/event-maintenance-development.md','docs/policy-succession-contract.md'] if n in names)
    compound_review='work/research/2026-11-06/compound-clause-source-review/'
    if compound_review+'selection.json' in names:
        exact.update(n for n in names if n.startswith(compound_review))
        exact.update({'scripts/condition_expression.py','scripts/condition_scoring.py'})
    for event_review in ['work/research/2026-11-06/instrument-event-migration/','work/research/2026-11-06/event-validity-migration/']:
        if event_review+'cohort.json' in names:
            exact.update(n for n in names if n.startswith(event_review))
    if 'data/expanded-csv' in names:
        exact.update({'data/expanded-csv', 'data/README.md'})
    if 'data/identities/legacy-moratoria.jsonl' in names:
        exact.update({'data/identities/legacy-moratoria.jsonl', 'docs/legacy-moratorium-identities.md',
                      'scripts/legacy_moratorium_identity.py', 'scripts/preview_legacy_identity.py',
                      'work/research/2026-11-06/seattle-identity-review/retirement-plan.json',
                      'work/research/2026-11-06/seattle-identity-review/retirement-validation.json'})
    sector_review = 'work/research/2026-11-06/el-dorado-sector-lineage/'
    if sector_review+'sector-visual-review.json' in names:
        exact.update(n for n in names if n.startswith(sector_review))
    pilot = 'work/research/2026-11-06/pilot-contract-review/'
    if pilot+'manifest.json' in names:
        # Keep the frozen fixture check runnable without private source bodies
        # or a full Git checkout. All inputs are selected from this revision.
        exact.update(n for n in names if n.startswith(pilot))
        exact.update({'scripts/audit_pilot_contracts.py', 'scripts/expanded_data.py',
                      'scripts/expanded_promotion.py', 'scripts/expanded_identity.py',
                      'scripts/audit_refresh_returns.py', 'scripts/visual_claim_review.py',
                      'scripts/check_expanded_publication.py','scripts/build_expanded_csv.py','scripts/instrument_event_maintenance.py'})
        validator=git('show',commit+':scripts/expanded_data.py').decode()
        dependencies=set(re.findall(r'work/schemas/expanded/\d+\.\d+\.\d+\.json',validator))
        if 'PROFILE_NAMES' in validator:
            import ast
            declaration=next(n for n in ast.parse(validator).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROFILE_NAMES' for t in n.targets))
            dependencies.update('work/schemas/expanded/'+name+'.json' for name in ast.literal_eval(declaration.value))
            if '1.0.2' in ast.literal_eval(declaration.value):
                assert 'scripts/instrument_event_maintenance.py' in names,'Missing event maintenance runtime dependency'
        assert dependencies<=set(names),'Validator profile absent from selected commit: '+str(dependencies-set(names))
        exact.update(dependencies)
        frozen = json.loads(git('show', commit+':'+pilot+'manifest.json'))
        for case in frozen['cases']:
            for evidence in case['evidence_files']:
                path = evidence['path']
                assert path.startswith('work/research/') and '..' not in Path(path).parts
                exact.add(path)
    # Optional for older revisions: never select a path absent from the tree.
    exact.update(n for n in PUBLIC_NOV7_METADATA if n in names)
    exact.update(n for n in ('work/research/2026-11-08/alabama-field-reconciliation/README.md', 'work/research/2026-11-08/alabama-field-reconciliation/application.json', 'work/research/2026-11-08/alabama-field-reconciliation/native-source-continuity.json', 'work/research/2026-11-08/alabama-field-reconciliation/hosted-selected-files.json', 'work/research/2026-11-08/policy-scope-export-development/README.md', 'work/research/2026-11-08/policy-scope-export-development/validation.json', 'work/research/2026-11-08/alabama-batches3to5-reconciliation/README.md', 'work/research/2026-11-08/alabama-batches3to5-reconciliation/application.json', 'work/research/2026-11-08/alabama-batches3to5-reconciliation/native-source-continuity.json', 'work/research/2026-11-08/policy-scope-export-development/portable-checkpoint-verification.json', 'work/research/2026-11-08/policy-scope-export-development/hosted-selected-files.json', 'work/research/2026-11-08/al-ak-az-ar-batches6to8-reconciliation/README.md', 'work/research/2026-11-08/al-ak-az-ar-batches6to8-reconciliation/application.json', 'work/research/2026-11-08/al-ak-az-ar-batches6to8-reconciliation/native-source-continuity.json') if n in names)
    exact.update(n for n in ('scripts/verify_release_candidate.py', 'scripts/validate_dataset.py', 'scripts/build_summary_stats.py',
                             'scripts/policy_scope_reviews.py', 'scripts/build_policy_scope_exports.py',
                             'docs/policy-scope-exports.md', 'data/state_policy_scope_reviews.jsonl',
                             'data/policy-scope/all-annotated.csv', 'data/policy-scope/reviewed-included.csv',
                             'data/policy-scope/not-explicitly-excluded-candidates.csv', 'data/policy-scope/receipt.json',
                             'data/sweep_coverage.json') if n in names)
    if 'scripts/build_policy_scope_exports.py' in names:
        required = {'scripts/verify_release_candidate.py', 'scripts/build_summary_stats.py', 'scripts/policy_scope_reviews.py', 'docs/policy-scope-exports.md',
                    'data/state_policy_scope_reviews.jsonl', 'data/policy-scope/all-annotated.csv',
                    'data/policy-scope/reviewed-included.csv',
                    'data/policy-scope/not-explicitly-excluded-candidates.csv', 'data/policy-scope/receipt.json'}
        assert required <= set(names), 'Incomplete policy-scope export: ' + str(required - set(names))
        scope_outputs = {n for n in names if n.startswith('data/policy-scope/')}
        assert scope_outputs == {n for n in required if n.startswith('data/policy-scope/')}, 'Unexpected policy-scope output set'
    # The summary builder consults state page existence and sweep coverage.
    stats = json.loads(git('show', commit+':data/summary_stats.json'))
    exact.update('states/'+detail['file'] for detail in stats.get('state_details', {}).values()
                 if detail.get('file') and 'states/'+detail['file'] in names)
    selected = sorted(n for n in names if n in exact or n.startswith(('data/expanded-snapshots/', 'data/expanded-csv-snapshots/')))
    assert exact <= set(selected), exact-set(selected)
    return selected


def build(destination, revision):
    commit = git('rev-parse', revision+'^{commit}').decode().strip()
    names = git('ls-tree', '-r', '--name-only', commit).decode().splitlines()
    selected = select_files(commit, names)
    # Capture the selected commit bytes once; both the scope check and archive use them.
    contents = {name: git('show', commit + ':' + name) for name in selected}
    if 'scripts/build_policy_scope_exports.py' in selected:
        with tempfile.TemporaryDirectory(prefix='policy-scope-release-') as tmp:
            root = Path(tmp)
            for name, data in contents.items():
                if name in ('data/expanded', 'data/expanded-csv'):
                    continue
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            subprocess.run([sys.executable, '-I', '-B', str(root / 'scripts/verify_release_candidate.py'),
                            '--scope-only', str(root)], check=True)
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
                    data = contents[name]
                    info = tarfile.TarInfo(name)
                    info.uid = info.gid = info.mtime = 0
                    info.mode = 0o644
                    if name in {'data/expanded', 'data/expanded-csv'}:
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
