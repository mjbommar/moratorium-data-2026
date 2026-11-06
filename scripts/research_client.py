#!/usr/bin/env python3
"""Bounded bc-web research client with persistent, pre-call reservations.

Use this from research jobs instead of ad-hoc Searcher loops. Interrupted attempts
still consume their cap; repeating a command cannot reset spend or overwrite evidence.
Limits are specified once by the coordinator in a job's client-config.json.
"""
import argparse
import asyncio
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import uuid


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def search_scope(query,hits):
    sites=sorted(set(m.group(1).lower().strip('.') for m in re.finditer(
        r'(?<![-\w])site:([a-z0-9.-]+)',query,re.I)))
    sites=[s for s in sites if s]
    if not sites:return {'status':'not_evaluated','declared_sites':[]}
    hosts=[(urlsplit(h['url']).hostname or '').lower() for h in hits]
    matched=sum(any(host==s or host.endswith('.'+s) for s in sites) for host in hosts)
    state=('empty_result_set' if not hits else 'no_returned_url_in_declared_sites' if not matched
           else 'all_returned_urls_in_declared_sites' if matched==len(hits) else 'partly_outside_declared_sites')
    return {'status':state,'declared_sites':sites,'matching_hits':matched,
            'nonmatching_hits':len(hits)-matched,'observed_hosts':sorted(set(hosts)),
            'scope':'Diagnostic of returned URL hosts, not query-language validation or evidence of absence. Check ambiguous OR branches and fetch substantive sources.'}


def reserve(directory, kind):
    config = json.loads((directory / "client-config.json").read_text())
    ledger = directory / "attempts.private.jsonl"
    with ledger.open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        events = [json.loads(x) for x in f if x.strip()]
        reserved = [x for x in events if x["state"] == "reserved"]
        count = sum(x["kind"] == kind for x in reserved)
        if count >= config["caps"].get(kind, 0):
            raise RuntimeError(f"Persistent {kind} cap reached: {count}")
        if kind in ("exa", "serpapi", "googlenews", "gdelt"):
            total = sum(x["kind"] in ("exa", "serpapi", "googlenews", "gdelt") for x in reserved)
            if total >= config["caps"].get("search_total", 0):
                raise RuntimeError(f"Persistent total search cap reached: {total}")
        attempt = {"attempt_id": uuid.uuid4().hex, "kind": kind, "state": "reserved", "reserved_at": timestamp(),
                   "client_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "config_sha256": hashlib.sha256((directory / "client-config.json").read_bytes()).hexdigest()}
        f.seek(0, 2); f.write(json.dumps(attempt) + "\n"); f.flush()
        return attempt


def finish(directory, attempt, **fields):
    with (directory / "attempts.private.jsonl").open("a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps({**attempt, **fields, "state": "finished", "finished_at": timestamp()}) + "\n")


async def execute(args):
    directory = args.directory.resolve()
    kind = args.backend if args.action == "search" else "fetch"
    attempt = reserve(directory, kind)
    stem = directory / (attempt["attempt_id"] + ".private")
    metadata = {"attempt_id": attempt["attempt_id"], "kind": kind}
    try:
        if args.action == "search":
            from bc_web.search import Searcher
            from bc_web.settings import BcWebSettings
            settings = BcWebSettings(search_throttle_retries=0)
            exchanges = []
            # Retain every decoded HTTP exchange, including failed/retried responses.
            # Redact actual credential values before any payload reaches disk.
            def sink(exchange):
                body = exchange.body
                original_hash = hashlib.sha256(body).hexdigest()
                for field in ("exa_api_key", "serpapi_api_key"):
                    secret = getattr(settings, field, None)
                    if secret:
                        body = body.replace(secret.get_secret_value().encode(), b"[REDACTED]")
                target = directory / f"{attempt['attempt_id']}-response-{len(exchanges):03}.private.body"
                with target.open("xb") as f:
                    f.write(body)
                exchanges.append({"artifact": str(target), "status": exchange.status,
                    "original_body_sha256": original_hash,
                    "stored_body_sha256": hashlib.sha256(body).hexdigest(),
                    "redacted": body != exchange.body})
                with (directory / "exchanges.private.jsonl").open("a") as f:
                    f.write(json.dumps({"attempt_id": attempt["attempt_id"], **exchanges[-1]}) + "\n")
            searcher = Searcher(settings, on_response=sink)
            # One reserved operation must not silently fan out into provider retries.
            # bc-web exposes the backend instance, but not ordinary search retries
            # through settings in the pinned revision.
            backend = searcher.backend(args.backend)
            backend.retries = 0
            backend.throttle_retries = 0
            try:
                options = {}
                if args.since: options['start_date'] = dt.date.fromisoformat(args.since)
                if args.until: options['end_date'] = dt.date.fromisoformat(args.until)
                if args.domains: options['include_domains'] = args.domains
                result = await searcher.search(args.query, backend=args.backend, max_results=args.max_results, **options)
                payload = result.model_dump(mode="json")
            finally:
                await searcher.close()
            metadata.update(query=args.query, hits=len(result.hits), cost_usd=result.cost_usd,
                            publication_window={'since':args.since,'until':args.until},max_results=args.max_results,
                            unpriced=result.cost_usd is None, exchanges=exchanges,
                            retry_policy="single provider attempt; failures retain reservation")
            if args.domains:
                metadata['include_domains']=args.domains
                metadata['query_scope_check']=search_scope(' '.join('site:'+d for d in args.domains),payload['hits'])
            elif args.backend=='serpapi':
                metadata['query_scope_check']=search_scope(args.query,payload['hits'])
        else:
            from bc_web import Retriever
            from bc_web.settings import BcWebSettings
            from bc_research.pipeline import document_text
            controls={"engine":"pydoll","headless":False} if args.mode=='browser' else {}
            if args.settle_ms is not None:controls['settle_ms']=args.settle_ms
            if args.wait_for_selector:controls['wait_for_selector']=args.wait_for_selector
            if args.record_network:controls['record_network']=True
            settings={"timeout_ms":45000}
            if args.conditional_cache:
                settings.update(cache_dir=directory/'cache.private',cache_ttl_s=0,
                                cache_max_mb=100,cache_revalidate=True)
            async with Retriever(BcWebSettings(**settings)) as r:
                result = await asyncio.wait_for(r.fetch(args.url, mode=args.mode,
                    **controls), timeout=85)
            payload = result.model_dump(mode="json", exclude={"raw", "pdf"})
            raw = result.raw or (result.html or "").encode()
            text, title = document_text(result)
            stem.with_suffix(stem.suffix + ".body").write_bytes(raw)
            stem.with_suffix(stem.suffix + ".txt").write_text(text)
            metadata.update(url=args.url, final_url=result.final_url, status=result.status,
                            ok=result.ok, title=title, chars=len(text),
                            body_sha256=hashlib.sha256(raw).hexdigest(),
                            text_sha256=hashlib.sha256(text.encode()).hexdigest())
            if args.mode=='browser':metadata['browser_controls']=controls
            metadata.update(from_cache=result.from_cache,revalidated=result.revalidated,
                            body_observed_at=payload.get('fetched_at'))
            if args.conditional_cache:
                metadata['cache_policy']='private job cache; ttl0; origin revalidation each call; 100MB cap'
                metadata['origin_attempt_statuses']=[a.get('status') for a in payload.get('attempts',[]) if a.get('status') is not None]
                metadata['freshness_scope']='Body reuse/revalidation only; no substantive source or legal-force acceptance.'
        target = stem.with_suffix(stem.suffix + ".json")
        with target.open("x") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        metadata["artifact"] = str(target)
        finish(directory, attempt, outcome="response", **metadata)
        print(json.dumps(metadata, indent=2))
    except Exception as exc:
        # Never log raw transport exceptions: provider URLs may contain API keys.
        finish(directory, attempt, outcome="error", error_type=type(exc).__name__)
        raise RuntimeError(f"Attempt {attempt['attempt_id']} failed: {type(exc).__name__}; cap reservation retained") from None


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--directory", type=Path, required=True)
    s = p.add_subparsers(dest="action", required=True)
    q = s.add_parser("search"); q.add_argument("query")
    q.add_argument("--backend", choices=["exa", "serpapi", "googlenews", "gdelt"], required=True)
    q.add_argument("--max-results", type=int, choices=range(1, 21), default=6)
    q.add_argument("--since", help="Publication date lower bound; omit for undated official pages")
    q.add_argument("--until", help="Publication date upper bound, not legal event cutoff")
    q.add_argument("--domain",dest="domains",action="append",default=[],help="Native backend include_domains filter; repeat for multiple domains. Exa sends includeDomains, SerpAPI compiles site operators. Returned hosts are diagnosed.")
    f = s.add_parser("fetch"); f.add_argument("url"); f.add_argument("--mode", choices=["http", "auto", "browser"], default="auto")
    f.add_argument('--settle-ms',type=int,choices=range(0,15001),metavar='0..15000',help='Bounded additional browser settle time for JavaScript portals')
    f.add_argument('--conditional-cache',action='store_true',help='HTTP only: use private job cache with zero TTL and conditional origin revalidation; never refresh legal facts automatically')
    f.add_argument('--record-network',action='store_true',help='Retain browser subrequest metadata privately for portal endpoint discovery')
    f.add_argument('--wait-for-selector',help='Wait for a known rendered CSS selector in explicit browser mode')
    args=p.parse_args()
    if args.action=='search' and args.domains and args.backend not in ('exa','serpapi'):
        p.error('--domain is supported only for Exa and SerpAPI in this client')
    if args.action=='fetch' and (args.settle_ms is not None or args.wait_for_selector or args.record_network) and args.mode!='browser':
        p.error('browser wait controls require --mode browser')
    if args.action=='fetch' and args.conditional_cache and args.mode!='http':
        p.error('--conditional-cache requires explicit --mode http')
    asyncio.run(execute(args))
