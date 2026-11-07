# Reviewed working-input handoff v2

`scripts/export_reviewed_handoff.py` exports an additive, immutable input snapshot from a pinned committed revision. The exporter and bundle builder must match that revision byte-for-byte. It never labels uncommitted working-tree data as `HEAD`.

The handoff keeps the familiar `data/` and `expanded/*.jsonl` compatibility paths. It adds current CSV views, the selected publication receipt and schemas, plus `source/`: the complete public replay tree selected by the source bundle builder, with retained generations, identity history, pointers, runtime and contracts. Compatibility files are byte-identical copies of named source-tree files, not independent authorities. The public upstream manifest is retained separately.

The version-2 manifest pins the source/exporter revision, exporter hash, upstream manifest, selected publication/table/CSV identities, profile, counts, compatibility mapping and every file, directory and allowed symlink. Event history, current accepted events and status views remain distinct. Current event acceptance does not establish instrument enforceability. Reviewed restriction/link records retain their source scope and review status without accepting any RDF or project-applicability join.

## Produce and verify

Commit the exact exporter and builder before production, then use the bc-modules Python environment:

```sh
BCPY=/home/mjbommar/projects/bc/bc-modules/.venv/bin/python
"$BCPY" scripts/export_reviewed_handoff.py NEW_DESTINATION --revision COMMIT
```

The producer builds from that Git tree, verifies/extracts the public bundle into staging, creates compatibility copies, checks the complete tree and runs the upstream publication/history and CSV checkers. Only a successful stage can become visible. Linux `renameat2(RENAME_NOREPLACE)` prevents a competing empty directory from being overwritten. An identical existing handoff is verified and reused; differing bytes, extra paths or unexpected symlinks fail. The tested environment is Linux with a symlink-capable filesystem and Python/jsonschema. The public tree excludes private source bodies and does not require Git for its offline checks.

Verification must start with an independently trusted verifier and manifest digest:

```sh
"$BCPY" /TRUSTED/CHECKOUT/scripts/export_reviewed_handoff.py \
  --verify HANDOFF_DIRECTORY --manifest-sha256 TRUSTED_MANIFEST_SHA256
```

The separately trusted consumer commit/delivery receipt pins the manifest and verifier hashes. A source-identical verifier may be installed in that trusted consumer checkout. Do not execute the packaged `verify_handoff.py` as its own trust bootstrap; authenticate its bytes first. Only after the expected manifest hash and exact tree match does verification invoke the packaged source checkers. Internal consistency does not authenticate wholesale replacement of an untrusted tip.

## Delivery scope

The new integration input is additive. Earlier November inputs, September bridge outputs, collaborator packets, project/disclosure cutoffs and project ownership remain intact. A transfer does not create a new accepted bridge release, current-force finding, proximity relationship, market outcome or causal assertion. Downstream temporal/RDF and project-link acceptance still follow the integration repository's own review contract.

The [delivery packet](../work/research/2026-11-06/integration-handoff-v2/README.md) records the pinned source, source/verifier checks, exact input counts, original-branch preservation, consumer commit/remote and unresolved delivery boundaries. This is a working handoff; the final freeze/release and broader freshness/quality gates remain separate.
