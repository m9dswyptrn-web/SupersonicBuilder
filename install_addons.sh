#!/bin/bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════
# SonicBuilder Addons Installation Script
# ═══════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════"
echo "  📦 SonicBuilder Addons Installer"
echo "════════════════════════════════════════════════════════════════"
echo ""

ADDONS_DIR="attached_assets"

# Check for ZIP files
if [ ! -d "$ADDONS_DIR" ]; then
  echo "❌ Error: $ADDONS_DIR directory not found"
  exit 1
fi

cd "$ADDONS_DIR"

# ───────────────────────────────────────────────────────────────────
# 1. Release Bumper v2.0.10 Addon
# ───────────────────────────────────────────────────────────────────

BUMPER_ZIP=$(ls -1 SonicBuilder_Release_Bumper_v2_0_10_Addon*.zip 2>/dev/null | head -1)
if [ -n "$BUMPER_ZIP" ]; then
  echo "📦 Installing Release Bumper Add-on..."
  unzip -o "$BUMPER_ZIP"
  cd ..
  
  # Append Makefile fragment (avoid duplicates)
  if ! grep -q "Makefile.release.addon" Makefile; then
    echo "" >> Makefile
    echo "# Release Bumper Addon" >> Makefile
    cat Makefile.release.addon >> Makefile
  fi
  
  git add scripts/release/*.py scripts/release/*.sh \
    .github/workflows/attach-release-notes.yml \
    RELEASE_NOTES Makefile 2>/dev/null || true
  git commit -m "chore(release): add v2.0.10 bumper + notes attach" || true
  echo "✅ Release Bumper installed"
  cd "$ADDONS_DIR"
else
  echo "⚠️  Release Bumper ZIP not found, skipping..."
fi

# ───────────────────────────────────────────────────────────────────
# 2. AutoBump v2.0.11 Addon
# ───────────────────────────────────────────────────────────────────

AUTOBUMP_ZIP=$(ls -1 SonicBuilder_AutoBump_v2_0_11_Addon*.zip 2>/dev/null | head -1)
if [ -n "$AUTOBUMP_ZIP" ]; then
  echo ""
  echo "📦 Installing AutoBump Add-on..."
  unzip -o "$AUTOBUMP_ZIP"
  cd ..
  
  if ! grep -q "Makefile.autobump.addon" Makefile; then
    echo "" >> Makefile
    echo "# AutoBump Addon" >> Makefile
    cat Makefile.autobump.addon >> Makefile
  fi
  
  git add scripts/release/next_version.py scripts/release/bump_and_tag_auto.sh \
    Makefile README_AutoBump_Addon.txt 2>/dev/null || true
  git commit -m "chore(release): add AutoBump Add-on" || true
  echo "✅ AutoBump installed"
  cd "$ADDONS_DIR"
else
  echo "⚠️  AutoBump ZIP not found, skipping..."
fi

# ───────────────────────────────────────────────────────────────────
# 3. Post-Release Guard Addon
# ───────────────────────────────────────────────────────────────────

GUARD_ZIP=$(ls -1 SonicBuilder_PostReleaseGuard_Addon*.zip 2>/dev/null | head -1)
if [ -n "$GUARD_ZIP" ]; then
  echo ""
  echo "📦 Installing Post-Release Guard Add-on..."
  unzip -o "$GUARD_ZIP"
  cd ..
  
  if ! grep -q "Makefile.postguard.addon" Makefile; then
    echo "" >> Makefile
    echo "# Post-Release Guard Addon" >> Makefile
    cat Makefile.postguard.addon >> Makefile
  fi
  
  git add scripts/guards/post_release_guard.py \
    .github/workflows/post-release-guard.yml \
    Makefile 2>/dev/null || true
  git commit -m "ci(guard): add post-release guard (assets+badges)" || true
  echo "✅ Post-Release Guard installed"
  cd "$ADDONS_DIR"
else
  echo "⚠️  Post-Release Guard ZIP not found, skipping..."
fi

# ───────────────────────────────────────────────────────────────────
# 4. Guard Dashboard Addon
# ───────────────────────────────────────────────────────────────────

DASHBOARD_ZIP=$(ls -1 SonicBuilder_GuardDashboard_Addon*.zip 2>/dev/null | head -1)
if [ -n "$DASHBOARD_ZIP" ]; then
  echo ""
  echo "📦 Installing Guard Dashboard Add-on..."
  unzip -o "$DASHBOARD_ZIP"
  cd ..
  
  git add scripts/guards/guard_status_badge.py \
    .github/workflows/guard-status-badge.yml \
    docs/badges/guard_status.json 2>/dev/null || true
  git commit -m "ci(guard): add Guard Dashboard (status badge + workflow)" || true
  echo "✅ Guard Dashboard installed"
  cd "$ADDONS_DIR"
else
  echo "⚠️  Guard Dashboard ZIP not found, skipping..."
fi

# ───────────────────────────────────────────────────────────────────
# 5. Docs Health Dashboard Addon
# ───────────────────────────────────────────────────────────────────

HEALTH_ZIP=$(ls -1 SonicBuilder_DocsHealthDashboard_Addon*.zip 2>/dev/null | head -1)
if [ -n "$HEALTH_ZIP" ]; then
  echo ""
  echo "📦 Installing Docs Health Dashboard Add-on..."
  unzip -o "$HEALTH_ZIP"
  cd ..
  
  git add scripts/health/build_docs_health_grid.py \
    .github/workflows/docs-health-dashboard.yml \
    docs/badges/docs_health.json 2>/dev/null || true
  git commit -m "docs(health): add Docs Health Dashboard (grid + composite badge)" || true
  echo "✅ Docs Health Dashboard installed"
  cd "$ADDONS_DIR"
else
  echo "⚠️  Docs Health Dashboard ZIP not found, skipping..."
fi

# ───────────────────────────────────────────────────────────────────
# 6. README Mini Health Addon
# ───────────────────────────────────────────────────────────────────

MINIHEALTH_ZIP=$(ls -1 SonicBuilder_ReadmeMiniHealth_Addon*.zip 2>/dev/null | head -1)
if [ -n "$MINIHEALTH_ZIP" ]; then
  echo ""
  echo "📦 Installing README Mini Health Add-on..."
  unzip -o "$MINIHEALTH_ZIP"
  cd ..
  
  if ! grep -q "Makefile.minihealth.addon" Makefile; then
    echo "" >> Makefile
    echo "# Mini Health Addon" >> Makefile
    cat Makefile.minihealth.addon >> Makefile
  fi
  
  git add scripts/badges/inject_docs_health_badge.py \
    Makefile 2>/dev/null || true
  git commit -m "docs(badges): add Mini Docs Health badge injector" || true
  echo "✅ README Mini Health installed"
  cd "$ADDONS_DIR"
else
  echo "⚠️  README Mini Health ZIP not found, skipping..."
fi

# ───────────────────────────────────────────────────────────────────
# 7. Docs MegaBundle
# ───────────────────────────────────────────────────────────────────

MEGABUNDLE_ZIP=$(ls -1 SonicBuilder_Docs_MegaBundle*.zip 2>/dev/null | head -1)
if [ -n "$MEGABUNDLE_ZIP" ]; then
  echo ""
  echo "📦 Installing Docs MegaBundle..."
  unzip -o "$MEGABUNDLE_ZIP"
  cd ..
  
  # Run installer if it exists
  if [ -f install_all.sh ]; then
    bash install_all.sh
  fi
  
  echo "✅ Docs MegaBundle installed"
  cd "$ADDONS_DIR"
else
  echo "⚠️  Docs MegaBundle ZIP not found, skipping..."
fi

cd ..

# ───────────────────────────────────────────────────────────────────
# Final Push
# ───────────────────────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Addon Installation Complete"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "⚠️  PAUSED: Review changes and run:"
echo "    git push"
echo ""
echo "🎯 New Make Targets Available:"
echo "   • make release_next_patch   - Auto-bump to next patch"
echo "   • make release_all          - Run v2.0.10 bumper flow"
echo "   • make post_release_guard   - Run post-release checks"
echo ""
