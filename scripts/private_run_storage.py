"""Cooperatively enforce a private workspace's retained byte budget."""
import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile
from contextlib import contextmanager

from bc_core.budget import BudgetExceeded


class StorageBudgetExceeded(BudgetExceeded):
    def __init__(self, reason):
        super().__init__(reason, 'storage')


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


class PrivateRunStorage:
    _policy = '.storage-policy.json'
    _lock = '.storage.lock'

    def __init__(self, root, max_bytes):
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 0:
            raise ValueError('max_bytes must be a nonnegative integer')
        original = Path(os.path.abspath(root))
        for part in (original, *original.parents):
            if part.is_symlink():
                raise ValueError('symlink in root path')
        if not original.is_dir():
            raise ValueError('root must be an existing directory')
        self.root = original.resolve()
        self.max_bytes = max_bytes
        with self._locked():
            self._usage()
            policy = self.root / self._policy
            expected = self.describe()
            if policy.exists():
                if json.loads(policy.read_text(encoding='utf-8')) != expected:
                    raise ValueError('storage policy does not match retained policy')
            else:
                data = _json_bytes(expected)
                self._reserve(len(data))
                fd = os.open(policy, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, 'wb') as out:
                    out.write(data)
                    out.flush()
                    os.fsync(out.fileno())
                self._sync_dir(self.root)

    def describe(self):
        return {'root': str(self.root), 'max_bytes': self.max_bytes}

    @contextmanager
    def _locked(self):
        fd = os.open(self.root / self._lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode) or os.fstat(fd).st_nlink != 1:
                raise ValueError('invalid storage lock')
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)

    def _usage(self):
        total = 0
        for directory, dirs, files in os.walk(self.root, followlinks=False):
            for name in dirs + files:
                path = Path(directory) / name
                info = path.lstat()
                if stat.S_ISLNK(info.st_mode):
                    raise ValueError(f'symlink forbidden: {path}')
                if stat.S_ISREG(info.st_mode):
                    if info.st_nlink != 1:
                        raise ValueError(f'hard link forbidden: {path}')
                    total += info.st_size
                elif not stat.S_ISDIR(info.st_mode):
                    raise ValueError(f'unsupported file type: {path}')
        return total

    def _reserve(self, size):
        usage = self._usage()
        if usage + size > self.max_bytes:
            raise StorageBudgetExceeded(f'storage budget exceeded: {usage} + {size} > {self.max_bytes}')

    def _target(self, path):
        path = Path(path)
        if path.is_absolute():
            try:
                path = path.relative_to(self.root)
            except ValueError:
                raise ValueError('path outside storage root') from None
        if not path.parts or any(p in ('..', '.') for p in path.parts):
            raise ValueError('invalid storage path')
        if path.parts[0] in (self._policy, self._lock):
            raise ValueError('reserved storage path')
        target = self.root / path
        parent = self.root
        for component in path.parts[:-1]:
            parent = parent / component
            if parent.is_symlink():
                raise ValueError('symlink forbidden')
            parent.mkdir(exist_ok=True, mode=0o700)
        if target.is_symlink():
            raise ValueError('symlink forbidden')
        return target

    @staticmethod
    def _sync_dir(path):
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def put_bytes(self, path, data, exclusive=False, mode=0o600):
        if not isinstance(data, bytes):
            raise TypeError('data must be bytes')
        with self._locked():
            self._usage()
            target = self._target(path)
            if exclusive and target.exists():
                raise FileExistsError(target)
            self._reserve(len(data))
            if exclusive:
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
                temp = None
            else:
                fd, name = tempfile.mkstemp(prefix='.storage-tmp-', dir=target.parent)
                temp = Path(name)
            try:
                with os.fdopen(fd, 'wb') as out:
                    os.fchmod(out.fileno(), mode)
                    out.write(data)
                    out.flush()
                    os.fsync(out.fileno())
                if temp is not None:
                    os.replace(temp, target)
                self._sync_dir(target.parent)
            finally:
                if temp is not None:
                    temp.unlink(missing_ok=True)

    def save_json(self, path, value, exclusive=False):
        self.put_bytes(path, _json_bytes(value), exclusive=exclusive)

    def append_jsonl(self, path, value):
        data = _json_bytes(value)
        with self._locked():
            self._usage()
            target = self._target(path)
            self._reserve(len(data))
            fd = os.open(target, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'ab') as out:
                out.write(data)
                out.flush()
                os.fsync(out.fileno())
            self._sync_dir(target.parent)

    def append_jsonl_stream(self, stream, value):
        data = _json_bytes(value)
        with self._locked():
            self._usage()
            fd = stream.fileno()
            info = os.fstat(fd)
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not flags & os.O_APPEND:
                raise ValueError('stream must be an append-only regular file')
            matches = [Path(d) / n for d, _, files in os.walk(self.root) for n in files
                       if (Path(d) / n).stat().st_ino == info.st_ino
                       and (Path(d) / n).stat().st_dev == info.st_dev]
            if len(matches) != 1 or matches[0].parent == self.root and matches[0].name in (self._policy, self._lock):
                raise ValueError('stream is not a storage file')
            self._reserve(len(data))
            stream.seek(0, os.SEEK_END)
            stream.write(data.decode('utf-8'))
            stream.flush()
            os.fsync(fd)
