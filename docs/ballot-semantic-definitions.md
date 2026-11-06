# Ballot classification semantics

These definitions clarify the current contract without changing historical
records. Each classification still requires field-specific source review.

## Advisory mechanism axis

`advisory_support` means that affirming the proposition expresses support for
the covered development, permission or enabling services. `advisory_opposition`
means that affirming it expresses opposition to, or a restriction on, that
development. The reference is the covered development, not grammatical support
for the proposition. Neither value reports the winning side or legal effect.

| Proposition | Mechanism | Affirmative direction |
|---|---|---|
| Should new data centers be permitted? | `advisory_support` | `facilitates` |
| Should the city implement a data-center moratorium? | `advisory_opposition` | `restricts` |
| Requested action unavailable or mixed | `unresolved` or separately reviewed provisions | `unresolved` or `mixed` |

A defeated permission question remains an `advisory_support` proposition. A
winning moratorium advisory question remains advisory; it does not itself create
an active moratorium. Read the complete requested action, exceptions and scope;
do not classify from the title, the word "support," or the winning vote alone.

Preserve the exact requested action when displaying this broad classification.
For example, Wrightstown's reproduced proposal concerns municipal infrastructure
and services for development within or affecting the village; it is not a blanket
development approval, and the final printed ballot remains unrecovered.

## Reporting and certification

`reporting_status` describes completion of the source's contest-count observation
at its stated geographic scope: `partial` when explicitly incomplete, `complete`
when a final contest canvass or explicit completion statement supports it, and
`unknown` when that basis is absent. A final county-part count is not a complete
whole-jurisdiction count. Preserve the part in `reporting_scope`.

Full precinct reporting alone supplies precinct counts; it does not establish
that outstanding ballots have finished counting. Certification has its own
source-qualified status, date and scope. Do not infer completion from certification
alone, or certification from completion. Retain recounts and amendments as
separate observations with explicit supersession when warranted.

## Legal references and governmental roles

`legal_basis` must preserve each reference's role: affirmative authority, default
rule overridden, exception or limitation. A notwithstanding citation is not
affirmative authority merely because it names a statute. Qualified prose is
allowed; leave applicability unresolved where the source does not settle it.

Keep requested actor, voting electorate and restriction territory distinct. A
township question addressed to a city council establishes neither identity
equivalence nor a later restriction's territory. Source-scoped claims can retain
these roles separately; dedicated role fields and the broader jurisdiction
relationship contract remain unfinished. Never fill unknown territory from a
government name alone.

## Composed support

An operative number and its measurement basis may need separate passages. Retain
the number, operator, unit, aggregation and material composition in the reviewed
value, with separate supporting claims as needed. Building area differs from
building-plus-associated-impervious-surface area. Extraction passage roles and
exact matches remain nominations for review, not accepted legal roles.

The [post-correction current-use audit](../work/audit/ballot-semantic-use-post-correction-2026-11-06.json)
checks consistency and direct field-value lineage at a pinned snapshot. It does
not reacquire sources or rewrite records. A claim without the named mechanism
value is a review flag, not proof that the underlying source lacks support.

## Current review queue

The [applied correction](../work/research/2026-11-06/ballot-semantic-lineage/README.md)
now supplies explicit mechanism support for those four provisions and a separate
Monterey Park successor with city-total count-completion/scope support. It also
qualifies Wrightstown's proposed geography and leaves Bloomington's restriction
territory unresolved. Earlier records and the initial audit remain retained.
The current targeted audit has no flags; it does not establish full source
entailment or close broader role contracts, freshness or legal-force review.
The following paragraph records the finding at the original baseline.

At snapshot `a5c897f0d64f46b06fc1d19564cd5b9522a5a4e41a1e25d2fd8c0f59ceea4a3a`,
all eight advisory provisions are directionally consistent with their reviewed
wording or proposed wording. Four mechanism decisions need stronger explicit
claim lineage: Wrightstown, Downe, Joliet and Bloomington. Monterey Park's single
`complete` result needs explicit completeness-and-scope lineage; its reviewed
final contest canvass is relevant positive evidence, while published geographic
scope remains unrecorded. This is not a rejection of those classifications.

Two read-only `gpt-6.1-terra` CLI reviews checked these records and the definitions.
They did not reacquire sources or re-examine the original PDF pages. Their findings
also prompted distinct audit flags for missing/conflicting accepted decisions and
unrecorded scope, and rejection of cross-field supersession. Direct page review,
field-specific claim additions and any canonical supersession remain required.
