"""Verify an explicit coordinator visual transcription against retained PDF or native PNG bytes.

This reproduces the reviewed rendering, not the human/agent visual judgement.
It never certifies an election or accepts a legal-effect claim.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import struct
import zlib
import tempfile


def digest(raw):return hashlib.sha256(raw).hexdigest()


def render_hash(body,page,dpi):
    with tempfile.TemporaryDirectory(prefix='ballot-visual-review-') as tmp:
        target=Path(tmp)/'page'
        subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-r',str(dpi),
            '-singlefile','-png',str(body),str(target)],check=True,capture_output=True,timeout=30)
        return digest(target.with_suffix('.png').read_bytes())


def png_dimensions(raw):
    """Check PNG container integrity/dimensions without transforming source pixels."""
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Native image is not PNG')
    offset=8; dimensions=None; data_seen=False
    while offset+12 <= len(raw):
        length=struct.unpack('>I',raw[offset:offset+4])[0]
        end=offset+12+length
        if end>len(raw):break
        kind=raw[offset+4:offset+8]; payload=raw[offset+8:end-4]
        crc=struct.unpack('>I',raw[end-4:end])[0]
        if zlib.crc32(kind+payload)&0xffffffff != crc:
            raise ValueError('Native PNG chunk checksum mismatch')
        if dimensions is None:
            if kind!=b'IHDR' or length!=13:
                raise ValueError('Native PNG header missing')
            dimensions=struct.unpack('>II',payload[:8])
            if not all(0<n<=100000 for n in dimensions):
                raise ValueError('Unsupported native PNG dimensions')
        elif kind==b'IHDR':
            raise ValueError('Duplicate native PNG header')
        if kind==b'IDAT':data_seen=True
        if kind==b'IEND':
            if length or end!=len(raw) or not data_seen:
                raise ValueError('Invalid native PNG ending')
            return dimensions
        offset=end
    raise ValueError('Truncated native PNG container')


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
    native=params.get('renderer')=='native-png'
    if native:
        if (set(params)!={'renderer','width','height'} or review.get('pdf_page') is not None
            or any(type(params[k]) is not int or params[k]<=0 for k in ['width','height'])):
            raise ValueError('Unsupported native PNG review parameters')
    elif (params.get('renderer')!='pdftoppm' or params['page']!=review['pdf_page']
          or not 1<=params['page']<=1000 or not 36<=params['dpi']<=300):
        raise ValueError('Unsupported visual rendering parameters')
    for version in index.get(source['url'],[]):
        if version['body_sha256']!=source['body_sha256'] or not version.get('body_artifact'):continue
        body=Path(version['body_artifact'])
        raw=body.read_bytes()
        if digest(raw)!=source['body_sha256']:continue
        if native:
            if png_dimensions(raw)!=(params['width'],params['height']):
                raise ValueError('Native PNG dimensions differ from reviewed source')
            if review['render_sha256']!=source['body_sha256']:
                raise ValueError('Native PNG review must pin original untransformed bytes')
            return True
        if render_hash(body,params['page'],params['dpi'])!=review['render_sha256']:
            raise ValueError('Reviewed rendering could not be reproduced')
        return True
    raise ValueError('Retained reviewed source body unavailable or drifted')
