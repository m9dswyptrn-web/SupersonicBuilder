#!/usr/bin/env python3
# precommit_bootstrap.py — Local hooks for the same checks as CI (plus hygiene)

from pathlib import Path

ROOT = Path(__file__).resolve().parent

PRECOMMIT = """repos:
  # --- Core hygiene ---
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: mixed-line-ending
      - id: check-yaml
      - id: check-json
        args: [--verbose]

  # --- Docs: markdownlint-cli2 (via npx or Docker; soft-skip if unavailable) ---
  - repo: local
    hooks:
      - id: markdownlint-cli2
        name: markdownlint-cli2 (Markdown)
        entry: bash scripts/markdownlint.sh
        language: system
        pass_filenames: false
        files: ^(docs/|README\\.md|CHANGELOG\\.md|.*\\.md)$

  # --- Docs: lychee link checker (binary or Docker; soft-skip if unavailable) ---
      - id: lychee-links
        name: lychee (link checker)
        entry: bash scripts/lychee_check.sh
        language: system
        pass_filenames: false

  # --- Docs: strict mkdocs build (fails on warnings) ---
      - id: mkdocs-strict
        name: mkdocs build --strict
        entry: bash scripts/mkdocs_strict.sh
        language: system
        pass_filenames: false

  # --- Docs: mkdocs nav sanity (reuses CI script) ---
      - id: mkdocs-nav-sanity
        name: mkdocs nav sanity
        entry: python .github/scripts/verify_mkdocs_nav.py
        language: system
        pass_filenames: false
"""

MARKDOWNLINT_SH = r"""#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

# Prefer npx (no global install required)
if command -v npx >/dev/null 2>&1; then
  echo "▶ Running markdownlint-cli2 via npx..."
  npx -y markdownlint-cli2 '**/*.md' --config .markdownlint.jsonc
  exit 0
fi

# Fallback: Docker (if installed)
if command -v docker >/dev/null 2>&1; then
  echo "▶ Running markdownlint-cli2 via Docker..."
  docker run --rm -v "$PWD:/work" -w /work ghcr.io/igorshubovych/markdownlint-cli:latest \
    '**/*.md' --config .markdownlint.jsonc
  exit 0
fi

echo "⚠ markdownlint-cli2 not available (no npx/docker). Skipping lint locally."
exit 0
"""

LYCHEE_SH = r"""#!/usr/bin/env bash
set -euo pipefail

ARGS=(--verbose --no-progress --accept 200,204,206,429 .)
if [[ -f lychee.toml ]]; then
  ARGS=(--config lychee.toml "${ARGS[@]}")
fi

if command -v lychee >/dev/null 2>&1; then
  echo "▶ Running lychee..."
  lychee "${ARGS[@]}"
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  echo "▶ Running lychee (Docker)..."
  docker run --rm -v "$PWD:/work" -w /work lycheeverse/lychee:latest "${ARGS[@]}"
  exit 0
fi

echo "⚠ lychee not found (no binary/docker). Skipping link check locally."
exit 0
"""

MKDOCS_STRICT_SH = r"""#!/usr/bin/env bash
set -euo pipefail

# Install mkdocs if needed (prefers your repo's requirements)
if ! command -v mkdocs >/dev/null 2>&1; then
  echo "▶ Installing mkdocs (no mkdocs on PATH)..."
  python -m pip install --upgrade pip >/dev/null
  if [[ -f requirements.docs.txt ]]; then
    python -m pip install -r requirements.docs.txt >/dev/null
  else
    python -m pip install mkdocs mkdocs-material >/dev/null
  fi
fi

echo "▶ mkdocs build --clean --strict"
mkdocs build --clean --strict
"""

def write(path: Path, text: str, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | 0o111)
    print(f"→ wrote {path}")

def main():
    write(ROOT / ".pre-commit-config.yaml", PRECOMMIT)
    write(ROOT / "scripts" / "markdownlint.sh", MARKDOWNLINT_SH, executable=True)
    write(ROOT / "scripts" / "lychee_check.sh", LYCHEE_SH, executable=True)
    write(ROOT / "scripts" / "mkdocs_strict.sh", MKDOCS_STRICT_SH, executable=True)
    print("\n✅ Pre-commit config installed.")
    print("Next:")
    print("  pip install pre-commit && pre-commit install")
    print("  pre-commit run --all-files")

if __name__ == "__main__":
    main()