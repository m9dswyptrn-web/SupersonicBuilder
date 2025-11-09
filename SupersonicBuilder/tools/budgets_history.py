#!/usr/bin/env python3
"""
Fetch last N GitHub releases, sum asset sizes, and render a sparkline SVG
WITH per-point <title> tooltips (tag + human size) and threshold-based coloring.

Outputs:
  - docs/budgets_sparkline.svg
  - docs/budgets_history.json  (ordered mapping: tag -> total_bytes)

Env (Actions or local):
  GITHUB_REPOSITORY (owner/repo)
  GITHUB_TOKEN or GH_TOKEN
  HISTORY_COUNT (optional, default 20)
  TOTAL_WARN_MB (optional, default 900)   -> turns last point YELLOW if >= warn
  TOTAL_HARD_MB (optional, default 1200)  -> turns last point RED if >= hard
"""
from __future__ import annotations
import os, json, math, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

def gh_get(url: str, token: str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "budgets-history"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def human_mb(n: int) -> str:
    return f"{n/1024/1024:.2f} MB"

def build_sparkline_with_tooltips(tags: list[str], totals: list[int], warn_mb: float, hard_mb: float,
                                  width=600, height=90, pad=8) -> str:
    """Render totals sparkline with shaded area + per-point tooltips and threshold-based coloring."""
    if not totals:
        return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"></svg>'

    # Determine status color for latest total
    last_bytes = totals[-1]
    last_mb = last_bytes/1024/1024
    if last_mb >= hard_mb:
        stroke = "#c53939"  # red
        shade  = "#c53939"
        status_label = f"🔴 {last_mb:.0f} MB ≥ {hard_mb:.0f} MB (HARD)"
    elif last_mb >= warn_mb:
        stroke = "#d4a21f"  # yellow
        shade  = "#d4a21f"
        status_label = f"🟡 {last_mb:.0f} MB ≥ {warn_mb:.0f} MB (WARN)"
    else:
        stroke = "#86c5ff"  # blue (OK)
        shade  = "#4ea8ff"
        status_label = f"🟢 {last_mb:.0f} MB OK (< {warn_mb:.0f} MB)"

    lo, hi = min(totals), max(totals)
    span = max(1, hi - lo)
    n = len(totals)

    if n == 1:
        xs = [pad + (width-2*pad)/2]
        ys = [height/2]
    else:
        xs = [pad + i*(width-2*pad)/(n-1) for i in range(n)]
        ys = [height-pad - (p - lo) * (height-2*pad)/span for p in totals]

    path_d = " ".join([f"{'M' if i==0 else 'L'}{xs[i]:.2f},{ys[i]:.2f}" for i in range(n)])
    area_d = f"M{xs[0]:.2f},{height-pad:.2f} " + " ".join([f"L{xs[i]:.2f},{ys[i]:.2f}" for i in range(n)]) + f" L{xs[-1]:.2f},{height-pad:.2f} Z"

    # Circles + tooltips
    pts = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        tag = tags[i] if i < len(tags) else f"#{i+1}"
        pts.append(
            f'<g><circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="#86c5ff" stroke="#e6eef8" stroke-width="1">'
            f'<title>{tag} — {human_mb(totals[i])}</title></circle></g>'
        )

    # Last point highlight uses status color
    cx, cy = xs[-1], ys[-1]
    last_dot = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="3.5" fill="{stroke}" stroke="#e6eef8" stroke-width="1"/>'

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
  xmlns="http://www.w3.org/2000/svg" role="img" aria-label="release size history">
  <defs>
    <linearGradient id="g" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="{shade}" stop-opacity="0.38"/>
      <stop offset="100%" stop-color="{shade}" stop-opacity="0.05"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0b0f14"/>
  <path d="{area_d}" fill="url(#g)"/>
  <path d="{path_d}" fill="none" stroke="{stroke}" stroke-width="2"/>
  {''.join(pts)}
  {last_dot}
  <!-- Legend chip -->
  <g>
    <rect x="{width-235}" y="8" rx="8" ry="8" width="225" height="24" fill="#1b2635" stroke="#203044"/>
    <text x="{width-224}" y="24" font-family="ui-sans-serif, -apple-system, Segoe UI, Roboto, Helvetica, Arial" font-size="12" fill="#e6eef8">
      {status_label}
    </text>
  </g>
</svg>"""

def main():
    repo = os.getenv("GITHUB_REPOSITORY", "")
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or ""
    count = int(os.getenv("HISTORY_COUNT", "20"))
    warn_mb = float(os.getenv("TOTAL_WARN_MB", "900"))
    hard_mb = float(os.getenv("TOTAL_HARD_MB", "1200"))
    if not repo or not token:
        print("⚠️  Missing GITHUB_REPOSITORY or token; skipping history generation.")
        return

    # Get releases (newest first), drop drafts/prereleases
    rels = gh_get(f"https://api.github.com/repos/{repo}/releases?per_page={count}", token)
    rels = [r for r in rels if not r.get("draft") and not r.get("prerelease")]
    rels.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    # Build (tag, total_size) newest first → reverse to oldest→newest
    items = [(r.get("tag_name",""), sum(int(a.get("size",0)) for a in r.get("assets",[]))) for r in rels]
    items = list(reversed(items))[:count]

    tags = [t for t, _ in items]
    totals = [v for _, v in items]

    # Write JSON (ordered mapping oldest→newest)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "budgets_history.json").write_text(json.dumps(dict(items), indent=2), encoding="utf-8")

    # Write SVG with thresholds + tooltips
    svg = build_sparkline_with_tooltips(tags, totals, warn_mb=warn_mb, hard_mb=hard_mb)
    (DOCS / "budgets_sparkline.svg").write_text(svg, encoding="utf-8")

    if totals:
        print(f"✅ History: {len(totals)} releases. Latest {tags[-1]} = {human_mb(totals[-1])} "
              f"(warn {warn_mb:.0f} MB, hard {hard_mb:.0f} MB)")
    else:
        print("⚠️  No releases found.")

if __name__ == "__main__":
    main()
