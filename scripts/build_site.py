#!/usr/bin/env python3
"""Render markdown docs to styled HTML pages for the GitHub Pages site.

Each .md file we want exposed on the site gets a sibling .html file with
the same design system as the landing page index.html.

Run from repo root:
    uv run --with markdown --with pymdown-extensions python3 scripts/build_site.py
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parents[1]

# Files to render. (source_md, output_html, page_title, depth)
# depth = number of "../" needed to reach the repo root from the html file.
PAGES: list[tuple[str, str, str, int]] = [
    ("docs/FAQ.md",          "docs/FAQ.html",          "FAQ",                       1),
    ("docs/methodology.md",  "docs/methodology.html",  "Methodology",               1),
    ("docs/codebook.md",     "docs/codebook.html",     "Codebook",                  1),
    ("docs/known-gaps.md",   "docs/known-gaps.html",   "Known gaps and limitations", 1),
    ("data/README.md",       "data/index.html",        "Data files",                 1),
    ("states/README.md",     "states/index.html",      "Browse by state",            1),
]

# All state pages
for state_md in sorted((REPO / "states").glob("*.md")):
    if state_md.name == "README.md":
        continue
    state_slug = state_md.stem
    title = " ".join(w.capitalize() for w in state_slug.split("-"))
    PAGES.append((f"states/{state_md.name}", f"states/{state_slug}.html", f"{title} — moratoria", 1))


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Moratorium Nation</title>
<meta name="description" content="{title} — Moratorium Nation, the open dataset and working paper on local-government moratoria targeting data centers, battery storage, solar, wind, and cryptocurrency mining across the United States.">
<style>
  :root {{
    --ink: #0f1419;
    --ink-soft: #4a5460;
    --bg: #fafaf7;
    --accent: #1f6feb;
    --line: #d8dadc;
    --code-bg: #f3f3ee;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0;
    font-family: ui-sans-serif, system-ui, -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    color: var(--ink);
    background: var(--bg);
    line-height: 1.6;
    font-size: 16px;
  }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  .topbar {{
    background: white;
    border-bottom: 1px solid var(--line);
    padding: 12px 24px;
  }}
  .topbar-inner {{
    max-width: 920px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 16px;
    flex-wrap: wrap;
  }}
  .topbar a.brand {{
    font-weight: 600;
    color: var(--ink);
    font-size: 15px;
    letter-spacing: -0.01em;
  }}
  .topbar a.brand:hover {{ text-decoration: none; color: var(--accent); }}
  .topbar nav {{
    display: flex;
    gap: 18px;
    font-size: 14px;
  }}
  .topbar nav a {{ color: var(--ink-soft); }}
  .topbar nav a:hover {{ color: var(--accent); }}

  main.doc {{
    max-width: 760px;
    margin: 0 auto;
    padding: 36px 24px 80px;
  }}
  main.doc .breadcrumb {{
    font-size: 13px;
    color: var(--ink-soft);
    margin-bottom: 20px;
  }}
  main.doc h1 {{
    font-size: clamp(26px, 3.4vw, 36px);
    line-height: 1.2;
    letter-spacing: -0.02em;
    margin: 0 0 14px;
  }}
  main.doc h2 {{
    font-size: 22px;
    margin: 36px 0 10px;
    letter-spacing: -0.01em;
    line-height: 1.3;
  }}
  main.doc h3 {{
    font-size: 17px;
    margin: 26px 0 8px;
    line-height: 1.3;
  }}
  main.doc h4 {{
    font-size: 15px;
    margin: 22px 0 6px;
    color: var(--ink-soft);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  main.doc p, main.doc ul, main.doc ol {{
    margin: 0 0 14px;
  }}
  main.doc ul, main.doc ol {{
    padding-left: 24px;
  }}
  main.doc li {{ margin: 4px 0; }}
  main.doc blockquote {{
    border-left: 3px solid var(--accent);
    margin: 14px 0;
    padding: 6px 16px;
    color: var(--ink-soft);
    background: white;
    border-radius: 0 6px 6px 0;
  }}
  main.doc blockquote p {{ margin: 4px 0; }}
  main.doc code {{
    background: var(--code-bg);
    border-radius: 3px;
    padding: 1px 5px;
    font-size: 0.92em;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }}
  main.doc pre {{
    background: var(--code-bg);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 12px 14px;
    overflow-x: auto;
    font-size: 13px;
    line-height: 1.5;
    margin: 14px 0;
  }}
  main.doc pre code {{
    background: transparent;
    padding: 0;
  }}
  main.doc hr {{
    border: none;
    border-top: 1px solid var(--line);
    margin: 30px 0;
  }}
  main.doc img {{
    max-width: 100%;
    border-radius: 6px;
    border: 1px solid var(--line);
  }}
  main.doc table {{
    border-collapse: collapse;
    margin: 16px 0;
    width: 100%;
    font-size: 14px;
    overflow-x: auto;
    display: block;
  }}
  main.doc table thead {{
    background: white;
  }}
  main.doc table th, main.doc table td {{
    border: 1px solid var(--line);
    padding: 8px 10px;
    text-align: left;
    vertical-align: top;
  }}
  main.doc table th {{
    font-weight: 600;
    background: white;
  }}
  main.doc table tbody tr:nth-child(even) td {{
    background: white;
  }}

  footer {{
    border-top: 1px solid var(--line);
    padding: 24px;
    text-align: center;
    color: var(--ink-soft);
    font-size: 13px;
  }}
  footer a {{ color: var(--ink-soft); }}
  footer a:hover {{ color: var(--accent); }}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="{home}">Moratorium Nation</a>
    <nav>
      <a href="{home}">Map</a>
      <a href="{prefix}states/index.html">States</a>
      <a href="{prefix}docs/FAQ.html">FAQ</a>
      <a href="{prefix}docs/methodology.html">Methodology</a>
      <a href="{prefix}paper/moratorium-nation-2026-04-30.pdf">Paper</a>
      <a href="https://github.com/mjbommar/moratorium-data-2026">GitHub</a>
    </nav>
  </div>
</div>

<main class="doc">
  <div class="breadcrumb"><a href="{home}">← Home</a></div>
  {body}
</main>

<footer>
  <a href="https://github.com/mjbommar/moratorium-data-2026">github.com/mjbommar/moratorium-data-2026</a>
  · Data CC-BY-4.0 · Code MIT
  · <a href="https://michaelbommarito.com/">Michael J. Bommarito</a>
</footer>

</body>
</html>
"""


# Targets we render to .html — these get rewritten in markdown links
RENDERED_TARGETS = {src for src, _, _, _ in PAGES}


def rewrite_md_links(html: str) -> str:
    """Rewrite .md links inside a rendered HTML doc to point at .html siblings.

    - Rewrites href="...some/path.md" → href="...some/path.html" only when the
      .md target is one we are rendering.
    - Leaves external links alone.
    - Special-cases data/README.md and states/README.md → data/index.html and
      states/index.html.
    - Leaves the .md untouched if we're not rendering it (so links to e.g.
      LICENSE-data still go to the GitHub blob — caller can choose to rewrite
      those separately).
    """

    def repl(match: re.Match[str]) -> str:
        full = match.group(0)
        target = match.group(1)

        # External or anchor links — leave alone.
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return full

        # Strip any anchor fragment for the lookup.
        path_only, _, frag = target.partition("#")

        # Normalize: pages live next to the .md, so a link from docs/FAQ.md to
        # "../states/ohio.md" resolves to "states/ohio.md" relative to the
        # current page. We need to figure out the absolute repo-root path.
        # But we don't actually need the absolute path because the rewrite
        # is purely textual (replace .md → .html / README.md → index.html).
        if path_only.endswith("README.md"):
            new_path = path_only[: -len("README.md")] + "index.html"
        elif path_only.endswith(".md"):
            new_path = path_only[:-3] + ".html"
        else:
            return full

        new = new_path + (f"#{frag}" if frag else "")
        return f'href="{new}"'

    return re.sub(r'href="([^"]+)"', repl, html)


def make_breadcrumb_for(out_path: Path, home_url: str) -> str:
    """States/foo.html and docs/foo.html show two-step breadcrumb."""
    parts = out_path.parts
    if len(parts) == 2 and parts[0] == "states" and parts[1] != "index.html":
        return (
            f'<div class="breadcrumb">'
            f'<a href="{home_url}">Home</a> / '
            f'<a href="index.html">States</a></div>'
        )
    if len(parts) == 2 and parts[0] == "docs":
        return f'<div class="breadcrumb"><a href="{home_url}">Home</a> / Docs</div>'
    return f'<div class="breadcrumb"><a href="{home_url}">← Home</a></div>'


def render() -> None:
    md = markdown.Markdown(
        extensions=[
            "extra",            # tables, fenced code, footnotes, attr_list
            "sane_lists",
            "toc",
            "pymdownx.tilde",   # ~~strikethrough~~
        ],
        extension_configs={
            "toc": {"permalink": False},
        },
    )

    for src, dst, title, depth in PAGES:
        src_path = REPO / src
        dst_path = REPO / dst
        text = src_path.read_text(encoding="utf-8")
        md.reset()
        body = md.convert(text)
        body = rewrite_md_links(body)

        prefix = "../" * depth          # path back to repo root from this html
        home = prefix + "index.html"

        breadcrumb = make_breadcrumb_for(Path(dst), home)
        body_with_breadcrumb = body  # breadcrumb is already in the template
        # Replace the default breadcrumb with the contextual one
        page_html = PAGE_TEMPLATE.format(
            title=title,
            home=home,
            prefix=prefix,
            body=body,
        ).replace(
            f'<div class="breadcrumb"><a href="{home}">← Home</a></div>',
            breadcrumb,
        )

        dst_path.write_text(page_html, encoding="utf-8")
        print(f"  {src}  →  {dst}")


if __name__ == "__main__":
    render()
    print(f"\nRendered {len(PAGES)} pages.")
