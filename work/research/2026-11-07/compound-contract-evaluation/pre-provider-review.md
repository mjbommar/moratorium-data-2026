# Independent pre-provider review

Reviewed 2026-11-07 around 11:38 UTC, repository HEAD `a99534259871c4d4b73a610fb5e1ca5eb35a2490`. **Not yet eligible for provider execution: the new protocol is untracked and its exact bytes are not committed at HEAD.** The runner enforces that requirement. No other concrete material blocker was established in this static review, subject to the limits below. This review authorizes no provider execution, spending, commit, or other action.

The directory was being prepared concurrently: README, offline-validation and storage-preflight appeared during this review. The review is tied to the bytes and hashes below; changes require re-review. No preparation command was run by this reviewer. No paid calls, installs, Git mutations, tracked edits or mock runs were performed. The offline record is self-reported, not an independently witnessed rerun; temporary mock artifacts were not retained for inspection.

## Comparison and boundaries

The previous comparison used 13 provider requests, including one unpriced failed attempt. Its 16-request cap is not replenished. The new README explicitly describes a separate allocation; new runner enforces a new namespace and 16 HTTP reservations, per-case call caps 4/8/2/2 with $0.75 reservation each and $12 total estimated reservations. This is additional potential spend, not the old remaining three requests. Estimated accounting is not a provider invoice ceiling or current independently verified pricing. This review confers no authorization for the new allocation.

The four case IDs, source IDs, body/text hashes, chunk settings, execution order, case caps and thresholds match the prior protocol. The 12 family slot entries and their criteria and supporting fields match; there are 24 case/slot judgments. The new required-slots file has its own hash and current snapshot metadata. Audit requires 95% support, zero high-impact non-supported candidates, every slot, full source coverage and quote/schema integrity; covered slots require one supported candidate and one complete clause. Semantic truth still depends on coordinator source review; reviewer identity strings alone do not prove independence. Prior outputs are not rescored. The stated scope correctly excludes unseen holdout, general accuracy and overall P4 closure.

Experiment identity and provider namespace differ from the old run. Protocol pins code and prompt bytes, canonical inputs, reviewer instructions, sources, runtime manifest and routing separately through fields and hash inventories. `prompt_revision` `a76ea6a` is a repository commit for the domain extraction instruction change, not the separate bc-evidence prompt file revision; current bc-evidence prompt hash `44ee2a732c204c7c061d4e4bc820ba787c8c74ab91490eca5db2395073045eb0` is unchanged from the previous protocol. The actual current domain adapter hash is pinned below. Runtime coverage excludes the standard library, shared libraries, OS, environment and external services. The manifest file hash and all 61 code and 22 canonical input hashes were checked against files; the manifest contents were not independently rebuilt or verified here. Both source bodies and texts matched their hashes.

`run.py` checks the pinned runtime, source and inventory hashes, pricing, routing, caps and admitted storage, then requires the provider directory to be absent and protocol bytes equal `git show HEAD:<path>` before creating it exclusively. It retains executed code; this proves committed protocol bytes, while pinned external and worktree code bytes are checked by hash, not required to be committed. The audit verifies retained code and accounting, reviews and slot references, and does not grant a gate to mock fixtures. Its review checks cannot mechanically establish substantive semantic coverage or true reviewer independence.

The newly appeared `offline-validation.json` binds this protocol hash and reports healthy 12 reservations/12 results and failure 13 reservations/12 results with one unpriced $0.75 held reservation, zero provider requests, replay without extra calls and audit passing. The runner contains both MockTransport paths and assertions for these figures. The generated storage preflight reports eight outputs checked with no errors. These reports are not independent raw transcripts, and this review did not rerun the tests or validate actual extraction quality. Neither the earlier experiment's tests nor its successful pre-provider review establish validation of these new bytes.

## SHA-256 at review

- `protocol.json`: `c6784744cc9a681457ee4d5a9428db38211383b46e9c10fe4b96bb545f638265`
- `run.py`: `16a202c0835309de07735d1355028b5ebe226831505018923e5cb4bc395daa81`
- `audit.py`: `101a320edc4b949ec6e15f41ca490d8bbd55d43f8e0e4fdea87220388015ca21`
- `prepare_protocol.py`: `1967449b513654e3c8ecfe698a2aba3f891191327c0dd9cf902ef815e7f5542a`
- `required-slots.json`: `fba7876a85a1844385b15b08d311f814346b0e6810929444a94cce857a064434`
- `reviewer-instructions.md`: `2ac5aeb94b94ab7ce0bd79344e956f31bf2a231bc124edfc89fbdb34c7530c7d`
- `runtime-files.json`: `202eb1adc0b8bf0f02ed457d1c871596060ca34be05dbecccc8be60a8f6c2ad1`
- `storage-admission.json`: `345b70f9d254bb4d7989ca4f4479fc35153038eb6c09cfb527906ff0106e4bac`
- `README.md`: `50f8160fdbe4dd3bb527839339d56f0b314c34a7da9be9172400238e6298a01c`
- `offline-validation.json`: `441619319af258866906bb0c8c5bc5eaa32b7c4c83fde2860b65dc82a6f9b012`
- `storage-preflight.json`: `8a73cff64617a34da86b6bb820979af108975b242a53fdc60888ad0075c8a075`
- `scripts/extract_domain_candidates.py`: `da59807e86af71b25027e70a83017d62070c8f7d6b7bdfd3293c1413868352e9`

Before any separately authorized evaluation, commit the exact reviewed protocol and intended packet at the root, recheck hashes and fresh provider storage and confirm the runtime and offline results remain applicable. Any changes to these artifacts invalidate this review's byte-specific conclusion.
