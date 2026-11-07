import importlib.util
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runtime_file_pins as pins


def test_manifest_detects_changed_added_and_removed_files(tmp_path, monkeypatch):
    package = tmp_path / 'package'
    package.mkdir()
    source = package / 'source.py'
    source.write_text('first')
    monkeypatch.setattr(pins, 'build_manifest', lambda: {
        'files_sha256': {str(p): pins._hash(p) for p in pins._tree(package)}
    })
    path = tmp_path / 'manifest.json'
    digest = pins.write_manifest(path)
    pins.verify_manifest(path, digest)
    source.write_text('second')
    with pytest.raises(RuntimeError, match='Runtime files changed'):
        pins.verify_manifest(path, digest)
    source.write_text('first')
    extra = package / 'data.json'
    extra.write_text('{}')
    with pytest.raises(RuntimeError, match='Runtime files changed'):
        pins.verify_manifest(path, digest)
    extra.unlink()
    source.unlink()
    with pytest.raises(RuntimeError, match='Runtime files changed'):
        pins.verify_manifest(path, digest)
    path.write_text('{}')
    with pytest.raises(RuntimeError, match='manifest hash mismatch'):
        pins.verify_manifest(path, digest)


def test_excludes_bytecode_recursively(tmp_path):
    cache = tmp_path / '__pycache__'
    cache.mkdir()
    (cache / 'x.py').write_text('x')
    (tmp_path / 'x.pyc').write_bytes(b'x')
    (tmp_path / 'data.json').write_text('{}')
    assert [p.name for p in pins._tree(tmp_path)] == ['data.json']


def test_real_bc_runtime_closure_and_overrides(monkeypatch):
    roots = [Path('/home/mjbommar/projects/bc/bc-modules-evidence-chunk-policy/bc-evidence/python'),
             Path('/home/mjbommar/projects/bc/bc-modules-sdk-retries/bc-llm/python')]
    if not all(p.is_dir() for p in roots):
        pytest.skip('BC override worktrees unavailable')
    # Resolve overrides in a fresh interpreter: prior tests may already have
    # imported installed packages, which sys.path mutation cannot replace.
    import subprocess
    code = "import sys,json; sys.path[:0]=" + repr([str(p) for p in roots] + [str(Path(pins.__file__).parent)]) + "; import runtime_file_pins as p; print(json.dumps(p.build_manifest()))"
    manifest = json.loads(subprocess.check_output([sys.executable, '-c', code], text=True))
    assert all(name in manifest['distributions'] for name in pins.ROOTS)
    assert manifest['active_packages']['bc-evidence'].startswith(str(roots[0]))
    assert manifest['active_packages']['bc-llm'].startswith(str(roots[1]))
    paths = manifest['files_sha256']
    assert any(p.endswith('/bc_content/temporal.py') for p in paths)
    assert any(p.endswith('/bc_content/facts.py') for p in paths)
    assert any(p.endswith('.so') for p in paths)
    assert not any('__pycache__' in p or p.endswith('.pyc') for p in paths)
    assert str(Path(sys.executable).resolve()) in paths


def test_missing_dependency_fails_clearly(monkeypatch):
    monkeypatch.setattr(pins, 'ROOTS', ('definitely-absent-runtime-package-xyz',))
    monkeypatch.setattr(pins, 'ACTIVE', {})
    with pytest.raises(RuntimeError, match='Missing runtime dependency'):
        pins.build_manifest()
