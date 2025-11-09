#!/usr/bin/env python3
"""
Collect per-asset historical sizes from the last N GitHub releases.

Outputs:
  - docs/budgets_asset_history.json   { "<asset name>": [bytes_oldest..bytes_newest], ... }

Env:
  GITHUB_REPOSITORY (owner/repo)
  GITHUB_TOKEN or GH_TOKEN
  HISTORY_COUNT (optional, default 12)
"""
from __future__ import annotations
import os, json, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

def gh_get(url: str, token: str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "budgets-asset-history"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    repo = os.getenv("GITHUB_REPOSITORY", "")
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or ""
    count = int(os.getenv("HISTORY_COUNT", "12"))
    if not repo or not token:
        print("⚠️  Missing GITHUB_REPOSITORY or token; skipping asset history.")
        return

    # newest first
    rels = gh_get(f"https://api.github.com/repos/{repo}/releases?per_page={count}", token)
    rels.sort(key=lambda r: r.get("created_at",""), reverse=True)

    # oldest..newest
    rels = [r for r in rels if not r.get("draft") and not r.get("prerelease")]
    rels = list(reversed(rels))[:count]

    # Build a name -> list of sizes (aligned by release order)
    all_names = set()
    for r in rels:
        for a in r.get("assets", []):
            all_names.add(a.get("name",""))
    series = { n: [] for n in sorted(all_names) }
    for r in rels:
        sizes = { a.get("name",""): int(a.get("size",0)) for a in r.get("assets",[]) }
        for n in series:
            series[n].append(int(sizes.get(n, 0)))  # 0 if missing this release

    DOCS.mkdir(parents=True, exist_ok=True)
    out = DOCS / "budgets_asset_history.json"
    out.write_text(json.dumps(series, indent=2), encoding="utf-8")
    print(f"✅ Wrote {out} ({len(series)} assets across {len(rels)} releases)")

if __name__ == "__main__":
    main()
