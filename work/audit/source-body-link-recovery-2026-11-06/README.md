# Private source-body compatibility-link recovery

A read-only screen found exact expected body hashes already retained in the
admitted private source-bodies CAS for 256 manifest entries whose listed raw-body
paths were missing. The reviewed plan restores only those absent, untracked paths
as ignored symlinks. No payload is copied, no existing file or link is replaced,
and no source manifest or publication flag changes.

The helper validates every target hash, manifest fingerprint, original row and
path before writing. Apply created 256 links; replay created zero and verified all
256 existing links. Every restored body was rehashed, every path is Git-ignored,
and each changed ignore file preserves its original bytes as a prefix. Original
source dates and claims remain unchanged. Recovery does not establish document
authenticity, successful legal extraction or current force.

The updated bridge covers 6,485 manifest entries and 3,042 verified-body versions.
There are 3,443 remaining manifest-path gaps, including 119 failed acquisitions
without recorded body hashes. Other private stores have not been exhaustively
searched; this is not a global loss claim. Native SQLite integrity and body/metadata
readback checks pass, with the active database on admitted NVMe and blobs retained
on /data0. The retained SQLite backup covers metadata, not independent blob restore.

Reproduce only against the exact pinned workstation paths and unchanged plan:

```sh
.venv/bin/python work/audit/source-body-link-recovery-2026-11-06/restore_reviewed_links.py \
  --plan work/audit/source-body-link-recovery-2026-11-06/plan.json \
  --receipt /data0/moratorium-refresh-2026/body-link-recovery-replay.json --apply
```

The helper refuses changed manifests, target hashes, tracked destinations and
conflicting existing paths. The checked-in plan, preview, apply and replay receipts
make this specific recovery inspectable; no raw source bytes are public artifacts.
