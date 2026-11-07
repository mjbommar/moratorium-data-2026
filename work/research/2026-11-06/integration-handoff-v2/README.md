# Integration working-input handoff v2

Implementation checkpoint: the exporter now builds an immutable source-pinned replay/input tree with compatible flat inputs, receipts/profiles and current/status CSV views. [Contract and usage](../../../../docs/reviewed-input-handoff.md) distinguish source review from downstream join acceptance and require an independently trusted verifier.

Two terra CLI reviews found the original uncommitted-byte/HEAD mismatch, missing replay context, verifier bootstrap ambiguity, destination race and incomplete directory/symlink checks. [Reconciliation](review-reconciliation.json) records fixes and review limits. Twelve behavioral transport tests cover those boundaries; the actual committed export/delivery is the next step, after committing the exact exporter.

The integration original local main differs from the remote and is preserved. Delivery is being prepared in a sparse worktree based on remote `b82a726cd186bdc343ebce023c6b89250a9be8a5`, retaining its unrelated tracker-seeds work. Existing November input snapshots and historical bridge/collaborator outputs must remain byte-identical. No RDF assertions, project applicability, legal-force decisions, market output or causal join are accepted by this transfer.

Actual source/consumer verification, manifest hashes, counts and remote refs will be added after the pinned export completes. No final release or hosted deployment is implied; broader plan gates remain open.
