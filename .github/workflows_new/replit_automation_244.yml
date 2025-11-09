#!/usr/bin/env python3
# security_bootstrap.py — Wire up CodeQL, dependency audits, secret scan, Dependabot (idempotent)

from pathlib import Path

ROOT = Path(__file__).resolve().parent

CODEQL = """name: Security: CodeQL

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '17 2 * * 1'  # weekly Monday 02:17 UTC
  workflow_dispatch:

permissions:
  contents: read
  security-events: write

jobs:
  analyze:
    name: CodeQL Analyze
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        language: [ 'python', 'javascript' ]
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
"""

DEP_AUDIT = """name: Security: Dependency Audit (pip-audit + Safety)

on:
  push:
    paths:
      - 'requirements*.txt'
      - 'pyproject.toml'
      - '.github/workflows/security-deps.yml'
  schedule:
    - cron: '33 3 * * *'   # daily 03:33 UTC
  workflow_dispatch:

permissions:
  contents: read

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: |
          python -m pip install --upgrade pip
          pip install pip-audit safety

      - name: Resolve dependencies (best-effort)
        run: |
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt || true
          fi

      - name: pip-audit (advisory DB)
        run: |
          pip-audit -r requirements.txt || pip-audit || true

      - name: Safety (vuln DB)
        run: |
          if [ -f requirements.txt ]; then
            safety check -r requirements.txt --full-report
          else
            echo "No requirements.txt; running safety against environment"
            safety check --full-report
          fi
"""

SECRETS = """name: Security: Secrets Scan (Gitleaks)

on:
  push:
  pull_request:
  schedule:
    - cron: '7 4 * * *'    # daily 04:07 UTC
  workflow_dispatch:

permissions:
  contents: read
  security-events: write

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          args: detect --source . --no-banner --redact --report-format sarif --report-path gitleaks.sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: gitleaks.sarif
"""

DEPENDABOT = """version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    labels: ["deps", "security"]
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels: ["deps", "ci"]
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    labels: ["deps", "web"]
"""

AUTOMERGE = """name: Dependabot Auto-merge

on:
  pull_request:
    types: [opened, synchronize, reopened]
  check_suite:
    types: [completed]
  workflow_run:
    workflows: ["Supersonic CI", "Docs (MkDocs)", "Docs Health"]
    types: [completed]

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - name: Dependabot metadata
        id: meta
        uses: dependabot/fetch-metadata@v2
        with:
          github-token: "${{ secrets.GITHUB_TOKEN }}"
      - name: Enable auto-merge if allowed
        run: |
          echo "PR: ${{ github.event.pull_request.html_url }}"
          gh pr merge --auto --rebase "$PR_URL"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_URL: ${{ github.event.pull_request.html_url }}
"""

PRECOMMIT_SEC = """# --- Security additions ---
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.10
  hooks:
    - id: bandit
      args: [-r, .]
- repo: https://github.com/codespell-project/codespell
  rev: v2.3.0
  hooks:
    - id: codespell
      args: ["-L", "crate,nd,te,ser,fo,ba"]  # common false-positives; edit as needed
"""

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"→ wrote {path}")

def merge_precommit_security():
    pc = ROOT / ".pre-commit-config.yaml"
    if not pc.exists():
        print("! .pre-commit-config.yaml not found (skipping security additions). Run your precommit bootstrap first.")
        return
    cur = pc.read_text(encoding="utf-8")
    if "bandit" in cur and "codespell" in cur:
        print("→ pre-commit already has bandit + codespell")
        return
    pc.write_text(cur.rstrip() + "\n\n" + PRECOMMIT_SEC + "\n", encoding="utf-8")
    print("→ added bandit + codespell to pre-commit")

def main():
    write(ROOT / ".github" / "workflows" / "codeql.yml", CODEQL)
    write(ROOT / ".github" / "workflows" / "security-deps.yml", DEP_AUDIT)
    write(ROOT / ".github" / "workflows" / "secrets-gitleaks.yml", SECRETS)
    write(ROOT / ".github" / "dependabot.yml", DEPENDABOT)
    write(ROOT / ".github" / "workflows" / "dependabot-automerge.yml", AUTOMERGE)
    merge_precommit_security()
    print("\n✅ Security pack installed.\n- CodeQL (Python + JS)\n- Dependency audits (pip-audit + Safety)\n- Gitleaks secret scan (SARIF)\n- Dependabot (pip, actions, npm) + auto-merge\n")

if __name__ == "__main__":
    main()