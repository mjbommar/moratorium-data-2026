# Data files

Use the CSV files in a spreadsheet or load them with Python, R, or other analysis tools. The [codebook](../docs/codebook.md) defines the columns.

## Downloads

| File | Contents |
|---|---|
| [Local inventory](moratorium_inventory.csv) | Local moratoria, proposals, and past actions |
| [State tracker](state_legislation.csv) | State policies and proposals |
| [Summary counts](summary_stats.json) | Counts by state, status, and other fields |
| [Ballot measures](expanded-csv/ballot_measures.csv) | Reviewed ballot measures and proposals |
| [Current ballot results](expanded-csv/measure_results_current.csv) | Latest result reports, with certification status |
| [All ballot result versions](expanded-csv/measure_results.csv) | Current and earlier result reports |

The local inventory has 1329 records. The state tracker has 449 records. A record may describe a proposal or a past action; these totals are not counts of current restrictions.

## Local records

- `moratorium_id` identifies a record across releases.
- `enacted_status` gives the recorded status: `active`, `extended`, `pending`, `replaced`, `expired`, `rescinded`, `rejected`, or `unknown`.
- `duration_days` describes the original term when a fixed number of days is known. Calendar months are not converted to a fixed number of days.
- `current_end_date_iso` records a known current end date, including an extension when confirmed.
- `latitude` and `longitude` identify a jurisdiction reference point. They do not show a project site or legal boundary.

There are coordinates for 1327 of 1329 records. The two without coordinates describe groups of proposals. Dates and status fields can be uncertain; read the accompanying notes.

```python
import pandas as pd

records = pd.read_csv("moratorium_inventory.csv")
selected = records[records["enacted_status"].isin(["active", "extended"])]
print(selected["state"].value_counts())
```

This selects records listed as active or extended. It does not confirm that each restriction remains in effect.

## State policy files

The raw state tracker keeps all records, including historical actions and records outside infrastructure scope. Use `policy_instrument_type`, `policy_mechanism`, `legal_effect_status`, and `scope_of_action` to select the records your analysis needs.

| Infrastructure review | Records |
|---|---:|
| Included | 384 |
| Excluded | 19 |
| Still unresolved | 46 |
| Not yet reviewed | 0 |
| Exploratory candidate file | 430 |

The [reviewed inclusion file](policy-scope/reviewed-included.csv) contains the included records. The [annotated file](policy-scope/all-annotated.csv) keeps every record and its review decision. The [candidate file](policy-scope/not-explicitly-excluded-candidates.csv) also includes unresolved records. It is intended for further research.

Read the [scope definitions](../docs/policy-scope-exports.md) before comparing totals. These are record counts, not counts of unique laws or confirmed current restrictions.

## Ballot records

The ballot tracker has 57 proposals and measures. It keeps 65 result versions, including earlier reports. There are 53 current result reports for 52 measures. Some measures have no result, and one measure can have reports from more than one area.

A reported result, certification, and legal effect are separate fields. Do not treat every approved measure as an effective moratorium. Some proposed measures remain outside the published tables because their identities or wording are unresolved. See [ballot results](../docs/ballot-results.md) and [known gaps](../docs/known-gaps.md).

The `expanded` and `expanded-csv` folders link to saved versions. Keep those links and their snapshot folders together when copying the complete dataset. The [publication documentation](../docs/expanded-promotion.md) describes the file layout.

## Historical text analysis

[structured_extractions.jsonl](structured_extractions.jsonl) contains 526 successful model extractions and 338 recorded call errors. The earlier clause analysis used 348 extractions with model confidence scores of at least 0.4. Those scores are model assessments, not measured accuracy.

[clause_extraction_analysis.json](clause_extraction_analysis.json) contains the earlier summary. The analysis predates April 28, 2026 and has not been repeated for every record in the current inventory.

## Versions and reuse

The next release is [v2026.11.11.post12](https://github.com/mjbommar/moratorium-data-2026/releases/tag/v2026.11.11.post12). Publication checks are running. [Post11](https://github.com/mjbommar/moratorium-data-2026/releases/tag/v2026.11.11.post11) is the current published version.

Use a tagged release for work that others need to reproduce. The main branch may contain later corrections. Record source dates vary; the publication date does not mean every record was checked that day.

The data is available under [CC BY 4.0](../LICENSE-data). Include the release version or access date when citing it.
