"""Verify an explicit coordinator visual transcription against retained PDF bytes.

This reproduces the reviewed rendering, not the human/agent visual judgement.
It never certifies an election or accepts a legal-effect claim.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def digest(raw):return hashlib.sha256(raw).hexdigest()


def render_hash(body,page,dpi):
    with tempfile.TemporaryDirectory(prefix='ballot-visual-review-') as tmp:
        target=Path(tmp)/'page'
        subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r',str(dpi),
            '-singlefile','-png',str(body),str(target)],check=True,capture_output=True,timeout=30)
        return digest(target.with_suffix('.png').read_bytes())


def verify(claim,source,index,review):
    if review.get('disposition')!='accepted_visual_values' or review.get('reviewer')!='coordinator':
        raise ValueError('Visual review is not explicitly accepted transcription')
    if (digest(json.dumps(claim,sort_keys=True,separators=(',',':')).encode())!=review['claim_sha256']
        or claim['claim_id']!=review['claim_id'] or claim['source_document_id']!=review['source_document_id']
        or source['source_document_id']!=review['source_document_id'] or claim['value']!=review['values']):
        raise ValueError('Visual claim drift or wrong target')
    if source['body_sha256']!=review['source_body_sha256']:
        raise ValueError('Visual source body hash mismatch')
    params=review['render_parameters']
    if params['renderer']!='pdftoppm' or params['page']!=review['pdf_page'] or not 1<=params['page']<=1000 or not 36<=params['dpi']<=300:
        raise ValueError('Unsupported visual rendering parameters')
    for version in index.get(source['url'],[]):
        if version['body_sha256']!=source['body_sha256'] or not version.get('body_artifact'):continue
        body=Path(version['body_artifact'])
        if digest(body.read_bytes())!=source['body_sha256']:continue
        if render_hash(body,params['page'],params['dpi'])!=review['render_sha256']:
            raise ValueError('Reviewed rendering could not be reproduced')
        return True
    raise ValueError('Retained reviewed PDF body unavailable or drifted')
