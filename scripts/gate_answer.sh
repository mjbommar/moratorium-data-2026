#!/usr/bin/env bash
# Coordinator gate for one answer file: schema, dry-run conflicts, archived evidence.
set -u
f="$1"
python3 - "$f" <<'PY'
import json, jsonschema, sys
s=json.load(open("work/schemas/research_decision.schema.json")); d=json.load(open(sys.argv[1]))
jsonschema.validate(d,s)
from collections import Counter
print("schema ok |", dict(Counter(x["outcome"] for x in d["decisions"])), "| candidates:", len(d.get("new_candidates",[])))
for x in d["decisions"]:
    if x["outcome"]=="status_changed": print("  ", x["moratorium_id"], "->", x.get("new_enacted_status"), x.get("confidence"))
for c in d.get("new_candidates",[]): print("  CAND", c["jurisdiction"], c["jurisdiction_type"], c["enacted_status"], c.get("date_enacted_iso"), c.get("duration_kind"), c.get("current_end_date_iso"), c["confidence"], sorted({e["source_type"] for e in c["evidence"]}))
PY
python3 scripts/apply_research.py --answers "$f" --dry-run 2>&1 | grep -iE "conflict|unknown|refuses|SKIP|rows_touched|rows_added|candidate_duplicate|low_confidence"
python3 scripts/check_evidence_archived.py "$f" | head -4
