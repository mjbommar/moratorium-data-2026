# End-date screening correction

The validator previously ignored `current_end_date_iso` when testing active rows. It added original `duration_days` to the original adoption date and called that result an expiry. Lodi therefore reappeared as an expired-term candidate despite its already recorded August successor and conditional February 2027 outer endpoint. The research worklist already preferred the recorded endpoint, but its question incorrectly described screening arithmetic as proof that the original term had ended.

The validator now prefers a recorded current endpoint and screens an extended record when that endpoint has passed. It does not reuse the original term for an extension with no recorded endpoint. Original adoption-plus-days arithmetic remains a screening tool; both validator warnings and worklist questions explicitly require effective-anchor and later-action review. Invalid current endpoints remain errors and do not silently fall back to old arithmetic.

Four regression tests cover the Lodi successor, a past extension endpoint, qualified arithmetic, and an invalid endpoint. Four native sparse-worklist tests also pass. Actual inventory warnings change only from ten to nine status screening flags: Lodi is removed. The 545 calendar-end and 61 missing-date warnings are unchanged. Dataset values, legal dispositions, review closures and public post7 delivery are unchanged. This tooling change will travel with the next source release.

Springfield was read back without network requests: its record already schedules the proposed extension vote for November 16, a future date at this review. No outcome was inferred or duplicate October 23 document fetch performed.
