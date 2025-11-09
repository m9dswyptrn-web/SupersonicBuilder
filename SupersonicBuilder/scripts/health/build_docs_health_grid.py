#!/usr/bin/env python3
import os, json, urllib.request, sys, re, pathlib

OWNER = os.getenv("OWNER", "m9dswyptrn-web")
REPO  = os.getenv("REPO",  "SonicBuilder")
BRANCH = os.getenv("BRANCH", "HEAD")
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"

BADGES = {
    "Docs Build":       f"https://github.com/{OWNER}/{REPO}/actions/workflows/docs-build.yml",
    "Docs Release":     f"https://github.com/{OWNER}/{REPO}/actions/workflows/docs-release.yml",
    "Pages Smoke":      f"{RAW}/docs/badges/pages_smoke.json",
    "Docs Coverage":    f"{RAW}/docs/badges/docs_coverage.json",
    "Guard Status":     f"{RAW}/docs/badges/guard_status.json",
}

def fetch_json(url):
    req = urllib.request.Request(url, headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def ok_color(color):
    return color in ("brightgreen", "green")

def eval_status():
    result = {}
    overall_ok = True
    for key, url in BADGES.items():
        if url.endswith(".json"):
            try:
                data = fetch_json(url)
                color = data.get("color","lightgrey")
                msg   = data.get("message","unknown")
                good  = ok_color(color)
                overall_ok = overall_ok and good
                result[key] = {"type":"json","url":url,"color":color,"message":msg,"ok":good}
            except Exception as e:
                result[key] = {"type":"json","url":url,"error":str(e),"ok":False}
                overall_ok = False
        else:
            result[key] = {"type":"actions","url":url,"ok":None}
    return overall_ok, result

def build_overall_badge(overall_ok):
    badge = {"schemaVersion":1,"label":"docs health","message":"ok" if overall_ok else "attention","color":"brightgreen" if overall_ok else "orange","labelColor":"2f363d"}
    pathlib.Path("docs/badges").mkdir(parents=True, exist_ok=True)
    with open("docs/badges/docs_health.json","w",encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)
    return badge

def grid_block(owner, repo):
    parts = []
    parts.append("<!-- SONICBUILDER:DOCS-HEALTH:START -->")
    parts.append("### 📊 Docs Health Dashboard")
    parts.append("")
    parts.append("<table>")
    parts.append("<tr>")
    parts.append(f'  <td><a href="https://github.com/{owner}/{repo}/actions/workflows/docs-build.yml">\n    <img alt="Docs Build" src="https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/docs-build.yml?label=Docs%20Build&logo=github">\n  </a></td>')
    parts.append(f'  <td><a href="https://github.com/{owner}/{repo}/actions/workflows/docs-release.yml">\n    <img alt="Docs Release" src="https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/docs-release.yml?label=Docs%20Release&logo=github">\n  </a></td>')
    parts.append("</tr>")
    parts.append("<tr>")
    parts.append(f'  <td><img alt="Pages Smoke" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/{owner}/{repo}/HEAD/docs/badges/pages_smoke.json"></td>')
    parts.append(f'  <td><img alt="Docs Coverage" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/{owner}/{repo}/HEAD/docs/badges/docs_coverage.json"></td>')
    parts.append("</tr>")
    parts.append("<tr>")
    parts.append(f'  <td><img alt="Post-Release Guard" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/{owner}/{repo}/HEAD/docs/badges/guard_status.json"></td>')
    parts.append(f'  <td><img alt="Docs Health" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/{owner}/{repo}/HEAD/docs/badges/docs_health.json"></td>')
    parts.append("</tr>")
    parts.append("</table>")
    parts.append("")
    parts.append("<!-- SONICBUILDER:DOCS-HEALTH:END -->")
    return "\n".join(parts)

def write_readme_block(block):
    path = pathlib.Path("README.md")
    text = path.read_text(encoding="utf-8") if path.exists() else "# SonicBuilder\n\n"
    start = "<!-- SONICBUILDER:DOCS-HEALTH:START -->"
    end   = "<!-- SONICBUILDER:DOCS-HEALTH:END -->"
    if start in text and end in text:
        import re
        text = re.sub(start + r"[\s\S]*?" + end, block, text, flags=re.M)
    else:
        lines = text.splitlines()
        if lines and lines[0].startswith("# "):
            lines.insert(1, "\n" + block + "\n")
            text = "\n".join(lines)
        else:
            text = block + "\n\n" + text
    path.write_text(text, encoding="utf-8")

def main():
    ok, details = eval_status()
    build_overall_badge(ok)
    block = grid_block(OWNER, REPO)
    write_readme_block(block)
    print(json.dumps({"overall_ok": ok, "details": details}, indent=2))

if __name__ == "__main__":
    main()