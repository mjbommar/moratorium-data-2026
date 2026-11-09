# Final figure and table reconciliation

All seven table generators were run against the reviewed working source; sector
counts and recorded-date distribution changed. The count, sector and date maps
are regenerated in PNG, SVG and PDF. The old and current state-count inputs agree;
sector/date inputs reflect the corrected rows.

The sector map previously inferred a single sector from prose and defaulted missing
classifications to data centers. It now uses the normalized sector arrays, counts
each recorded sector on multi-sector rows, shows tied dominant sectors as Mixed,
separates general pauses as Other and never promotes missing values to data centers.
Two focused regressions cover conflicting prose, multiple sectors, ties and invalid
values. Both pass. The sector map and date heatmap were visually inspected.

Recorded-date labels now explicitly allow unverified or scheduled dates, avoiding
an adoption claim based solely on the legacy date field. Legal-authority, home-rule,
preemption and statutory-duration maps retain the paper's historical classifications;
no new legal survey or paper PDF is claimed. [Figure boundaries](../../../../figures/README.md)
and [verification](verification.json) state inputs, counts and artifact hashes.

The archive selector now includes the public figures, tables, associated generator
code and dated release notes. A subsequent prepared package must bind this commit;
the earlier prepared asset hashes are historical preparation only. Final publication
and the explicit experimental gate decision remain open.
