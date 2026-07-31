# Rejected candidates

Research output that was deliberately **not** merged, kept with the reasoning so
the decision is reviewable and is not silently re-litigated next refresh.

## Subsidy freezes generally

The Arizona case below is not isolated. The Illinois sweep surfaced a parallel
action — the Governor's pause on the state **Data Center Investment Program**,
which suspends tax-incentive eligibility while permitting continues untouched.
Illinois officials expressly disclaimed it as a moratorium in their own
announcement. It is excluded on the same reasoning, and it is not in
`state_legislation.csv` either, because that file tracks *bills* and this was an
executive action.

Two independent researchers reached this exclusion independently once the rule
was written into `docs/codebook.md`, which is the argument for writing scope
rules down rather than re-deciding them case by case. Expect more of these: as
states cool on data-center subsidies, "pause the incentive" is a politically
cheaper move than "pause the permits", and headline coverage will describe both
as moratoria.

## `AZ-tax-incentive-freeze.json`

Arizona HB 4168 s.31 (2026 Session Laws Ch. 140) imposes a three-year freeze,
2026-07-01 to 2029-06-30, on **new applications to the state's data-center tax
relief program** under A.R.S. 41-1519.

Excluded from `data/moratorium_inventory.csv` because it is not a moratorium in
this dataset's sense. The inventory records pauses on *accepting or approving new
development* — an instrument that stops a project from being permitted. HB 4168
stops nothing from being built; it suspends eligibility for a subsidy. A
developer may proceed exactly as before, just without the tax abatement.

Admitting it would have made Arizona appear to have a development moratorium when
it has none, and would have blurred a distinction the dataset exists to keep
sharp. The researcher who found it flagged the ambiguity rather than asserting it,
which is the correct handling.

It **is** a real and relevant policy action, so it was instead recorded in
`data/state_legislation.csv`, where enacted state bills belong.

Note for future passes: the underlying research correctly established that **no
Arizona city or county had adopted a development moratorium as of 2026-07-31** —
Tucson, Pima County, Flagstaff, Marana, Pinal County, and Casa Grande all had
active disputes or zoning work underway but no enacted pause. Arizona's absence
from the inventory is a finding, not a gap.
