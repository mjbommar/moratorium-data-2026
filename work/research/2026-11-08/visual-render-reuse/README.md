# Reuse PDF renders within one evidence audit

The verifier now shares reproduced PDF page hashes within one audit, keyed by verified body hash, page, DPI, resolved renderer path and executable hash. Every receipt still independently checks its claim/value binding, rereads and hashes the source body, and compares its own expected primary and additional page hashes. The cache is neither persistent nor supplied by receipt JSON; standalone verification and native PNG/JPEG behavior remain unchanged.

Independent code review and real-PDF adversarial probes accepted the change. Focused suites passed 29 visual-review and nine evidence-audit tests. The coordinator then rechecked all **586 actual publication proofs** against the pre-change published receipt: canonical JSON proofs match exactly. Actual PDF renders fell **314 to 110**, and the measured audit took **36.418 seconds** (not an uncached wall-clock comparison). [Full proof comparison](full-proof-comparison.json) pins the source generation and publication hash.

The initial comparison script incorrectly compared Python tuple spans to JSON array spans; canonical JSON normalization corrected the comparison without changing any evidence proof. This optimization changes rendering work, not factual acceptance, freshness, source acquisition or the P4 gate.
