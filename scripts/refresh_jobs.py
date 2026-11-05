#!/usr/bin/env python3
"""Explicit, resumable Codex CLI jobs. Research workers never edit canonical CSVs.

Job specs are JSON: id, prompt_file, owned_paths. Launch is always explicit;
existing jobs must be inspected, never restarted merely because observation timed out.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import signal
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MODEL = "gpt-6.1-terra"


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n")
    tmp.replace(path)


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else {"error": p.stderr.strip()}


def baseline(output):
    files = {}
    for rel in ["data/moratorium_inventory.csv", "data/state_legislation.csv",
                "../servercountry.org/public/data/all_projects.csv"]:
        p = ROOT / rel
        with p.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        files[rel] = {"resolved_path": str(p.resolve()),
                      "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                      "rows": len(rows), "columns": list(rows[0]) if rows else []}
    repos = {}
    for name in [ROOT.name, "moratorium-paper", "servercountry.org",
                 "datacenter-paper-2026", "datacenter-data-integration"]:
        p = ROOT.parent / name
        repos[name] = {"head": git(p, "rev-parse", "HEAD"),
                       "status": git(p, "status", "--short")}
    bc = Path.home() / "projects/bc/bc-modules"
    save(output, {"recorded_at": now(), "research_as_of": "2026-11-05",
                  "files": files, "repositories": repos,
                  "bc_modules": {"head": git(bc, "rev-parse", "HEAD"),
                                 "status": git(bc, "status", "--short")},
                  "cli_model": MODEL,
                  "limitation": "File snapshot; no record status independently refreshed yet."})


def worker(spec_path, directory):
    spec = json.loads(Path(spec_path).read_text())
    directory = Path(directory)
    prompt = Path(spec["prompt_file"]).read_text()
    command = ["codex", "--search", "exec", "--model", MODEL,
               "--sandbox", "danger-full-access", "-c", 'approval_policy="never"',
               "-c", 'model_reasoning_effort="medium"', "--cd", str(ROOT),
               "--json", "--output-last-message", str(directory / "last-message.txt"), "-"]
    meta = {"job_id": spec["id"], "supervisor_pid": os.getpid(), "model": MODEL,
            "owned_paths": spec["owned_paths"], "started_at": now(),
            "state": "running", "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "command": command, "host": os.uname().nodename}
    with (directory / "events.jsonl").open("w") as out, (directory / "stderr.log").open("w") as err:
        child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                 cwd=ROOT, text=True, start_new_session=True)
        meta["child_pid"] = child.pid
        save(directory / "status.json", meta)
        try:
            child.communicate(prompt, timeout=1800)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            meta["timed_out"] = True
        meta.update(ended_at=now(), exit_code=child.returncode,
                    state="finished" if child.returncode == 0 else "failed")
        save(directory / "status.json", meta)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    b = sub.add_parser("baseline"); b.add_argument("output", type=Path)
    for name in ["launch", "status", "_worker"]:
        s = sub.add_parser(name); s.add_argument("spec", type=Path); s.add_argument("--runs", type=Path, required=True)
    a = p.parse_args()
    if a.action == "baseline":
        baseline(a.output); print(a.output); return
    spec = json.loads(a.spec.read_text())
    if not spec["id"] or any(x not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for x in spec["id"]):
        p.error("job ID must be a safe lowercase path component")
    directory = a.runs.resolve() / spec["id"]
    if a.action == "_worker":
        worker(a.spec.resolve(), directory); return
    if a.action == "status":
        status = json.loads((directory / "status.json").read_text())
        for field in ["supervisor_pid", "child_pid"]:
            try:
                os.kill(status[field], 0); status[field + "_exists"] = True
            except (ProcessLookupError, KeyError):
                status[field + "_exists"] = False
        print(json.dumps(status, indent=2)); return
    directory.mkdir(parents=True, exist_ok=False)
    save(directory / "status.json", {"job_id": spec["id"], "state": "starting", "created_at": now()})
    with (directory / "supervisor.log").open("w") as log:
        proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_worker",
                                 str(a.spec.resolve()), "--runs", str(a.runs.resolve())],
                                stdout=log, stderr=log, start_new_session=True, cwd=ROOT)
    print(json.dumps({"job_id": spec["id"], "supervisor_pid": proc.pid, "directory": str(directory)}))


if __name__ == "__main__":
    main()
