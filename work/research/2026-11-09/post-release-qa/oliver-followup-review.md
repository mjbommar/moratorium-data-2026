# Oliver County phase two: independent targeted source follow-up

**Recommendation: no canonical change.** The current `nd-oliver-county-2025-p2` row already records the May 6 adoption, the 90-day motion, the different standards-dependent language, and the unresolved recording, publication and operative interval. This follow-up identifies the county-linked zoning compilation and narrows what that specific document can show, but does not resolve those questions or establish an end date. Retain `enacted_status=unknown` as the unresolved recorded stage, `duration_kind=unknown`, and blank `duration_days` and `current_end_date_iso`; do not mistake the unknown stage for uncertainty about the recorded May vote. The prior independent review reached the same disposition.

## What the new source clears and narrows

The captured [county P&Z ordinance index](https://olivercountynd.org/index.asp?SEC=42082F2D-F36B-481F-8A2C-A7A4C5DC3852) has a child navigation link to [Ordinance](https://olivercountynd.org/index.asp?SEC=69381416-4330-439E-BD97-A1714AA34C22); the latter's document link points to the [zoning ordinance and table of contents PDF](https://olivercountynd.org/vertical/sites/%7B6E6CB90D-6F4C-4198-8B57-AAF2D42615E1%7D/uploads/PZ_Ordinance_and_TOC.pdf). The actual captured HTML bodies establish both links. Receipts report successful captures on 2026-11-09 14:50–14:51 UTC; this is a post-cutoff observation, not proof of the site's contents at the prior review's 2026-11-07 cutoff.

The actual PDF has 122 physical pages. Its cover, physical page 1, identifies a 2026 revision and states commission approval on June 4, 2026. Its introduction, physical page 10, printed page 1, section 1.3, states an effective date of September 11, 2025. These are distinct statements within the compilation; the source alone does not reconcile their relationship or establish an effective date for every revision. Sections 1.6–1.7 on physical page 10 address other restrictions and interpretation, while section 1.9 on physical page 11 contains a general repeal of conflicting regulations. No determination is made that this provision affected Resolution 2025-02. Section 31.12 on physical page 103, within a separate section of the compilation, also states an adoption-related effective rule; it does not settle the phase-two moratorium.

A case-insensitive search of the complete 122-page `pdftotext -layout` extraction found no literal data-center, cryptocurrency, moratorium, or Resolution 2025-02 match (including common spacing/hyphen variants). The receipt's separately retained text likewise has a verified hash. This is a text-extraction finding about this identified compilation, subject to extraction limitations; it neither proves that no other instrument exists nor establishes the content or termination of a separate instrument. The existence of later general zoning and its date statements do not establish that phase two ended or that the relevant standards were adopted.

## Original May 6 record and remaining gap

The actual [May 6, 2025 commission minutes](https://olivercountynd.org/index.asp?SEC=B1B18045-A2A7-4C31-8160-D9E9D255E81C), HTML body lines 1809–1826, retained text lines 243–277, record a 2–1 carried motion approving the two moratoriums for 90 days. The minutes then reproduce the separate solar Resolution 2025-03 and the data-center and cryptocurrency Resolution 2025-02. The latter's operative text instead describes the period necessary to develop and adopt applicable standards and conditions effectiveness on recording and publication. Both observations are in the same original body; the compilation supplies no evidence reconciling them. The solar resolution cannot supply phase two's operative anchor or endpoint.

The new PDF is a zoning compilation, not an independently executed copy of Resolution 2025-02 or evidence that it was recorded and published. The outstanding evidence remains the executed final resolution and any amendments, recording and publication proof and dates, and relevant intervening county actions or standards sufficient to establish the operative interval and later stage. Neither the minutes' reproduction nor this compilation verifies those events. This review makes no claim that the moratorium remains in force or expired at any particular time.

## Verification and provenance

All hashes below are SHA-256, independently computed from retained files, and match the three new receipts. The text hashes are the retained `.private.txt` bytes, not substitutes for body hashes.

| Source | Body SHA-256 | Retained text SHA-256 | Locator |
|---|---|---|---|
| County index | `79d7079a76fbc1b0e3ae71fdc0a07f9d1ee137eda13ca8d3fec73bce25f8a781` | `4aa12cc13a91f67f50a708b4cdaeaf40af860537fb8ab27f9b5f5aa7454c2b82` | Child navigation link |
| Ordinance page | `5ebb746ac8c72011046a509b5bed2e1bc2beccc6401659b8ad5d820646089b26` | `a8d088a6e729ef409da448dd078817e216f10b2c29bbd041837deb8c10bd2113` | Document link |
| Zoning PDF | `53e8407cfaed161026a3c8cafc78bdef9c3ad85533756aee14b67598298572e4` | `2918989f0e171e57b14e8435be632b08f4484f39d52be9e9e9b6e21b2eb27cc3` | Physical pages 1, 10–11, 103 |
| May 6 minutes | `9e6d9ef7fcf27e8eaf05af1dc6bcca5d726bebba45eda9b4f2d65d1b6ce20a5d` | `c3a1bbc2d0c5d98ba053945c25a90ec3c35a63bc48b501d564b43092001b15cf` | Body lines 1809–1826; text lines 243–277 |

The local layout extraction SHA-256 is `ac64fe84d169f30f332123c49e5487cafd84acfd795d93e3cc7a7c24015fecaf`; rerunning `pdftotext -layout` on the verified PDF produced identical bytes. Inventory file SHA at review was `04307f453bb7ee3a36cfde8d8ac07487ab7a8ab8a3f17eeaa71dc878e5d96a70`; prior report SHA was `b0461ec50c688d4722d96ab22edb4934e456e90c27fac8c9c2d07a097346f353`. These are review-time identifiers, not write authorization. The review was limited to the specified row, prior report, receipts and their exact artifacts, and original minutes. No network, API, canonical, Git, store, or other source search was used.
