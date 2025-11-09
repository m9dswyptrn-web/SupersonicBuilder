#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supersonic_verify_pages.py
------------------------------------------------------------
Scans ./docs for broken links/assets.
Checks:
  • Relative links: file existence under ./docs
  • External links (optional): HTTP HEAD/GET
  • Hints mode: propose fixes for common issues

Usage:
  python supersonic_verify_pages.py [--externals] [--hints]
Exit 0 if OK, 1 if any broken items found.
"""

from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
import argparse, sys, re, difflib

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    import requests
except Exception:
    requests = None

DOCS = Path("docs")
ENTRY = DOCS / "Supersonic_Dashboard.html"

def _read_html(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def _parse_links(html: str):
    links = set()
    if BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(href=True): links.add(tag["href"])
        for tag in soup.find_all(src=True):  links.add(tag["src"])
    else:
        links |= set(re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I))
        links |= set(re.findall(r'src=["\']([^"\']+)["\']',  html, flags=re.I))
    links = {l.strip() for l in links if l.strip() and not l.startswith("#") and not l.startswith("javascript:")}
    return sorted(links)

def _is_external(url: str) -> bool:
    u = urlparse(url)
    return bool(u.scheme and u.netloc)

def _normalize_rel(base: Path, href: str) -> Path:
    if href.startswith("/"):
        return (DOCS / href.lstrip("/")).resolve()
    return (base.parent / href).resolve()

def _check_external(url: str) -> tuple[bool,str]:
    if not requests:
        return (True, "external-skip(no-requests)")
    try:
        r = requests.head(url, timeout=6, allow_redirects=True)
        if r.status_code >= 400 or r.status_code == 405:
            r = requests.get(url, timeout=10, stream=True)
        ok = 200 <= r.status_code < 400
        return (ok, f"http {r.status_code}")
    except Exception as e:
        return (False, f"error {e}")

def _index_docs_paths() -> list[str]:
    return [p.relative_to(DOCS).as_posix() for p in DOCS.rglob("*") if p.is_file()]

def _hint_case_insensitive(target_rel: str, paths_index: list[str]) -> str | None:
    lower_map = {p.lower(): p for p in paths_index}
    q = target_rel.lower()
    if q in lower_map and lower_map[q] != target_rel:
        return f"Case mismatch. Try: {lower_map[q]}"
    return None

def _hint_fuzzy(target_rel: str, paths_index: list[str]) -> str | None:
    candidates = difflib.get_close_matches(target_rel, paths_index, n=1, cutoff=0.6)
    if candidates:
        return f"Closest match: {candidates[0]}"
    return None

def _hint_leading_slash(href: str, page_rel: str) -> str | None:
    if not href.startswith("/") and href.startswith("SonicBuilder/"):
        return f"Use docs-root absolute: /{href}"
    if href.startswith("/") and (page_rel.count("/") >= 1):
        return f"Use relative path (drop leading slash) if embedding within subfolders."
    return None

def _hint_outside_docs(target: Path) -> str | None:
    try:
        target.relative_to(DOCS)
        return None
    except Exception:
        return "Points outside /docs. Add source to deploy copy list or adjust href."

def scan(externals: bool=False, hints: bool=False) -> int:
    if not ENTRY.exists():
        print(f"❌ Missing entry: {ENTRY}")
        if hints:
            print("💡 Hint: Run your dashboard generator, then deploy to /docs.")
        return 1

    broken = 0; checked = 0
    paths_index = _index_docs_paths()

    html_files = [ENTRY] + [p for p in DOCS.rglob("*.html") if p != ENTRY]
    for page in html_files:
        page_rel = page.relative_to(DOCS).as_posix()
        print(f"🔎 Page: /{page_rel}")
        refs = _parse_links(_read_html(page))
        if not refs:
            print("  (no links)")
            continue
        for href in refs:
            checked += 1
            if _is_external(href):
                if externals:
                    ok, meta = _check_external(href)
                    print(f"  {'✅' if ok else '❌'} ext {href} [{meta}]")
                    if not ok: broken += 1
                else:
                    print(f"  ⏭️  ext {href} [skipped]")
                continue

            target = _normalize_rel(page, href)
            outside_hint = _hint_outside_docs(target) if hints else None
            try:
                target_rel = target.relative_to(DOCS).as_posix()
            except Exception:
                target_rel = f"(outside:{target})"

            exists = target.exists() and outside_hint is None
            print(f"  {'✅' if exists else '❌'} rel {href} → /{target_rel}")

            if not exists:
                broken += 1
                if hints:
                    if outside_hint:
                        print(f"    💡 {outside_hint}")
                        print("    💡 Add to deploy include list in supersonic_deploy_pages.py → INCLUDE = […]")
                    h_case = _hint_case_insensitive(target_rel if "outside:" not in target_rel else href, paths_index)
                    if h_case: print(f"    💡 {h_case}")
                    h_fuzzy = _hint_fuzzy(target_rel if 'outside:' not in target_rel else href, paths_index)
                    if h_fuzzy: print(f"    💡 {h_fuzzy}")
                    h_slash = _hint_leading_slash(href, page_rel)
                    if h_slash: print(f"    💡 {h_slash}")

    print(f"\nSummary: checked {checked} refs → broken {broken}")
    if broken and hints:
        print("💡 General fixes:")
        print("  • Ensure you ran: make_commander_dashboard.py → supersonic_deploy_pages.py")
        print("  • For assets under SonicBuilder/, prefer href='/SonicBuilder/…' in docs-root HTML.")
        print("  • If files exist in repo but not in /docs, add their subfolders to INCLUDE in supersonic_deploy_pages.py.")
    return 0 if broken == 0 else 1

def main():
    ap = argparse.ArgumentParser(description="Verify Pages links under ./docs")
    ap.add_argument("--externals", action="store_true", help="Also check external URLs (requires requests)")
    ap.add_argument("--hints", action="store_true", help="Suggest fixes for broken links")
    args = ap.parse_args()
    sys.exit(scan(externals=args.externals, hints=args.hints))

if __name__ == "__main__":
    main()
