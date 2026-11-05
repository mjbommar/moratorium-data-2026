#!/usr/bin/env python3
"""Replay verified pilot bytes/claims into bc-store and bc-evidence, without network.

Source assertions remain unscored and partial. Importing located excerpts does not
mark any document fully extracted or any legal/electoral proposition accepted.
"""
import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'work/research/2026-11-05'


def index(store_path, evidence_path):
    from bc_store import Store
    from bc_evidence.db import EvidenceDB
    bodies={};texts={}
    for lane in ['maine-pilot','ohio-pilot']:
        for p in (BASE/lane).glob('*.private*'):
            if p.suffix not in ['.pdf','.html','.body','.bin','.txt']:continue
            raw=p.read_bytes();bodies.setdefault(hashlib.sha256(raw).hexdigest(),raw)
            if p.suffix in ['.txt','.html','.body','.bin']:
                try: text=p.read_text()
                except UnicodeDecodeError: continue
                texts.setdefault(hashlib.sha256(text.encode()).hexdigest(),text)
    normalized=BASE/'normalized-pilot'
    sources=[json.loads(x) for x in (normalized/'source_documents.jsonl').read_text().splitlines()]
    claims=defaultdict(list)
    for line in (normalized/'claims.jsonl').read_text().splitlines():
        c=json.loads(line);claims[c['source_document_id']].append(c)
    # Verify every required source before opening a writable database.
    for s in sources:
        if s['body_sha256'] not in bodies or s['text_sha256'] not in texts:
            raise ValueError('Missing verified payload/text for '+s['source_document_id'])
    receipt=[]
    with Store(store_path) as store, EvidenceDB(evidence_path) as db:
        for s in sources:
            timestamp=dt.datetime.fromisoformat(s['retrieved_at'].replace('Z','+00:00')).timestamp()
            src=store.upsert_source(s['url'],s['url'],at=timestamp)
            obs=store.record(src,payload=bodies[s['body_sha256']],payload_sha256=s['body_sha256'],
                at=timestamp,original_source_document_id=s['source_document_id'],
                observation_scope='Replay of prior archived retrieval; not a fresh HTTP request')
            text=texts[s['text_sha256']]
            store.derive(obs,'text',text=text,producer='moratorium-pilot-normalized-text-v1')
            sid=s['source_document_id']
            db.add_document(doc_id=sid,url=s['url'],final_url=s['url'],text=text,words=len(text.split()),
                            kind='pilot-archived-source',fetch_observation=obs.id,
                            published=None,extract_error='Partial scoped pilot import; full extraction pending')
            rows=[]
            for c in claims[sid]:
                _,a,b=c['span'].split(':');a,b=int(a),int(b)
                if text[a:b]!=c['quote']:raise ValueError('Quote drift: '+c['claim_id'])
                rows.append(dict(claim_id=c['claim_id'],cell_ids=[],text=json.dumps(c['value'],ensure_ascii=False),
                    claim_type='source_assertion',stance='asserted',quote=c['quote'],char_start=a,char_end=b,
                    verified=True,date_supported=None,subject=c['subject']['id'],predicate=c['predicate'],
                    confidence=0.0,extractor_model='gpt-6.1-terra CLI + deterministic span import; unscored'))
            db.put_claims(sid,rows,relevance=0.0,summary='Scoped pilot excerpts only; unscored, no legal acceptance.',
                          error='Partial scoped pilot import; full extraction pending')
            # put_claims normally closes extraction; this import has read only scoped excerpts.
            db.conn.execute('UPDATE documents SET extracted_at=NULL WHERE doc_id=?',(sid,))
            receipt.append({'source_document_id':sid,'observation_id':obs.id,
                            'body_sha256':obs.payload_sha256,'text_sha256':s['text_sha256'],'claims':len(rows)})
        counts={'documents':len(db.q('SELECT doc_id FROM documents')),'claims':len(db.q('SELECT claim_id FROM claims')),
                'fully_extracted_documents':len(db.q('SELECT doc_id FROM documents WHERE extracted_at IS NOT NULL'))}
    return {'store':str(store_path),'evidence_db':str(evidence_path),'sources':receipt,'counts':counts,
            'limitations':['No network request or model call performed.','Confidence/relevance0 are unscored storage placeholders, not calibrated probabilities.','Verified means quote located; no substantive acceptance or complete-document extraction.']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--store',type=Path,required=True);p.add_argument('--evidence-db',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args();r=index(a.store,a.evidence_db);a.receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['counts']))
