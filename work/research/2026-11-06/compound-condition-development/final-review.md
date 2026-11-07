**Verdict: no remaining actual bugs found in the reviewed scope.** The current implementation addresses the prior findings: native output separates group constraints from local validation, unknown-node text remains in scoring, invalid groups remain visible alongside valid facts, and canonical condition validation uses the pinned schema. The reviewed publication paths also cover downgrade rejection, exact replay, withdrawal history, and full-document condition quote locations.

Using the requested Python interpreter, the relevant condition, extraction, audit, publication, CSV, handoff, and event-maintenance tests passed: **144 tests and 26 subtests**.

This was an offline, read-only review; no live provider request or extraction-quality gate was run. The active canonical profile remains **1.0.2**, and the development contract has not been promoted. No files were edited, paid APIs called, or commits made.
