# Alabama session and history followup

Two guarded status narratives now identify the official April 9, 2026 regular-session adjournment date and November 9 re-observation of the returned action lists. No stage, legal-effect or last-action date changes, and neither record is closed.

The fresh official GraphQL response returns nine HB403 and 22 SB265 history entries, matching the earlier observed counts and latest actions. The result type is `InstrumentHistorysResults`, but the response contains no completeness/page metadata. A separate schema query was rejected because introspection is disabled; the HTTP 200 error response is not factual bill evidence and remains private attempt metadata. Public client retrieval did not establish the history query’s pagination contract. No complete-history claim follows from matching counts.

The official Legislature site explicitly identifies the regular session as adjourned April 9. Its linked current status-sheet PDF instead identifies **2026 First Special Session**, generated May 8, and contains no HB403/SB265 observations. That is a different session, not proof that either regular-session bill failed. The historic House report index links April 9 / 2026RS / legislative day 30 to `H-R1-30.pdf`. The actual one-page PDF says there were no House first readings that day. It is a first-readings report, not a complete journal or final-action record.

The official glossary defines adjournment sine die as final termination of a session; its legislative-process page describes bill passage and gubernatorial handling. Neither capture establishes a named terminal disposition for these two bills. Preserve unknown categories rather than treating the general explanation as a complete bill-specific history.

The current [adjudications](alabama-session-adjudications.json) retain procedural completeness and terminal questions, and also expose unresolved sponsor-party, companion-identity and separate-substitute questions already present in canonical prose. Their absence from the older flat question index did not make them resolved. No new contrary factual claim is added.

[Source clocks and hashes](alabama-session-sources.json) and the [exact cell application](alabama-session-field-application.json) preserve the successful source observations. Unused scripts and rejected schema results are retained privately. All IDs, local records, ballot observations, scope partitions and disposition counts are unchanged.
