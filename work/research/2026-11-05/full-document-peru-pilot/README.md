# Peru full-document extraction pilot

Actual model extraction processed the complete registered OCR of Peru's one-page
proposed data-center moratorium. The source PDF hash matches the previously
reviewed official download. The whole-page image was inspected again, and the
printed clauses are represented in the OCR. Handwritten date/signature errors
remain in that derivation and must not supply accepted dates or identities.

The actual bc-evidence `extract_document()` path processed one chunk and produced
five claims covering purpose, definition, development-approval scope, exemption
and conditional duration/effectiveness. All five quotes match exact character
spans in the supplied OCR. All five instrument observations remain `proposed`,
with no actual occurrence dates. One quote exceeds the prompt's requested
300-character maximum; that advice is not enforced by the library's schema.

The API model was explicitly `openai:gpt-6-sol`, low effort, native structured
output, maximum 6,000 output tokens, one backend/provider request per attempt,
no agent repair or transport retries. The workspace allows at most two backend
calls and $0.50 in cumulative allocations, reserving $0.25 before each call.
Successful priced calls settle at the library's estimated cost; failures and
interruptions retain reservations. Unknown pricing or a reservation overrun
stops the workspace pending reconciliation. Reservations rely on a conservative
per-call allowance and bounded backend; they cannot guarantee a provider invoice
will equal the local price table.

One paid backend call used 1,613 input and 1,094 output tokens, estimated at
$0.024472 using the installed bc-llm price table. A real replay completed with
zero additional backend calls. `receipt.json` records source/context/output
hashes, exact-span checks, settings, coverage, cost basis and replay accounting.
Full private outputs, request state, ledger and driver remain in the named
private workspace.

This is one complete **text-chunk extraction pass**, not completed legal review
or a complete ballot dataset. No canonical facts or production EvidenceDB
timestamps changed. Domain-typed extraction, multi-document calibration and
review remain open. The existing 13-document/90-claim EvidenceDB import still
has zero completed extraction timestamps; this separate run must not silently
change that historical import's accounting.
