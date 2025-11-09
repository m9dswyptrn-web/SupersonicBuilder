#!/usr/bin/env python3
import os, json, argparse, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sh(cmd, check=True):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return out.decode("utf-8","ignore").strip()
    except subprocess.CalledProcessError as e:
        if check: raise
        return e.output.decode("utf-8","ignore").strip()

def latest_tag():
    val = sh(["git","describe","--tags","--abbrev=0"], check=False)
    return val or "v0.0.0"

def guessed_repo():
    url = sh(["git","config","--get","remote.origin.url"], check=False)
    if url.endswith(".git"): url=url[:-4]
    return url

def pages_url(tag):
    # best-effort Pages guess; workflow rewrites as needed
    repo = guessed_repo()
    # convert SSH/HTTPS to https web
    if repo.startswith("git@"):
        _, host_path = repo.split(":",1)
        host = "github.com"
        web = f"https://{host}/{host_path}"
    else:
        web = repo.replace("git://","https://").replace("http://","https://")
    try:
        parts = web.split("github.com/")[1]
        user, name = parts.split("/",1)
        return f"https://{user}.github.io/{name}/{tag}/"
    except Exception:
        return web

def release_url(tag):
    repo = guessed_repo().replace(".git","").replace("git@github.com:","https://github.com/").replace("git://","https://").replace("http://","https://")
    if "github.com" not in repo:
        return repo
    parts = repo.split("github.com/")[1]
    return f"https://github.com/{parts}/releases/tag/{tag}"

def post_json(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8","ignore")
    except Exception as e:
        print(f"[webhook] failed for {url}: {e}")
        return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", default="SonicBuilder_Supersonic_Overlays_MEGA_v2.zip")
    args = ap.parse_args()

    tag = latest_tag()
    rel = release_url(tag)
    pages = pages_url(tag)

    summary = ""
    log = (ROOT / "logs" / "supersonic_changelog.log")
    if log.exists():
        try: summary = log.read_text(encoding="utf-8").splitlines()[0][:300]
        except Exception: pass

    payload = {
        "project": "SonicBuilder Supersonic",
        "version": tag,
        "asset": args.asset,
        "summary": summary or "Build complete.",
        "release_url": rel,
        "preview_url": pages
    }

    disc = os.getenv("SUP_DISCORD_WEBHOOK","").strip()
    slack = os.getenv("SUP_SLACK_WEBHOOK","").strip()

    if disc:
        d_payload = {"content": f"**{payload['project']}** {payload['version']}\\n{payload['summary']}\\nRelease: {payload['release_url']}\\nPreview: {payload['preview_url']}"}
        post_json(disc, d_payload)
    if slack:
        s_payload = {"text": f"*{payload['project']}* {payload['version']}\n{payload['summary']}\nRelease: {payload['release_url']}\nPreview: {payload['preview_url']}"}
        post_json(slack, s_payload)

    print(json.dumps(payload, indent=2))

if __name__=="__main__":
    main()
