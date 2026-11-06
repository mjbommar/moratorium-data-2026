# California remaining-return review — November 6, 2026

This follows the [chaptered-policy review](../ca-policy-wave1/README.md). All six remaining existing California records now have a bounded coordinator disposition, with explicit limits. This does not establish complete California legal-force freshness.

| Record | Reviewed result | Canonical action |
|---|---|---|
| AB 1095 | Official history explicitly records January 31 constitutional death and February 2 filing with Chief Clerk | Retain failed_died / failed; add primary history URL |
| AB 93 | Official history records October 11, 2025 veto and January 22, 2026 removal of veto consideration | Retain vetoed / failed; add primary history URL |
| SB 1298 (2023–2024) | Official history records November 30, 2024 return from committee and Assembly without further action | Retain prior-session failed disposition; add primary history URL |
| AB 2170 | Latest displayed action remains May 14, 2026 held under submission | Add primary history URL; ultimate disposition unresolved |
| AB 222 | Latest displayed action remains August 29, 2025 held under submission | Add primary history URL; ultimate disposition unresolved |
| SB 978 | Latest displayed action is May 14, 2026 held in committee and under submission; March 23 proposed text materially differs from the old summary | Correct proposal summary, mechanism and scope; add primary history URL; ultimate disposition unresolved |

The first three decisions confirm recorded terminal disposition only, from primary histories acquired November 5. The other three retain their existing legislative categories provisionally. A committee hold is not itself a terminal disposition, and no automatic death-by-deadline inference is made.

## SB 978 amendment interpretation

The March 23 amended HTML contains sixteen `strike` elements, including a deleted clause requiring onsite solar, wind or battery-only backup generation. Some deleted passages also have nested `s` elements. Flattened text retains that deleted language and would misrepresent the surviving proposal. The independently reacquired body is preserved, and a registered derivation removes `strike`/`s` and script/style content while retaining the surviving proposed text. This is an interpretation of amendment markup, not enacted law.

The surviving text proposes a special rate structure for data centers taking transmission-level electrical service with estimated peak demand of at least 75 MW; cost-shift protections and upfront infrastructure costs; prefunding a 15-year incremental zero-carbon resources contract; and prevailing-wage and skilled-and-trained-workforce requirements. Accordingly, the primary mechanism becomes utility_large_load_restriction and scope becomes mixed. The old backup-only restriction is explicitly identified as deleted in the replacement summary. Remaining drafting inconsistencies, including surviving references to a large-scale energy user, are not silently repaired or treated as enacted requirements.

`review.json` pins the body and deletion-aware extraction hashes, removed passages, original evidence integrity checks and six record dispositions. `answers.json` is the reviewed application contract, guarded by the exact 14-row California baseline. The original full HTML extraction from wave 1 and the original native acquisition text remain retained; the new derivation belongs to a separate fresh acquisition, so older evidence is not overwritten.

## Search limits and counts

One bounded Exa official-domain query returned four results: the matching SB 978 status page, an unrelated AB 978, an earlier-session AB 2170, and a general bill search page. These do not prove final disposition. The indexed SB 978 status snippet shows an April 20 committee action, older than the retained May 14 history action; it is not promoted as the latest action. Two HTTP acquisitions independently recover the current SB 978 amended text and history. The search cost reported by the provider is $0.007; it is not a dollar estimate for all activity.

This batch changes nine fields across six existing rows: six primary URLs and SB 978's summary, mechanism and scope. There are no new policy rows, enactment changes, local instrument changes or ballot-table changes. Totals remain 441 state-policy actions, 439 bills, 91 enacted bills, 1,293 local instruments and 1,071 classified in force. Later implementation and full substantive/current-force review remain open. Earlier wave-1 pending lists are historical receipts; this packet records their subsequent bounded disposition without rewriting them.

Validation: `make data site check` passed (zero errors, 282 data warnings; all 49 documented counts match). Replay proposes zero additional field edits. Exact CSV comparison confirms only the nine intended field changes across six records. `validation.json` pins the completed check log.
