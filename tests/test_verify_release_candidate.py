import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile

import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('release_verifier', Path(__file__).resolve().parents[1] / 'scripts/verify_release_candidate.py')
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


def candidate(tmp_path, change=None):
    target = 'a' * 64
    entries = [('data/expanded', 'symlink', 'expanded-snapshots/' + target),
               ('data/expanded-csv', 'symlink', 'expanded-csv-snapshots/' + target),
               ('data/expanded-snapshots/' + target + '/publication.json', 'file', '{}'),
               ('data/expanded-csv-snapshots/' + target + '/manifest.json', 'file', '{}')]
    if change:
        entries = change(entries)
    records = []
    with tarfile.open(tmp_path / 'candidate.tar', 'w') as tar:
        for name, kind, value in entries:
            data = value.encode()
            info = tarfile.TarInfo(name)
            if kind == 'symlink':
                info.type = tarfile.SYMTYPE; info.linkname = value
                tar.addfile(info)
            else:
                info.size = len(data); tar.addfile(info, io.BytesIO(data))
            records.append({'path': name, 'kind': kind, 'bytes': len(data), 'sha256': v.digest(data)})
    raw = (tmp_path / 'candidate.tar').read_bytes()
    manifest = {'archive': {'name': 'candidate.tar', 'bytes': len(raw), 'sha256': v.digest(raw)}, 'files': records}
    raw = json.dumps(manifest).encode()
    (tmp_path / 'manifest.json').write_bytes(raw)
    return v.digest(raw)


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_safe_fixture_restore(self):
        expected = candidate(self.path)
        manifest, contents = v.verify_archive(self.path, expected)
        root = v.restore_tree(self.path / 'restore', manifest, contents)
        self.assertEqual((root / 'data/expanded/publication.json').read_text(), '{}')
        self.assertTrue((root / 'data/expanded-csv').is_symlink())
        with self.assertRaises(FileExistsError):
            v.restore_tree(root, manifest, contents)

    def test_wrong_independent_hash(self):
        candidate(self.path)
        with self.assertRaisesRegex(ValueError, 'Manifest SHA256'):
            v.verify_archive(self.path, '0' * 64)

    def test_reject_bad_members(self):
        changes = [
            lambda e: e + [('../escape', 'file', 'bad')],
            lambda e: e + [e[-1]],
            lambda e: [('data/expanded', 'symlink', '../../outside')] + e[1:],
            lambda e: [('data/expanded', 'file', 'expanded-snapshots/' + 'a' * 64)] + e[1:],
            lambda e: e + [('extra-link', 'symlink', 'target')],
        ]
        for change in changes:
            with self.subTest(change=change):
                expected = candidate(self.path, change)
                with self.assertRaises(ValueError):
                    v.verify_archive(self.path, expected)

    def test_archive_type_mismatch(self):
        candidate(self.path)
        path = self.path / 'candidate.tar'
        raw = path.read_bytes()
        # First header is the expanded symlink; turn it into a regular file and
        # repair the tar header checksum while retaining manifest metadata.
        header = bytearray(raw[:512]); header[156:157] = b'0'
        header[148:156] = b'        '
        header[148:156] = ('%06o\0 ' % sum(header)).encode()
        path.write_bytes(bytes(header) + raw[512:])
        manifest = json.loads((self.path / 'manifest.json').read_bytes())
        raw = path.read_bytes()
        manifest['archive']['sha256'] = v.digest(raw)
        raw = json.dumps(manifest).encode()
        (self.path / 'manifest.json').write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'type mismatch'):
            v.verify_archive(self.path, v.digest(raw))


if __name__ == '__main__':
    unittest.main()
