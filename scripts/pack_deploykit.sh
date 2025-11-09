#!/usr/bin/env bash
set -euo pipefail

KIT_NAME="SonicBuilder_Complete_DeployKit_v1"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="dist/${KIT_NAME}_${STAMP}.zip"

echo "==> Creating DeployKit: $OUT"
mkdir -p dist/.kit

# Core sources
rsync -av --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.mypy_cache' \
  --exclude '.pytest_cache' \
  --exclude 'dist' \
  ./ dist/.kit/src/

# Minimal .env template (no secrets)
cat > dist/.kit/ENV_TEMPLATE <<'EOF'
# --- SonicBuilder DeployKit (.env template) ---
# Fill these in before running `make ship`
GIT_USER_NAME=
GIT_USER_EMAIL=
GIT_REMOTE=https://github.com/m9dswyptrn-web/SonicBuilder.git
GH_TOKEN=        # fine-grained token
EOF

# Quick start doc
cat > dist/.kit/DEPLOYKIT_README.md <<'EOF'
# SonicBuilder Complete DeployKit

## What's inside
- Full project sources (minus build caches)
- `.env` template for local/CI secrets
- One-shot deploy commands (below)

## One-shot (local/CLI)
1) `python3 -m venv .venv && source .venv/bin/activate`
2) `pip install -r requirements.txt`
3) `cp dist/.kit/ENV_TEMPLATE .env` and fill values
4) `make init`
5) `make ship`

## One-shot (Replit)
1) Upload this ZIP, unpack to project root
2) Put your token in **Secrets** as `GH_TOKEN`
3) Open shell and run: `make ship`

Artifacts will appear in GitHub Releases and GitHub Pages.
EOF

# Compress
(cd dist/.kit && zip -r ../tmp.zip . >/dev/null)
mkdir -p dist
mv dist/tmp.zip "$OUT"
rm -rf dist/.kit

echo "==> Done: $OUT"
