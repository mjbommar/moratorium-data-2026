# Legacy source bridge and remaining gaps

The November 6 inventory covers all 6,455 source-manifest entries without rewriting
any original manifest. Exact line hashes and legacy keys map to private native
bc-store observations and metadata derivations. The mapping preserves original
URLs, hashes, retrieval times and publication flags. Store contents remain private.

2,756 entries have retained, hash-matching original bodies and were imported.
They map to 2,755 observations because two text versions share one original fetch.
The other 3,699 entries lack a matching original body locally; they are explicit
gaps, not hash-only payload imports. This does not prove source absence or loss of
every later version. No archive, factual review or extraction completeness is inferred.

The native database passed integrity checking on local NVMe. Payload and exact
manifest-line readbacks passed; the full replay report is identical. Content-addressed
blobs and the retained SQLite metadata backup are under admitted /data0 storage.
The backup is not an independent full-corpus restore. Storage preflight and mapping
hashes are recorded in validation.json and the adjacent storage receipts.

Reproduce inventory with the bc-modules Python environment:

```sh
~/projects/bc/bc-modules/.venv/bin/python scripts/bridge_legacy_sources.py \
  --output /data0/moratorium-refresh-2026/legacy-source-inventory.private.json
```

For an explicit replay, follow docs/refresh-operations.md, run storage preflight,
and add `--store` plus `--apply`. No network, public source export, legal-force
acceptance, publication-flag change or canonical data change occurs.
