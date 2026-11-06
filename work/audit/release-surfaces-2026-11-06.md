# Release consumer surface inventory — November 6, 2026

Status: initial tracked-text inventory complete; substantive copy review and delivery dispositions remain open. This is not a claim that all listed files are affected or current.

| Checkout | Tracked text/metadata surfaces | With pattern matches | Required disposition |
|---|---:|---:|---|
| `moratorium-data-2026` | 136 | 136 | Review current/generated/historical role; no consumer update accepted by this inventory |
| `moratorium-paper` | 378 | 373 | Review current/generated/historical role; no consumer update accepted by this inventory |
| `datacenter-paper-2026` | 1,324 | 1,296 | Review current/generated/historical role; no consumer update accepted by this inventory |
| `datacenter-data-integration` | 2,820 | 2,732 | Review current/generated/historical role; no consumer update accepted by this inventory |
| `servercountry.org` | 127 | 102 | Review current/generated/historical role; no consumer update accepted by this inventory |
| `fightadatacenter.com` | 12 | 8 | Review current/generated/historical role; no consumer update accepted by this inventory |
| `datacenter-2026-book` | 966 | 850 | Review current/generated/historical role; no consumer update accepted by this inventory |

The catalogue contains 5,763 surfaces, of which 5,497 have candidate pattern matches. These are file counts, not claims, completed reviews or publication requirements. Each entry pins its SHA-256, matched line categories/counts and up to eight sample line numbers. Source prose remains in its owning repository. Checkout HEADs and worktree-state fingerprints are observations, not remote/deployment verification.

## Required review lanes

| Surface group | Authoritative input / owner | Next concrete action |
|---|---|---|
| Dataset README, state pages, downloads, codebook, methodology and FAQ | Canonical moratorium CSVs and expanded snapshot in this repository | Reconcile narrative, examples and legal/electoral denominators; passing numeric checks do not accept prose |
| Landing page, site templates, timeline, maps and charts | Canonical generators plus manually maintained copy | Inspect rendered content, titles, legends, filters and download links; audit binary figures separately |
| Changelog, citation metadata, release body and assets | Final pinned release commit and manifest | Preserve historical entries; select release version only after data/freshness gates; verify actual remote release/assets |
| Moratorium paper and bundled PDF | `moratorium-paper` and this repository’s historical paper copy | Decide revised paper versus explicitly historical edition; inspect body/abstract/tables and actual PDF, not only text matches |
| Project paper and integration memos/exports | Server Country canonical project facts; integration-owned reviewed links | Pin distinct project/disclosure cutoffs and rebuild affected claims/links without implying full project-corpus refresh |
| Server Country, Fight a Data Center and book editions | Respective canonical project/manuscript/site owners | Review templates and chapters, distinguish historical editions and verify deployed outputs separately |
| Author sites and additional consumers | Ownership/discovery unresolved | Locate affected references; record explicit current, historical or pending disposition |

## Verification and limits

Representative README matches were inspected across the named checkouts. Scaffold text such as `astro@latest` is a keyword match, not proof of an outdated research claim. Historical-candidate/generated-candidate path hints are not approved dispositions. All entries deliberately remain `requires_review`.

The collector scans tracked UTF-8 Markdown, LaTeX, HTML, Astro, TSX, citation files and selected metadata. It excludes research/raw archives and immutable expanded generations. PDFs, charts/images, deployments, remote refs and unlisted consumers remain separate work. Per-record freshness and unresolved legal histories also remain required; this inventory does not renew source dates.

Reproduce: `python3 scripts/audit_release_surfaces.py --output work/audit/release-surfaces-2026-11-06.json`. The [JSON catalogue](release-surfaces-2026-11-06.json) pins the collector hash and source observations. Regeneration creates a new observation; preserve the release’s final manifest independently.
