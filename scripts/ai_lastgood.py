#!/usr/bin/env python3
import subprocess, json, os

def gh_json(cmd):
    out = subprocess.check_output(cmd, shell=True, text=True)
    return json.loads(out.strip())

repo = subprocess.check_output("gh repo view --json nameWithOwner --jq .nameWithOwner", shell=True, text=True).strip()
tag = subprocess.check_output("gh release list --limit 1 --json tagName --jq '.[0].tagName'", shell=True, text=True).strip()
if not tag:
    print("⚠️  No releases found.")
    exit(1)

user, name = repo.split("/")
pages_url = f"https://{user}.github.io/{name}/{tag}/"
release_url = f"https://github.com/{repo}/releases/tag/{tag}"

print(f"\n🟢 Last Known Good (LKG): {tag}")
print(f"🌐 Pages:   {pages_url}")
print(f"📦 Release: {release_url}")

try:
    info = gh_json('gh run list --limit 1 --json name,conclusion,updatedAt')
    if info:
        run = info[0]
        print(f"🧩 Last pipeline: {run['name']} → {run['conclusion']} @ {run['updatedAt']}")
except Exception as e:
    print("ℹ️  Could not fetch pipeline info:", e)

os.system(f"open {pages_url} || xdg-open {pages_url}")
