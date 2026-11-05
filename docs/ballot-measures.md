# Reviewed ballot records: scope and interpretation

The [generated results view](ballot-results.md) follows the pinned canonical
publication. It is a reviewed subset, not the complete November election census.
Each displayed row is a current result observation, and multiple observations of
one measure remain separate. Blank, other-vote and turnout categories are not
filled with zero when the source omits them.

The November 5 initial cohorts cover Eliot Question 5 and Sabattus's Data Center
Moratorium question at the November 3, 2026 elections. Both questions ask enactment
of a temporary ordinance. Their bindingness and restrictive yes direction describe
the proposed mechanism; neither is a finding of present enforceability.
[Official Eliot sample ballot](https://www.eliotme.gov/DocumentCenter/View/3950/Sample-Ballot---Town-PDF),
[official Sabattus sample ballot](https://storage.googleapis.com/juniper-media-library/571/2026/10/Nov%202026%20Sabattus%20Sample%20Ballot.pdf).

The signed returns certify the respective counts. Sabattus's clerk certifies on
November 4; the return omits total ballots and blank votes. Eliot's moderator return
is dated November 3 and reports blanks and total ballots separately. Certification
of election results remains distinct from certification or implementation of an
ordinance.
[Eliot return, PDF page 3](https://www.eliotme.gov/DocumentCenter/View/3997/Election-Results-November-3-2026---Eliot-Maine-PDF),
[Sabattus clerk return](https://storage.googleapis.com/juniper-media-library/571/2026/11/Sabattus%20-%20Clerk%20Return%20of%20Votes%20-%20Municipal%20Election.pdf).

A separate secondary report supplies reported approval for both questions. The
canonical records distinguish that reported outcome from a calculated passage rule.
No denominator, threshold or legal passage rule is invented from vote arithmetic.
The earlier Eliot official-source-only observation remains unchanged; an explicit
successor adds the reported approval. Supersession removes the earlier observation
from the current view, not from history.
[Secondary approval report](https://www.bangordailynews.com/2026/11/05/politics/elections/maine-election-towns-temporary-data-center-bans/).

Eliot's proposed ordinance specifies 180 days from effectiveness and an accessory
server-equipment exception. Paragraph 5 refers both to voter enactment and seven
days after adoption. Sabattus's question summarizes a nominal May 2, 2027 endpoint
(180 days), subject to extension or repeal by municipal officers; its operative
mechanism/definition, applicability and effective-date clauses require ordinance
review. The question summary is not substituted for executed operative text.
[Eliot official proposed text](https://www.eliotme.gov/DocumentCenter/View/3909/Ballot-Question-5----Proposed-Ordinance---Data-Center-Moratorium-PDF).

No current legal-force restriction, instrument event or measure/instrument link has
been accepted in these initial cohorts, and their publication does not add active
legacy moratorium rows. Other jurisdictions, earlier and future elections, legal
implementation, passage rules and the full freshness accounting remain work in progress.

Canonical tables are available at `data/expanded/<table>.jsonl` in a checkout.
Resolve the directory once when reading several tables. The immutable
[first Eliot snapshot](../data/expanded-snapshots/0d3783df2c0d66dabd7c36163910b9dfd4d88a6ff056032735975f97bb7fa906/publication.json)
and [Sabattus/result-update snapshot](../data/expanded-snapshots/7b960c58dd52c2f643647e306616966d4590a652c0b9caf11c108ea2edc3f421/publication.json)
preserve the exact tables, source versions and publication plans. Visual source
review is not a claim of full-document extraction coverage.

The [Sabattus review packet](../work/research/2026-11-05/sabattus-promotion/publication-plan.json) and
[publication receipt](../work/audit/sabattus-canonical-publication-2026-11-05.json)
record local publication. The [replay receipt](../work/audit/sabattus-canonical-replay-2026-11-05.json)
and [offline consistency check](../work/audit/sabattus-publication-consistency-2026-11-05.json)
validate retained publication behavior; they do not reacquire sources or establish
current legal force. GitHub release, full public exports, remaining measures and
consumer updates retain the separate release gates.
