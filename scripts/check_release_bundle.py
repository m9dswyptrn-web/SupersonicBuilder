#!/usr/bin/env python3
import json, os, re, sys, urllib.request

OWNER = os.getenv("OWNER", "m9dswyptrn-web")
REPO  = os.getenv("REPO",  "SonicBuilder")
ASSET_RE = re.compile(r"^SonicBuilder_Manual_v[0-9]+\.[0-9]+\.[0-9]+(?:[+A-Za-z0-9._-]+)?_g[0-9a-fA-F]{7,8}\.zip$")

def gh_json(url, token=None):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def latest_release(owner, repo, token=None):
    return gh_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", token=token)

def main():
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or os.getenv("TOKEN")
    rel   = latest_release(OWNER, REPO, token)
    tag   = rel.get("tag_name", "unknown")
    assets = rel.get("assets", [])
    found = []
    for a in assets:
        name = a.get("name", "")
        if ASSET_RE.match(name):
            found.append(name)

    if found:
        message = f"{tag} ✓"
        color   = "brightgreen"
    else:
        message = f"{tag} missing"
        color   = "red"

    badge = {
        "schemaVersion": 1,
        "label": "docs bundle",
        "message": message,
        "color": color,
        "labelColor": "2f363d"
    }

    os.makedirs("docs/status", exist_ok=True)
    with open("docs/status/docs_bundle_status.json", "w", encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)

    print(json.dumps({"tag": tag, "matching_assets": found}, indent=2))

if __name__ == "__main__":
    sys.exit(main())
