(function () {
  'use strict';
  var app = document.getElementById('explorer-app');
  if (!app) return;
  var search = document.getElementById('record-search');
  var filters = ['state', 'sector', 'status'].map(function (key) { return document.getElementById('record-' + key); });
  var rows = [], matches = [], page = 0, size = 25, sort = 'jurisdiction', direction = 1;
  var labels = {data_center:'Data centers', battery_storage:'Battery storage', solar:'Solar', wind:'Wind', cryptocurrency_mining:'Cryptocurrency mining', cryptocurrency:'Cryptocurrency mining', crypto:'Cryptocurrency mining'};
  function sectors(row) { try { return JSON.parse(row.sectors || '[]'); } catch (_) { return []; } }
  function label(value) { return labels[value] || value.replace(/_/g, ' ').replace(/^./, function(c) { return c.toUpperCase(); }); }
  function cell(tr, text) { var td = document.createElement('td'); td.textContent = text; tr.appendChild(td); return td; }
  function render() {
    var query = search.value.toLocaleLowerCase().trim();
    matches = rows.filter(function (row) {
      return (!query || row._search.includes(query)) && (!filters[0].value || row.state === filters[0].value) &&
        (!filters[1].value || sectors(row).includes(filters[1].value)) && (!filters[2].value || row.enacted_status === filters[2].value);
    });
    matches.sort(function (a,b) { return direction * String(a[sort] || '').localeCompare(String(b[sort] || ''), 'en', {numeric:true}) || a.moratorium_id.localeCompare(b.moratorium_id); });
    page = Math.min(page, Math.max(0, Math.ceil(matches.length / size) - 1));
    var body = document.getElementById('record-rows'); body.replaceChildren();
    matches.slice(page * size, (page + 1) * size).forEach(function (row) {
      var tr = document.createElement('tr');
      cell(tr, row.jurisdiction); cell(tr, row.state); cell(tr, sectors(row).map(label).join(', ') || 'Unspecified'); cell(tr, label(row.enacted_status || 'unknown'));
      cell(tr, row.date_enacted_iso || 'Not established');
      var td = cell(tr, ''), details = document.createElement('details'), summary = document.createElement('summary');
      summary.textContent = 'Read record'; details.appendChild(summary);
      [['Record ID','moratorium_id'], ['Listed enactment date and qualifications','date_enacted'], ['Date uncertainty','date_enacted_uncertainty'], ['Recorded status','current_status'], ['Duration','duration'], ['Legal basis','legal_basis'], ['Reason for action','trigger'], ['Affected projects and exceptions','affected_projects'], ['Outcome','outcome']].forEach(function (field) {
        if (!row[field[1]]) return;
        var p = document.createElement('p'), strong = document.createElement('strong'); strong.textContent = field[0] + ': '; p.appendChild(strong); p.appendChild(document.createTextNode(row[field[1]])); details.appendChild(p);
      });
      var link = document.createElement('a'); link.href = 'states/' + row.state.toLowerCase().replace(/\s+/g, '-') + '.html'; link.textContent = 'Open state records and sources'; details.appendChild(link); td.appendChild(details); body.appendChild(tr);
    });
    if (!matches.length) { var tr = document.createElement('tr'), td = cell(tr, 'No records match these filters.'); td.colSpan = 6; body.appendChild(tr); }
    document.getElementById('record-count').textContent = matches.length.toLocaleString() + ' of ' + rows.length.toLocaleString() + ' records';
    document.getElementById('record-page').textContent = matches.length ? 'Page ' + (page + 1) + ' of ' + Math.ceil(matches.length / size) : 'No results';
    document.getElementById('record-prev').disabled = page === 0;
    document.getElementById('record-next').disabled = (page + 1) * size >= matches.length;
    document.getElementById('record-export').disabled = !matches.length;
    document.querySelectorAll('[data-sort]').forEach(function (button) { var th = button.parentElement; th.removeAttribute('aria-sort'); if (button.dataset.sort === sort) th.setAttribute('aria-sort', direction === 1 ? 'ascending' : 'descending'); });
  }
  search.addEventListener('input', function () { page = 0; render(); });
  filters.forEach(function (filter) { filter.addEventListener('change', function () { page = 0; render(); }); });
  document.querySelectorAll('[data-sort]').forEach(function (button) { button.addEventListener('click', function () { direction = sort === button.dataset.sort ? -direction : 1; sort = button.dataset.sort; page = 0; render(); }); });
  document.getElementById('record-prev').onclick = function () { page--; render(); };
  document.getElementById('record-next').onclick = function () { page++; render(); };
  document.getElementById('record-reset').onclick = function () { search.value = ''; filters.forEach(function(f) { f.value = ''; }); page = 0; render(); };
  document.getElementById('record-export').onclick = function () {
    var keys = Object.keys(rows[0]).filter(function (key) { return key !== '_search'; });
    function escape(value) { value = String(value == null ? '' : value); if (/^[\s]*[=+@-]/.test(value) && !/^-?\d+(\.\d+)?$/.test(value)) value = "'" + value; return '"' + value.replace(/"/g, '""') + '"'; }
    var csv = [keys.map(escape).join(',')].concat(matches.map(function(row) { return keys.map(function(key) { return escape(row[key]); }).join(','); })).join('\r\n');
    var url = URL.createObjectURL(new Blob(['\ufeff' + csv + '\r\n'], {type:'text/csv;charset=utf-8'}));
    var a = document.createElement('a'); a.href = url; a.download = 'moratoria-filtered.csv'; a.click(); setTimeout(function() { URL.revokeObjectURL(url); }, 1000);
  };
  fetch('site/moratoria-records.json').then(function (response) { if (!response.ok) throw new Error('Could not load records'); return response.json(); }).then(function (data) {
    rows = data;
    rows.forEach(function(row) { row._search = Object.values(row).join(' ').toLocaleLowerCase(); });
    [rows.map(function(r) { return r.state; }), rows.flatMap(sectors), rows.map(function(r) { return r.enacted_status; })].forEach(function(values, index) {
      Array.from(new Set(values)).filter(Boolean).sort().forEach(function(value) { var option = document.createElement('option'); option.value = value; option.textContent = index ? label(value) : value; filters[index].appendChild(option); });
    });
    app.hidden = false; document.getElementById('explorer-message').hidden = true; render();
  }).catch(function () { document.getElementById('explorer-message').textContent = 'The record browser could not load. Download the complete CSV above or browse records by state.'; });
})();
