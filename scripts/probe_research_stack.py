#!/usr/bin/env python3
"""Small live stack probe; retain private search/fetch payloads, publish metadata.

Run with the bc-modules interpreter. At most four search calls and two browser
fetches; no external LLM API calls. A failed capability is reported, not hidden.
"""
import argparse
import asyncio
import datetime as dt
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace


async def run(out):
    from bc_core.budget import BudgetMeter
    from bc_core.text import locate_quote
    from bc_evidence.search import Cell, SearchPolicy, official_queries
    from bc_research import ResearchContext, ResearchSearch
    from bc_research.pipeline import document_text
    from bc_spec import Value
    from bc_web import Retriever
    from bc_web.chrome import find_chrome
    from bc_web.search import Searcher, SearchQuery
    from bc_web.settings import BcWebSettings

    out.mkdir(parents=True, exist_ok=True)
    report = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(), "stages": {},
              "model_calls": 0, "cost_note": "SerpAPI unknown plan rate: call-bounded, not claimed free or dollar-bounded."}
    def write(name, obj):
        (out / name).write_text(json.dumps(obj, indent=2, default=str) + "\n")
    meter = BudgetMeter(caps={"search": 4})
    searcher = Searcher(meter=meter)
    subject = Value(id="ca-hayward-city", label="Hayward California",
                    metadata={"iso2": "US", "official_hosts": ["hayward-ca.gov"]})
    cell = Cell(spec="moratorium-pilot", subject=subject,
                topic=Value(id="moratorium", label="data center moratorium"))
    queries = official_queries(cell, SimpleNamespace(query_terms=["data center", "moratorium"], native_terms={}),
                               (dt.date(2026, 10, 1), dt.date(2026, 11, 6)), False,
                               SearchPolicy(today=dt.date(2026, 11, 5), per_query=5))
    queries["semantic_exa"] = SearchQuery(query="Hayward California city council October 2026 data center moratorium adopted", backend="exa", max_results=5)
    report["stages"]["bc_spec_and_bc_evidence_queries"] = {"cell_id": cell.id, "queries": {k:q.model_dump(mode="json") for k,q in queries.items()}}
    try:
        fused = await searcher.search_many(queries)
        write("fusion.private.json", fused.model_dump(mode="json"))
        report["stages"]["search_many"] = {"hits": len(fused.hits), "errors": str(fused.errors)}
        rs = ResearchSearch(searcher, backends=("exa",), reputation=False)
        result = await rs.run("Hayward California data center moratorium October 2026",
                             ResearchContext(topic="Local infrastructure moratoria", goal="Locate operative text and adoption evidence"),
                             tier="search", max_results=5)
        write("research.private.json", result.model_dump(mode="json"))
        report["stages"]["bc_research_search"] = {"candidates": len(result.rows) if hasattr(result,"rows") else len(result.kept)}
    except Exception as exc:
        report["stages"]["search_error"] = {"type": type(exc).__name__, "message": str(exc)[:400]}
    finally:
        await searcher.close()
    settings = BcWebSettings(headless=False, default_engine="pydoll", timeout_ms=45000)
    report["chrome"] = str(find_chrome())
    urls = ["https://www.hayward-ca.gov/discover/news/oct26/hayward-city-council-enacts-immediate-moratorium-new-data-centers",
            "https://ballotpedia.org/Data_center-related_ballot_measures,_2026"]
    async with Retriever(settings) as retriever:
        for i,url in enumerate(urls):
            try:
                page = await asyncio.wait_for(retriever.fetch(url, mode="browser", engine="pydoll", headless=False), timeout=80)
                write(f"browser-{i}.private.json", page.model_dump(mode="json", exclude={"raw", "pdf"}))
                text,_ = document_text(page)
                (out / f"browser-{i}.private.txt").write_text(text)
                raw = page.raw or (page.html or "").encode()
                (out / f"browser-{i}.private.bin").write_bytes(raw)
                # locate_quote deliberately refuses tiny snippets (<12 chars).
                phrase = text.split("\n")[0][:200]
                located = locate_quote(text, phrase) if phrase in text else None
                report["stages"][f"pydoll_{i}"] = {"url": url, "ok": page.ok, "status": page.status,
                    "chars": len(text), "body_sha256": hashlib.sha256(raw).hexdigest(),
                    "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "quote_probe": str(located),
                    "attempts": [x.model_dump(mode="json") for x in page.attempts]}
            except Exception as exc:
                report["stages"][f"pydoll_{i}"] = {"url": url, "error": type(exc).__name__, "message": str(exc)[:400]}
    report["search_budget"] = {"counts": meter.counts, "known_usd": meter.spent_usd}
    report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    write("report.json", report)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    asyncio.run(run(args.output))
