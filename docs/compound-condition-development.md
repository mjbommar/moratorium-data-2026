# Compound condition development contract

Validation profile [1.0.3](../work/schemas/expanded/1.0.3.json) adds an optional
`measure_provisions.condition_clauses` field to the retained record format
`schema_version: "1.0.0"`. The published snapshot still selects **1.0.2**; this
contract has not migrated, reinterpreted or accepted existing records. Missing
condition clauses leave the grouping of legacy flat thresholds unspecified.

Each clause retains its purpose, assertion context, exact `source_text`, and a
recursive expression. Purposes distinguish definitions, prohibition triggers,
procedure triggers, safe harbors and exemptions. Expression nodes preserve:

- `all` and `any` groups with distinct nonempty members;
- `at_least` groups with a count between one and the number of members;
- threshold leaves with operator, numeric value, units, measurement basis,
  aggregation rule and scope;
- explicit text predicates for nonnumeric gates or unsimplified comparisons;
- unknown expressions carrying source text, without an inferred logical operator.

Groups have at most 128 members. Numeric booleans and nonfinite threshold values
are invalid. Native parsing retains structurally valid groups with semantic errors
so a bad group does not discard neighboring valid facts. Full Python and canonical
JSON Schema validation reject duplicates, empty groups and impossible cardinality.
The canonical schema contains those constraints directly; historical publication
replay does not import the mutable development Python validator.

For example, Mandan's reviewed proposed prohibition uses capacity **OR** demand,
while a separate below-threshold provision requires **both** to be below the
threshold. Harwood's proposed procedures distinguish any one major trigger from
at least two moderate triggers, subject to discretionary municipal approval.
These examples are known development cases. They do not establish final ballot
wording, qualification, enactment or current force. The water-capacity comparison
may remain a text predicate or unknown expression; no capacity is invented to
force a scalar normalization. See the [source review](../work/research/2026-11-06/north-dakota-ballot-primary-review/README.md).

Extraction transport [1.2.0](../work/schemas/extraction/1.2.0.json) embeds a
separate native-output model. It omits unsupported full-validation keywords;
the installed pydantic-ai OpenAI transformer converts discriminated `oneOf`
branches to supported `anyOf` branches. Offline tests inspect that transformed
object-root schema. They are compatibility evidence, not a successful live
provider invocation. The adapter freezes the Python contract hash and canonical
schema hash in its resumable context, locates clause and unknown-node quotations,
flags context conflicts, and never automatically promotes candidates.

The complete-clause scoring path permits reordered group members but rejects
changed operators, counts, roles, contexts, threshold bases, missing/extra members
and changed unknown-node content. Clause quotations are checked separately from
semantic equality. Matching a frozen expectation is not source entailment or
measured discovery recall. The older scalar-threshold scoring path remains for
its original frozen evaluation; it does not establish compound-clause coverage.

Publication support carries forward event-validity checks, receipt-bound sealed
generations, exact replay and retained withdrawal history. Once a publication
selects 1.0.3, publication/checker paths reject downgrading it to 1.0.2. CSV views
include the compound field under the selected profile, preserving its nested JSON
in one cell. New field values still require separate source claims and scoped
acceptance decisions before publication.

The [full controlled-runner preflight](../work/research/2026-11-06/compound-condition-development/full-runner-preflight.json)
now verifies synthetic success, reconstructed-backend cache replay, failure
retention and request-cap enforcement using the real SDK and bc-evidence pipeline
with mock HTTP only. This is transport/control evidence, not extraction accuracy.

Remaining gates: source-grounded development adjudication, a separately frozen
evaluation cohort and caps, and a successful quality evaluation. The historical result is
still **32/36 supported, below 95%, with zero review-ready documents**. No new
extraction-provider call or canonical fact promotion was made by this increment.
