# Frequently Asked Questions

## What is this dataset?

A list of every local-government moratorium we could identify in the United States that targets one of these kinds of new development:

- **Data centers** (server farms, including hyperscale and AI computing facilities)
- **Cryptocurrency mining** facilities
- **Battery energy storage systems** (BESS) — large lithium-ion installations
- **Solar farms** (utility-scale)
- **Wind farms** (utility-scale)

Each row is one moratorium adopted by one local government (a city, county, township, etc.). The dataset covers the period 2018 through April 2026, with a sharp acceleration in 2025–2026.

## What is a moratorium?

A moratorium is a temporary pause that a local government places on accepting or approving permit applications for certain kinds of new development. Common features:

- **Time-limited.** Most run 6 to 12 months. Some go up to 24 months. A few are open-ended.
- **Defined scope.** They cover only the specific kinds of projects named in the ordinance — not all development.
- **Paired with a study process.** The local government typically commits to studying impacts and writing permanent rules during the pause.
- **Adopted by ordinance or resolution.** A formal vote of a city council, county commission, township board, etc.

A moratorium is **not** a permanent ban. It is a temporary pause, intended to give regulators time to catch up.

## Why are local governments doing this?

The short version: **infrastructure is moving faster than zoning codes can adapt.**

A typical hyperscale data center is 100+ megawatts of computing power, hundreds of thousands of square feet, with diesel backup generators, water-cooling systems, and electrical demand that can rival a small city. Most local zoning codes were written before this kind of facility existed and don't define it, classify it, or set standards for noise, water use, generator emissions, fire safety, or grid impact.

Faced with a specific proposal, a local government has two choices: approve under inadequate rules, or pause to write new rules. The moratorium is the second option.

The same dynamic applies to battery storage (especially after the January 2025 Moss Landing fire), to large solar and wind installations, and to cryptocurrency mining sites.

## Why does this matter?

Three reasons:

1. **Capital flow.** Announced data center capital commitments alone now exceed $1 trillion. Moratoria delay or block individual projects, with consequences for siting decisions, ratepayer costs, and regional economic development.
2. **Climate transition.** Moratoria targeting solar, wind, and battery storage slow the buildout of clean-energy infrastructure that climate policy depends on.
3. **Local democracy.** Moratoria are one of the most visible ways local governments push back against industries that have political support at the state and federal level. Tracking them maps a real political phenomenon.

## How was this dataset compiled?

Three phases:

1. **Document collection.** AI-assisted research agents scanned municipal websites, agenda portals, board meeting minutes, planning commission records, state legislative databases, and news coverage across all 50 states. We collected approximately 4,400 original documents (PDFs, HTML pages, Word files), totaling ~12 GB.
2. **Classification.** Each document was classified by type (ordinance, resolution, agenda, news article, etc.) and tagged for whether it was moratorium-related. About 709 documents are moratorium-related.
3. **Structured extraction.** From the 709 moratorium documents, we used a large language model with a detailed schema to extract structured data: jurisdiction, dates, duration, sectors covered, exemptions, and 40+ other clause-level features. After confidence filtering, 348 instruments are coded line-by-line.

Each extracted record was manually reviewed for jurisdiction names and state codes; the resulting cleaned inventory has 223 rows.

For full methodology, see [`methodology.md`](methodology.md).

## How accurate is the data?

**Confident on:** state, jurisdiction, jurisdiction type, sectors covered, approximate enactment date.

**Less confident on:** exact ordinance numbers (many small townships don't post numbered ordinances online), final dispositions of pending or recently-extended moratoria, exact dates within ±a few weeks for events the local government hasn't published minutes for.

**Where confidence is low**, we mark a row with `verify_notes` indicating exactly what's uncertain and why. We never invent dates, ordinance numbers, or vote counts.

The mean confidence score on the 348 line-coded entries is **0.72** (range 0.40 to 0.95) on a 0-to-1 scale assigned by the language model.

## My town is on the list — is that bad?

No, this is just an inventory of local-government action. A moratorium isn't a sign that something is wrong; it's a sign that your local government is actively managing land-use decisions. Many of the moratoria on this list have been replaced by permanent regulations within 6 to 12 months — exactly as intended.

## My town isn't on the list — does that mean we don't have a moratorium?

It's possible we missed it. The dataset is built from publicly available records, and many small townships don't post agendas, minutes, or ordinances online. If you know of a moratorium we missed, [open an issue](https://github.com/mjbommar/moratorium-data-2026/issues/new?template=new-moratorium.md) and we'll add it in the next release.

## Can I use this data for my own analysis / article / report?

Yes. The data is published under [Creative Commons Attribution 4.0](../LICENSE-data). You can reuse, redistribute, remix, and even use it commercially, as long as you credit the source. Suggested citation is in the [README](../README.md#how-to-cite).

If you publish something based on this data, we'd love to hear about it — drop a note in [Discussions](https://github.com/mjbommar/moratorium-data-2026/discussions) or email Michael directly.

## How often is this updated?

The current snapshot is **April 2026**. Refreshes are roughly quarterly. Each refresh is a tagged release on GitHub (`v2026.04`, `v2026.10`, …) so you can pin your analysis to a specific version.

The moratorium wave is still accelerating: 130+ moratoria were enacted in just the first four months of 2026. Expect this dataset to grow.

## Who built this?

[Michael J. Bommarito](mailto:michael.bommarito@gmail.com), with substantial AI-assisted research. Methodology is fully documented and reproducible.

## What if I disagree with how something is classified?

Open an issue with the specific row and your reasoning. Classification rules are documented in [`codebook.md`](codebook.md); we'll either update the row or document the disagreement.

## What's next on this dataset?

1. **A landing page** with a searchable, filterable table (planned for the next release).
2. **A Zenodo deposit** with a permanent DOI per release.
3. **Geocoding** of each jurisdiction so the data plays nicely with mapping tools.
4. **Outcome tracking** — following each moratorium from enactment through replacement, extension, expiration, or rescission.

## Other questions?

[Open a question issue](https://github.com/mjbommar/moratorium-data-2026/issues/new?template=question.md) or email [Michael](mailto:michael.bommarito@gmail.com).
