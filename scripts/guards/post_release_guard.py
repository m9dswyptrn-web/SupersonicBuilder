#!/usr/bin/env python3
import json, os, re, sys, urllib.request

OWNER = os.getenv("OWNER", "m9dswyptrn-web")
REPO  = os.getenv("REPO",  "SonicBuilder")
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("TOKEN")
# Expected assets (regex); tweak if your names differ
ASSET_REQ = [
    r"SonicBuilder_Manual_v[0-9]+\.[0-9]+\.[0-9]+.*_g[0-9a-fA-F]{7,8}.*dark.*\.pdf$",
    r"SonicBuilder_Manual_v[0-9]+\.[0-9]+\.[0-9]+.*_g[0-9a-fA-F]{7,8}.*light.*\.pdf$",
]
RE_ASSETS = [re.compile(p) for p in ASSET_REQ]

BADGE_ENDPOINTS = [
    f"https://raw.githubusercontent.com/{OWNER}/{REPO}/HEAD/docs/badges/pages_smoke.json",
    f"https://raw.githubusercontent.com/{OWNER}/{REPO}/HEAD/docs/badges/docs_coverage.json",
]

def gh_json(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def http_json(url):
    req = urllib.request.Request(url, headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def issues_create(title, body):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
    data = json.dumps({"title": title, "body": body}).encode()
    req = urllib.request.Request(url, data=data, headers={"Accept":"application/vnd.github+json","Content-Type":"application/json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def main():
    rel = gh_json(f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest")
    tag = rel.get("tag_name","unknown")
    assets = [a.get("name","") for a in rel.get("assets", [])]

    missing = []
    for rex in RE_ASSETS:
        if not any(rex.search(a) for a in assets):
            missing.append(rex.pattern)

    badge_errors = []
    for url in BADGE_ENDPOINTS:
        try:
            b = http_json(url)
            if not all(k in b for k in ("schemaVersion","color","message")):
                badge_errors.append(f"{url} (invalid schema)")
        except Exception as e:
            badge_errors.append(f"{url} ({e})")

    ok = (len(missing) == 0 and len(badge_errors) == 0)

    print(json.dumps({
        "tag": tag,
        "assets": assets,
        "missing_asset_patterns": missing,
        "badge_errors": badge_errors,
        "ok": ok
    }, indent=2))

    if ok:
        return 0

    title = f"[Guard] Post-release issues detected for {tag}"
    lines = []
    lines.append("Automated post-release guard detected problems.\n")
    lines.append(f"**Tag:** {tag}\n")
    lines.append("**Missing asset patterns:**")
    if missing:
        for m in missing: lines.append(f"- {m}")
    else:
        lines.append("- None")
    lines.append("\n**Badge errors:**")
    if badge_errors:
        for b in badge_errors: lines.append(f"- {b}")
    else:
        lines.append("- None")
    lines.append("""

**Suggestions**
- Re-run Docs Release workflow, or
- Verify artifact names in dist/ match required regex (dark/light PDF), and
- Ensure badges JSON written to docs/badges/ by workflows.

> This issue was created automatically by scripts/guards/post_release_guard.py
""")
    body = "\n".join(lines)
    try:
        issues_create(title, body)
        print("Issue opened for post-release anomalies.")
    except Exception as e:
        print(f"WARNING: failed to open issue: {e}")
    return 1

if __name__ == "__main__":
    sys.exit(main())