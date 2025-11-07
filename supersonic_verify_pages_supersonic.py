from pathlib import Path
from bs4 import BeautifulSoup
import requests, os, sys

DOCS = Path("docs")
EXTERNALS = os.getenv("EXTERNALS", "true").lower() == "true"
HINTS = os.getenv("HINTS", "true").lower() == "true"

def check_html(p: Path):
    html = p.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    errors = 0
    for a in soup.find_all("a"):
        href = a.get("href")
        if not href: 
            continue
        if href.startswith("#"):
            name = href[1:]
            if not soup.find(id=name) and not soup.find(attrs={"name": name}):
                errors += 1
                print(f"[internal-anchor-missing] {p}:{href}")
        elif href.startswith(("http://","https://")):
            if not EXTERNALS: 
                continue
            try:
                r = requests.head(href, allow_redirects=True, timeout=10)
                if r.status_code >= 400:
                    errors += 1
                    print(f"[external-bad] {p}:{href} -> {r.status_code}")
            except Exception as e:
                errors += 1
                print(f"[external-error] {p}:{href} -> {e}")
        else:
            if not (p.parent / href).exists():
                errors += 1
                print(f"[internal-missing] {p}:{href}")
    return errors

def main():
    if not DOCS.exists():
        print("docs/ missing; nothing to verify")
        return 0
    total = 0
    for p in DOCS.rglob("*.html"):
        total += check_html(p)
    if total and HINTS:
        print("\nHINT: Create docs/_fixed_preview and place repaired files there to use with the preview workflow.")
    print(f"Done. link_issues={total}")
    return 0 if total == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
