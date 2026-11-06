# Legacy moratorium identities

`data/moratorium_inventory.csv` contains current instrument records. An explicitly reviewed duplicate may be removed from that table only with its full original row and permanent ID retained in the append-only [`legacy-moratoria.jsonl`](../data/identities/legacy-moratoria.jsonl) registry. This registry is separate from expanded-domain UUID allocation. A retirement does not create a new moratorium, establish current enforceability or automatically merge fields.

The first retirement maps `wa-seattle-2026-2` to the existing `wa-seattle-2026`: both describe Seattle Ordinance 127447 / CB121214. The [reviewed plan](../work/research/2026-11-06/seattle-identity-review/retirement-plan.json) pins both rows, the entire input CSV, the proposed output and prior registry hash. The [application receipt](../work/research/2026-11-06/seattle-identity-review/retirement-validation.json) verifies one retirement, no survivor field changes and an idempotent replay. Original observations for both rows remain in the event. Divergent project assertions and later operative history require separate field review; none were copied from the retired row or newly accepted by this identity transaction.

Resolve either ID from the repository root:

```sh
python3 scripts/legacy_moratorium_identity.py --lookup wa-seattle-2026-2
```

The result includes requested ID, canonical ID, alias status and current surviving row. Consumers should retain original cited IDs and resolve aliases when joining to current CSV records. Raw CSV counts and maps count only surviving records. Expanded foreign-key validation admits retained aliases after checking that each resolves to a current record. Research changes against retired IDs are rejected with the surviving ID; they require explicit re-review rather than automatic redirection.

Registry events retain reviewer/time, rationale, source URL/body fingerprints, full preimages, input/output CSV hashes and the previous registry byte hash. Validation rejects changed preimages, duplicate aliases/events, cycles, dangling targets and an alias still present in the current CSV. Hashes establish integrity against the reviewed transaction, not independent source authenticity.

Application replaces each file atomically; the CSV and registry become a single published transaction in Git. A local interruption between replacements is recovered by replaying the exact retained plan. Replays after subsequent legitimate survivor edits preserve those edits. Publish both files together. Release bundles include the registry and this document; historical bundles without a registry retain their original behavior. Downstream snapshots must be reconciled before final publication.
