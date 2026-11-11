# Moratorium Data 2026

This project tracks local pauses on data centers, battery storage, solar, wind, and cryptocurrency mining in the United States. It also tracks related state policies and ballot measures.

**[Open the dashboard](https://mjbommar.github.io/moratorium-data-2026/)** · [Browse states](states/README.md) · [Download local records](data/moratorium_inventory.csv) · [Read ballot results](docs/ballot-results.md)

The current release is [v2026.11.11.post13](https://github.com/mjbommar/moratorium-data-2026/releases/tag/v2026.11.11.post13), published November 11, 2026. Some records still have open questions.

## What the data contains

| Tracker | Records |
|---|---:|
| Local moratoria and proposals | 1329 |
| State policies and proposals | 449 |
| Ballot measures and proposals | 57 |

The local records cover 47 states. The three trackers count different kinds of actions, so their totals should not be added together. Some records describe proposals or past actions. Some still combine several actions that need further review.

## Local record status

| Status listed in the data | Records |
|---|---:|
| Active | 886 |
| Extended | 199 |
| Pending | 64 |
| Replaced | 84 |
| Expired | 77 |
| Rescinded | 12 |
| Rejected | 3 |
| Unknown | 4 |

These are recorded classifications. They do not confirm that every restriction is still in effect. Read the record's sources and notes before using it to assess a project or a legal requirement.

## What changed in this update

A Dark mode button on every public page switches between light and dark colors. The site remembers your choice.

Rice, Minnesota’s signed September 21 minutes confirm a 5–0 vote on Resolution 092126-27 for a data-center study and moratorium. The full instrument and its effective-date provisions remain unconfirmed.

Gallatin, Tennessee’s record now includes the October 20 hearing and the unsigned six-month draft in the November 3 packet. Its proposed exceptions depend on prior approvals. The record does not establish final adoption or whether a particular Meta project qualifies for an exception.

Ten text fields changed across the two records. No record changed status, and all headline totals are unchanged. See the [release notes](work/research/2026-11-11/release-2026.11.11.post13/README.md).

## State policy

The state tracker includes bills, resolutions, executive actions, and preliminary legislative memos. A state record may affect permits, utilities, or local authority without creating a moratorium.

| Type of state record | Records |
|---|---:|
| Bill | 427 |
| Legislative resolution | 12 |
| Preliminary legislative memo | 3 |
| Legislative amendment | 1 |
| Other state action | 6 |

For infrastructure analysis, use the [reviewed inclusion file](data/policy-scope/reviewed-included.csv). The raw tracker keeps historical and out-of-scope records so earlier findings remain available.

| Infrastructure review | Records |
|---|---:|
| Included | 384 |
| Excluded | 19 |
| Still unresolved | 46 |
| Not yet reviewed | 0 |
| Exploratory candidate file | 430 |

The candidate file includes unresolved records. It is not a count of confirmed infrastructure restrictions. [Read the file definitions](docs/policy-scope-exports.md).

## Ballot measures

The ballot tracker contains proposals, advisory questions, temporary pauses, permanent restrictions, and zoning changes. Read the question to understand what a yes vote means.

| Stage listed in the data | Records |
|---|---:|
| Vote recorded | 52 |
| Scheduled | 3 |
| In litigation | 1 |
| Unknown | 1 |

There are 53 current result reports for 52 measures. One measure can have reports from more than one area. The data keeps 65 result versions, including earlier reports. The data has 5 current reports with certified results.

A reported vote, a certified result, and a restriction taking effect are separate events. Ballot approval does not automatically add a local moratorium to the inventory. Some candidate measures remain outside the published tables because their identities or wording are unresolved. See [ballot results](docs/ballot-results.md) and [known gaps](docs/known-gaps.md).

## Coverage and limits

We searched all 50 states, but we may have missed local actions. The main November search ended November 7. Later source checks have their own dates.

There are 979 local records with verification flags. Other records can still have unresolved details. The review queue contains 1347 open records; reviews closed 192 records after corrections and 239 without changes. Those reviews cover specific recorded facts, not a general finding that each law remains in effect.

The map has coordinates for 1327 of 1329 local records. The two without coordinates describe groups of proposals. Markers identify jurisdictions; they do not show project sites or legal boundaries.

An earlier analysis examined 348 moratorium texts from 211 jurisdictions, collected before April 28, 2026. The [April paper](paper/moratorium-nation-2026-04-30.pdf) and its findings have not been updated for the current inventory.

## Use the data

Open [moratorium_inventory.csv](data/moratorium_inventory.csv) in Excel, Google Sheets, or other spreadsheet software. For records listed as active or extended, filter `enacted_status` to those two values. The [codebook](docs/codebook.md) defines the columns.

```python
import pandas as pd

url = "https://raw.githubusercontent.com/mjbommar/moratorium-data-2026/main/data/moratorium_inventory.csv"
records = pd.read_csv(url)
selected = records[records["enacted_status"].isin(["active", "extended"])]
print(selected["state"].value_counts())
```

[Data files and examples](data/README.md) explain the state and ballot downloads. [Methodology](docs/methodology.md) describes collection and review. The [refresh runbook](docs/refresh-operations.md) covers the update process.

## Corrections and contributions

To report a missing record or an error, [open an issue](https://github.com/mjbommar/moratorium-data-2026/issues/new/choose). Include the jurisdiction, the record ID if available, and a source. We review suggested changes before adding them.

## How to cite

Use [CITATION.cff](CITATION.cff) for the dataset citation. Include the release version or access date so readers can find the data you used. Cite the April paper separately when using its findings.

The data is available under [CC BY 4.0](LICENSE-data). The code is available under [MIT](LICENSE-code). The project is maintained by [Michael J. Bommarito](https://michaelbommarito.com/) with AI-assisted research. Source files and review records document the work.
