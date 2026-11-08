# Native journal reader development increment

The extractor now persists a unique logical invocation ID before dispatch and binds it with the logical descriptor to each observed HTTP reservation. State format `rule-unit-state-2` and capture format `controlled-model-capture-3` reject incompatible retained state without silently migrating or resetting its allowance. Original histories remain untouched.

The read-only native journal reader reconciles retained planned, logical and HTTP populations, response bytes and boundary output. It reports retries, orphan and unbound reservations, missing evidence, charges and unknown output cardinality. Retained-file consistency is separate from complete history: even consistent files cannot attest all historical dispatches. Unobserved units and unproven dispatch remain incomplete; observed reservations are lower bounds. CLI status remains incomplete and exits nonzero. Raw/boundary equality does not verify the request or its legal meaning.

The independent reviewer accepted this bounded increment after reproducing the coherent-removal counterexample and nine synthetic replay scenarios. Seven offline suites passed 88 tests and 60 subtests; the coordinator independently reran the same suites with the same result. The [verification receipt](verification.json) binds the reviewed code and private reports by hash. No provider call or paid evaluation was made.

Private file inspection rejects symlinks and FIFOs and uses descriptor checks and advisory locks. This assumes a cooperative workspace; it does not authenticate history or protect against a hostile owner rewriting all retained evidence. No global historical immutability is claimed.

Endpoint identity, exact SDK wire serialization, prospective audit integration, source/role semantics, and frozen calibration/fresh holdout remain open. This increment is not a passed P4 evaluation, a complete adapter or release authorization.
