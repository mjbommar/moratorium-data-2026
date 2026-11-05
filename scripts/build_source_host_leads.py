#!/usr/bin/env python3
"""Build source-qualified jurisdiction host leads from existing research evidence.

These are retrieval leads, not assertions that a host is current or that a legal
claim was correct. Models should discover hosts from these records rather than
inventing municipality domains from names.
"""
from collections import defaultdict
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
PRIMARY={'ordinance','resolution','minutes','agenda','staff_report','court_filing','legislature'}


def build():
    leads=defaultdict(dict)
    for path in sorted((ROOT/'work/answers').rglob('*.json')):
        try: data=json.loads(path.read_text())
        except (ValueError,UnicodeError):continue
        if not isinstance(data,dict):continue
        for row in data.get('decisions',[]):
            mid=row.get('moratorium_id')
            if not mid:continue
            for ev in row.get('evidence',[]):
                if ev.get('source_type') not in PRIMARY:continue
                url=ev.get('url','');host=urlsplit(url).hostname
                if not host:continue
                entry=leads[mid].setdefault(url,{'host':host,'url':url,'source_type':ev['source_type'],'answer_files':[]})
                name=str(path.relative_to(ROOT))
                if name not in entry['answer_files']:entry['answer_files'].append(name)
    return {'status':'source-qualified retrieval leads; current host ownership/authority not independently reverified',
            'records':{mid:sorted(items.values(),key=lambda x:x['url']) for mid,items in sorted(leads.items())}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=build();a.output.write_text(json.dumps(result,indent=2)+'\n')
    print('IDs with primary-source host leads:',len(result['records']))
