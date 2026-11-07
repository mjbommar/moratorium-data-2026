# Integration working-input handoff v2

Implementation checkpoint: the exporter now builds an immutable source-pinned replay/input tree with compatible flat inputs, receipts/profiles and current/status CSV views. [Contract and usage](../../../../docs/reviewed-input-handoff.md) distinguish source review from downstream join acceptance and require an independently trusted verifier.

Two terra CLI reviews found the original uncommitted-byte/HEAD mismatch, missing replay context, verifier bootstrap ambiguity, destination race and incomplete directory/symlink checks. [Reconciliation](review-reconciliation.json) records fixes and review limits. Twelve behavioral transport tests cover those boundaries; the actual committed export/delivery is the next step, after committing the exact exporter.

The integration original local main differs from the remote and is preserved. Delivery is being prepared in a sparse worktree based on remote `b82a726cd186bdc343ebce023c6b89250a9be8a5`, retaining its unrelated tracker-seeds work. Existing November input snapshots and historical bridge/collaborator outputs must remain byte-identical. No RDF assertions, project applicability, legal-force decisions, market output or causal join are accepted by this transfer.

Actual source/consumer verification, manifest hashes, counts and remote refs will be added after the pinned export completes. No final release or hosted deployment is implied; broader plan gates remain open.

## Completed working-input delivery

The committed exporter at `68d4ddd1793af6f5518d04ac29ca457cfb151f94` produced the full replay handoff. A second export returned `already_present` with the same manifest. Independent consumer verification passed 32 publication generations and all 18 CSV views. [Delivery evidence](delivery-validation.json) records the manifest, counts, checks and remote revision.

Integration main is verified at `836a5a79f1f0a8d0118d8ea598fddf5be007cb7d`. All 836 committed snapshot members matched verified working bytes; four historical trees retained their baseline Git hashes. Separately committed verifier and delivery documentation provide external trust pins. The third terra review's two documentation findings were resolved before commit. The original divergent local integration main remains preserved; use the delivered remote revision or the dedicated worktree.

This completes this working-input transfer, including stable IDs and reviewed relationship states, without changing project ownership. It does not complete downstream RDF/project acceptance, broader freshness gates or the final release. Earlier pending statements above describe the implementation checkpoint.
