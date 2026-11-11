"""Build the local-record browser from the complete published inventory."""
import csv
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def write_explorer_data():
    with (ROOT / 'data/moratorium_inventory.csv').open(newline='') as source:
        rows = list(csv.DictReader(source))
    (ROOT / 'site/moratoria-records.json').write_text(json.dumps(rows, ensure_ascii=False) + '\n')

def explorer():
    return '''<section class="record-explorer" id="explore" aria-labelledby="explore-title">
  <h2 id="explore-title">Explore local moratoria</h2>
  <p>Search all local records, including those without map coordinates. Status describes the recorded action; check the details for dates and unresolved questions. State policies and ballot measures have separate trackers.</p>
  <p><a href="data/moratorium_inventory.csv" download>Download the complete local inventory (CSV)</a></p>
  <div id="explorer-app" hidden>
    <div class="explorer-filters">
      <label>Search records<input id="record-search" type="search" placeholder="Place, project, ordinance, or keyword"></label>
      <label>State<select id="record-state"><option value="">All states</option></select></label>
      <label>Sector<select id="record-sector"><option value="">All sectors</option></select></label>
      <label>Recorded status<select id="record-status"><option value="">All statuses</option></select></label>
    </div>
    <div class="explorer-actions"><button type="button" id="record-reset">Clear filters</button><button type="button" id="record-export">Export matching records (CSV)</button><span id="record-count" role="status" aria-live="polite"></span></div>
    <div class="record-table-scroll" tabindex="0" role="region" aria-label="Moratorium records; scroll horizontally for more columns">
      <table class="record-table"><caption>Local moratorium records. Select a column heading to sort.</caption><thead><tr>
        <th scope="col" aria-sort="ascending"><button data-sort="jurisdiction" type="button">Place ↕</button></th>
        <th scope="col"><button data-sort="state" type="button">State ↕</button></th>
        <th scope="col"><button data-sort="sectors" type="button">Sector ↕</button></th>
        <th scope="col"><button data-sort="enacted_status" type="button">Recorded status ↕</button></th>
        <th scope="col"><button data-sort="date_enacted_iso" type="button">Listed enactment date ↕</button></th>
        <th scope="col">Details</th>
      </tr></thead><tbody id="record-rows"></tbody></table>
    </div>
    <div class="explorer-actions"><button type="button" id="record-prev">Previous</button><span id="record-page"></span><button type="button" id="record-next">Next</button></div>
  </div>
  <p id="explorer-message">Loading the record browser. The complete CSV is also available above.</p>
  <noscript><p>Enable JavaScript to search and filter records here, or browse <a href="states/index.html">records by state</a>.</p></noscript>
</section>'''
