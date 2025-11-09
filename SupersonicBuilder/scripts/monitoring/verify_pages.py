#!/usr/bin/env python3
import os, sys, json, time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

GH_USER = os.getenv("GH_USER", "m9dswyptrn-web")
GH_REPO = os.getenv("GH_REPO", "SonicBuilder")
BASE = f"https://{GH_USER}.github.io/{GH_REPO}"

ENDPOINTS = {
    "home": f"{BASE}/",
    "latest_pdf": f"{BASE}/downloads/latest.pdf",
    "pdf_health": f"{BASE}/docs/badges/pdf-health.json",
    "pages_deploy": f"{BASE}/docs/badges/pages-deploy.json",
    "last_updated": f"{BASE}/docs/badges/updated.json",
    "downloads_json": f"{BASE}/docs/badges/downloads.json",
    "latest_json": f"{BASE}/docs/badges/latest.json",
    "size_json": f"{BASE}/docs/badges/size.json",
}

def head(url):
    try:
        req = Request(url, method="HEAD")
        with urlopen(req, timeout=15) as r:
            code = r.getcode()
            length = r.headers.get("Content-Length", "")
            return code, int(length) if length.isdigit() else None
    except Exception as e:
        return f"ERR:{type(e).__name__}", None

def get_json(url):
    try:
        with urlopen(url, timeout=20) as r:
            return r.getcode(), json.loads(r.read().decode("utf-8"))
    except HTTPError as e:
        return e.code, {"error": f"HTTP {e.code}"}
    except URLError as e:
        return "ERR", {"error": f"URL error {e.reason}"}
    except Exception as e:
        return "ERR", {"error": str(e)}

def main():
    lines = []
    lines.append(f"GitHub Pages Verification Report")
    lines.append(f"Repo: {GH_USER}/{GH_REPO}")
    lines.append(f"Base: {BASE}")
    lines.append(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    lines.append("")

    # Check home
    code, _ = head(ENDPOINTS["home"])
    lines.append(f"[home]             {code}  {ENDPOINTS['home']}")

    # Check latest.pdf
    code, size = head(ENDPOINTS["latest_pdf"])
    ok_pdf = (code == 200 and (size is None or size > 0))
    lines.append(f"[latest.pdf]       {code}  size={size}  ok={ok_pdf}  {ENDPOINTS['latest_pdf']}")

    # JSON endpoints
    for key in ("pdf_health", "pages_deploy", "last_updated", "downloads_json", "latest_json", "size_json"):
        code, js = get_json(ENDPOINTS[key])
        preview = js if isinstance(js, dict) else {"data": str(js)[:120]}
        # Keep preview compact
        preview_str = json.dumps(preview)[:300]
        lines.append(f"[{key}]")
        lines.append(f"  Status: {code}")
        lines.append(f"  URL: {ENDPOINTS[key]}")
        lines.append(f"  JSON: {preview_str}")
        lines.append("")

    report = "\n".join(lines)
    with open("pages_verification_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print("\n✅ Saved: pages_verification_report.txt")

if __name__ == "__main__":
    sys.exit(main())
