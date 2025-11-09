PY ?= python

# SonicBuilder modular makefile (local helpers + CI-parity targets)
-include make/sonicbuilder.mk
-include Makefile.smoketest.addon

-include make_patches/MAKEFRAG.urls
-include make_patches/MAKEFRAG.repo
-include make_patches/MAKEFRAG.two_up_qr
-include make_patches/MAKEFRAG.onebutton
-include MAKEFRAG.version_hint
-include MAKEFRAG.docs

.PHONY: build_dark build_light release_local verify ingest_schematics index_diagrams two_up_raster parts_tools parts_tools_light release_notes seal certificate bump stamp_meta all i2s_index i2s_qr i2s_qr_2up appendix_pdf init build-docs verify-docs nextgen_appendix final_manual_pro pro_cover parts_sheet appendix_wiring build-all

build_dark: index_diagrams
        $(PY) scripts/builder.py

build_light: index_diagrams
        $(PY) scripts/builder.py --light

release_local: build_dark build_light parts_tools parts_tools_light
        @mkdir -p dist
        @cp -f output/*.pdf dist/ 2>/dev/null || true
        @cd dist && rm -f SHA256SUMS.txt && for f in *.pdf; do sha256sum "$$f" >> SHA256SUMS.txt 2>/dev/null; done || true
        @$(MAKE) release_notes
        @echo "[ok] dist ready with release notes"

verify:
        @echo "== Verifying environment =="
        @$(PY) scripts/verify_setup.py

ingest_schematics:
        @echo "== Ingesting schematics from assets/schematics_drop_here =="
        @$(PY) scripts/import_schematics.py

index_diagrams:
        @echo "== Generating Wiring Diagram Index =="
        @$(PY) scripts/gen_wiring_index.py

two_up_raster:
        @echo "== Building two-up raster from dark manual =="
        @$(PY) scripts/rasterize_pdf.py --pdf output/supersonic_manual_dark.pdf --outdir output/raster_dark
        @$(PY) scripts/two_up_raster.py --png-dir output/raster_dark --out output/supersonic_manual_two_up_dark.pdf
        @echo "[ok] two-up ready: output/supersonic_manual_two_up_dark.pdf"

parts_tools:
        @$(PY) scripts/gen_parts_tools.py --yaml parts_tools.yaml --out output/parts_tools_dark.pdf

parts_tools_light:
        @$(PY) scripts/gen_parts_tools.py --yaml parts_tools.yaml --out output/parts_tools_light.pdf --light

release_notes:
        @$(PY) scripts/gen_release_notes.py --dist dist
        @echo "[ok] Release notes generated at dist/RELEASE_NOTES.md"

# DocsPipeline integration targets
init:
        @echo "== Initializing environment =="
        @$(PY) -m pip install --upgrade pip
        @$(PY) -m pip install -r requirements.txt
        @echo "✅ init complete"

build-docs:
        @echo "== Building SuperSonic manual =="
        @$(PY) scripts/supersonic_build_all.py --version v2.1.0-SB-4P
        @echo "✅ build-docs complete"

verify-docs:
        @echo "== Verifying docs =="
        @$(PY) scripts/verify_docs.py out/SonicBuilder_Supersonic_Manual_v2.1.0-SB-4P.pdf
        @echo "✅ verify-docs complete"

# NextGen Engineering Appendix (v2.2.0-SB-NEXTGEN)
nextgen_appendix:
        @echo "== Building NextGen Engineering Appendix =="
        @$(PY) scripts/make_nextgen_appendix.py --in docs/nextgen --out out/NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf --theme dark
        @echo "✅ NextGen appendix complete"

# Build everything: core manual + NextGen appendix
build-all:
        @echo "== Building Complete Documentation Set =="
        @$(MAKE) --no-print-directory build-docs
        @$(MAKE) --no-print-directory nextgen_appendix
        @echo "✅ build-all complete"
        @echo "📦 Output files:"
        @ls -lh out/SonicBuilder_Supersonic_Manual_v2.1.0-SB-4P.pdf 2>/dev/null || echo "  ⚠️  Core manual not found"
        @ls -lh out/NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf 2>/dev/null || echo "  ⚠️  NextGen appendix not found"

# PRO manual component generators
pro_cover:
        @echo "== Generating PRO cover page =="
        @$(PY) scripts/make_pro_cover.py

parts_sheet:
        @echo "== Generating parts sheet =="
        @$(PY) scripts/make_parts_sheet_simple.py

appendix_wiring:
        @echo "== Generating wiring appendix =="
        @$(PY) scripts/make_appendix_wiring.py

# Complete PRO manual assembly
final_manual_pro:
        @echo "== Building Complete PRO Manual =="
        @$(MAKE) --no-print-directory pro_cover
        @$(MAKE) --no-print-directory parts_sheet
        @$(MAKE) --no-print-directory build-docs
        @$(MAKE) --no-print-directory appendix_wiring
        @$(MAKE) --no-print-directory nextgen_appendix
        @$(PY) scripts/merge_pdfs.py --pro --theme dark
        @echo "✅ final_manual_pro complete"

seal:
        @echo "== Generating SonicBuilder Official Seal =="
        @mkdir -p Founder_Seal
        @$(PY) scripts/gen_seal.py
        @echo "[ok] Seal assets generated in Founder_Seal/"

certificate:
        @echo "== Generating Founder Certificate #0001 =="
        @mkdir -p certificates
        @$(PY) scripts/gen_founder_certificate.py
        @echo "[ok] Certificates generated in certificates/"

# ===== Local Docs Build/Release System (with commit stamping) =====
# Version detection (tag > VERSION file > default)
VERSION ?= $(shell \
        (git describe --tags --abbrev=0 2>/dev/null) || \
        (tr -d '\r\n' < VERSION 2>/dev/null) || \
        echo v2.0.9+SB-appendix-demo \
)
COMMIT ?= $(shell git rev-parse --short=12 HEAD 2>/dev/null || echo unknown)
BUILD_DATE ?= $(shell date -u +%Y-%m-%dT%H:%M:%SZ)
REPO_URL ?= $(shell git config --get remote.origin.url 2>/dev/null || echo unknown)
OUTPUT_DIR ?= release_assets

# Git clean guard
.PHONY: git_guard
git_guard:
        @echo "==> Checking working tree cleanliness..."
        @if [ -z "$$(git status --porcelain)" ]; then \
        echo "✅ Clean working tree"; \
        elif [ "$$ALLOW_DIRTY" = "1" ]; then \
        echo "⚠️  Dirty tree, but ALLOW_DIRTY=1 set — proceeding anyway"; \
        else \
        echo "❌ Working tree has uncommitted changes."; \
        echo "   Commit or stash changes, or run with ALLOW_DIRTY=1 to override."; \
        exit 1; \
        fi

# Build docs locally (same as CI)
.PHONY: docs_build_local
docs_build_local:
        @mkdir -p $(OUTPUT_DIR)
        @echo "==> Building docs for $(VERSION) (commit g$(COMMIT))"
        @$(PY) -m pip install -q reportlab pypdf pillow qrcode pdf2image 2>/dev/null || true
        @SB_VERSION="$(VERSION)" SB_COMMIT="$(COMMIT)" SB_BUILD_DATE="$(BUILD_DATE)" SB_REPO="$(REPO_URL)" \
        $(MAKE) docs_ci VERSION="$(VERSION)" || { echo "ERROR: docs_ci failed"; exit 1; }

# Package artifacts (stamp, rename, zip, checksum)
.PHONY: docs_package_local
docs_package_local: docs_build_local
        @echo "==> Stamping PDF metadata (commit: g$(COMMIT))"
        @SB_VERSION="$(VERSION)" SB_COMMIT="$(COMMIT)" SB_BUILD_DATE="$(BUILD_DATE)" SB_REPO="$(REPO_URL)" \
        $(PY) scripts/stamp_commit_meta.py $(OUTPUT_DIR)
        @echo "==> Renaming PDFs to include commit hash"
        @cd $(OUTPUT_DIR) && for f in *.pdf; do \
        [ -f "$$f" ] || continue; \
        base=$${f%.pdf}; \
        mv "$$f" "$${base}_g$(COMMIT).pdf"; \
        done 2>/dev/null || true
        @echo "==> Creating zip archives"
        @cd $(OUTPUT_DIR) && for d in */; do \
        [ -d "$$d" ] || continue; \
        name=$${d%/}; \
        zip -rq "$${name}_g$(COMMIT).zip" "$$d"; \
        done 2>/dev/null || true
        @echo "==> Generating checksums"
        @cd $(OUTPUT_DIR) && rm -f *.sha256 SHA256SUMS.txt && \
        for f in *.pdf *.zip; do \
        [ -f "$$f" ] && shasum -a 256 "$$f" | awk '{print $$1"  "$$2}' >> SHA256SUMS.txt; \
        done 2>/dev/null || true
        @echo "==> Artifacts packaged:"
        @ls -lh $(OUTPUT_DIR)/*.pdf $(OUTPUT_DIR)/*.zip 2>/dev/null || true

# One-shot local release (with git guard)
.PHONY: docs_release_local
docs_release_local: git_guard docs_package_local
        @echo "==> ✅ Local release ready in $(OUTPUT_DIR) for $(VERSION)"
        @echo "    Total size: $$(du -sh $(OUTPUT_DIR) | awk '{print $$1}')"

# Preview Latest Docs README block
.PHONY: docs_latest_block
docs_latest_block:
        @echo "<!-- SB_LATEST_DOCS_BEGIN -->"
        @echo "### Latest documentation bundle"
        @echo ""
        @echo "**Release:** \`$(VERSION)\`"
        @echo "**Commit:** [g$(COMMIT)](https://github.com/OWNER/REPO/commit/$$(git rev-parse HEAD 2>/dev/null || echo $(COMMIT)))"
        @echo ""
        @echo "**View release:** https://github.com/OWNER/REPO/releases/tag/$(VERSION)"
        @echo ""
        @echo "| File | Size |"
        @echo "|---|---:|"
        @cd $(OUTPUT_DIR) 2>/dev/null && \
        for f in *.zip *.pdf; do \
        [ -f "$$f" ] && printf "| %s | %s |\n" "$$f" "$$(du -h "$$f" | awk '{print $$1}')"; \
        done 2>/dev/null || echo "| (no artifacts yet) | - |"
        @echo "<!-- SB_LATEST_DOCS_END -->"

# ===== Release Notes Preview Helpers =====
# Helper function for human-readable sizes
HUMAN := awk 'function human(n){split("B KB MB GB TB",u);i=1;while(n>=1024&&i<5){n/=1024;i++}printf "%.2f %s", n,u[i]} {print human($$1)}'

# Preview verified assets table (matches CI format)
.PHONY: assets_table_preview
assets_table_preview:
        @echo ""
        @echo "<!-- SB_ASSETS_TABLE_BEGIN -->"
        @echo "### Download assets (verified)"
        @echo ""
        @echo "| File | Size | SHA256 |"
        @echo "|---|---:|---|"
        @bash -c 'set -e; shopt -s nullglob; \
        for f in $(OUTPUT_DIR)/*; do \
        [ -f "$$f" ] || continue; \
        sz_bytes=$$(stat -c %s "$$f" 2>/dev/null || stat -f%z "$$f"); \
        sz_human=$$(echo $$sz_bytes | $(HUMAN)); \
        sha=$$(shasum -a 256 "$$f" | awk "{print $$1}"); \
        echo "| $${f##*/} | $$sz_human | \`$${sha:0:12}…\` |"; \
        done'
        @echo "<!-- SB_ASSETS_TABLE_END -->"

# Preview parts help (only shows if .zip.partNN files exist)
.PHONY: parts_help_preview
parts_help_preview:
        @echo "<!-- SB_PARTS_HELP_BEGIN -->"
        @echo "### How to reassemble multi-part ZIPs"
        @echo
        @echo "**macOS / Linux:**"
        @echo
        @echo '```bash'
        @echo 'cat <file>.zip.part* > <file>.zip'
        @echo 'unzip <file>.zip'
        @echo '```'
        @echo
        @echo "**Windows (PowerShell):**"
        @echo
        @echo '```powershell'
        @echo 'Get-ChildItem <file>.zip.part* | Get-Content -Encoding Byte -ReadCount 0 | Set-Content -Encoding Byte <file>.zip'
        @echo 'Expand-Archive .\\<file>.zip'
        @echo '```'
        @echo
        @echo "**Parts included:**"
        @echo
        @echo "| Part | Size |"
        @echo "|---|---:|"
        @bash -c 'set -e; shopt -s nullglob; \
        for f in $(OUTPUT_DIR)/*.zip.part*; do \
        sz=$$(du -h "$$f" | awk "{print \$$1}"); \
        echo "| $${f##*/} | $$sz |"; \
        done || true'
        @echo "<!-- SB_PARTS_HELP_END -->"

# Full release notes section preview (table + parts help if present)
.PHONY: release_notes_preview
release_notes_preview:
        @$(MAKE) --no-print-directory assets_table_preview
        @bash -c 'shopt -s nullglob; \
        parts=($$(ls $(OUTPUT_DIR)/*.zip.part* 2>/dev/null)); \
        if [ $${#parts[@]} -gt 0 ]; then \
        $(MAKE) --no-print-directory parts_help_preview; \
        fi'

# Write preview to file for sharing
.PHONY: release_notes_preview_md
release_notes_preview_md:
        @{ $(MAKE) --no-print-directory release_notes_preview; } > RELEASE_NOTES_PREVIEW.md
        @echo "Wrote RELEASE_NOTES_PREVIEW.md"

# ===== IDS Watch (v2.2.3) =====
# Auto-watch CAN logs and re-export ID artifacts
.PHONY: ids-watch
ids-watch:
        python tools/can/ids_watch.py --csv out/can_log.csv --jsonl out/teensy_raw.jsonl

# ===== Diagnostics (v1.0.0) =====
# Collect project state for troubleshooting
DIAG_OUT ?= diag/diag_bundle.zip
.PHONY: diag diag-pdf
diag:
        python tools/diag/diag_collect.py --out $(DIAG_OUT)

diag-pdf:
        python tools/diag/diag_collect.py --out $(DIAG_OUT) --include-pdf

# ===== Support Flow (v1.0.1) =====
# Chains CAN ID parse/export with support bundle creation
.PHONY: support-flow support-auto ids-flow support-bundle

# IDS flow: parse CAN logs and export artifacts
ids-flow:
        @echo "== Running IDS flow =="
        @if [ -n "$(IDS_LOG)" ] && [ -f "$(IDS_LOG)" ]; then \
        python tools/can/id_discovery_to_tags.py --in $(IDS_LOG) --out-prefix out/ids; \
        elif [ -n "$(IDS_JSONL)" ] && [ -f "$(IDS_JSONL)" ]; then \
        python tools/can/id_discovery_to_tags.py --jsonl $(IDS_JSONL) --out-prefix out/ids; \
        else \
        echo "Error: Set IDS_LOG=<csv> or IDS_JSONL=<jsonl>"; \
        exit 1; \
        fi
        @mkdir -p exports/ids
        @STAMP=$$(date +%Y%m%d_%H%M%S); \
        COMMIT=$$(git rev-parse --short HEAD 2>/dev/null || echo "no-git"); \
        EXPORT_DIR="exports/ids/$${STAMP}_$${COMMIT}"; \
        mkdir -p "$$EXPORT_DIR"; \
        cp out/ids_summary.csv "$$EXPORT_DIR/" 2>/dev/null || true; \
        cp out/ids_tag_template.json "$$EXPORT_DIR/" 2>/dev/null || true; \
        echo "✅ IDS artifacts exported to $$EXPORT_DIR"

# Support bundle: collect diagnostics
support-bundle:
        @echo "== Creating support bundle =="
        @mkdir -p support
        @python tools/diag/diag_collect.py --out support/support_bundle.zip
        @echo "✅ Support bundle: support/support_bundle.zip"

# Full support flow: ids-flow -> support-bundle
support-flow: ids-flow support-bundle
        @echo "✅ Support flow complete: see support/support_bundle.zip"

# Auto mode: watch CAN logs and run full flow on changes
support-auto:
        python tools/support/support_auto.py --csv out/can_log.csv --jsonl out/teensy_raw.jsonl

# Include diagnostics/support fragment
-include MAKEFRAG.support.mk

# ===== Supersonic Commander Operations =====
.PHONY: supersonic-rebuild supersonic-deploy supersonic-verify supersonic-verify-ext supersonic-preview-fix supersonic-promote supersonic-rollback supersonic-serve supersonic-audit

supersonic-rebuild:
        $(PY) supersonic_build_secure_all.py

supersonic-deploy:
        $(PY) supersonic_deploy_pages.py

supersonic-verify:
        $(PY) supersonic_verify_pages.py --hints

supersonic-verify-ext:
        $(PY) supersonic_verify_pages.py --hints --externals

supersonic-preview-fix:
        $(PY) supersonic_verify_autofix_preview.py

supersonic-promote:
        $(PY) supersonic_promote_preview.py

supersonic-rollback:
        @$(PY) supersonic_docs_rollback.py --list
        @echo "To restore: python supersonic_docs_rollback.py --use _backup_YYYYMMDD_HHMMSS --yes"

supersonic-serve:
        $(PY) supersonic_settings_server.py

supersonic-audit:
        @test -f docs/_ops_log.txt && tail -n 50 docs/_ops_log.txt || echo "No audit log yet"

# =====================================
# SonicBuilder AutoDeploy Makefile
# =====================================

.PHONY: ship deploy verify notify dryrun docs init clean preflight artifact-inventory

# --- Preflight & Artifact Inventory ------------------------------------------

preflight:
        @echo "🔎 Preflight: checking required tools and files..."
        @command -v git >/dev/null || (echo "❌ git missing"; exit 1)
        @command -v python3 >/dev/null || (echo "❌ python3 missing"; exit 1)
        @[ -n "$$(git config user.name || true)" ] || git config user.name "SonicBuilder AutoDeploy"
        @[ -n "$$(git config user.email || true)" ] || git config user.email "autodeploy@users.noreply.github.com"
        @echo "✅ Preflight OK"

artifact-inventory:
        @echo "📦 Artifact inventory (out/ and dist/):"
        @{ ls -lh out/*.pdf 2>/dev/null || true; ls -lh out/*.sha256 2>/dev/null || true; \
        ls -lh dist/*.pdf 2>/dev/null || true; }

# --- Deployment Pipeline -----------------------------------------------------

# Full deployment pipeline (with preflight)
ship: preflight deploy verify notify
        @echo "✅ SonicBuilder full deploy complete!"

# Deploy everything to GitHub
deploy:
        @echo "🚀 Deploying everything to GitHub..."
        $(PYTHON3) deploy_all_to_github.py

# Verify GitHub Actions workflows
verify:
        @echo "🔍 Verifying workflows..."
        @$(PYTHON3) -m pip install --quiet requests 2>/dev/null || true
        @$(PYTHON3) deploy_verify.py || echo "⚠️ Verification step failed (non-blocking)"

# Send webhook notifications
notify:
        @echo "📣 Sending notifications..."
        @$(PYTHON3) deploy_notify.py || echo "ℹ️ No webhooks configured"

# Dry run: test connection without pushing
dryrun:
        @echo "🧪 Dry run: testing GitHub connection..."
        @git remote -v
        @echo "✅ Remote configured for $(shell git config --get remote.origin.url 2>/dev/null || echo 'NOT SET')"

# Docs-only build and deploy (with preflight)
docs: preflight build_dark
        @echo "📚 Building docs with dark theme..."
        @$(MAKE) deploy verify notify

# Initialize environment
init:
        @echo "⚙️ Initializing environment..."
        @pip install -r requirements.txt
        @chmod +x deploy_chain.sh deploy_all_to_github.py deploy_verify.py deploy_notify.py
        @echo "✅ Environment ready!"

# Clean deployment artifacts
clean-deploy:
        @echo "🧹 Cleaning deployment artifacts..."
        @rm -f deploy_summary.json
        @rm -f *.log 2>/dev/null || true
        @echo "✅ Clean complete!"

# --- Web Gallery generation (HTML + lightbox) -------------------------------
WEB_GALLERY_HTML ?= docs/images/mobo_back/gallery.html

web-gallery:
        @python3 scripts/mobo_gallery_build_web.py
        @echo "✅ Web gallery rendered at $(WEB_GALLERY_HTML)"
# --- Docs Coverage Badge ---
coverage-badge:
        @python3 scripts/check_docs_coverage.py
        @echo "JSON badge written to docs/status/docs_coverage_status.json"
.PHONY: coverage-badge
# --- Pages Smoke Badge ---
pages-smoke-badge:
        @python3 scripts/pages_smoke_badge.py
        @echo "JSON badge written to docs/status/pages_smoke_status.json"
.PHONY: pages-smoke-badge

# --- DeployKit Packaging ---
.PHONY: package_deploykit
package_deploykit:
        @bash scripts/pack_deploykit.sh

# --- Theme Switch & PDF Previews ---
PREVIEW_PAGES ?= 6

.PHONY: build_dark_preview build_light_preview slice_preview
build_dark_preview: build_dark slice_preview
        @echo "Dark preview ready: dist/preview/"

build_light_preview: build_light slice_preview
        @echo "Light preview ready: dist/preview/"

slice_preview:
        @python3 scripts/tools/pdf_slice.py dist $(PREVIEW_PAGES) dist/preview

# --- README Badge Updater ---
.PHONY: badges
badges:
        @python3 scripts/update_readme_docs_badges.py
        @git add README.md || true
-include Makefrag.badges
# --- Release Addon (v2.0.10) ---
.PHONY: release_bump release_notes release_tag release_all

release_bump:
        @chmod +x scripts/release/bump_and_tag.sh
        @scripts/release/bump_and_tag.sh v2.0.10

release_notes:
        @python3 scripts/release/gen_changelog.py

release_tag:
        @git tag v2.0.10 || true
        @git push --tags || true

release_all: release_bump
        @echo "Release v2.0.10 queued."

# --- AutoBump Addon ---
.PHONY: release_next_patch release_next_minor release_next_major release_next_explicit

release_next_patch:
        @chmod +x scripts/release/bump_and_tag_auto.sh
        @scripts/release/bump_and_tag_auto.sh --level patch

release_next_minor:
        @chmod +x scripts/release/bump_and_tag_auto.sh
        @scripts/release/bump_and_tag_auto.sh --level minor

release_next_major:
        @chmod +x scripts/release/bump_and_tag_auto.sh
        @scripts/release/bump_and_tag_auto.sh --level major

# Usage: make release_next_explicit VERSION=v2.0.11
release_next_explicit:
        @chmod +x scripts/release/bump_and_tag_auto.sh
        @if [ -z "$(VERSION)" ]; then echo "Set VERSION=vX.Y.Z"; exit 2; fi
        @scripts/release/bump_and_tag_auto.sh --explicit "$(VERSION)"

# --- Post-Release Guard (manual) ---
.PHONY: post_release_guard
post_release_guard:
        @OWNER?=$(shell git remote get-url origin | sed -E 's#.*github.com[:/](.*)/.*#\1#')
        @REPO?=$(shell basename `git rev-parse --show-toplevel`)
        @OWNER=$(OWNER) REPO=$(REPO) python3 scripts/guards/post_release_guard.py

# --- Mini Docs Health badge injector ---
# DISABLED: .PHONY: badges_mini_health
badges_mini_health:
        @OWNER?=$(shell git remote get-url origin | sed -E 's#.*github.com[:/](.*)/.*#\1#')
        @REPO?=$(shell basename `git rev-parse --show-toplevel`)
        @OWNER=$(OWNER) REPO=$(REPO) python3 scripts/badges/inject_docs_health_badge.py

# --- Pipeline Status & PR Workflow Helpers ---
.PHONY: pipeline_status docs_ready_label

pipeline_status:
        @python3 scripts/badges/insert_pipeline_status.py

docs_ready_label:
        @if [ -z "$(PR)" ]; then echo "Usage: make docs_ready_label PR=123"; exit 2; fi
        @echo "Labeling PR #$(PR) as docs:ready…"
        @gh issue edit $(PR) --add-label "docs:ready"

# Makefile helpers for Pages (optional)
.PHONY: pages_build pages_open pages

pages_build:
        mkdir -p public
        rsync -a --delete docs/ public/ || true
        mkdir -p public/downloads
        if [ -d dist ]; then rsync -a dist/*.pdf public/downloads/ 2>/dev/null || true; fi
        @echo "Static site prepared in ./public"

pages_open:
        @echo "After CI deploys, visit: https://$$(git config --get remote.origin.url | sed -E 's#^.*github.com[:/]|\.git$$##g' | sed 's#^#https://github.io/#')"

pages:
        @echo "📄 Deploying to GitHub Pages..."
        @git add -A 2>/dev/null || true
        @git diff-index --quiet HEAD || git commit -m "ci(pages): publish site w/ dynamic downloads & badges" || true
        @git push || true
        @gh workflow run pages.yml -R m9dswyptrn-web/SonicBuilder || echo "Trigger workflow manually in GitHub Actions"
        @echo "✅ Triggered Pages deployment. Watch: https://github.com/m9dswyptrn-web/SonicBuilder/actions"

# ===== Security Suite (Semgrep + Hardening) =====
.PHONY: semgrep semgrep-ci harden harden-check

semgrep:
        @semgrep --config .semgrep.yml || true

semgrep-ci:
        @semgrep ci --config .semgrep.yml

harden-check:
        @python3 tools/hardening/patch_subprocess.py --check

harden:
        @python3 tools/hardening/patch_subprocess.py --apply
        @git add -A
        @git commit -m "security(hardening): sanitize subprocess usage" || true

# ===== Secure Build System =====
.PHONY: secure-build secure-backup backup-list backup-restore

secure-build:
        @python3 scripts/secure_build.py --build

secure-backup:
        @python3 scripts/secure_build.py --backup

backup-list:
        @python3 scripts/secure_build.py --list

backup-restore:
        @if [ -z "$(BACKUP)" ]; then echo "Usage: make backup-restore BACKUP=<backup_name>"; exit 1; fi
        @python3 scripts/secure_build.py --restore $(BACKUP)

# ===== Pages Verification & Badge Sync =====
.PHONY: verify-pages restore-badges sync-badges

verify-pages:
        @echo "🔍 Verifying GitHub Pages deployment..."
        @python3 scripts/monitoring/verify_pages.py || echo "⚠️  verify_pages.py not found"

restore-badges:
        @echo "🔄 Restoring and syncing badges..."
        @bash scripts/restore_and_sync.sh

sync-badges: restore-badges

# ===== Supersonic Package Bundles =====
.PHONY: package-all package-core package-security package-diagnostics package-addons package-failsafe

package-all:
        @echo "📦 Building all Supersonic bundles..."
        @python3 setup/package_all.py

package-core:
        @python3 setup/build_supersonic_core.py

package-security:
        @python3 setup/build_supersonic_security.py

package-diagnostics:
        @python3 setup/build_supersonic_diagnostics.py

package-addons:
        @python3 setup/build_supersonic_addons.py

package-failsafe:
        @python3 setup/build_supersonic_failsafe.py

# ===== Autodeploy System =====
.PHONY: autodeploy rollback-help

autodeploy:
        @echo "🚀 Running SonicBuilder Autodeploy..."
        @python3 founder_autodeploy/founder_autodeploy.py

rollback-help:
        @echo "🔄 Rollback Helper Usage:"
        @python3 founder_autodeploy/rollback_helper.py --help

# ===== Installation & Setup =====
.PHONY: secure-install autofill-github pages-serve

secure-install:
        @echo "🛡️  Installing SonicBuilder Secure Suite..."
        @bash install_secure_suite.sh

autofill-github:
        @echo "🔧 Auto-filling GitHub user/repo information..."
        @bash autofill_github_info.sh

pages-serve:
        @echo "🌐 Serving GitHub Pages locally at http://localhost:8000"
        @echo "📁 Serving from: docs/"
        @echo ""
        @echo "Available endpoints:"
        @echo "  • http://localhost:8000/index.html"
        @echo "  • http://localhost:8000/badges/*.json"
        @echo "  • http://localhost:8000/downloads/*.pdf"
        @echo ""
        @echo "Press Ctrl+C to stop..."
        @cd docs && python3 -m http.server 8000

# ===== Auto-Healer System Health Monitoring =====
.PHONY: system_json

system_json:
        @echo "== Generating System Health Summary =="
        @$(PY) scripts/gen_system_json.py
        @echo "✅ System health summary generated"

# ============================================================
# UPLOADED COMMAND SNIPPETS (Auto-integrated)
# ============================================================

.PHONY: snippets-help snippets-list

snippets-help:
        @echo "Available snippet commands:"
        @ls scripts/util/snippet_*.sh 2>/dev/null | sed 's|scripts/util/snippet_||' | sed 's|.sh||' | awk '{print "  make snippet-" $$1}'

snippets-list:
        @for f in scripts/util/snippet_*.sh; do echo "$$f:"; cat "$$f" | grep -v "^#"; echo ""; done

snippet-%:
        @bash scripts/util/snippet_$*.sh


# ============================================================
# INTEGRATED PACKAGES (Audio, Manifests, ExactFit)
# ============================================================

.PHONY: addons-help addons-audio addons-manifest addons-exactfit addons-all

addons-help:
        @echo "Available addon packages:"
        @echo "  make addons-audio      - Install audio integration tools"
        @echo "  make addons-manifest   - Install manifest generation tools"  
        @echo "  make addons-exactfit   - Install ExactFit helpers"
        @echo "  make addons-all        - Install all addon packages"

addons-audio:
        @echo "Installing audio integration packages..."
        @find packages/audio -name "*.sh" -exec chmod +x {} \;
        @find packages/audio -name "*.py" -exec chmod +x {} \;
        @echo "✅ Audio addons ready"

addons-manifest:
        @echo "Installing manifest packages..."
        @find packages/manifests -type f -name "*.pdf" -exec cp {} docs/resources/ \; 2>/dev/null || true
        @echo "✅ Manifest addons ready"

addons-exactfit:
        @echo "Installing ExactFit packages..."
        @find packages/exactfit -name "*.sh" -exec chmod +x {} \;
        @find packages/exactfit -name "*.py" -exec chmod +x {} \;
        @echo "✅ ExactFit addons ready"

addons-all: addons-audio addons-manifest addons-exactfit
        @echo "✅ All addon packages installed"


# ============================================================
# LEGACY BUILDERS (Active & Executable)
# ============================================================

.PHONY: builders-help builders-list builder-v1 builder-v2

builders-help:
        @echo "Available builders:"
        @echo "  make builder-v1          - Run SonicBuilder v1.0.0 (legacy)"
        @echo "  make builder-v2          - Run SonicBuilder v2.0.0 (legacy)"
        @echo "  make builder-supersonic  - Run Supersonic Edition (full-featured)"
        @echo "  make builders-list       - List all available builders"
        @echo ""
        @echo "Supersonic commands: pack, clean, prepare, notes, manifest, sums, sbom, qr"
        @echo "Example: make builder-supersonic ARGS='pack'"

builders-list:
        @ls -1 builders/*.py 2>/dev/null || echo "No builders found"

builder-v1:
        @echo "Running SonicBuilder v1.0.0..."
        @python3 builders/sonicbuilder_v1.0.0.py

builder-v2:
        @echo "Running SonicBuilder v2.0.0..."
        @python3 builders/sonicbuilder_v2.0.0.py

builder-supersonic:
        @echo "Running SonicBuilder Supersonic Edition..."
        @python3 builders/sonicbuilder_supersonic.py $(ARGS)


# ============================================================
# NEW BUILD SCRIPTS (Enhanced with Manifest Hooks)
# ============================================================

.PHONY: build-help build-enhanced build-enhanced-v2 build-manifest-only

build-help:
        @echo "Enhanced build scripts:"
        @echo "  make build-enhanced        - Run build.sh with manifest hooks"
        @echo "  make build-enhanced-v2     - Run build_variant2.sh"
        @echo "  make build-manifest-only   - Generate manifest package only"

build-enhanced:
        @echo "Running enhanced build with manifest hooks..."
        @bash builders/build.sh --render-manifest

build-enhanced-v2:
        @echo "Running build variant 2..."
        @bash builders/build_variant2.sh

build-manifest-only:
        @echo "Generating manifest package only..."
        @bash builders/build.sh --manifest-only


# ============================================================
# NEW SNIPPETS (81 Additional Command Examples)
# ============================================================

.PHONY: new-snippets-help new-snippets-list new-snippet

new-snippets-help:
        @echo "New snippet batch (81 snippets):"
        @echo "  make new-snippets-list         - List all new snippets"
        @echo "  make new-snippet N=<num>       - Show specific snippet"
        @echo ""
        @echo "Example: make new-snippet N=10"

new-snippets-list:
        @echo "New snippets available:"
        @ls -1 scripts/snippets/new_batch/ | sort -V

new-snippet:
        @if [ -z "$(N)" ]; then echo "Usage: make new-snippet N=<number>"; exit 1; fi
        @echo "=== New Snippet $(N) ==="
        @cat scripts/snippets/new_batch/snippet_$(N).txt


# ============================================================
# PRE-BUILT PACKAGES (25 Build Variants)
# ============================================================

.PHONY: packages-help packages-list packages-extract

packages-help:
        @echo "Pre-built packages (25 variants):"
        @echo "  make packages-list          - List all available packages"
        @echo "  make packages-extract       - Extract all packages to temp/"

packages-list:
        @echo "Available build packages:"
        @ls -1 packages/builds/*.zip | xargs -n1 basename | sort

packages-extract:
        @echo "Extracting all packages..."
        @mkdir -p temp/extracted_packages
        @for zip in packages/builds/*.zip; do \
        name=$$(basename "$$zip" .zip); \
        mkdir -p "temp/extracted_packages/$$name"; \
        unzip -q "$$zip" -d "temp/extracted_packages/$$name"; \
        done
        @echo "✅ All packages extracted to temp/extracted_packages/"


# ============================================================
# MANIFEST DOCUMENTATION
# ============================================================

.PHONY: manifest-docs-help manifest-docs-view

manifest-docs-help:
        @echo "Manifest documentation:"
        @echo "  make manifest-docs-view     - View manifest documentation"

manifest-docs-view:
        @echo "=== Manifest README (Dark) ==="
        @cat docs/manifest/SonicBuilder_Manifest_README_Dark.md
        @echo ""
        @echo "=== Manifest README (Light) ==="
        @cat docs/manifest/SonicBuilder_Manifest_README_Light.md


# ===================================================================
# SUPERSONIC EDITION TOOLS
# ===================================================================

.PHONY: supersonic-help supersonic-demos supersonic-build-all supersonic-diff supersonic-lean

supersonic-help:
        @echo "Supersonic Edition tools:"
        @echo "  make supersonic-demos       - Generate demo PDFs (dark + light)"
        @echo "  make supersonic-diff        - Render CHANGELOG to HTML"
        @echo "  make supersonic-build-all   - Full build automation"
        @echo "  make supersonic-lean        - Create lean standalone package"
        @echo ""
        @echo "Example: make supersonic-demos"

supersonic-demos:
        @python3 builders/make_demo_dark_pdf.py
        @python3 builders/make_demo_light_pdf.py

supersonic-diff:
        @if [ -f "CHANGELOG.md" ]; then \
        python3 SonicBuilder/tools/diff_render_html.py --md CHANGELOG.md --out diff.html --title "SonicBuilder Changelog"; \
        echo "[ok] diff.html created"; \
        else \
        echo "[warn] CHANGELOG.md not found"; \
        fi

supersonic-build-all:
        @python3 builders/supersonic_build_all.py

supersonic-build-all-publish:
        @python3 builders/supersonic_build_all.py --publish

supersonic-lean:
        @python3 builders/make_supersonic_lean.py

supersonic-lean-auto:
        @python3 builders/make_supersonic_lean_auto.py

supersonic-verify:
        @python3 builders/supersonic_verify.py

supersonic-mission-cards:
        @python3 builders/make_supersonic_cards_autoattach.py

supersonic-mission-cards-open:
        @python3 builders/make_supersonic_cards_autoattach.py --auto-run


# ===== Supersonic Commander Control Panel =====
.PHONY: supersonic-rebuild supersonic-deploy supersonic-verify supersonic-verify-ext supersonic-preview-fix supersonic-promote supersonic-rollback supersonic-serve supersonic-health

supersonic-rebuild:
        $(PY) supersonic_build_secure_all.py

supersonic-deploy:
        $(PY) supersonic_deploy_pages.py

supersonic-verify:
        $(PY) supersonic_verify_pages.py --hints

supersonic-verify-ext:
        $(PY) supersonic_verify_pages.py --hints --externals

supersonic-preview-fix:
        $(PY) supersonic_verify_autofix_preview.py

supersonic-promote:
        $(PY) supersonic_promote_preview.py

supersonic-rollback:
        @$(PY) supersonic_docs_rollback.py --list
        @echo ""
        @echo "Usage: python supersonic_docs_rollback.py --use _backup_YYYYMMDD_HHMMSS --yes"

supersonic-serve:
        $(PY) supersonic_settings_server.py

supersonic-health:
        @$(PY) healthcheck.py --host 127.0.0.1 --port 8080 --retries 30 --sleep 1

# ========== Supersonic Health Scan ==========
PY := python3
HEALTH := supersonic_full_health_scan.py

.PHONY: health-scan health-ci health-apply health-apply-ci health-undo health-open health-clean-ledgers

## Scan only (writes docs/HEALTH_REPORT.md, exit nonzero on criticals)
health-scan:
        @$(PY) $(HEALTH)

## Scan + run your single green gate (make ci-check or safe fallback)
health-ci:
        @$(PY) $(HEALTH) --ci-check

## Auto-organize orphan .py files into tools/ | supersonic_pkg/ | extras/snippets/
## and log the moves to .supersonic/moves.log (create if missing)
health-apply:
        @mkdir -p .supersonic
        @touch .supersonic/moves.log
        @$(PY) $(HEALTH) --apply --log-file .supersonic/moves.log

## Apply + CI gate in one go
health-apply-ci:
        @mkdir -p .supersonic
        @touch .supersonic/moves.log
        @$(PY) $(HEALTH) --apply --ci-check --log-file .supersonic/moves.log

## Undo moves from a ledger (default: .supersonic/moves.log). Usage:
##   make health-undo                      # uses default log
##   make health-undo LOG=path/to/moves.log
##   make health-undo LOG=.supersonic/moves_2025-11-03T13-22-55Z.log
health-undo:
        @$(PY) $(HEALTH) --undo --log-file $(if $(LOG),$(LOG),.supersonic/moves.log)

## Open the latest health report (macOS 'open' or Linux 'xdg-open')
health-open:
        @if [ -f docs/HEALTH_REPORT.md ]; then \
        if command -v open >/dev/null 2>&1; then open docs/HEALTH_REPORT.md; \
        elif command -v xdg-open >/dev/null 2>&1; then xdg-open docs/HEALTH_REPORT.md >/dev/null 2>&1 || true; \
        else echo "Report at docs/HEALTH_REPORT.md"; fi; \
        else echo "No docs/HEALTH_REPORT.md yet. Run 'make health-scan'."; fi

## Clean all move ledgers
health-clean-ledgers:
        @rm -f .supersonic/moves*.log .supersonic/moves.log 2>/dev/null || true
        @echo "Ledgers removed."

# ========== Sync Enhancements v4 Ultimate Edition ==========
.PHONY: sync-config sync-throttle-status sync-stats sync-hourly sync-test-webhook sync-check-ignore sync-dashboard sync-clear-history sync-clear-throttle sync-enhancements-help

## View current sync configuration
sync-config:
        @$(PY) tools/sync_config.py | jq . || $(PY) tools/sync_config.py

## View throttle status (rate limits, backoff)
sync-throttle-status:
        @$(PY) tools/sync_throttle.py status

## View sync statistics (24h summary)
sync-stats:
        @$(PY) tools/sync_history.py stats

## View hourly sync activity
sync-hourly:
        @$(PY) tools/sync_history.py hourly

## Test webhook notification
sync-test-webhook:
        @$(PY) tools/sync_webhooks.py sync_success '{"duration_sec": 1.5, "files_changed": 3, "commit_hash": "test123"}'

## Check which files would be ignored by .syncignore
sync-check-ignore:
        @$(PY) tools/sync_ignore.py

## Open sync metrics dashboard (port 8088)
sync-dashboard:
        @echo "🚀 Starting Sync Metrics Dashboard on http://localhost:8088/api/sync/dashboard"
        @$(PY) tools/sync_metrics_api.py 8088

## Clear sync history (reset all metrics)
sync-clear-history:
        @rm -f .cache/sync_history.jsonl
        @echo "✅ Sync history cleared"

## Clear throttle state (reset rate limits)
sync-clear-throttle:
        @rm -f .cache/sync_throttle.json
        @echo "✅ Throttle state cleared"

## Show help for sync enhancements
sync-enhancements-help:
        @echo "📊 Sync Enhancements v4 Ultimate Edition"
        @echo ""
        @echo "Configuration:"
        @echo "  make sync-config              - View current sync configuration"
        @echo ""
        @echo "Monitoring:"
        @echo "  make sync-stats               - View 24h sync statistics"
        @echo "  make sync-hourly              - View hourly sync activity"
        @echo "  make sync-throttle-status     - View rate limit & backoff status"
        @echo "  make sync-dashboard           - Open visual metrics dashboard"
        @echo ""
        @echo "Testing:"
        @echo "  make sync-test-webhook        - Test webhook notifications"
        @echo "  make sync-check-ignore        - Check .syncignore patterns"
        @echo ""
        @echo "Maintenance:"
        @echo "  make sync-clear-history       - Reset all sync metrics"
        @echo "  make sync-clear-throttle      - Reset rate limits"
        @echo ""
        @echo "Documentation: tools/SYNC_ENHANCEMENTS.md"


# --- Supersonic health/sync/log helpers ---
.PHONY: ping ready log-tail log-size log-archives
ping:
        @curl -s $${BASE:-http://localhost:$$(PORT)}/api/ping | jq -r . || curl -s $${BASE:-http://localhost:$$(PORT)}/api/ping

ready:
        @curl -s -o /dev/null -w "%{http_code}\n" $${BASE:-http://localhost:$$(PORT)}/api/ready

log-tail:
        @tail -n 200 logs/app.log 2>/dev/null || echo "(no logs/app.log yet)"

log-size:
        @python3 -c "from pathlib import Path; p=Path('logs'); size=sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) if p.exists() else 0; print(f'Total logs size: {size/1024:.1f} KB')"

log-archives:
        @ls -lh logs/archive/*.gz 2>/dev/null || echo "(no archives yet)"

# --- Supersonic doctor (health report + web endpoints) ---
.PHONY: doctor doctor-serve doctor-open doctor-test
doctor:
        @python3 supersonic_doctor.py

doctor-serve:
        @python3 -m tools.doctor_endpoints

doctor-open:
        @python3 -c "import webbrowser; webbrowser.open('http://localhost:8080/doctor')"

doctor-test:
        @curl -sS -H "X-Doctor-Key: $${DOCTOR_KEY:-}" http://localhost:8080/health | python3 -m json.tool

# --- Supersonic project scanner ---
.PHONY: scan scan-apply scan-zip scan-full
scan:
        @python3 supersonic_project_doctor.py

scan-apply:
        @python3 supersonic_project_doctor.py --apply-panel

scan-zip:
        @python3 supersonic_project_doctor.py --zip

scan-full:
        @python3 supersonic_project_doctor.py --apply-panel --zip

# --- Flask control panel installation ---
.PHONY: panel-install panel-logs panel-open logs-tail
panel-install:
        @python3 install_flask_control_panel.py

panel-logs:
        @python3 upgrade_panel_logs.py

panel-open:
        @python3 -c "import os, webbrowser; url = os.environ.get('APP_URL', 'http://127.0.0.1:5000') + '/panel'; print('Opening:', url); webbrowser.open(url)"

logs-tail:
        @curl -fsS -H "X-Doctor-Key: $${DOCTOR_KEY:-}" "http://127.0.0.1:5000/logs/tail?n=400" | python3 -c "import sys, json; d=json.load(sys.stdin); [print(ln) for ln in d.get('lines',[])]"

# --- Health endpoint diagnostics ---
.PHONY: health-upgrade diag-local
health-upgrade:
        @python3 upgrade_health_endpoint.py

diag-local:
        @echo "==> /health"
        @curl -fsS -H "X-Doctor-Key: $${DOCTOR_KEY:-}" "http://127.0.0.1:5000/health" | jq .
        @echo "==> /logs/tail (last 60)"
        @curl -fsS -H "X-Doctor-Key: $${DOCTOR_KEY:-}" "http://127.0.0.1:5000/logs/tail?n=200" | jq -r '.lines[]' | tail -n 60

# --- Supersonic bootstrapper ---
.PHONY: supersonic-bootstrap supersonic-status supersonic-revert
supersonic-bootstrap:
        @python3 supersonic_bootstrap.py --all

supersonic-status:
        @python3 supersonic_bootstrap.py --status

supersonic-revert:
        @python3 supersonic_bootstrap.py --revert

# --- Testing ---
.PHONY: test test-verbose cov
test:
        @pytest -q

test-verbose:
        @pytest -vv

cov:
        @pytest -q --cov=. --cov-report=term-missing --cov-report=xml

# --- Code Quality ---
.PHONY: fmt lint badge pre-commit-install
fmt:
        @black . && isort .

lint:
        @flake8 .

badge:
        @python -m coverage_badge -o coverage.svg -f

pre-commit-install:
        @pre-commit install

# --- Supersonic Control Panel & Doctor ---
.PHONY: panel doctor snapshot clean-export preflight doctor-full

panel:
        python -c "import webbrowser; webbrowser.open('http://127.0.0.1:5000/panel')"

doctor:
        curl -s http://127.0.0.1:5000/health | python3 -m json.tool

doctor-full:
        python3 tools/supersonic_doctor.py

snapshot:
        python3 scripts/snapshot_full.py

clean-export:
        python3 scripts/clean_and_export.py

preflight:
        python3 tools/supersonic_preflight.py
# --- End Supersonic Pack ---

# ===== GitHub Release Tools (SupersonicBuilder) =====
.PHONY: gh-check gh-push gh-push-tags gh-release-patch gh-release-minor gh-release-major gh-release gh-clean-remote

gh-check:
	@tools/verify_github_ready.sh

gh-push:
	@tools/push_branch.sh main

gh-push-tags:
	@source tools/gh.sh && with_auth_remote git push origin --tags
	@echo "✅ Pushed tags"

gh-release-patch:
	@BRANCH=main tools/release_now.sh --patch --push-branch

gh-release-minor:
	@BRANCH=main tools/release_now.sh --minor --push-branch

gh-release-major:
	@BRANCH=main tools/release_now.sh --major --push-branch

gh-release:
	@[ -n "$(TAG)" ] || (echo "Usage: make gh-release TAG=vX.Y.Z" && exit 2)
	@BRANCH=main tools/release_now.sh --tag "$(TAG)" --push-branch

gh-clean-remote:
	@git remote set-url origin "https://github.com/m9dswyptrn-web/SupersonicBuilder.git"
	@echo "🧼 origin cleaned"
