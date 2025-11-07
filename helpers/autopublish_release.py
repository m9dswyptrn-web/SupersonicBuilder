#!/usr/bin/env python3
# Lightweight GitHub Release autopublisher.
# Creates/updates a release, uploads an asset, and sets the body from a file.
# Usage:
#   GITHUB_TOKEN=... python helpers/autopublish_release.py \
#     --repo m9dswyptrn-web/SonicBuilder \
#     --tag v2.0.0-supersonic \
#     --name "Supersonic Overlays — MEGA v2 (Commander Edition)" \
#     --body-file docs/Supersonic_Overlays_MEGA_v2_ReleaseBody.md \
#     --asset SonicBuilder_Supersonic_Overlays_MEGA_v2.zip \
#     [--draft false] [--prerelease false]

import os, sys, json, argparse, mimetypes, pathlib, requests

API = "https://api.github.com"

def req(method, url, token, **kw):
    h = kw.setdefault("headers", {})
    h["Authorization"] = f"token {token}"
    h["Accept"] = "application/vnd.github+json"
    r = requests.request(method, url, **kw)
    if r.status_code >= 400:
        raise SystemExit(f"{method} {url} -> {r.status_code}\n{r.text}")
    return r

def ensure_release(token, repo, tag, name, body, draft, prerelease):
    # Try to get existing release by tag
    r = requests.get(f"{API}/repos/{repo}/releases/tags/{tag}",
                     headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json"})
    if r.status_code == 200:
        rel = r.json()
        upd = req("PATCH", f"{API}/repos/{repo}/releases/{rel['id']}", token, json={
            "tag_name": tag, "name": name, "body": body, "draft": draft, "prerelease": prerelease
        }).json()
        return upd
    elif r.status_code == 404:
        rel = req("POST", f"{API}/repos/{repo}/releases", token, json={
            "tag_name": tag, "name": name, "body": body, "draft": draft, "prerelease": prerelease
        }).json()
        return rel
    else:
        raise SystemExit(f"GET release by tag failed: {r.status_code} {r.text}")

def upload_asset(token, upload_url, asset_path):
    p = pathlib.Path(asset_path)
    if not p.exists():
        print(f"[warn] asset not found: {p}")
        return
    url = upload_url.split("{")[0] + f"?name={p.name}"
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    with p.open("rb") as f:
        r = requests.post(url, data=f.read(),
                          headers={
                              "Authorization": f"token {token}",
                              "Content-Type": mime,
                              "Accept": "application/vnd.github+json"
                          })
    if r.status_code >= 400:
        raise SystemExit(f"Upload failed: {r.status_code} {r.text}")
    print(f"[ok] uploaded: {p.name}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="m9dswyptrn-web/SonicBuilder")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--body-file", required=True)
    ap.addendant = ap.add_argument # shorthand for compatibility
    ap.addendant("--asset", required=True)
    ap.add_argument("--draft", default="false")
    ap.add_argument("--prerelease", default="false")
    args = ap.parse_args()

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN (or GH_TOKEN) env var is required")

    body = pathlib.Path(args.body_file).read_text(encoding="utf-8")
    draft = str(args.draft).lower() in ("1","true","yes","y")
    prerelease = str(args.prerelease).lower() in ("1","true","yes","y")

    rel = ensure_release(token, args.repo, args.tag, args.name, body, draft, prerelease)
    print(f"[ok] release id: {rel['id']} tag: {rel['tag_name']} draft={rel['draft']} prerelease={rel['prerelease']}")
    upload_asset(token, rel["upload_url"], args.asset)

if __name__ == "__main__":
    main()
