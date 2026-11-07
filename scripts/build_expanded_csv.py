#!/usr/bin/env python3
"""Derive versioned CSV downloads from one reviewed expanded generation."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from uuid import uuid4

from expanded_data import IDS, SCHEMA, profile_path
from expanded_promotion import fingerprint, read_snapshot, sealed_generation

ROOT = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def render_table(table, records, schema, id_field=None):
    properties = schema['$defs'][table]['properties']
    key=id_field or IDS[table]
    columns = ['schema_version', key, *sorted(set(properties) - {'schema_version', key})]
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(columns)
    for record in sorted(records, key=lambda row: row[key]):
        if set(record) - set(columns):
            raise ValueError('CSV would omit unknown fields: ' + table)
        cells = []
        for column in columns:
            value = record.get(column)
            if value is None:
                cells.append('')
            elif isinstance(value, str):
                cells.append(value)
            else:
                cells.append(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                       separators=(',', ':'), allow_nan=False))
        writer.writerow(cells)
    return stream.getvalue().encode('utf-8'), columns


def current_results(records):
    by_id = {row['result_observation_id']: row for row in records}
    if len(by_id) != len(records):
        raise ValueError('Duplicate result observation ID')
    superseded = set()
    for key in by_id:
        seen = set()
        cursor = key
        while cursor is not None:
            if cursor in seen:
                raise ValueError('Cyclic result supersession')
            if cursor not in by_id:
                raise ValueError('Missing superseded result')
            seen.add(cursor)
            parent = by_id[cursor]['supersedes_id']
            if parent is not None:
                superseded.add(parent)
            cursor = parent
    return [row for key, row in by_id.items() if key not in superseded]


def build_outputs(snapshot):
    snapshot=snapshot.resolve(strict=True)
    from check_expanded_publication import check
    data_root=snapshot.parent.parent
    check(data_root/'expanded',data_root/'identities/expanded.jsonl',
          data_root/'moratorium_inventory.csv',data_root/'state_legislation.csv',generation_path=snapshot)
    raw = read_snapshot(snapshot)
    generation = fingerprint(raw)
    receipt_bytes = (snapshot / 'publication.json').read_bytes()
    receipt = json.loads(receipt_bytes)
    if receipt['sha256'] != generation:
        raise ValueError('Expanded generation does not match its publication fingerprint')
    profile=receipt['plan'].get('validation_profile',{}).get('name','1.0.0')
    if profile=='1.0.2':
        from expanded_promotion import validate_plan
        validate_plan(receipt['plan'])
    schema_bytes = (profile_path(profile) if profile=='1.0.2' else SCHEMA).read_bytes()
    schema = json.loads(schema_bytes)
    records = {name: [json.loads(line) for line in body.decode('utf-8').splitlines()]
               for name, body in raw.items()}
    outputs = {}
    files = {}
    views = [(name, name, records[name],name,None) for name in IDS]
    views.append(('measure_results_current', 'measure_results', current_results(records['measure_results']),'measure_results',None))
    if profile=='1.0.2':
        from instrument_event_maintenance import inspect
        state=inspect({name:{r[IDS[name]]:r for r in values} for name,values in records.items()})
        views.append(('instrument_events_current','instrument_events',state['current_events'],'instrument_events',None))
        statuses=[{'schema_version':'1.0.0',**r} for r in state['statuses']]
        views.append(('instrument_event_status','instrument_event_status',statuses,'instrument_events','event_id'))
    for name, table, rows, source_table, id_field in views:
        body, columns = render_table(table, rows, schema,id_field)
        filename = name + '.csv'
        outputs[filename] = body
        files[filename] = {'sha256': sha(body), 'rows': len(rows), 'columns': columns,
                           'source_table': source_table}
    manifest = {'schema_version': '1.0.0', 'source_snapshot': snapshot.name,
                'source_publication_sha256': sha(receipt_bytes), 'schema_sha256': sha(schema_bytes),
                'generator_sha256': sha(Path(__file__).read_bytes()),
                'source_tables': {name + '.jsonl': sha(body) for name, body in sorted(raw.items())},
                'files': files,
                'encoding': {'charset': 'UTF-8', 'line_ending': 'LF', 'null_or_absent': 'empty cell',
                             'strings': 'literal text with CSV quoting',
                             'numbers_and_booleans': 'JSON scalar spelling',
                             'objects_and_arrays': 'compact JSON within a CSV cell'},
                'scope': 'Derived convenience views, not authoritative records or new evidence acceptance. '
                         'JSONL preserves null versus empty strings and absent fields. Current results '
                         'exclude explicitly superseded observations only; separate reporting scopes are retained.'}
    if profile=='1.0.2':
        manifest['validation_profile']=receipt['plan']['validation_profile']
        manifest['source_table_snapshot_sha256']=generation
        manifest['event_views']={'retained':'instrument_events.csv','current_accepted':'instrument_events_current.csv','status':'instrument_event_status.csv','meaning':'Review-state acceptance, not current legal force. Retained rows include withdrawn history.'}
    outputs['manifest.json'] = (json.dumps(manifest, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    return fingerprint(outputs), outputs


def verify_generation(directory, outputs):
    if directory.is_symlink() or not directory.is_dir() or {p.name for p in directory.iterdir()} != set(outputs):
        raise ValueError('CSV projection file set differs')
    for name, body in outputs.items():
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.read_bytes() != body:
            raise ValueError('CSV projection differs: ' + name)


def publish(data_root, generation, outputs, check=False):
    pointer = data_root / 'expanded-csv'
    generations = data_root / 'expanded-csv-snapshots'
    target = generations / generation
    if check:
        if not pointer.is_symlink() or pointer.readlink().is_absolute() or pointer.resolve() != target.resolve():
            raise ValueError('CSV pointer does not match the current expanded generation')
        verify_generation(target, outputs)
        return 'matches'
    generations.mkdir(parents=True, exist_ok=True)
    if target.exists():
        verify_generation(target, outputs)
    else:
        with tempfile.TemporaryDirectory(prefix='.csv-', dir=generations) as temp:
            staging = Path(temp) / 'generation'
            staging.mkdir()
            for name, body in outputs.items():
                (staging / name).write_bytes(body)
            staging.rename(target)
    if pointer.exists() and not pointer.is_symlink():
        raise ValueError('Refusing to replace a CSV directory or regular file')
    relative = Path('expanded-csv-snapshots') / generation
    temporary = data_root / ('.expanded-csv-' + uuid4().hex)
    try:
        temporary.symlink_to(relative)
        os.replace(temporary, pointer)
    finally:
        temporary.unlink(missing_ok=True)
    return 'generated'


def download_block(generation, outputs):
    manifest = json.loads(outputs['manifest.json'])
    prefix = 'expanded-csv-snapshots/' + generation + '/'
    lines = ['<!-- BEGIN EXPANDED CSV DOWNLOADS -->',
             '| CSV view | Records |', '|---|---:|']
    for filename, metadata in sorted(manifest['files'].items()):
        lines.append(f"| [{filename}]({prefix}{filename}) | {metadata['rows']} |")
    lines += ['', f"[Projection manifest]({prefix}manifest.json) pins the source generation, schema, exporter and every file hash.",
              '<!-- END EXPANDED CSV DOWNLOADS -->']
    return '\n'.join(lines)


def sync_download_links(readme, generation, outputs, check=False):
    text = readme.read_text()
    begin = '<!-- BEGIN EXPANDED CSV DOWNLOADS -->'
    end = '<!-- END EXPANDED CSV DOWNLOADS -->'
    if text.count(begin) != 1 or text.count(end) != 1:
        raise ValueError('Data README needs one CSV download block')
    first = text.index(begin)
    last = text.index(end, first) + len(end)
    expected = text[:first] + download_block(generation, outputs) + text[last:]
    if check:
        if expected != text:
            raise ValueError('Data README CSV links or counts differ')
    else:
        readme.write_text(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    snapshot = (ROOT / 'data/expanded').resolve(strict=True)
    generation, outputs = build_outputs(snapshot)
    state = publish(ROOT / 'data', generation, outputs, args.check)
    sync_download_links(ROOT / 'data/README.md', generation, outputs, args.check)
    print(json.dumps({'state': state, 'source_snapshot': snapshot.name, 'projection_sha256': generation, 'csv_views': len(outputs) - 1}))


if __name__ == '__main__':
    main()
