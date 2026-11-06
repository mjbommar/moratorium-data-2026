# Bloomington and Joliet: primary recovery and limits

This packet recovers official ballot/return evidence for two pending Illinois
groups. It does not allocate canonical identities, publish either measure or
establish a current legal restriction. The frozen ledger remains sixteen scoped
publications / 40 pending groups.

| Question | Official yes / no | Confirmed distinction | Remaining issue |
|---|---:|---|---|
| Bloomington moratorium advisory question | 21,851 / 6,316 | A yes vote favors advising a moratorium; specimen and export both identify it as advisory | Township qualification/government identity and final certification |
| Joliet Township data-center question | 3,800 / 14,207 | Township electorate; question addresses Joliet City Council; yes favors approval | Original referral/advisory authority, final certification and accounting difference |

## Bloomington

Exa located the [official specimen page](https://bloomingtonelectionsil.gov/november-3-2026-general-election/specimen-ballot/).
Its linked [three-page specimen PDF](https://bloomingtonelectionsil.gov/wp-content/uploads/2026/09/26GILBLO_SAMPLE_3.pdf)
places the data-center question under **ADVISORY REFERENDA**, on page 3. That
page was visually reviewed. The question asks whether the City of Bloomington
should implement a moratorium on creation of large-scale data centers. No
numeric size threshold or duration is stated by the question. Its restrictive
yes direction differs from the four Madison township permission questions.

The page is signed by the election-board executive director and certifies that
the **specimen ballot** is a true copy for the November 3 election. This does
not certify election returns, enact a moratorium or establish an operative date.
The City of Bloomington election-board administration and city ballot context
are established. Those facts do not, by themselves, resolve the separate legal
government under which the advisory question was qualified.

[WGLT's June report](https://www.wglt.org/local-news/2026-06-02/bloomington-residents-put-questions-on-data-centers-grocery-tax-international-weapons-to-nov-vote)
describes a special meeting of City of Bloomington Township residents and later
township qualification. That secondary account supplies a follow-up lead, not an
accepted city/township alias or original qualification record. The advisory
question also remains distinct from the existing city-council instrument in the
legacy inventory; no instrument relationship is accepted here.

A fresh headed bc-web/pydoll visit to the official results portal, with a 2,000 ms
settle, linked report version **385593**. The [linked ZIP](https://results.enr.clarityelections.com//IL/Bloomington/127392/385593/reports/summary.zip)
was fetched independently; its original empty client text was preserved and the
exact CSV member registered separately. Its counts are unchanged from the
earlier retained report. The portal displayed November 4, 10:38:55 AM, without
an explicit timezone.

The CSV labels 60 reporting units as **areas**, not precincts; those fields are
not silently mapped to precinct counts. It reports 53,070 registrations and
29,115 ballots cast. The 948 difference from yes/no is not assigned to blanks
or under/overvotes. No final certification was recovered.

## Joliet Township

The retained [county referenda list](https://www.willcountyclerk.gov/november-3-2026-general-election/referenda-list-november-3-2026-general-election/)
places the construction question under **JOLIET TOWNSHIP**. Its wording addresses
the **Joliet City Council**. The official CSV independently names the contest
Joliet Township Referenda Data Center. The addressed city council is therefore
kept distinct from the electoral government.

Fresh HTTP reacquisition of the wording page failed. The failure is retained;
the successful earlier primary version supplies wording, without being relabelled
a fresh fetch. A fresh headed pydoll visit to the results portal linked the
[official CSV ZIP](https://results.enr.clarityelections.com//IL/Will/127394/384833/reports/summary.zip),
version **384833**, whose counts confirm the earlier secondary report. Its portal
displayed November 3, 10:41:32 PM, without an explicit timezone. The CSV reports
37 of 37 precincts, 43,102 registrations and 18,601 ballots cast.

It also explicitly reports **32 overvotes and 557 undervotes**. Under the ordinary
one-response accounting sum:

`18,601 − (3,800 + 14,207 + 32 + 557) = 5`.

That arithmetic difference remains unresolved. No five-blank/other-vote category,
physical ballot loss or explanation is inferred, and no source value is changed
to force reconciliation. This needs clarification before accepting a complete
ballot accounting. Precinct completion is not final certification. Earlier
secondary descriptions call the question advisory; original referral/authority
evidence remains outstanding in this review.

## Verification and scope

Eight reviewed source versions match retained body/text archive hashes. Eleven
claims pass exact-text/CSV or reproducible visual checks, including three
page-specific specimen reviews. Report hyperlinks were checked in the retained
browser HTML, and CSV member bytes were compared directly against both ZIPs.
The new recovery added six archive versions; raw content remains private.

The bounded recovery used all eight fetch reservations, including one failed
fetch, and two Exa searches costing $0.014. Original referral/qualification
records, certification, source accounting and later legal implementation remain
open. These findings update the two existing pending seed groups without
changing canonical measure counts or the legacy inventory.
