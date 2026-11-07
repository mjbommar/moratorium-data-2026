"""Pin active Python runtime files; no network, installation, or provider calls.

The manifest covers the interpreter executable, distribution RECORD files and
metadata, and active editable package trees. It does not capture the standard
library, shared OS libraries, kernel, environment, external services, or data
outside these trees; it is not full operating-system reproducibility.
"""
from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import importlib.util
import json
import sys
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOTS = ('bc-core', 'bc-content', 'bc-research', 'bc-llm', 'bc-evidence',
         'openai', 'pydantic-ai-slim', 'httpx2', 'packaging')
ACTIVE = {'bc-core': 'bc_core', 'bc-content': 'bc_content',
          'bc-research': 'bc_research', 'bc-llm': 'bc_llm',
          'bc-evidence': 'bc_evidence'}
BOUNDARY = (__doc__.split('\n\n', 1)[1].strip())


def _included(path):
    return '__pycache__' not in path.parts and path.suffix not in ('.pyc', '.pyo')


def _hash(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _tree(path):
    return sorted(p for p in path.rglob('*') if p.is_file() and _included(p))


def _active_path(module):
    spec = importlib.util.find_spec(module)
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError(f'Active package {module} is missing or has no package directory')
    locations = list(spec.submodule_search_locations)
    if len(locations) != 1:
        raise RuntimeError(f'Active package {module} has ambiguous locations: {locations}')
    return Path(locations[0]).resolve()


def build_manifest():
    """Collect a deterministic manifest using this process's active import paths."""
    files = {}
    distributions = {}
    pending = [(name, frozenset()) for name in ROOTS]
    visited = set()
    active = {name: str(_active_path(module)) for name, module in ACTIVE.items()}

    def add(path):
        path = Path(path).absolute()
        if not _included(path):
            return
        if not path.is_file():
            raise RuntimeError(f'Runtime file missing: {path}')
        files[str(path)] = _hash(path)

    add(Path(sys.executable).resolve())
    while pending:
        name, extras = pending.pop()
        name = canonicalize_name(name)
        key = (name, extras)
        if key in visited:
            continue
        visited.add(key)
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError as exc:
            raise RuntimeError(f'Missing runtime dependency: {name}; use the prepared BC environment') from exc
        if dist.files is None:
            raise RuntimeError(f'No installed file inventory for {name}')
        distributions[name] = dist.version
        for entry in dist.files:
            path = Path(dist.locate_file(entry))
            if _included(path):
                add(path)
        requirements = list(dist.requires or [])
        # Editable distributions list only a .pth and metadata in RECORD. Pin
        # the actual import location, including override trees and nested data.
        direct = dist.read_text('direct_url.json')
        editable = bool(direct and json.loads(direct).get('dir_info', {}).get('editable'))
        if name in active:
            package = Path(active[name])
            for path in _tree(package):
                add(path)
            project = package.parent.parent / 'pyproject.toml'
            if project.is_file():
                add(project)
                requirements.extend(tomllib.loads(project.read_text())['project'].get('dependencies', []))
        elif editable:
            top = dist.read_text('top_level.txt')
            modules = top.splitlines() if top else [name.replace('-', '_')]
            for module in modules:
                spec = importlib.util.find_spec(module)
                if spec and spec.submodule_search_locations:
                    for location in spec.submodule_search_locations:
                        for path in _tree(Path(location)):
                            add(path)
                elif spec and spec.origin and Path(spec.origin).is_file():
                    add(spec.origin)
                else:
                    raise RuntimeError(f'Cannot locate editable runtime package {module} for {name}')
                source = Path(json.loads(direct)['url'].removeprefix('file://')) / 'pyproject.toml'
                if source.is_file():
                    add(source)
        for raw in requirements:
            req = Requirement(raw)
            if req.marker and not any(req.marker.evaluate({'extra': extra}) for extra in (set(extras) | {''})):
                continue
            try:
                installed = metadata.version(req.name)
            except metadata.PackageNotFoundError as exc:
                raise RuntimeError(f'Missing runtime dependency {req} required by {name}') from exc
            if req.specifier and not req.specifier.contains(installed, prereleases=True):
                raise RuntimeError(f'Incompatible runtime dependency {req} required by {name}: installed {installed}')
            pending.append((req.name, frozenset(req.extras)))
    return {'schema_version': 'runtime-files-1', 'boundary': BOUNDARY,
            'interpreter': {'executable': str(Path(sys.executable).absolute()),
                            'resolved_executable': str(Path(sys.executable).resolve()),
                            'version': sys.version},
            'active_packages': active, 'distributions': dict(sorted(distributions.items())),
            'files_sha256': dict(sorted(files.items()))}


def write_manifest(path):
    """Write the separate manifest and return its SHA-256."""
    path = Path(path)
    path.write_text(json.dumps(build_manifest(), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return _hash(path)


def verify_manifest(path, expected_sha256):
    """Fail closed if manifest bytes or the active runtime differ; return None."""
    path = Path(path)
    if _hash(path) != expected_sha256:
        raise RuntimeError(f'Runtime manifest hash mismatch: {path}')
    expected = json.loads(path.read_text(encoding='utf-8'))
    actual = build_manifest()
    if expected != actual:
        for section in ('interpreter', 'active_packages', 'distributions', 'files_sha256', 'schema_version', 'boundary'):
            if expected.get(section) != actual.get(section):
                if section == 'files_sha256':
                    old, new = expected.get(section, {}), actual[section]
                    changed = sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
                    raise RuntimeError(f'Runtime files changed: {changed[:10]}')
                raise RuntimeError(f'Runtime manifest mismatch: {section}')
        raise RuntimeError('Runtime manifest has unexpected fields')
