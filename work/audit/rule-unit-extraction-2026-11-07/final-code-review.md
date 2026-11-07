# Independent final review: rule-unit extraction

**Verdict: no remaining material blockers found for the declared offline and controlled opt-in development scope.** This is a read-only review of the implementation and tests; this report is the only file I wrote. No installs, network or provider calls, or Git mutations were performed. Live extraction quality, provider acceptance, source freshness and P4 remain unproven.

## Findings

The prior central blockers are addressed, subject to the explicitly documented boundary that the local unkeyed seal is not authentication. Invalid, unpriced and non-finite accounting is rejected before it enters the ledger; the failed reservation and reconciliation stop are saved, and replay stops before dispatch. State and separate seal are checked, followed by context, request, reservation, accounting, status, output and success-relationship validation before calls. Independent accidental changes to attempts, charges or statuses break the seal; deletion of either ledger file, or both while the lock remains, fails closed. A coordinated edit of both files, restoration of a previously valid pair, or deletion of all workspace evidence cannot be detected by this scheme; the documentation says so and calls for an external protected audit trail when needed.

Reservations are written and sealed before dispatch. A surviving reservation blocks replay; interruption between state and seal replacements leaves a mismatch. The failure-injection tests show that post-dispatch state or seal write failures prevent redispatch, while a packet write failure after the sealed success allows safe continuation. A stale or absent packet is a documented disposable derivative, rebuilt only after validation; it is not a historical authenticated record. Changed context is rejected before packet reconstruction and retained state and packet are preserved.

Workspace admission checks ownership and private permissions, rejects symlink components and unsafe, hard-linked or non-regular named artifacts, and uses private file modes and atomic writes. The optional `PrivateRunStorage` is bounded to a strict descendant of its policy root and enforces its cooperative retained-byte limit. These checks assume no hostile concurrent manipulation of ancestors; the policy root must also be private. They are not an adversarial filesystem sandbox. The default directory writer does not impose a retained-byte cap unless the optional policy is supplied.

Every planned slot appears in the packet, including failed, reserved and not-attempted slots, with explicit status and unresolved outcome when no successful response exists. Each request contains the full unchanged source, followed by the slot; the adapter calls the backend directly, bypassing the generic claim selector. It performs no canonical acceptance or promotion. Document identity and provenance are copied when supplied, while the original body digest and text-to-body relationship remain caller assertions. Context and plan preservation, full UTF-8 byte limit, quote flags and unaccepted candidates are exercised. The plan is externally supplied and does not establish inventory completeness; exact quotes and validation flags do not prove entailment or extraction quality.

The two offline NativeOutput tests use the actual OpenAI SDK, PydanticAI backend and an HTTP mock, covering a candidate, an unresolved response, free replay and a failed request with a persistent cap. They inspect the emitted JSON-schema request and permit either `strict` value. The adapter validates the typed response and unit ID after return, and runs the separate condition validator when constructing the packet; invalid or ambiguous conditions can remain flagged candidates requiring human review, not accepted facts. These tests do not establish live provider acceptance of every nested schema or output variant. The generic backend interface does not enforce its own HTTP retry, tool or settings controls; the documented separately controlled transport and backend configuration remain necessary for live use.

## Verification

- Existing BC interpreter: `python -B -m unittest discover -s tests -p 'test_rule_unit*.py' -v` — **17 tests passed**, including **2** offline native transport tests. The failure/resume coverage includes invalid accounting and restart, failed/cancelled calls, interrupted reservations, state/seal/packet write failures, mixed charges and dollar exhaustion, as well as resealed structural corruption; it goes beyond checking hash calculation alone.
- Additional temporary-directory offline probes: deleting both state and seal while retaining the lock rejected replay with no additional call; a hard-linked lock was rejected; and a 100-byte storage policy exhausted before any backend call. These probes did not modify the reviewed files.
- The suite uses mocked or scripted responses; its success is not a live model, provider, or legal-quality evaluation.

## Reviewed SHA-256 hashes

```text
2889852b991405e5771088165f37d65e32397bb10745e296ea2887496fd8a469  ../code-review.md
5484d232e00893fd0015957a278aea7d31393b7305baa8abd68fb66583d9a3c3  ../ledger-fixes.md
02c69bdf7f876bdf7ded0a8e0fec89d577457062a51eb19de98503c3eb152cd3  scripts/extract_rule_units.py
477ecb7c6d4a417c4e7dd0d1b96cfe6d0bfe48b3233af2486ee704705d9814c5  tests/test_rule_unit_extraction.py
bee155ba0a8b96174da9beb1d005c9eaf51f1fccb37c618a8dc2b9ad3e5f5234  tests/test_rule_unit_native_transport.py
7554969694c03819c312149f576e3360dd2b1ae1fd5cd25ee7075fb6ab22970f  docs/rule-unit-extraction.md
```
