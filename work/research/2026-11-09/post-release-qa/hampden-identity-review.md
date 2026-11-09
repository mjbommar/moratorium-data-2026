# Hampden identity provenance follow-up — 2026-11-09

**Decision: the two records identify the same instrument and May 26 action.** The supported mapping is alias `wi-hampden-2026-2` to canonical `wi-hampden-2026`. A guarded retirement is prepared for separate review; nothing was applied. This decision is limited to identity and does not establish effective date, current legal force, or accuracy of either row's other fields.

The earlier hold was correct on the evidence then located: the alias row itself had no citation and its source was untraced. The newly located historical answer supplies the missing positive connection. In commit `4a53040`, the No. 13 Hampden answer in `work/answers/qa3-gaps/gaps-5.json` expressly cites the ordinance PDF, describes its twelve-month/earlier-ending provision and possible six-month amendment, and identifies the existing-data-center nonconforming-use provision. The same commit's No. 18 answer in `work/answers/qa4/leads-WI.json` cites that PDF and the May 26 special board minutes. Both raw IDs were added in that commit; each historical CSV row corresponds to its respective answer across jurisdiction, date narrative, duration, legal basis, trigger, status, outcome and other checked fields. The saved historical No. 13 answer is byte-identical to the committed answer (SHA-256 `fb4d0adab316aa330c4ee67f8d3e3b8555460e1c42d20d55f53e415297482fbf`).

The original manifest **in that commit**, key `5d41700ee871ac9f`, records the PDF URL and a September 23, 2026 14:25:13 UTC fetch with body SHA-256 `58aa88d8ea74f971fc11a8e26edd1a40665eb8a9810977f9aa7c64a36f506a32`. The actual retained PDF independently hashes to exactly that value. Thus this is a historical body match, not an assumption that a URL still serves the same content. The original manifest's later working-copy `published` annotation is not needed for the pin.

## Evidence examined

- [Town ordinance PDF](https://townofhampden.wi.gov/docs/ch-18-data-center-temporary-moratorium.pdf), SHA-256 `58aa88d8ea74f971fc11a8e26edd1a40665eb8a9810977f9aa7c64a36f506a32`: page 1 header visually reads handwritten **18**; article 3 contains the specific term and extension; page 2 article 5 addresses existing nonconforming data centers. The September retained extraction reads the number as 13. A fresh rendering of the actual retained PDF was visually inspected. Its terms correspond to the No. 13 answer's cited source and content; the particular extraction or model process that produced that answer has not been established.
- [May 26 special board minutes](https://townofhampden.wi.gov/docs/special-public-n-board-meeting-minutes-2026-05-26.pdf), SHA-256 `45b57f3d208040b1c0feb88733043011ee6cdfdd972d1c3ca59ed11e6e3be0c6`: page 1, special board meeting, records the motion passing to enact Ordinance No. 18 with the same title as presented. Repeated pages in this retained PDF repeat the same minutes, not separate enactments.
- [June 16 board minutes](https://townofhampden.wi.gov/docs/town-board-meeting-minutes-2026-06.pdf), SHA-256 `25b4131d7bcadd43468f46b45cdc9e48085405336557710d2c0cd93fed4ff82a`: page 1, citizen correspondence, identifies that Ordinance No. 18 as passed May 26, and the board approves the May 26 special meeting minutes.

The No. 13 answer's date narrative attributes May 26 to a town page's last update, while its own notes say May 27 and the previously retained town page also says May 27. This is an unresolved source/date assertion, not an identity gap: the answer's explicit PDF citation, historical body pin, body content, scan header and minutes positively connect the two records. No claim that a separate Ordinance 13 does not exist is needed. The scan's article 6 addresses effectiveness; neither this identity review nor the retirement preview determines when its requirements were satisfied.

## Guarded preview

The current records exactly match the prior assignment's complete row preimages. Row hashes use the protocol's UTF-8, sorted-key, compact JSON encoding:

- Canonical `wi-hampden-2026`: `dfd46d3087f690c86bf0c9ec9bb49d30be60803619fdabc30162fbef99f92daa`.
- Alias `wi-hampden-2026-2`: `d13d156a88a10127ecdacd0caf75f44f7b7eeb1715e29d66358409b7ad6cc3f0`.
- Entire inventory before: `5806ad1a8fb2b8587cb1d63820e4fa6765792319bf838f3474e91ad07f7a975e`.
- Prior registry: `8abc04716797ba89e210531f2956407b1407ff3a3fd06ff64e4d38fcb8a6fc82`.
- Projected inventory after: `533bab9144db8cc57fe2280ba7165238031231583b2cee9d84f52f4344b1b4d2`.

The private plan follows `docs/legacy-moratorium-identities.md` and the exact schema of `scripts/legacy_moratorium_identity.py`. The structural preview returned `preview_only_not_applied`; the retirement dry run returned `ready`. The proposed output retains every survivor field unchanged; the plan contains the complete alias preimage, and application would record it and the canonical preimage in the append-only registry. This is a transaction preview, not a validation of legal identity by the script. The independent policy CSV correction is outside this transaction. Before any separate application, the reviewer must recheck the full inventory, registry and row guards; regenerate the plan and repeat the preview if any guard has changed. After authorized application, validate alias lookup and replay and reconcile downstream snapshots and release assets. No field merging is proposed.
