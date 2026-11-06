# Ohio wave 4 primary follow-up

Four reviewed claims from three primary source versions supplement the [Sunbury/Upper Sandusky review](../ohio-ballot-wave4-review/README.md). They remain unpublished: canonical counts are still33 measures /23 pending candidate groups.

- **Trenton city, Butler County:** the county election-office CMS list identifies Issue17 as proposed Article IX Section9.06, “Prohibition of Construction of a Data Center.” It prints `(F)09-04-2026 (C)09-09-2026`; these terms are retained literally, without interpreting them as final result certification or legal-effect dates. The official election-night contest reports3541yes/903no,79.68%yes and8/8 precincts. Its “Yes, Winner” label does not establish certification, a formal legal outcome or operative force. No municipal ballot/registration/under/over/blank counts are accepted. Exact primary ballot text remains unrecovered.
- **Upper Sandusky:** August17,2026 city minutes describe residents' circulated petitions and Board of Elections signature certification. They explain that council placement is neither support nor opposition to the proposal. The minutes record unanimous adoption of the placement ordinance, printed **85-14**. That unusual printed identifier is preserved without guessing a correction. Procedural placement is distinct from adopting the substantive prohibition; petition qualification is distinct from result certification. The original petition, independent BOE certification instrument and complete charter amendment remain unrecovered.

The minutes help reconcile the worker's petition-versus-council-referral descriptions: petition origin and subsequent council placement are different stages. The complete qualification chain still requires independent underlying instruments. The official minutes were also visually checked at150DPI, physical page4; accepted claims here use exact located source text.

## Acquisition accounting and exclusions

The dedicated follow-up cap was **two Exa searches and six fetch attempts**; all were used and are terminal. Exa reported **$0.014** total. No SerpAPI calls or new model-extraction calls occurred. The original completed distributed Terra queue was not restarted.

The two successful target sources were the Butler CMS list and Upper Sandusky minutes. The current Butler official homepage also loaded; it identifies the county election office, links its November ballot-list path and uses the same Revize county CMS. Exact byte-equivalence between the CMS list and the homepage's `.gov` list URL was not fetched within this cap and is not asserted.

The remaining three attempts did not recover usable target evidence:

- The pydoll Butler state-hosted sample-ballot path returned HTTP200 but **`ok:false`, “Not a Customer.”** Its contents are excluded from claim support. Butler's official homepage instead links its own ElectionLink sample-ballot service, a possible future recovery route.
- The guessed `www.boe.ohio.gov/butler/` homepage returned404 and is excluded.
- The Daily Chief Union notice search URL loaded successfully with pydoll, but its actual body was an unrelated sheriff's-sale notice. Neither search title nor active-notice URL establishes that the requested election notice was rendered. It is excluded from election claims.

All original acquisitions, failures, provider responses and reservations remain in the private ledger. Three reviewed exact body/text versions are archived and verified, including the retained Trenton return. Full texts remain private. Trenton's complete ballot, Upper Sandusky's complete text/underlying qualification records, Sprigg's full plan, final canvasses, operative histories and census completeness remain open.

```bash
/home/mjbommar/projects/bc/bc-modules/.venv/bin/python work/research/2026-11-06/ohio-wave4-primary-recovery/verify.py \
  --evidence-directory /data0/moratorium-refresh-2026/discovery/ballot-oh-004 \
  --evidence-directory /data0/moratorium-refresh-2026/ohio-wave4-primary-recovery
```

`validation.json` confirms four evidence-verified claims and three archived exact versions. This packet does not publish canonical records or establish current force.
