#!/usr/bin/env python3
"""Recheck retained source lineage and reviewed claims; performs no publication."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_refresh_returns import evidence_index, audit_expanded_evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-directory', action='append', type=Path, required=True)
    args = parser.parse_args()
    review = json.loads(Path(__file__).with_name('review.json').read_text())
    index = {}
    for directory in args.evidence_directory:
        part, errors, _ = evidence_index(directory)
        if errors:
            raise ValueError(errors)
        for url, versions in part.items():
            index.setdefault(url, []).extend(versions)
    errors, proofs = audit_expanded_evidence(
        {'source_documents': review['sources'], 'claims': review['claims']},
        index, review['visual_reviews'])
    if errors:
        raise ValueError(errors)
    if not all(proof['evidence_verified'] for proof in proofs):
        raise ValueError('One or more claims have no located text or accepted visual support')
    entries = [json.loads(line) for line in
               (ROOT / 'work/sources/ND/manifest.jsonl').read_text().splitlines()]
    for source in review['sources']:
        if not any(entry.get('ok') and entry.get('text_chars', 0) > 0
                   and source['url'] in (entry['url'], entry.get('final_url'))
                   and entry.get('sha256') == source['body_sha256']
                   and entry.get('text_sha256') == source['text_sha256']
                   for entry in entries):
            raise ValueError('Missing archived source version: ' + source['source_document_id'])
    print(json.dumps({'sources': len(review['sources']), 'claims_verified': len(proofs),
                      'archive_versions_verified': len(review['sources']),
                      'scope': 'Evidence integrity and reviewed text/visual transcription only; no canonical publication, certification or legal-force determination.'}, indent=2))


if __name__ == '__main__':
    main()
