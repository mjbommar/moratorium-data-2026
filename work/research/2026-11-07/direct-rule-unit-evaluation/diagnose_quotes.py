"""Read-only post-run diagnostics; never repair or accept generated quotations."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


def diagnose(protocol_path):
    raw = Path(protocol_path).read_bytes()
    protocol = json.loads(raw)
    root = Path(protocol['private_root'])/'provider'
    marker = json.loads((root/'execution.private.json').read_text())
    if marker['protocol_sha256'] != hashlib.sha256(raw).hexdigest():
        raise ValueError('Execution/protocol mismatch')
    results = {}
    for case in protocol['cases']:
        text = Path(case['text_path']).read_text()
        if hashlib.sha256(text.encode()).hexdigest() != case['text_sha256']:
            raise ValueError('Source changed')
        flat = re.sub(r'\s+', ' ', text)
        packet = json.loads((root/case['case_id']/'rule-units-candidates.private.json').read_text())
        quotes, units, contexts = Counter(), Counter(), Counter()
        for unit in packet['units']:
            if unit.get('review_flags'):
                units['units_with_flags'] += 1
            units.update(unit.get('review_flags', []))
            if unit.get('clause'):
                contexts[unit['clause']['assertion_context']] += 1
            for item in unit.get('supporting_quotes', []) + unit.get('condition_quote_locations', []):
                quotes['checked_quote_instances'] += 1
                if not item['spans']:
                    quotes['unlocated_quote_instances'] += 1
                    if not item['quote'].strip():
                        quotes['empty_or_whitespace_quotes'] += 1
                    elif re.sub(r'\s+', ' ', item['quote']) in flat:
                        quotes['unlocated_but_whitespace_match'] += 1
                    else:
                        quotes['unlocated_without_whitespace_match'] += 1
                elif len(item['spans']) > 1:
                    quotes['multiple_exact_locations'] += 1
        results[case['case_id']] = dict(planned=packet['planned_count'],
            returned_candidates=packet['candidate_count'], unresolved=packet['unresolved_count'],
            unit_flags=dict(units), quote_instances=dict(quotes),
            returned_assertion_contexts=dict(contexts))
    return dict(protocol_sha256=marker['protocol_sha256'], cases=results,
        scope='Counts only. Whitespace comparison is diagnostic, not an alignment, source correction, quote acceptance or semantic judgment. Original candidates and flags are unchanged.')


if __name__ == '__main__':
    print(json.dumps(diagnose(sys.argv[1]), indent=2))
