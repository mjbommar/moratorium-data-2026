# Edgewater proposed-restriction migration

Status: canonical publication applied; all 498 claim proofs verified. Full build/check passed; all 151 tests pass.

The retained official county Amendment 4 title, summary and question identify a proposed charter restriction. This candidate gives that proposed restriction an explicit identity and records a `proposes` relationship from the already published ballot measure. The restriction status and adoption, effectiveness, applicability and end dates remain unknown. The accepted link means the proposal relationship is supported, not that voters enacted an operative instrument or that any current permit is barred. No adoption/effect event or project-applicability link is added.

The source is the same exact primary version already used for the measure; the candidate retargets independently accepted, quote-verified claims to the restriction and relationship. All existing rows and legacy CSVs are unchanged. This is one scoped migration increment, not completion of the broader restriction/event migration. Identity/publication plans pin all reviewed bytes.

Preflight exposed a publication-gate incompatibility with the schema’s required unknown date objects. The gate now permits only the exact all-empty four-field date sentinel as unresolved; populated bounds, explanatory text and extra keys still fail. The 45 expanded-data tests pass, including those rejection cases. Full evidence preflight has been restarted after this concrete gate correction; canonical data remained unchanged at that stage. `primary-verification.json` separately verifies the exact retained county wording and source hashes.

The corrected preflight returned `ready`; its candidate fingerprint and counts are retained in `preflight.json`. Publication repeats the full evidence gate under the actual registry. Legacy counts and previously published ballot/result rows remain unchanged.

Applied publication adds one restriction with unknown legal status and one accepted `proposes` link. No instrument events or legacy CSV changes occur; 49 measures, 55 retained results and the 49/7 candidate disposition remain unchanged.
