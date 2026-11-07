# Typed inventory appendix rendering

The appendix table now reads recorded original-duration and sector fields. It no longer picks an extension fragment from prose or classifies wind coverage from a place name such as Irwindale. A comparison found 179 rows where the prior prose-sector heuristic disagreed with canonical sector arrays; all 1,330 current rows now follow the recorded arrays. Only the first three sectors are displayed, as labelled. This corrects presentation, not the underlying legal evidence.

Fixed original days display only a valid recorded integer. Calendar, date-limited, event-based, indefinite and unknown terms stay distinct; calendar terms are not converted to guessed days. Conditions and full terms remain in the CSV. The table explicitly warns that recorded legacy values may remain unverified. Instrument form remains a labelled heuristic.

The ordinary data target regenerates the table, and the check target rejects a stale table. Regression tests cover original 45 versus extension 15, calendar/unknown terms, incidental prose/place names, and missing/invalid sector metadata. See reconciliation.json for the exact pre-heuristic/canonical comparison and source fingerprint.
