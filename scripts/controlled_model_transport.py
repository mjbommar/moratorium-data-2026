"""Persistent, credential-free HTTP request caps for explicit OpenAI extraction runs.

The caller admits/creates a private workspace under its storage policy first.
Capture format controlled-model-capture-2 retains private HTTP body bytes and
hashes. Historical events without capture fields are not verified captures.
No headers, paths, URL queries, or userinfo are recorded. Use
``with controller.bind_request_descriptor(sha256):`` around each logical model
invocation to bind the caller's descriptor hash; callers must wire this hook
and reconcile incomplete attempts. The descriptor is not the wire-body hash.
The binding is a lowercase SHA256 of a caller-defined descriptor, not the
descriptor itself. Context variables isolate independently bound asyncio tasks;
child tasks inherit their creation context. Bind each invocation before creating
its task, and keep the scope through the awaited call. Missing bindings remain
null. A pending response blocks every subsequent dispatch, including concurrent
tasks and other processes; the caller must stop and reconcile failures.
Request streams are rejected, and responses are buffered before SDK validation.
Incomplete response streams are recorded as incomplete and never delivered.
"""

import fcntl
import hashlib
from contextlib import contextmanager, nullcontext
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import os
import stat
from pathlib import Path
from uuid import uuid4


CAPTURE_FORMAT = "controlled-model-capture-2"


class ControlledModelTransport:
    def __init__(self, directory, *, max_requests, context_sha256, storage_policy=None,
                 max_request_bytes=8 * 1024 * 1024, max_response_bytes=8 * 1024 * 1024):
        self.directory = Path(directory)
        self.storage_policy = storage_policy
        if storage_policy is not None:
            root = Path(storage_policy.root)
            absolute = Path(os.path.abspath(self.directory))
            try:
                absolute.relative_to(root)
            except ValueError:
                raise ValueError("HTTP workspace must be inside the storage root") from None
            if absolute.resolve() != absolute:
                raise ValueError("symlink in HTTP workspace path")
        for value in (max_request_bytes, max_response_bytes):
            if type(value) is not int or value < 1:
                raise ValueError("capture byte limits must be positive integers")
        self.max_request_bytes = max_request_bytes
        self.max_response_bytes = max_response_bytes
        self._descriptor = ContextVar("controlled_model_descriptor", default=None)
        self._check_directory()
        if not self.directory.is_dir():
            raise ValueError(
                "Create an admitted private workspace before configuring HTTP transport"
            )
        if type(max_requests) is not int or max_requests < 1:
            raise ValueError("HTTP request cap must be a positive integer")
        if (
            not isinstance(context_sha256, str)
            or len(context_sha256) != 64
            or any(c not in "0123456789abcdef" for c in context_sha256)
        ):
            raise ValueError("Frozen context SHA256 required")
        self.policy = {
            "schema_version": "controlled-model-http-1",
            "max_requests": max_requests,
            "context_sha256": context_sha256,
        }
        self.ledger = self.directory / "http-attempts.private.jsonl"
        self.clients = []
        # The policy and reservations share one lock so concurrent constructors
        # cannot silently replace an earlier cap or refill a retained workspace.
        if not os.path.lexists(self.ledger) and any(os.path.lexists(self.directory / n) for n in ("http-policy.private.json", "http-capture-policy.private.json")):
            raise ValueError("HTTP ledger missing; reconcile workspace")
        with self._open_ledger() as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            policy_path = self.directory / "http-policy.private.json"
            policy_preexisting = os.path.lexists(policy_path)
            if policy_preexisting:
                self._check_file(policy_path)
                if json.loads(policy_path.read_text()) != self.policy:
                    raise ValueError(
                        "HTTP workspace policy changed; inspect retained reservations"
                    )
            else:
                stream.seek(0)
                if stream.read() or os.path.lexists(self.directory / "http-capture-policy.private.json"):
                    raise ValueError("HTTP ledger has no retained policy")
                self._put_exclusive(policy_path, self._encoded(self.policy))
            capture_policy = self.directory / "http-capture-policy.private.json"
            expected = {"capture_format": CAPTURE_FORMAT,
                        "max_request_bytes": self.max_request_bytes,
                        "max_response_bytes": self.max_response_bytes}
            if os.path.lexists(capture_policy):
                self._check_file(capture_policy)
                if json.loads(capture_policy.read_text()) != expected:
                    raise ValueError("HTTP capture policy changed; inspect workspace")
            else:
                stream.seek(0)
                if stream.read() or policy_preexisting:
                    raise ValueError("HTTP capture policy missing; reconcile workspace")
                self._put_exclusive(capture_policy,
                    (json.dumps(expected, sort_keys=True) + "\n").encode())
            self._validate_workspace(stream)

    def _check_directory(self):
        absolute = Path(os.path.abspath(self.directory))
        if absolute.resolve() != absolute:
            raise ValueError("symlink in HTTP workspace path")
        info = absolute.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
            raise ValueError("HTTP workspace must be an owned private directory")
        if self.storage_policy is not None:
            from private_run_storage import PrivateRunStorage
            if not isinstance(self.storage_policy, PrivateRunStorage):
                raise ValueError("admitted private storage policy required")
            root = Path(self.storage_policy.root)
            current = absolute
            while True:
                st = current.lstat()
                if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid() or st.st_mode & 0o077:
                    raise ValueError("storage directories must be owned and private")
                if current == root:
                    break
                current = current.parent
            for name in ('.storage-policy.json', '.storage.lock'):
                self._check_file(root / name)
            if json.loads((root / '.storage-policy.json').read_text()) != self.storage_policy.describe():
                raise ValueError("storage policy drift")

    @staticmethod
    def _check_file(path):
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
                info.st_uid != os.geteuid() or info.st_mode & 0o077):
            raise ValueError(f"unsafe private file: {path}")
        return info

    def _open_ledger(self):
        self._check_directory()
        fd = os.open(self.ledger, os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
                    info.st_uid != os.geteuid() or info.st_mode & 0o077):
                raise ValueError("unsafe private ledger")
            return os.fdopen(fd, 'a+', encoding='utf-8')
        except BaseException:
            os.close(fd)
            raise

    def _validate_workspace(self, stream):
        self._check_directory()
        for name, expected in (("http-policy.private.json", self.policy),
                ("http-capture-policy.private.json", {"capture_format": CAPTURE_FORMAT,
                 "max_request_bytes": self.max_request_bytes, "max_response_bytes": self.max_response_bytes})):
            path = self.directory / name
            self._check_file(path)
            if json.loads(path.read_text()) != expected:
                raise ValueError("HTTP policy drift; stop and reconcile the workspace")
        rows = self.events(stream)
        reservations, terminals = {}, {}
        expected_artifacts = set()
        def artifact(name, expected_name, size=None, digest=None):
            if name != expected_name:
                raise ValueError("Invalid journal artifact name")
            path = self.directory / name
            info = self._check_file(path)
            if size is not None and info.st_size != size:
                raise ValueError("Journal artifact size mismatch")
            if digest is not None and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError("Journal artifact digest mismatch")
            expected_artifacts.add(name)
        def integer(v, maximum):
            return type(v) is int and 0 <= v <= maximum
        def sha(v):
            return isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v)
        for row in rows:
            ident = row.get('attempt_id')
            if row.get('capture_format') != CAPTURE_FORMAT:
                raise ValueError("Old HTTP history is unverified and charged; reconcile workspace")
            if not isinstance(ident, str) or len(ident) != 32 or any(c not in '0123456789abcdef' for c in ident):
                raise ValueError("Invalid HTTP attempt ID")
            if row['state'] == 'reserved':
                if set(row) != {'capture_format', 'request_capture_complete', 'wire_request_sha256', 'wire_request_bytes', 'request_body_file', 'request_descriptor_sha256', 'response_capacity_bytes', 'response_pending_file', 'journal_reservation_file', 'state', 'attempt_id', 'method', 'scheme', 'host', 'port', 'observed_at'}:
                    raise ValueError('Invalid reservation fields')
                if any(r not in terminals for r in reservations):
                    raise ValueError('Invalid HTTP ledger ordering')
                method, scheme, host, port = row['method'], row['scheme'], row['host'], row['port']
                if (not isinstance(method, str) or not method.isascii() or not 1 <= len(method) <= 32 or not method.isalpha() or scheme not in ('http', 'https') or not isinstance(host, str) or not host.isascii() or not 1 <= len(host) <= 253 or (port is not None and (type(port) is not int or not 1 <= port <= 65535)) or not isinstance(row['observed_at'], str)):
                    raise ValueError('Invalid reservation metadata')
                if ident in reservations or ident in terminals:
                    raise ValueError("Invalid HTTP ledger ordering")
                if (row.get('request_capture_complete') is not True or
                    not integer(row.get('wire_request_bytes'), self.max_request_bytes) or
                    not sha(row.get('wire_request_sha256')) or
                    (row.get('request_descriptor_sha256') is not None and not sha(row['request_descriptor_sha256'])) or
                    row.get('response_capacity_bytes') != self.max_response_bytes):
                    raise ValueError("Invalid HTTP reservation")
                reservations[ident] = row
                artifact(row.get('request_body_file'), f'{ident}-request.private.body', row['wire_request_bytes'], row['wire_request_sha256'])
                if row.get('response_pending_file') != f'{ident}-response.pending.private.body' or row.get('journal_reservation_file') != f'{ident}-journal-reservation.private.bytes':
                    raise ValueError("Invalid reservation artifacts")
            else:
                if set(row) != {'state', 'attempt_id', 'capture_format', 'response_capture_complete', 'wire_response_sha256', 'wire_response_bytes', 'response_body_file', 'status', 'observed_at'} or not isinstance(row.get('observed_at'), str):
                    raise ValueError('Invalid response fields')
                if ident not in reservations or ident in terminals:
                    raise ValueError("Invalid HTTP ledger ordering")
                if (type(row.get('response_capture_complete')) is not bool or
                    not integer(row.get('wire_response_bytes'), self.max_response_bytes) or
                    not sha(row.get('wire_response_sha256')) or type(row.get('status')) is not int or not 100 <= row['status'] <= 999):
                    raise ValueError("Invalid HTTP response")
                terminals[ident] = row
                artifact(row.get('response_body_file'), f'{ident}-response.private.body', row['wire_response_bytes'], row['wire_response_sha256'])
        for ident, reservation in reservations.items():
            response = terminals.get(ident)
            if response is None:
                raise ValueError("Incomplete response capture; unresolved reservation requires reconciliation")
            if not response['response_capture_complete']:
                raise ValueError("Incomplete response capture; reconcile workspace")
            bound = {"state": "response", "attempt_id": ident, "capture_format": CAPTURE_FORMAT,
                     "response_capture_complete": False, "wire_response_sha256": "f" * 64,
                     "wire_response_bytes": self.max_response_bytes,
                     "response_body_file": f"{ident}-response.private.body", "status": 999,
                     "observed_at": "9999-12-31T23:59:59.999999+00:00"}
            remaining = len(self._encoded(bound)) + self.max_response_bytes - response['wire_response_bytes'] - len(self._encoded(response))
            artifact(reservation['journal_reservation_file'], f'{ident}-journal-reservation.private.bytes', remaining)
            with (self.directory / reservation['journal_reservation_file']).open('rb') as capacity:
                while chunk := capacity.read(1024 * 1024):
                    if any(chunk):
                        raise ValueError('Journal capacity artifact altered')
        for path in self.directory.iterdir():
            if path.name.endswith(('-journal-reservation.private.bytes', '-request.private.body', '-response.private.body', '-response.pending.private.body')) and path.name not in expected_artifacts:
                raise ValueError("Unjournaled response or orphan capture; reconcile workspace")
        return rows

    @staticmethod
    def events(stream):
        stream.seek(0)
        raw = stream.read()
        if raw and not raw.endswith("\n"):
            raise ValueError("Incomplete HTTP ledger; reconcile before continuing")
        rows = [json.loads(s) for s in raw.splitlines()]
        reserved = {r["attempt_id"] for r in rows if r["state"] == "reserved"}
        responded = [r["attempt_id"] for r in rows if r["state"] == "response"]
        if (
            len(reserved) != sum(r["state"] == "reserved" for r in rows)
            or len(responded) != len(set(responded))
            or not set(responded) <= reserved
            or any(r["state"] not in ("reserved", "response") for r in rows)
        ):
            raise ValueError("Invalid HTTP ledger history")
        return rows

    @staticmethod
    def _encoded(event):
        return (json.dumps(event, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")

    def _storage_lock(self):
        return self.storage_policy._locked() if self.storage_policy is not None else nullcontext()

    def _append_reserved(self, stream, event, journal_slot):
        """Transfer reserved bytes to the ledger; never release an uncertain write."""
        data = self._encoded(event)
        with self._storage_lock():
            with journal_slot.open("r+b") as reserve:
                available = os.fstat(reserve.fileno()).st_size
                if len(data) > available:
                    raise ValueError("journal reservation exhausted; reconcile workspace")
                stream.seek(0, os.SEEK_END)
                stream.write(data.decode("utf-8"))
                stream.flush()
                os.fsync(stream.fileno())
                reserve.truncate(available - len(data))
                reserve.flush()
                os.fsync(reserve.fileno())

    def append(self, stream, event):
        if self.storage_policy is not None:
            self.storage_policy.append_jsonl_stream(stream, event)
            return
        stream.seek(0, 2)
        stream.write(json.dumps(event, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())

    @contextmanager
    def bind_request_descriptor(self, sha256):
        """Associate a caller descriptor hash with attempts in this async scope."""
        if not isinstance(sha256, str) or len(sha256) != 64 or any(
            c not in "0123456789abcdef" for c in sha256
        ):
            raise ValueError("request descriptor SHA256 required")
        token = self._descriptor.set(sha256)
        try:
            yield
        finally:
            self._descriptor.reset(token)

    def _put_exclusive(self, path, data):
        if self.storage_policy is not None:
            self.storage_policy.put_bytes(path.absolute(), data, exclusive=True, mode=0o600)
        else:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, "wb") as out:
                out.write(data)
                out.flush()
                os.fsync(out.fileno())
            self._sync_directory()

    def _put_raw_exclusive(self, path, data):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        self._sync_directory()

    def _sync_directory(self):
        fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    async def before_request(self, request):
        from bc_core.budget import BudgetExceeded

        try:
            body = request.content
        except Exception as exc:
            raise ValueError("streaming request bodies are unsupported") from exc
        if len(body) > self.max_request_bytes:
            raise ValueError("request capture byte limit exceeded")
        with self._open_ledger() as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            rows = self._validate_workspace(stream)
            if sum(r["state"] == "reserved" for r in rows) >= self.policy["max_requests"]:
                raise BudgetExceeded("Persistent provider HTTP request cap reached", "llm")
            # These fields are the only request metadata journaled. Bounds make
            # the encoded reservation finite even for caller-supplied requests.
            method, scheme, host, port = request.method, request.url.scheme, request.url.host, request.url.port
            if (not isinstance(method, str) or not method.isascii() or
                not 1 <= len(method) <= 32 or not method.isalpha() or
                scheme not in ("http", "https") or not isinstance(host, str) or
                not host.isascii() or not 1 <= len(host) <= 253 or
                (port is not None and (type(port) is not int or not 1 <= port <= 65535))):
                raise ValueError("request metadata outside capture bounds")
            ident = uuid4().hex
            request_path = self.directory / f"{ident}-request.private.body"
            slot_path = self.directory / f"{ident}-response.pending.private.body"
            journal_slot = self.directory / f"{ident}-journal-reservation.private.bytes"
            event = {
                "capture_format": CAPTURE_FORMAT, "request_capture_complete": True,
                "wire_request_sha256": hashlib.sha256(body).hexdigest(),
                "wire_request_bytes": len(body), "request_body_file": request_path.name,
                "request_descriptor_sha256": self._descriptor.get(),
                "response_capacity_bytes": self.max_response_bytes,
                "response_pending_file": slot_path.name,
                "journal_reservation_file": journal_slot.name,
                "state": "reserved", "attempt_id": ident, "method": method,
                "scheme": scheme, "host": host, "port": port,
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }
            # Response fields have fixed maximum widths. The response count can
            # never exceed the capacity and status is constrained to three digits.
            response_bound = {
                "state": "response", "attempt_id": ident, "capture_format": CAPTURE_FORMAT,
                "response_capture_complete": False, "wire_response_sha256": "f" * 64,
                "wire_response_bytes": self.max_response_bytes,
                "response_body_file": f"{ident}-response.private.body", "status": 999,
                "observed_at": "9999-12-31T23:59:59.999999+00:00",
            }
            journal_bytes = len(self._encoded(event)) + len(self._encoded(response_bound))
            # The ledger lock serializes transport attempts; the storage lock
            # makes the size check and creation atomic with other storage users.
            with self._storage_lock():
                if self.storage_policy is not None:
                    self.storage_policy._reserve(len(body) + self.max_response_bytes + journal_bytes)
                self._put_raw_exclusive(journal_slot, bytes(journal_bytes))
                self._put_raw_exclusive(request_path, body)
                self._put_raw_exclusive(slot_path, bytes(self.max_response_bytes))
            self._append_reserved(stream, event, journal_slot)
            request.extensions["controlled_model_attempt_id"] = ident

    async def after_response(self, response):
        import httpx2

        ident = response.request.extensions.get("controlled_model_attempt_id")
        with self._open_ledger() as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            rows = self.events(stream)
            reservation = next((r for r in rows if r["state"] == "reserved"
                                and r["attempt_id"] == ident), None)
            if not reservation or reservation.get("capture_format") != CAPTURE_FORMAT:
                raise ValueError("Provider response lacks a captured HTTP reservation")
            if any(r["state"] == "response" and r["attempt_id"] == ident for r in rows):
                raise ValueError("Repeated provider response event")

        slot = self.directory / reservation["response_pending_file"]
        final = self.directory / f"{ident}-response.private.body"
        if "journal_reservation_file" not in reservation:
            raise ValueError("Old reservation lacks journal capacity; reconcile workspace")
        journal_slot = self.directory / reservation["journal_reservation_file"]
        digest = hashlib.sha256()
        size = 0
        complete = False
        try:
            with slot.open("r+b", buffering=0) as out:
                async def raw_chunks():
                    if response.is_stream_consumed:
                        # MockTransport may return an eagerly buffered Response.
                        # Encoded eager content has lost its original wire form.
                        if not hasattr(response, "_content") or response.headers.get("content-encoding"):
                            raise ValueError("original response bytes unavailable")
                        yield response.content
                    else:
                        async for value in response.aiter_raw():
                            yield value

                async for chunk in raw_chunks():
                    remaining = reservation["response_capacity_bytes"] - size
                    part = chunk[:remaining]
                    written = out.write(part)
                    if written is None:
                        raise OSError("response capture write failed")
                    digest.update(part[:written])
                    size += written
                    if written != len(part):
                        raise OSError("short response capture write")
                    if len(part) != len(chunk):
                        raise ValueError("response capture byte limit exceeded")
                complete = True
        finally:
            # Retain unused response capacity as a persistent charge. Grow the
            # charge first so a failed transfer never refunds uncertain bytes.
            with self._storage_lock():
                with journal_slot.open("r+b") as reserve:
                    reserve.truncate(os.fstat(reserve.fileno()).st_size +
                                     reservation["response_capacity_bytes"] - size)
                    reserve.flush()
                    os.fsync(reserve.fileno())
                with slot.open("r+b") as out:
                    out.truncate(size)
                    out.flush()
                    os.fsync(out.fileno())
            if final.exists():
                raise ValueError("Response artifact already exists; reconcile workspace")
            os.rename(slot, final)
            self._sync_directory()
            with self._open_ledger() as stream:
                fcntl.flock(stream, fcntl.LOCK_EX)
                self.events(stream)
                if type(response.status_code) is not int or not 100 <= response.status_code <= 999:
                    raise ValueError("response status outside capture bounds")
                self._append_reserved(stream, {
                    "state": "response", "attempt_id": ident,
                    "capture_format": CAPTURE_FORMAT,
                    "response_capture_complete": complete,
                    "wire_response_sha256": digest.hexdigest(),
                    "wire_response_bytes": size,
                    "response_body_file": final.name,
                    "status": response.status_code,
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                }, journal_slot)
        response.stream = httpx2.ByteStream(final.read_bytes())
        response.is_stream_consumed = False
        response.is_closed = False

    def client_factory(self, proxy, *, transport=None):
        import httpx2

        client = httpx2.AsyncClient(
            proxy=proxy,
            transport=transport,
            follow_redirects=False,
            event_hooks={
                "request": [self.before_request],
                "response": [self.after_response],
            },
        )
        self.clients.append(client)
        return client

    def require_model(self, model):
        sdk = getattr(model, "client", None)
        if getattr(sdk, "max_retries", None) != 0:
            raise ValueError(
                "Provider SDK retries must be explicitly zero before extraction; update bc-llm"
            )
        # A pinned SDK integration check: reject opaque/unobserved transports,
        # rather than assuming that a backend-level limit observes HTTP retries.
        if not any(getattr(sdk, "_client", None) is client for client in self.clients):
            raise ValueError(
                "Provider model does not use this controlled HTTP transport"
            )
        return model
