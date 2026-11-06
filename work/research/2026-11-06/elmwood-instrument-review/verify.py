#!/usr/bin/env python3
"""Verify retained Elmwood evidence and applied correction receipt; no refetches."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_refresh_returns import evidence_index
from bc_core.text import locate_quote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-directory', type=Path, required=True)
    args = parser.parse_args()
    directory = Path(__file__).parent
    review = json.loads((directory / 'review.json').read_text())
    answers = directory / 'answers.json'
    assert hashlib.sha256(answers.read_bytes()).hexdigest() == review['answers_sha256']
    index, errors, _ = evidence_index(args.evidence_directory)
    assert not errors, errors
    archive = [json.loads(line) for line in (ROOT / 'work/sources/MI/manifest.jsonl').read_text().splitlines()]
    versions = {}
    for source in review['source_versions']:
        version = next(x for x in index[source['url']]
                       if x['attempt_id'] == source['attempt_id']
                       and x['body_sha256'] == source['body_sha256']
                       and x['text_sha256'] == source['reviewed_text_sha256'])
        versions[source['attempt_id']] = version
        assert any(x.get('ok') and x.get('sha256') == source['body_sha256']
                   and x.get('text_sha256') == source['reviewed_text_sha256']
                   and source['url'] in (x['url'], x.get('final_url')) for x in archive)
    for claim in review['located_evidence']:
        version = versions[claim['attempt_id']]
        assert version['body_sha256'] == claim['body_sha256']
        assert version['text_sha256'] == claim['text_sha256']
        assert locate_quote(version['text'], claim['quote']) is not None
    for visual in review['visual_reviews']:
        render = args.evidence_directory / f"{visual['document']}-page{visual['page']}.png"
        assert hashlib.sha256(render.read_bytes()).hexdigest() == visual['render_sha256']
    receipt = json.loads((ROOT / review['apply_receipt']).read_text())
    expected = json.loads(answers.read_text())['decisions'][0]['changes']
    assert not receipt['conflicts'] and len(receipt['changes']) == len(expected) == 4
    for change in receipt['changes']:
        assert change['moratorium_id'] == review['moratorium_id']
        wanted = expected[change['column']]
        assert change['before'] == wanted['from'] and change['after'] == wanted['to']
    print(json.dumps({'source_versions_verified': len(versions),
                      'quotes_verified': len(review['located_evidence']),
                      'renders_verified': len(review['visual_reviews']),
                      'applied_field_changes_verified': len(expected),
                      'scope': 'Retained lineage and historical apply receipt only; not current force, publication, complete successor identity or later-law absence.'}, indent=2))


if __name__ == '__main__':
    main()
