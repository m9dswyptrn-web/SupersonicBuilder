#!/usr/bin/env bash
set -euo pipefail

echo "==> Generating v2.4.0 release bundle..."

mkdir -p docs .github/workflows docs/sonic/android15_board assets

########################################
# 1. RELEASE NOTES
########################################
cat > docs/RELEASE_NOTES_v2.4.0.md << 'NOTES'
# Supersonic v2.4.0 – Deployment-Ready Release

## Highlights

- **Full health monitoring stack**
  - Port + file health probes (`./rs health`)
  - Metrics generator & badges (`./rs metrics`, `./rs metrics-plus`)
  - Log rotation & compression

- **Autonomy + Self-Heal Enhancements**
  - `./rs guard` loop with automatic restart on failure
  - Watchdog for RAM/CPU with webhook + email hooks
  - Doctor/Doctor-Plus orchestration (`./rs doctor`, `./rs doctor-plus`)

- **Car Install Mode (Chevy Sonic Integration)**
  - `./rs car-install on|off` – turn car mode on or off
  - Sonic install checklist (`./rs sonic-checklist show|export`)
  - Car metrics exporter (`./rs car-metrics` → `metrics/car_mode.json`)

- **Android 15 Board Map Integration**
  - Board photo pipeline ready for EOENKK Android 15 head unit
  - Placeholder doc: `docs/sonic/android15_board/BOARD_MAP_PLACEHOLDER.md`
  - CLI helper: `android15_board_setup.py` (used by build tools)

- **Docs & GitHub Readiness**
  - Expanded `README.md` & `replit.md`
  - Added `GITHUB_DEPLOYMENT.md` for deployment playbook
  - Security audit: .gitignore, env handling, basic secret hygiene

## New Commands (v2.4.0)

### Monitoring
- `./rs health`          – Probe ports/files → `logs/health.json`
- `./rs metrics`         – Refresh badges from health data
- `./rs metrics-plus`    – Full pipeline: health → metrics → Pages sync
- `./rs diag`            – Full diagnostic
- `./rs doctor-plus`     – Repo check + health + car install summary

### Autonomy + Guard
- `./rs launch-all`      – Start status server + shell bridge + board
- `./rs guard 5`         – 5s guard loop, auto heal on failure

### Car Install
- `./rs car-install on`  – Enable car install mode
- `./rs car-install off` – Disable car install mode
- `./rs sonic-checklist show`   – View Sonic install checklist
- `./rs sonic-checklist export` – Export to `metrics/sonic_checklist.json`
- `./rs car-metrics`     – Export car profile metrics

## GitHub Pages

- Metrics & health artifacts prepared for publication on GitHub Pages.
- See `.github/workflows/pages-metrics.yml` for automation.
- Default path: `gh-pages` branch → `/` site root.

## Upgrade Notes

- Existing configs are preserved wherever possible.
- Version file: `version.txt` set to `2.4.0`.
- If upgrading from pre-2.x:
  - Run `./rs doctor-plus` once after pulling.
  - Review `GITHUB_DEPLOYMENT.md` before first release.
NOTES

########################################
# 2. BOARD MAP PLACEHOLDER
########################################
cat > docs/sonic/android15_board/BOARD_MAP_PLACEHOLDER.md << 'BOARD'
# EOENKK Android 15 Head Unit – Board Map (Placeholder)

This document is the landing page for the EOENKK Android 15 head unit
circuit board photos and mapping.

## How to Use

1. Place your JPEG photos here:

   - `docs/sonic/android15_board/photos/front_*.jpg`
   - `docs/sonic/android15_board/photos/back_*.jpg`

2. Update this document with:

   - Labeled connector callouts
   - Power, ground, and speaker paths
   - Any PNP tap points we decide to use for the Sonic integration

3. The UI "Board Map" button in **Car Install Mode** will link here.

## File Layout (expected)

- `docs/sonic/android15_board/BOARD_MAP_PLACEHOLDER.md`
- `docs/sonic/android15_board/photos/`
  - `front_01.jpg`, `front_02.jpg`, ...
  - `back_01.jpg`, `back_02.jpg`, ...

Once the final map is created, this file can be renamed to
`BOARD_MAP.md` and the placeholder note removed.
BOARD

mkdir -p docs/sonic/android15_board/photos

########################################
# 3. README ADD-ON (BADGES + LINKS)
########################################
# Append a short GitHub-focused block if not already present.
if ! grep -q "Supersonic v2.4.0" README.md 2>/dev/null; then
  cat >> README.md << 'RMD'

---

## Supersonic v2.4.0 – GitHub Deployment

This repository is wired for:

- ✅ Full health monitoring & self-heal
- ✅ Car Install Mode for a 2014 Chevy Sonic + EOENKK Android 15 head unit
- ✅ GitHub Pages metrics dashboard
- ✅ Release preflight GitHub Actions

Key docs:

- `docs/RELEASE_NOTES_v2.4.0.md`
- `GITHUB_DEPLOYMENT.md`
- `docs/sonic/android15_board/BOARD_MAP_PLACEHOLDER.md`

See **GITHUB_DEPLOYMENT.md** for a step-by-step deployment guide.
RMD
fi

########################################
# 4. VERSION FILE
########################################
echo "2.4.0" > version.txt

########################################
# 5. GITHUB ACTIONS – PREFLIGHT CI
########################################
cat > .github/workflows/release-preflight.yml << 'YML'
name: Release Preflight

on:
  workflow_dispatch:
  push:
    branches: [ main ]

jobs:
  preflight:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run basic sanity imports
        run: |
          python -c "import main"
          python -c "import builder"
          python -c "import serve_pdfs"

      - name: Run metrics refresh (dry run)
        run: |
          if [ -f rs ]; then
            chmod +x rs
            ./rs health || true
          fi

      - name: Archive logs and metrics
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: preflight-artifacts
          path: |
            logs/**
            metrics/**
            docs/RELEASE_NOTES_v2.4.0.md
YML

########################################
# 6. GITHUB ACTIONS – PAGES METRICS
########################################
cat > .github/workflows/pages-metrics.yml << 'PAGES'
name: Metrics → GitHub Pages

on:
  workflow_dispatch:
  push:
    branches: [ main ]

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Generate metrics
        run: |
          if [ -f rs ]; then
            chmod +x rs
            ./rs health || true
            ./rs metrics || true
          fi

      - name: Prepare Pages content
        run: |
          mkdir -p public
          cp -r metrics public/metrics || true
          cp -r docs public/docs || true
          echo "<html><body><h1>Supersonic Metrics</h1><p>See /metrics and /docs.</p></body></html>" > public/index.html

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
PAGES

echo "==> v2.4.0 release bundle files generated."
