#!/usr/bin/env python3
"""
Setup default GitHub labels for a repo using the REST API.

Usage:
  export GITHUB_TOKEN=ghp_...   # repo admin or maintain access
  python scripts/setup_labels.py --repo your-org/your-repo
Optional:
  --labels .github/labels.yml
"""
import argparse, os, sys, json, time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Please: pip install requests")
    sys.exit(1)

def load_labels(path):
    text = Path(path).read_text(encoding="utf-8")
    labels = []
    current = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line: continue
        if line.startswith("- name:"):
            if current: labels.append(current); current = {}
            current["name"] = line.split(":",1)[1].strip()
        elif line.strip().startswith("color:"):
            current["color"] = line.split(":",1)[1].strip()
        elif line.strip().startswith("description:"):
            current["description"] = line.split(":",1)[1].strip()
    if current: labels.append(current)
    return labels

def upsert_label(session, repo, label):
    url = f"https://api.github.com/repos/{repo}/labels/{label['name']}"
    r = session.get(url)
    data = {"name": label["name"], "color": label["color"].lstrip("#"), "description": label.get("description","")}
    if r.status_code == 200:
        u = session.patch(url, json=data)
        print(f"UPDATE {label['name']}: {u.status_code}")
    else:
        url = f"https://api.github.com/repos/{repo}/labels"
        c = session.post(url, json=data)
        print(f"CREATE {label['name']}: {c.status_code}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="owner/repo")
    p.add_argument("--labels", default=".github/labels.yml")
    args = p.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN env var required. Create a classic token or use a PAT with 'repo' scope.")
        sys.exit(2)

    labels = load_labels(args.labels)
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}", "Accept":"application/vnd.github+json", "X-GitHub-Api-Version":"2022-11-28"})
    for lab in labels:
        upsert_label(s, args.repo, lab)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
