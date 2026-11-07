# State-policy legal-form migration

Thirteen existing rows move out of the `bill` bucket: ten `legislative_resolution` rows and three `legislative_precursor` rows. All 442 IDs, compound observations and every other cell are preserved. Typed bill rows change from 440 to 427; this is a form correction, not thirteen new actions, repeals, failed bills or an independently deduplicated bill census. Local and ballot totals are unchanged.

Two disjoint source-review jobs and a contract job requested `gpt-6.1-terra`; a fourth bounded source job recovered the twelve original Arkansas PDFs linked from retained official detail pages. The earlier source-review jobs made no network calls. The supplemental job was limited to twelve exact PDF fetches with no searches or extra model APIs; original jobs/caps were unchanged. CLI spend remains separately unpriced. No new automated extraction trial was run.

## Evidence and retained limits

The [source review](source-review.json) verifies 45 exact quoted source spans and original body/text hashes for all thirteen rows. The three official Pennsylvania memo-to-bill associations remain associations: no identity merge or text-equivalence inference. Arkansas's compound row retains all twelve resolutions; Hawaii's SCR95/SR90 row retains both instruments. The source review verifies each named constituent rather than inferring form solely from a prefix. Additional identity/grain and canonical relationship migration remain open.

The coordinator also reviewed New Jersey SR18, Pennsylvania SR185 and Hawaii HR196 directly from retained official records, and visually checked Arkansas HR1013 page 1. Its HOUSE RESOLUTION title and HR1013 identifier coexist with a resolving clause referring to the Senate and Senator King. The [visual receipt](visual-review.json) preserves that inconsistency; only the generic resolution form is accepted. No sponsor, chamber, legal effect, disposition, date or provision value is inferred from this form review.

## Contract and public counts

The additive forms are accepted in existing-row decisions, new-row decisions, apply validation and dataset validation. Whole-row baseline protection remains mandatory for these reviewed corrections. Tests cover both forms, new and existing records, unknown-form rejection and stale-row rejection. Legacy free-text bill labels and every stable ID are unchanged. Consumers with closed legal-form enums must accept the new values before adopting this working snapshot.

`state_policy_instrument_type_counts` publishes the form breakdown. `top_states_by_bills` now ranks only rows typed bill; it previously used all policy records. The former all-policy ranking is preserved explicitly as `top_states_by_policy_actions`, with the same pair-array shape. This fixes a denominator error rather than asserting a change in political activity. Current README/codebook, landing copy and generated state pages distinguish row populations from unique bills or binding restrictions. Three additional document-number guards cover the new form breakdown.

The [exact diff](exact-diff.json), per-state answers and full preimage baseline retain the thirteen type-only corrections. The November 5 cohort remains distinct from November 7 acquisition/review dates. Wider form coverage, all-field freshness, canonical state-policy relationships/identity migration, consumer synchronization and final release remain open.

[Validation](validation.json): all 372 tests pass, including six new form-contract tests and one ranking-denominator test. Full data/site/check and the final copy rebuild pass with zero errors, 491 unchanged warnings and all 56 documented numbers matching. Replay proposes zero answer edits and zero archive additions. Twenty selected versions are newly archived; native migration/readback now covers 6,780 manifest entries and 3,337 verified-body versions with the same 3,443 historical gaps. No private source text is tracked. The independent reviewer found no material scoped blocker; root subsequently verified the build terminal exit. No final release or deployment was published.
