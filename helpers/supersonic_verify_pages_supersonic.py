import sys, pathlib, requests
from bs4 import BeautifulSoup
ROOT = pathlib.Path("docs")
bad = []
if not ROOT.exists():
    print("docs/ not found; skipping verify"); sys.exit(0)
for html in ROOT.rglob("*.html"):
    soup = BeautifulSoup(html.read_text("utf-8", errors="ignore"), "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("http://","https://")):
            try:
                r = requests.head(href, allow_redirects=True, timeout=10)
                if r.status_code >= 400: bad.append((html, href, r.status_code))
            except Exception as e:
                bad.append((html, href, repr(e)))
        else:
            if not (html.parent / href).resolve().exists():
                bad.append((html, href, "missing"))
if bad:
    print("Broken links:"); [print(f" - {h}: {u} -> {s}") for h,u,s in bad]; sys.exit(1)
print("Docs verify passed.")
