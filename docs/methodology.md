# Methodology

This project collects local moratoria and related state policies and ballot measures. It records what the available sources support and identifies details that still need confirmation.

The local inventory has 1329 records from 47 states. The local and state files contain 1778 records in total. These are records of government actions and proposals, not a count of laws confirmed to be in effect today.

## Sources

We search official government websites, ordinance collections, meeting agendas and minutes, state legislative records, news archives, and relevant court records. Searches have covered all 50 states. Coverage varies because some local governments do not publish searchable records.

Where possible, we obtain the ordinance, resolution, completed meeting record, or official vote return. News reports help find actions and explain their context. A search result or news summary does not replace the underlying document when a legal detail remains disputed or unclear.

We keep source files and retrieval dates. A file hash identifies the saved version. Extracted text, OCR output, and page images are kept separately so a reviewer can compare them with the original. A failed download is recorded as a gap, not as proof that no action occurred.

## Collection and review

AI tools help search for sources and suggest structured entries. For recent corrections, separate extraction and review steps check the proposed changes against the retained sources. The review records identify the fields considered, the supporting sources, and the questions left open.

A review can confirm a historical fact without resolving every question about a record. For example, completed minutes may establish that a resolution passed while leaving its exact effective date or later amendment unresolved.

The [review queue](../work/research/2026-11-09/post-release-qa/outstanding-record-questions.jsonl) lists the remaining questions. The [review history](../work/research/2026-11-08/full-record-dispositions/README.md) explains the completed and open reviews. Model names, requests, source versions, and other research details are recorded in the audit files.

## Local records

The intended unit is one moratorium instrument per record. Some older records combine actions or describe groups of proposals. Those cases remain identified for further review.

The inventory records the jurisdiction, sector, authority, stated purpose, dates, term, status, affected projects, and outcome when known. The [codebook](codebook.md) defines each field.

An agenda establishes that an item was scheduled. A first reading establishes that stage of consideration. Neither establishes final adoption. A blank signature line or a future passage date printed in a draft is not evidence that passage occurred.

Adoption and effectiveness are also separate. A restriction may depend on publication, filing, or another condition. We leave an effective date or end date unknown when the sources do not establish the required condition. Calendar terms are not converted to a fixed number of days.

The status fields describe the sources reviewed. We do not assume uninterrupted legal effect from an old adoption record, or automatic expiration from a proposed end date. Later amendments, replacements, court orders, and project-specific exceptions may require additional evidence.

## State policy

The state tracker includes bills, resolutions, executive actions, preliminary legislative memos, and other actions. These can affect permits, utility procedures, incentives, or local authority without imposing a local moratorium.

The raw file retains historical records and records outside infrastructure scope. The [scope exports](policy-scope-exports.md) separate reviewed inclusions, exclusions, and unresolved cases. A memo and a related bill can remain separate records. Counts therefore do not necessarily represent unique bills or enacted restrictions.

## Ballot measures

The ballot tracker contains 57 proposals and measures. It distinguishes the question, the election, reported results, certification, and any related legal instrument. A question may be advisory, binding, temporary, permanent, or specific to a zoning change.

The latest result reports are shown in [ballot results](ballot-results.md). Earlier versions remain in the data. A measure can have reports from several areas, so the number of reports can exceed the number of measures with results.

Approval, certification, and a restriction taking effect require separate evidence. A missing result does not establish defeat. A proposed election date does not establish that a question reached the ballot. [Scope and interpretation](ballot-measures.md) explains the unresolved cases.

## Map locations

There are coordinates for 1327 of 1329 local records. The two without coordinates describe groups of proposals. The points identify jurisdictions; they do not show project sites, jurisdiction boundaries, or the area subject to a restriction.

Recent corrections use official Census reference points after checking the jurisdiction's identity. Earlier coordinates have not all been checked again. Shared town names and county names can cause errors. See the [geographic limitations](known-gaps.md#geocoding-caveats-added-v2026042).

## Historical text analysis

An earlier collection produced 526 successful structured extractions and 338 recorded model-call errors. The clause analysis used 348 extractions with model confidence scores of at least 0.4, covering 211 jurisdictions. These scores are model assessments, not measured accuracy.

The [November 13 second edition](../paper/moratorium-nation-2026-11-13.pdf) withdraws these clause-prevalence percentages. Both historical confidence-filtered cohorts include unrelated documents, summaries, and repeated actions. A model confidence score did not establish eligibility, and a missing field in a summary does not prove that the legal instrument lacked a clause. Six reviewed texts now illustrate drafting choices without estimating national prevalence. The [April paper](../paper/moratorium-nation-2026-04-30.pdf) remains a historical edition.

## Applying corrections

A proposed correction records both the old value and the new value. Before applying it, the update process checks that the old value still matches the current record. This prevents a stale review from overwriting a newer correction.

CSV updates are staged as complete files, then replace the destination. The process preserves file mode and requests file and directory synchronization. A failure after replacement can leave the new file visible even if durable storage has not been confirmed. These guarantees depend on the filesystem. Source and audit receipts record the inputs and accepted changes; they do not substitute for factual review.

Ballot publication checks record identities, source references, schemas, and links between tables. New result versions retain earlier versions rather than deleting them. The [data contracts](expanded-data-contracts.md) and [publication protocol](expanded-promotion.md) describe those checks.

## Releases and site checks

A data release is built from a fixed commit. Checks compare archive contents, saved versions, and repeat builds. Restore checks confirm that the archived files can reproduce the tables. Download checks compare public assets with the release files. Site checks compare deployed files and test the dashboard in a browser.

These checks establish file consistency and delivery. They do not establish complete source coverage or the present effect of every law.

The current release is [v2026.11.11.post13](https://github.com/mjbommar/moratorium-data-2026/releases/tag/v2026.11.11.post13), published November 11, 2026. Some records still have open questions.

The main November search ended November 7. Later source checks keep their own dates. A new release date does not mean every record was checked that day.

## Reproduce the site

The repository includes the CSV files, saved ballot tables, source references, and build scripts. Use a tagged release when reproducing published work. The [data guide](../data/README.md) explains the saved versions and current file links.

```sh
make validate
make site
make check
```

Run these commands in the project's Python environment. `make validate` checks the local and state CSV files. `make site` builds the dashboard and documentation. `make check` also checks generated tables and ballot publication records. The [refresh runbook](refresh-operations.md) describes the research tools and update steps.

## Limits

The inventory may miss actions, particularly where records are not online. Some entries still have uncertain identities, dates, text, or later outcomes. Search coverage is uneven, and the dataset is not a probability sample.

Counts describe the records collected. They should not be used to estimate national prevalence without accounting for those limits. The project does not predict whether a proposal will pass or a project will be built. See [known gaps](known-gaps.md) before using the data.
