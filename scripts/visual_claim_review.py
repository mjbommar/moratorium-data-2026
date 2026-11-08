"""Verify an explicit coordinator visual transcription against retained PDF or native PNG/JPEG bytes.

This reproduces the reviewed rendering, not the human/agent visual judgement.
It never certifies an election or accepts a legal-effect claim.
"""
import hashlib
from contextlib import contextmanager
from contextvars import ContextVar
import io
import json
from pathlib import Path
import shutil
import subprocess
import struct
import zlib
import tempfile

_render_cache=ContextVar('visual_render_cache',default=None)
_renderer_path=ContextVar('visual_renderer_path',default='pdftoppm')


@contextmanager
def audit_render_cache():
    """Give one audit its own render results, including in nested audits."""
    token=_render_cache.set({})
    try:
        yield
    finally:
        _render_cache.reset(token)


def _cached_render_hash(body,body_hash,page,dpi):
    cache=_render_cache.get()
    if cache is None:
        return render_hash(body,page,dpi)
    executable=shutil.which('pdftoppm')
    if executable is None:
        raise FileNotFoundError('pdftoppm executable not found')
    executable=Path(executable).resolve(strict=True)
    key=(body_hash,page,dpi,str(executable),digest(executable.read_bytes()))
    if key not in cache:
        token=_renderer_path.set(str(executable))
        try:
            cache[key]=render_hash(body,page,dpi)
        finally:
            _renderer_path.reset(token)
    return cache[key]


def digest(raw):return hashlib.sha256(raw).hexdigest()


def render_hash(body,page,dpi):
    with tempfile.TemporaryDirectory(prefix='ballot-visual-review-') as tmp:
        target=Path(tmp)/'page'
        subprocess.run([_renderer_path.get(),'-f',str(page),'-l',str(page),'-r',str(dpi),
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


def jpeg_metadata(raw):
    """Decode strictly and retain stored dimensions plus EXIF display orientation."""
    from PIL import Image, ImageFile
    if not raw.startswith(b'\xff\xd8') or not raw.endswith(b'\xff\xd9'):
        raise ValueError('Native image is not a complete JPEG')
    if ImageFile.LOAD_TRUNCATED_IMAGES:
        raise ValueError('Strict native JPEG decoding required')
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format!='JPEG':raise ValueError('Native image format is not JPEG')
            width,height=im.size
            if not (0<width<=100000 and 0<height<=100000 and width*height<=50000000):
                raise ValueError('Unsupported native JPEG dimensions')
            orientation=im.getexif().get(274,1)
            if type(orientation) is not int or not 1<=orientation<=8:
                raise ValueError('Unsupported native JPEG EXIF orientation')
            im.load()  # Decode without EXIF transpose, resizing, cropping or resaving.
            return width,height,orientation
    except (OSError,ValueError,Image.DecompressionBombError) as exc:
        raise ValueError('Invalid native JPEG image') from exc


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
    renderer=params.get('renderer')
    native=renderer in ('native-png','native-jpeg')
    if native:
        fields={'renderer','width','height'} | ({'exif_orientation'} if renderer=='native-jpeg' else set())
        if (set(params)!=fields or review.get('pdf_page') is not None
            or any(type(params.get(k)) is not int or params[k]<=0 for k in ['width','height'])):
            raise ValueError('Unsupported native image review parameters')
        if renderer=='native-jpeg' and (type(params['exif_orientation']) is not int or not 1<=params['exif_orientation']<=8):
            raise ValueError('Unsupported native JPEG orientation parameters')
    elif (params.get('renderer')!='pdftoppm' or params['page']!=review['pdf_page']
          or not 1<=params['page']<=1000 or not 36<=params['dpi']<=300):
        raise ValueError('Unsupported visual rendering parameters')
    additional=review.get('additional_pdf_pages',[])
    if not isinstance(additional,list) or len(additional)>16 or native and additional:
        raise ValueError('Unsupported additional PDF pages')
    seen={params.get('page')}
    for page in additional:
        if (not isinstance(page,dict) or set(page)!={'page','dpi','render_sha256'}
            or type(page['page']) is not int or not 1<=page['page']<=1000
            or type(page['dpi']) is not int or not 36<=page['dpi']<=300
            or page['page'] in seen or not isinstance(page['render_sha256'],str)
            or len(page['render_sha256'])!=64 or any(c not in '0123456789abcdef' for c in page['render_sha256'])):
            raise ValueError('Invalid additional PDF page parameters')
        seen.add(page['page'])
    for version in index.get(source['url'],[]):
        if version['body_sha256']!=source['body_sha256'] or not version.get('body_artifact'):continue
        body=Path(version['body_artifact'])
        raw=body.read_bytes()
        body_hash=digest(raw)
        if body_hash!=source['body_sha256']:continue
        if native:
            if renderer=='native-png':
                if png_dimensions(raw)!=(params['width'],params['height']):
                    raise ValueError('Native PNG dimensions differ from reviewed source')
            elif jpeg_metadata(raw)!=(params['width'],params['height'],params['exif_orientation']):
                raise ValueError('Native JPEG dimensions/orientation differ from reviewed source')
            if review['render_sha256']!=source['body_sha256']:
                raise ValueError('Native image review must pin original untransformed bytes')
            return True
        if _cached_render_hash(body,body_hash,params['page'],params['dpi'])!=review['render_sha256']:
            raise ValueError('Reviewed rendering could not be reproduced')
        for page in additional:
            if _cached_render_hash(body,body_hash,page['page'],page['dpi'])!=page['render_sha256']:
                raise ValueError('Additional reviewed rendering could not be reproduced')
        return True
    raise ValueError('Retained reviewed source body unavailable or drifted')
