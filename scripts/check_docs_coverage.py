#!/usr/bin/env python3
import os, re, json, sys, urllib.request
OWNER = os.getenv("OWNER", "m9dswyptrn-web")
REPO  = os.getenv("REPO",  "SonicBuilder")
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
PATTERN_DARK  = os.getenv("DOCS_ASSET_REGEX_DARK",  r"SonicBuilder_Manual_.*?_g[0-9a-fA-F]{7,8}.*(dark|DARK).*\.zip$")
PATTERN_LIGHT = os.getenv("DOCS_ASSET_REGEX_LIGHT", r"SonicBuilder_Manual_.*?_g[0-9a-fA-F]{7,8}.*(light|LIGHT).*\.zip$")
RE_DARK  = re.compile(PATTERN_DARK)
RE_LIGHT = re.compile(PATTERN_LIGHT)
def gh_json(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())
def latest_release(owner, repo):
    return gh_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest")
def main():
    rel = latest_release(OWNER, REPO)
    tag = rel.get("tag_name", "unknown")
    assets = [a.get("name","") for a in rel.get("assets", [])]
    has_dark  = any(RE_DARK.search(n) for n in assets)
    has_light = any(RE_LIGHT.search(n) for n in assets)
    color = "brightgreen" if (has_dark and has_light) else ("orange" if (has_dark or has_light) else "red")
    msg   = f"{tag} dark+light" if (has_dark and has_light) else (f"{tag} partial" if (has_dark or has_light) else f"{tag} none")
    badge = {"schemaVersion":1, "label":"docs coverage","message":msg,"color":color,"labelColor":"2f363d"}
    os.makedirs("docs/status", exist_ok=True)
    with open("docs/status/docs_coverage_status.json","w",encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)
    print(json.dumps({"tag": tag, "has_dark": has_dark, "has_light": has_light, "assets": assets}, indent=2))
if __name__ == "__main__":
    sys.exit(main())
