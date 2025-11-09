#!/usr/bin/env python3
# Adds a Docs Health CI: markdown lint, link check, strict mkdocs build, nav sanity

from pathlib import Path

ROOT = Path(__file__).resolve().parent

WORKFLOW = """name: Docs Health

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - '.github/workflows/docs-health.yml'
      - '.markdownlint.*'
      - 'lychee.toml'
  pull_request:
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - '.github/workflows/docs-health.yml'
      - '.markdownlint.*'
      - 'lychee.toml'
  schedule:
    - cron: '17 3 * * *'  # daily 03:17 UTC
  workflow_dispatch:

permissions:
  contents: read

jobs:
  markdownlint:
    name: Markdown Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: markdownlint-cli2
        uses: DavidAnson/markdownlint-cli2-action@v17
        with:
          globs: |
            **/*.md
          config: .markdownlint.jsonc
          fix: false

  links:
    name: Link Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: lychee link checker
        uses: lycheeverse/lychee-action@v2
        with:
          args: >
            --config lychee.toml
            --verbose
            --no-progress
            --accept 200,204,206,429
            .
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  mkdocs_strict:
    name: MkDocs Strict Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install MkDocs & plugins
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.docs.txt ]; then
            pip install -r requirements.docs.txt
          else
            pip install mkdocs mkdocs-material
          fi
      - name: Build (strict)
        run: mkdocs build --clean --strict

  nav_sanity:
    name: Nav Sanity (mkdocs.yml)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Check nav files exist
        run: |
          python .github/scripts/verify_mkdocs_nav.py
"""

MARKDOWNLINT = """{
  // markdownlint-cli2 config (JSONC)
  "config": {
    "MD013": { "line_length": 120, "code_blocks": false, "tables": false },
    "MD033": { "allowed_elements": ["br", "sub", "sup", "kbd", "img"] },
    "MD041": false
  },
  "ignores": [
    "site/**",
    "dist/**",
    "static/**",
    "node_modules/**"
  ]
}
"""

LYCHEE = """# lychee link checker config
# Docs: https://github.com/lycheeverse/lychee
exclude = [
  "mailto:*",
  "tel:*"
]

# Don’t fail the build on transient flakiness; 429 = rate-limited
accept = [200, 204, 206, 429]

# Treat GitHub Pages build URLs and localhost previews as OK
include_verbatim = true

[headers]
# Add any custom headers if needed, e.g.,
# "https://example.com" = { Authorization = "Bearer $TOKEN" }

[github]
exclude_private = true
"""

VERIFY_NAV = r"""# .github/scripts/verify_mkdocs_nav.py
import sys, os
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    print("Installing PyYAML ...", file=sys.stderr)
    os.system("python -m pip install pyyaml >/dev/null 2>&1")
    import yaml  # type: ignore

ROOT = Path(__file__).resolve().parents[2]  # repo root
mk = ROOT / "mkdocs.yml"
docs = ROOT / "docs"

def iter_nav_items(nav):
    if isinstance(nav, list):
        for item in nav:
            yield from iter_nav_items(item)
    elif isinstance(nav, dict):
        for _, v in nav.items():
            if isinstance(v, str):
                yield v
            else:
                yield from iter_nav_items(v)

if not mk.exists():
    print("mkdocs.yml not found; skipping.", file=sys.stderr)
    sys.exit(0)

cfg = yaml.safe_load(mk.read_text(encoding="utf-8"))
nav = cfg.get("nav", [])
missing = []
for rel in iter_nav_items(nav):
    if rel.startswith("http://") or rel.startswith("https://"):
        continue
    p = docs / rel
    if not p.exists():
        missing.append(rel)

if missing:
    print("❌ mkdocs.yml references missing files:\n  - " + "\n  - ".join(missing))
    sys.exit(1)

print("✅ mkdocs nav sanity: all referenced files exist.")
"""

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"→ wrote {path}")

def main():
    write(ROOT / ".github" / "workflows" / "docs-health.yml", WORKFLOW)
    write(ROOT / ".markdownlint.jsonc", MARKDOWNLINT)
    write(ROOT / "lychee.toml", LYCHEE)
    write(ROOT / ".github" / "scripts" / "verify_mkdocs_nav.py", VERIFY_NAV)
    print("\n✅ Docs Health CI installed.")
    print("Runs on: push/PR to docs, nightly, and manual dispatch.")

if __name__ == "__main__":
    main()