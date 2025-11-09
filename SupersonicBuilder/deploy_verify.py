#!/usr/bin/env python3
"""
Polls GitHub Actions runs until everything in the latest page is done.
Requires GH_TOKEN (or GITHUB_TOKEN) in Replit Secrets with repo + workflow scopes.
"""
import os, time, sys, requests

OWNER = os.getenv("GITHUB_USER", "m9dswyptrn-web")
REPO  = os.getenv("REPO_SLUG", "SonicBuilder")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

if not TOKEN:
    print("❌ Missing GH_TOKEN in Replit Secrets (scopes: repo, workflow).")
    sys.exit(1)

API = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs"

def fetch():
    r = requests.get(API, headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json"
    }, timeout=30)
    r.raise_for_status()
    return r.json().get("workflow_runs", [])[:8]

def line(name, st, concl, url):
    mark = "✅" if concl == "success" else ("❌" if st == "completed" else "🕓")
    print(f"{mark} {name:28} {(concl or st or '').upper():10}  {url}")

print("🔍 Watching latest workflows… (Ctrl+C to stop)")
all_good = False
for _ in range(100):  # ~75 minutes max (45s * 100)
    runs = fetch()
    completed = 0; failures = 0
    print("-"*92)
    for w in runs:
        line(w["name"], w["status"], w.get("conclusion"), w["html_url"])
        if w["status"] == "completed":
            completed += 1
            if w.get("conclusion") != "success":
                failures += 1
    if runs and completed == len(runs) and failures == 0:
        all_good = True
        break
    time.sleep(45)

print("\n" + ("✅ All workflows succeeded!" if all_good else "⚠️ Some workflows unfinished or failed."))
sys.exit(0 if all_good else 2)
