#!/usr/bin/env python3
"""Apply research decision files to the inventory, deterministically.

Research produces JSON decision files (work/schemas/research_decision.schema.json).
This script is the only thing that writes those findings into
data/moratorium_inventory.csv. Prose never edits the CSV.

Discipline borrowed from the sibling servercountry.org data-maintenance workflow:

  * Answer files must be named explicitly (--answers) or by an explicit
    directory (--answers-dir). The script never selects a file by mtime.
  * Every decision's `changes.<column>.from` must match the value currently in
    the CSV. A mismatch means the answer was written against a different
    revision, so the field is skipped and reported as a conflict rather than
    silently clobbering newer data. --allow-drift overrides, deliberately.
  * Decisions with outcome=unresolvable, or confidence below --min-confidence,
    are recorded and skipped.
  * Every applied change is written to an audit log.

Run from repo root:
    python3 scripts/apply_research.py --answers-dir work/answers/status --dry-run
    python3 scripts/apply_research.py --answers-dir work/answers/status
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "data" / "moratorium_inventory.csv"
SCHEMA = REPO / "work" / "schemas" / "research_decision.schema.json"
AUDIT_DIR = REPO / "work" / "audit"

VERIFY_MARKER_RE = re.compile(r"\[VERIFY[^\]]*\]", re.IGNORECASE)
SLUG_RE = re.compile(r"[^a-z0-9]+")

# Columns a decision is allowed to touch. Derived columns are recomputed, not set.
PROTECTED_COLUMNS = {"moratorium_id", "has_verify_tags", "verify_count", "state_abbrev"}

# Fields that appear in a worklist packet but are not inventory columns.
# Researchers naturally try to write the corrected value back to them; the real
# content lands in `duration` / `current_status`, so drop these quietly rather
# than reporting a conflict that needs no action.
PACKET_ONLY_FIELDS = {
    "computed_expiry", "days_past_expiry", "buckets", "priority", "questions",
    "verify_markers", "context",
}

# Column order for newly constructed rows.
INVENTORY_COLUMNS = [
    "state", "state_abbrev", "jurisdiction", "jurisdiction_type", "date_enacted",
    "duration", "legal_basis", "trigger", "current_status", "affected_projects",
    "outcome", "has_verify_tags", "verify_count", "cite_count", "activity_level",
    "enacted_status", "moratorium_id", "latitude", "longitude", "date_enacted_iso",
    "date_enacted_uncertainty", "duration_days", "duration_kind", "sectors",
    "trigger_categories",
]

STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
}


def slugify(text: str) -> str:
    return SLUG_RE.sub("-", text.lower()).strip("-")


def instrument_key(legal_basis: str) -> str:
    """Normalized instrument identifier extracted from `legal_basis`.

    One jurisdiction can adopt several distinct moratoria on the same day --
    Shelby County, IA adopted Resolutions 2026-14/15/16/17 covering solar,
    battery storage, data centers, and wind respectively. Those are four
    instruments and therefore four rows, so deduplication cannot key on
    jurisdiction alone. Returns "" when no instrument number is recoverable,
    in which case the caller falls back to conservative jurisdiction matching.
    """
    if not legal_basis:
        return ""
    # Prefer an explicit ordinance/resolution number, e.g. "Resolution 2026-14",
    # "Ord. No. 3063", "Resolution #21 FYR 25/26".
    m = re.search(
        r"\b(ordinance|resolution|ord|res)\b[\s.#no:]*([0-9][0-9a-z\-/]*)",
        legal_basis, re.IGNORECASE,
    )
    if m:
        return f"{m.group(1).lower().rstrip('.')}-{m.group(2).lower()}"
    return ""


# The inventory contains typographic punctuation (43 em dashes, 6 en dashes, a
# few ellipses and math symbols). Researchers working under an ASCII-only house
# style transliterate these when quoting a value back, which would otherwise
# read as a mismatch. Comparison is therefore done on a canonical form; writing
# still uses the exact strings.
_COMPARE_MAP = {
    "—": "--", "–": "-", "…": "...", "≥": ">=", "≤": "<=",
    "‘": "'", "’": "'", "“": '"', "”": '"', " ": " ",
    "§": "section",
}


def canon(text: str) -> str:
    """Canonical form used only for comparing researcher text against the CSV."""
    out = text or ""
    for src, dst in _COMPARE_MAP.items():
        out = out.replace(src, dst)
    # An em dash may be transliterated as "--" or as a single "-", so collapse
    # runs of hyphens rather than betting on which convention was used.
    out = re.sub(r"-{2,}", "-", out)
    return re.sub(r"\s+", " ", out).strip().lower()


def strip_marker(text: str, marker: str) -> str:
    """Remove one [VERIFY ...] marker and tidy the whitespace it leaves behind."""
    if marker in text:
        out = text.replace(marker, "")
    else:
        # Match on canonical form so a transliterated quote still finds its
        # marker, but delete the verbatim text that is actually in the field.
        target = canon(marker)
        for found in VERIFY_MARKER_RE.findall(text):
            if canon(found) == target:
                out = text.replace(found, "")
                break
        else:
            return text
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([,.;])", r"\1", out)
    out = re.sub(r"\(\s*\)", "", out)
    return out.strip()


def rel_to_repo(path: Path) -> str:
    """Repo-relative path string, tolerant of relative CLI arguments."""
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def read_inventory() -> tuple[list[dict], list[str]]:
    # newline="" keeps the CRLF terminators intact; passing it to open() rather
    # than Path.read_text() keeps this working on Python 3.12.
    with open(INV, encoding="utf-8", newline="") as f:
        src = f.read()
    reader = csv.DictReader(io.StringIO(src))
    return list(reader), list(reader.fieldnames or [])


def write_inventory(rows: list[dict], fieldnames: list[str]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    with open(INV, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())


FIXED_TERM_HINT = re.compile(
    r"\b(\d+\s*(days?|months?|years?)|one\s+year|two\s+years|six\s+months|"
    r"eighteen\s*\(?18\)?\s*months?|twelve\s+months)\b", re.IGNORECASE,
)


def enforce_duration_invariant(row: dict) -> str | None:
    """Keep duration_days populated iff duration_kind is fixed_days.

    Researchers routinely set one without the other. Left alone, the merge would
    write a combination the validator rejects, and a later normalization pass
    would clear it -- only for the next merge to write it back. Enforcing the
    codebook rule here breaks that loop at the source.
    """
    kind = row["duration_kind"]
    days = row["duration_days"].strip()
    if kind == "fixed_days" and not days:
        return None  # reconcile_durations derives the value from the text
    if kind != "fixed_days" and days:
        if FIXED_TERM_HINT.search(row["duration"] or ""):
            row["duration_kind"] = "fixed_days"
            return f"duration_kind {kind} -> fixed_days (duration text states a term)"
        row["duration_days"] = ""
        return f"duration_days cleared (duration_kind={kind} takes no term length)"
    return None


ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_MONTH = re.compile(r"^\d{4}-\d{2}$")
ISO_YEAR = re.compile(r"^\d{4}$")


def enforce_date_invariant(row: dict) -> str | None:
    """Keep date_enacted_uncertainty consistent with date_enacted_iso's precision.

    Researchers who write an approximate date ("adopted ~2026-02-26") often pair a
    full day-precision value with `month_only`, which the codebook forbids. The
    honest resolution keeps the day -- it is real information -- and downgrades
    the flag to `unverified`, rather than discarding the day to match the flag.
    """
    iso = row["date_enacted_iso"].strip()
    unc = row["date_enacted_uncertainty"]
    if not iso:
        return None
    if ISO_DAY.match(iso) and unc in {"month_only", "year_only"}:
        row["date_enacted_uncertainty"] = "unverified"
        return f"date_enacted_uncertainty {unc} -> unverified (day-precision date retained)"
    if ISO_MONTH.match(iso) and unc not in {"month_only", "unverified", "range"}:
        row["date_enacted_uncertainty"] = "month_only"
        return f"date_enacted_uncertainty {unc} -> month_only (month-precision date)"
    if ISO_YEAR.match(iso) and unc not in {"year_only", "unverified", "range"}:
        row["date_enacted_uncertainty"] = "year_only"
        return f"date_enacted_uncertainty {unc} -> year_only (year-precision date)"
    return None


def recompute_verify(row: dict) -> None:
    count = sum(len(VERIFY_MARKER_RE.findall(v or "")) for v in row.values())
    row["verify_count"] = str(count)
    row["has_verify_tags"] = "True" if count else "False"


def load_answers(paths: list[Path], schema: dict | None) -> list[tuple[Path, dict]]:
    out = []
    for path in sorted(paths):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  SKIP {path.name}: invalid JSON ({exc})")
            continue
        if schema is not None:
            try:
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as exc:
                loc = "/".join(str(p) for p in exc.absolute_path)
                print(f"  SKIP {path.name}: schema violation at {loc or '<root>'}: {exc.message}")
                continue
        out.append((path, data))
    return out


def make_moratorium_id(candidate: dict, taken: set[str]) -> str:
    abbrev = STATE_ABBREV.get(candidate["state"], "xx").lower()
    slug = slugify(candidate["jurisdiction"])
    iso = (candidate.get("date_enacted_iso") or "").strip()
    year = iso[:4] if re.match(r"^\d{4}", iso) else "undated"
    base = f"{abbrev}-{slug}-{year}"
    if base not in taken:
        return base
    n = 2
    while f"{base}-{n}" in taken:
        n += 1
    return f"{base}-{n}"


def verify_note_for(candidate: dict) -> str:
    """A [VERIFY] marker describing what a weakly-evidenced new row still needs.

    A row admitted on news-only evidence deserves the same machine-visible
    uncertainty flag as a legacy unverified row; otherwise it silently reads as
    established fact and never resurfaces in a worklist.
    """
    gaps = []
    if not instrument_key(candidate.get("legal_basis", "")):
        gaps.append("instrument number")
    if not (candidate.get("duration_days") or candidate.get("duration")):
        gaps.append("duration")
    if not (candidate.get("date_enacted_iso") or "").strip():
        gaps.append("adoption date")
    sources = {e.get("source_type", "other") for e in candidate.get("evidence", [])}
    primary = sources - {"news", "other"}
    if not primary:
        gaps.append("primary source (news-only evidence)")
    detail = "; ".join(gaps) if gaps else "details"
    conf = candidate.get("confidence")
    conf_txt = f" at confidence {conf}" if conf is not None else ""
    return f"[VERIFY {detail} not confirmed{conf_txt} in the 2026-07 refresh]"


def build_row(candidate: dict, mid: str, activity_level: str) -> dict:
    iso = (candidate.get("date_enacted_iso") or "").strip()
    days = candidate.get("duration_days")
    row = {c: "" for c in INVENTORY_COLUMNS}
    row.update({
        "state": candidate["state"],
        "state_abbrev": STATE_ABBREV.get(candidate["state"], ""),
        "jurisdiction": candidate["jurisdiction"],
        "jurisdiction_type": candidate["jurisdiction_type"],
        "date_enacted": candidate.get("date_enacted", ""),
        "duration": candidate.get("duration", ""),
        "legal_basis": candidate.get("legal_basis", ""),
        "trigger": candidate.get("trigger", ""),
        "current_status": candidate.get("current_status", ""),
        "affected_projects": candidate.get("affected_projects", ""),
        "outcome": candidate.get("outcome", ""),
        "cite_count": "0",
        "activity_level": activity_level,
        "enacted_status": candidate.get("enacted_status", "active"),
        "moratorium_id": mid,
        "date_enacted_iso": iso,
        "date_enacted_uncertainty": candidate.get("date_enacted_uncertainty", "unverified"),
        "duration_days": "" if days in (None, "") else str(int(days)),
        "duration_kind": candidate.get("duration_kind", "unknown"),
        "sectors": json.dumps(candidate.get("sectors", ["data_center"]), separators=(",", ":")),
        "trigger_categories": json.dumps(candidate.get("trigger_categories", []), separators=(",", ":")),
    })
    # New rows go through the same codebook invariants as edited ones; a
    # researcher pairing an approximate day-precision date with `month_only`
    # would otherwise land an invalid row straight into the CSV.
    enforce_duration_invariant(row)
    enforce_date_invariant(row)
    recompute_verify(row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--answers", nargs="+", help="explicit answer file paths")
    src.add_argument("--answers-dir", help="directory of answer files (*.json)")
    ap.add_argument("--dry-run", action="store_true", help="report without writing")
    ap.add_argument("--allow-drift", action="store_true",
                    help="apply changes even when `from` does not match the current CSV value")
    ap.add_argument("--min-confidence", type=float, default=0.4,
                    help="skip decisions below this confidence (default: 0.4)")
    ap.add_argument("--no-candidates", action="store_true", help="ignore new_candidates arrays")
    ap.add_argument("--verify-threshold", type=float, default=0.7,
                    help="new rows below this confidence get a [VERIFY] marker (default: 0.7)")
    args = ap.parse_args()

    if args.answers:
        paths = [Path(p) for p in args.answers]
    else:
        paths = sorted(Path(args.answers_dir).glob("*.json"))
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"ERROR: missing answer file(s): {[str(p) for p in missing]}")
        return 2
    if not paths:
        print("ERROR: no answer files found")
        return 2

    schema = None
    if jsonschema is not None and SCHEMA.exists():
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    else:
        print("WARNING: jsonschema unavailable or schema missing; structural validation skipped")

    print(f"Loading {len(paths)} answer file(s)...")
    answers = load_answers(paths, schema)
    print(f"  {len(answers)} file(s) passed validation")

    rows, fieldnames = read_inventory()
    by_id = {r["moratorium_id"]: r for r in rows}
    taken_ids = set(by_id)
    # Activity level is a per-state attribute; reuse the state's existing value
    # so a new row does not invent one.
    activity_by_state = {r["state"]: r["activity_level"] for r in rows}

    audit: list[dict] = []
    conflicts: list[str] = []
    skipped: list[str] = []
    stats: Counter = Counter()
    touched: set[str] = set()
    new_rows: list[dict] = []

    for path, data in answers:
        for dec in data.get("decisions", []):
            mid = dec["moratorium_id"]
            stats[f"outcome:{dec['outcome']}"] += 1
            row = by_id.get(mid)
            if row is None:
                conflicts.append(f"{path.name}: unknown moratorium_id {mid!r}")
                stats["skipped_unknown_id"] += 1
                continue
            if dec["outcome"] == "unresolvable":
                skipped.append(f"{path.name}: {mid} unresolvable")
                continue
            conf = dec.get("confidence")
            if conf is not None and conf < args.min_confidence:
                skipped.append(f"{path.name}: {mid} confidence {conf} < {args.min_confidence}")
                stats["skipped_low_confidence"] += 1
                continue

            # --- field changes -------------------------------------------------
            rewritten: set[str] = set()
            for column, change in (dec.get("changes") or {}).items():
                if column in PACKET_ONLY_FIELDS:
                    stats["ignored_packet_only_field"] += 1
                    continue
                if column not in fieldnames:
                    conflicts.append(f"{path.name}: {mid} unknown column {column!r}")
                    continue
                if column in PROTECTED_COLUMNS:
                    conflicts.append(f"{path.name}: {mid} refuses to set protected column {column!r}")
                    continue
                current = row[column]
                # Check "already applied" before the drift guard so re-running the
                # same answer file is a clean no-op rather than a wall of
                # conflicts. Incremental application is the normal workflow here:
                # states land at different times.
                if canon(current) == canon(change["to"]):
                    stats["already_applied"] += 1
                    continue
                # Pre-empt a write the codebook invariant would immediately undo.
                # Without this the merge and the normalizer ping-pong: the answer
                # sets duration_days, the invariant clears it, and the next run
                # sets it again, rewriting the CSV on every otherwise-no-op pass.
                if column == "duration_days" and change["to"].strip():
                    kind = (dec.get("changes") or {}).get("duration_kind", {}).get("to") or row["duration_kind"]
                    if kind != "fixed_days" and not FIXED_TERM_HINT.search(row["duration"] or ""):
                        stats["skipped_duration_invariant"] += 1
                        continue
                if canon(current) != canon(change["from"]) and not args.allow_drift:
                    conflicts.append(
                        f"{path.name}: {mid}.{column} `from` mismatch "
                        f"(csv={current[:60]!r} answer={change['from'][:60]!r})"
                    )
                    stats["skipped_drift"] += 1
                    continue
                audit.append({
                    "moratorium_id": mid, "column": column, "before": current,
                    "after": change["to"], "reason": change.get("reason", ""),
                    "source": path.name,
                })
                row[column] = change["to"]
                rewritten.add(column)
                touched.add(mid)
                # Researchers set enacted_status either here or via
                # new_enacted_status; count both under one heading so the
                # release notes can quote a single honest number.
                stats["status_changed" if column == "enacted_status" else "fields_changed"] += 1

            # --- status ---------------------------------------------------------
            new_status = dec.get("new_enacted_status")
            if new_status and new_status != row["enacted_status"]:
                audit.append({
                    "moratorium_id": mid, "column": "enacted_status",
                    "before": row["enacted_status"], "after": new_status,
                    "reason": dec.get("notes", ""), "source": path.name,
                })
                row["enacted_status"] = new_status
                touched.add(mid)
                stats["status_changed"] += 1

            # --- verify markers ---------------------------------------------------
            for res in dec.get("verify_resolutions", []):
                if res["resolution"] == "still_unverifiable":
                    stats["verify_still_open"] += 1
                    continue
                field = res["field"]
                if field not in fieldnames:
                    conflicts.append(f"{path.name}: {mid} verify on unknown field {field!r}")
                    continue
                before = row[field]
                after = strip_marker(before, res["marker"])
                if after == before:
                    # A `changes` entry in this same decision commonly rewrites the
                    # whole field, carrying the marker away with it. That satisfies
                    # the resolution rather than conflicting with it. Test for the
                    # specific marker: a rewrite may legitimately introduce a new,
                    # different marker while retiring this one.
                    already_gone = not any(
                        canon(found) == canon(res["marker"])
                        for found in VERIFY_MARKER_RE.findall(before)
                    )
                    if field in rewritten and already_gone:
                        stats[f"verify_{res['resolution']}"] += 1
                        stats["verify_resolved_via_field_rewrite"] += 1
                        continue
                    # Marker absent from the whole row: a previous run of this
                    # same answer file already stripped it. Idempotent no-op.
                    if already_gone and not any(
                        canon(found) == canon(res["marker"])
                        for value in row.values()
                        for found in VERIFY_MARKER_RE.findall(value or "")
                    ):
                        stats["verify_already_resolved"] += 1
                        continue
                    conflicts.append(f"{path.name}: {mid} marker not found in {field!r}")
                    continue
                audit.append({
                    "moratorium_id": mid, "column": field, "before": before,
                    "after": after, "reason": f"[VERIFY {res['resolution']}] {res.get('note', '')}",
                    "source": path.name,
                })
                row[field] = after
                touched.add(mid)
                stats[f"verify_{res['resolution']}"] += 1

        # --- new candidates -------------------------------------------------------
        if args.no_candidates:
            continue
        for cand in data.get("new_candidates", []):
            conf = cand.get("confidence")
            if conf is not None and conf < args.min_confidence:
                skipped.append(f"{path.name}: candidate {cand['jurisdiction']} confidence {conf}")
                stats["candidate_low_confidence"] += 1
                continue
            abbrev = STATE_ABBREV.get(cand["state"], "")
            cand_instrument = instrument_key(cand.get("legal_basis", ""))
            same_jurisdiction = [
                r for r in rows
                if r["state_abbrev"] == abbrev
                and slugify(r["jurisdiction"]) == slugify(cand["jurisdiction"])
            ]
            dupe = None
            for existing in same_jurisdiction:
                existing_instrument = instrument_key(existing["legal_basis"])
                # Distinct, identifiable instruments in the same jurisdiction are
                # distinct rows (see instrument_key). Only treat as a duplicate
                # when the instruments match, or when either side is unidentifiable.
                if not cand_instrument or not existing_instrument:
                    dupe = existing
                    break
                if cand_instrument == existing_instrument:
                    dupe = existing
                    break
            if dupe is not None:
                skipped.append(
                    f"{path.name}: candidate {abbrev} {cand['jurisdiction']!r} "
                    f"({cand_instrument or 'no instrument number'}) treated as duplicate of "
                    f"{dupe['moratorium_id']} ({instrument_key(dupe['legal_basis']) or 'no instrument number'})"
                )
                stats["candidate_duplicate"] += 1
                continue
            if same_jurisdiction:
                stats["candidate_same_jurisdiction_distinct_instrument"] += 1
            mid = make_moratorium_id(cand, taken_ids)
            taken_ids.add(mid)
            row = build_row(cand, mid, activity_by_state.get(cand["state"], "Low"))
            conf = cand.get("confidence")
            if conf is not None and conf < args.verify_threshold:
                marker = verify_note_for(cand)
                row["current_status"] = (row["current_status"] + " " + marker).strip()
                recompute_verify(row)
                stats["candidate_flagged_for_verification"] += 1
            new_rows.append(row)
            audit.append({
                "moratorium_id": mid, "column": "<new row>", "before": "",
                "after": f"{cand['state']} / {cand['jurisdiction']}",
                "reason": cand.get("notes", ""), "source": path.name,
            })
            stats["candidates_added"] += 1

    for mid in touched:
        for enforce, stat in ((enforce_duration_invariant, "duration_invariant_enforced"),
                              (enforce_date_invariant, "date_invariant_enforced")):
            msg = enforce(by_id[mid])
            if msg:
                audit.append({
                    "moratorium_id": mid, "column": "<typed column invariant>",
                    "before": "", "after": msg,
                    "reason": "codebook invariant enforced at merge time",
                    "source": "apply_research.py",
                })
                stats[stat] += 1
        recompute_verify(by_id[mid])

    rows.extend(new_rows)
    rows.sort(key=lambda r: (r["state"], r["jurisdiction"]))

    # ---- report --------------------------------------------------------------
    print("\nSummary")
    for key in sorted(stats):
        print(f"  {key:28s} {stats[key]}")
    print(f"  {'rows_touched':28s} {len(touched)}")
    print(f"  {'rows_added':28s} {len(new_rows)}")

    if conflicts:
        print(f"\n{len(conflicts)} conflict(s) — NOT applied:")
        for c in conflicts[:25]:
            print(f"  {c}")
        if len(conflicts) > 25:
            print(f"  ... and {len(conflicts) - 25} more")
    if skipped:
        print(f"\n{len(skipped)} skipped:")
        for s in skipped[:15]:
            print(f"  {s}")
        if len(skipped) > 15:
            print(f"  ... and {len(skipped) - 15} more")

    if args.dry_run:
        print("\nDry run — nothing written.")
        return 0

    if not audit:
        print("\nNo changes to apply.")
        return 0

    write_inventory(rows, fieldnames)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    audit_path = AUDIT_DIR / f"apply-{stamp}.json"
    audit_path.write_text(json.dumps({
        "applied_at": stamp,
        "answer_files": [rel_to_repo(p) for p, _ in answers],
        "stats": dict(stats),
        "conflicts": conflicts,
        "skipped": skipped,
        "changes": audit,
    }, indent=2) + "\n", encoding="utf-8")

    print(f"\nWrote {INV.relative_to(REPO)} ({len(rows)} rows)")
    print(f"Wrote {audit_path.relative_to(REPO)} ({len(audit)} change records)")
    print("\nNow run: python3 scripts/validate_dataset.py --today <date>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
