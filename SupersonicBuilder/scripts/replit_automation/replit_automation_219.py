#!/usr/bin/env python3
# changelog_bootstrap.py — Auto Changelog page + GitHub workflow

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CHANGELOG_MD = """# Changelog

This page is auto-generated from **GitHub Releases**.
- Draft notes are maintained by Release Drafter.
- When you publish a tag (e.g., `v1.0.0`), the release notes are synced here.

> Latest 30 releases are shown below. Older releases remain available on GitHub.
"""

WORKFLOW = """name: Docs: Sync Changelog from Releases
on:
  release:
    types: [published]

permissions:
  contents: write

jobs:
  build-changelog:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Build changelog (from GitHub Releases)
        env:
          GITHUB_OWNER: ${{ github.repository_owner }}
          GITHUB_REPO:  ${{ github.event.repository.name }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python .github/scripts/build_changelog.py

      - name: Commit changelog
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/changelog.md
          git commit -m "docs: update changelog from release ${{ github.event.release.tag_name }}" || echo "No changes"
          git push
"""

SCRIPT = r"""# .github/scripts/build_changelog.py
import os, sys, json, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

OWNER = os.environ.get("GITHUB_OWNER")
REPO  = os.environ.get("GITHUB_REPO")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

if not OWNER or not REPO:
    print("Missing GITHUB_OWNER/REPO", file=sys.stderr)
    sys.exit(1)

API = f"https://api.github.com/repos/{OWNER}/{REPO}/releases?per_page=30"
headers = {"Accept": "application/vnd.github+json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))

def md_escape(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")

releases = fetch(API)

out = []
out.append("# Changelog\n")
out.append("_Auto-generated from GitHub Releases. Edit release notes on GitHub; this page syncs on each published release._\n")

if not releases:
    out.append("\n_No releases found yet._\n")
else:
    for rel in releases:
        tag = rel.get("tag_name") or "untagged"
        name = rel.get("name") or tag
        url  = rel.get("html_url")
        created = rel.get("published_at") or rel.get("created_at")
        when = created or ""
        if when:
            try:
                dt = datetime.fromisoformat(when.replace("Z","+00:00")).astimezone(timezone.utc)
                when = dt.strftime("%Y-%m-%d")
            except Exception:
                pass
        out.append(f"\n## {name} ({tag}) — {when}\n")
        body = rel.get("body") or ""
        body = md_escape(body).strip()
        if body:
            out.append("\n" + body + "\n")
        else:
            out.append("\n_No notes provided._\n")
        assets = rel.get("assets") or []
        if assets:
            out.append("\n**Assets:**\n")
            for a in assets:
                a_name = a.get("name")
                a_url  = a.get("browser_download_url") or url
                size   = a.get("size") or 0
                # simple size formatting
                units = ["B","KB","MB","GB","TB"]; i=0; v=float(size)
                while v>=1024 and i<len(units)-1: v/=1024; i+=1
                size_s = f"{v:.0f} {units[i]}" if v>=10 else f"{v:.1f} {units[i]}"
                out.append(f"- [{a_name}]({a_url}) ({size_s})")
            out.append("")

Path("docs").mkdir(parents=True, exist_ok=True)
Path("docs/changelog.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("→ wrote docs/changelog.md")
"""

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"→ wrote {path}")

def patch_mkdocs():
    mk = ROOT / "mkdocs.yml"
    if not mk.exists():
        print("! mkdocs.yml not found; add 'changelog.md' manually to nav.")
        return
    text = mk.read_text(encoding="utf-8")

    # Ensure nav has an "About" or top-level section we can append near; otherwise, append at end.
    if "changelog.md" not in text:
        # Try to place under DevOps; else at end.
        if "  - DevOps:" in text:
            text = text.replace("  - DevOps:\n", "  - DevOps:\n      - Changelog: changelog.md\n", 1)
        else:
            if "\nnav:" in text:
                text = re.sub(r"(?ms)(nav:\s*\n)", r"\1  - Changelog: changelog.md\n", text, count=1)
            else:
                # As a last resort, append a nav with only Changelog
                text += "\nnav:\n  - Changelog: changelog.md\n"
        (ROOT / "mkdocs.yml").write_text(text, encoding="utf-8")
        print("→ patched mkdocs.yml (added Changelog to nav)")
    else:
        print("→ mkdocs.yml already references changelog.md (no change)")

def main():
    # Page + workflow + script
    write(ROOT / "docs" / "changelog.md", CHANGELOG_MD)
    write(ROOT / ".github" / "workflows" / "changelog-sync.yml", WORKFLOW)
    write(ROOT / ".github" / "scripts" / "build_changelog.py", SCRIPT)
    patch_mkdocs()
    print("\n✅ Changelog bootstrap complete.")
    print("Next: commit & push. On next tag publish, docs/changelog.md updates automatically.")

if __name__ == "__main__":
    main()