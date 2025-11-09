#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🛡️  SonicBuilder Secure Suite Installer v1.1              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Progress counter
STEP=0
total_steps=8
ERRORS=0
WARNINGS=0

progress() {
    STEP=$((STEP + 1))
    echo -e "${BLUE}[$STEP/$total_steps]${NC} $1"
}

error() {
    echo -e "${RED}   ✗ ERROR: $1${NC}"
    ERRORS=$((ERRORS + 1))
}

warn() {
    echo -e "${YELLOW}   ⚠️  WARNING: $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

ok() {
    echo -e "${GREEN}   ✓ $1${NC}"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    warn "Not a git repository. Run: git init"
fi

progress "📁 Creating directory structure..."
mkdir -p .github/workflows
mkdir -p tools/hardening
mkdir -p scripts/monitoring
mkdir -p docs/badges
mkdir -p backups
ok "Directory structure created"

progress "🔧 Checking for required tools..."
if command -v python3 >/dev/null 2>&1; then
    ok "Python3 found: $(python3 --version)"
else
    error "Python3 required but not installed"
    exit 1
fi

progress "🛡️  Verifying security workflows..."
WORKFLOW_COUNT=0
for workflow in semgrep.yml security-hardening.yml pages-health-badge.yml pages-deploy-badge.yml; do
    if [ -f ".github/workflows/$workflow" ]; then
        ok "$workflow exists"
        WORKFLOW_COUNT=$((WORKFLOW_COUNT + 1))
    else
        warn "$workflow missing (expected in .github/workflows/)"
    fi
done

if [ $WORKFLOW_COUNT -eq 0 ]; then
    error "No security workflows found. Required files:"
    echo "     • .github/workflows/semgrep.yml"
    echo "     • .github/workflows/security-hardening.yml"
    echo ""
    echo "   These files should be created from your project template or restored from backup."
fi

progress "🔐 Verifying security rules..."
if [ -f ".semgrep.yml" ]; then
    ok ".semgrep.yml exists"
else
    warn ".semgrep.yml missing (Semgrep security rules)"
fi

if [ -f "tools/hardening/patch_subprocess.py" ]; then
    ok "patch_subprocess.py exists"
    chmod +x tools/hardening/patch_subprocess.py
else
    warn "tools/hardening/patch_subprocess.py missing (subprocess hardening tool)"
fi

progress "💾 Verifying secure build system..."
if [ -f "scripts/secure_build.py" ]; then
    ok "secure_build.py exists"
    chmod +x scripts/secure_build.py
else
    error "scripts/secure_build.py missing (CRITICAL - secure build system)"
    echo "     This file provides backup, build, and restore functionality."
fi

progress "📊 Verifying monitoring tools..."
MONITOR_COUNT=0
for script in verify_pages.py pages_watch.sh; do
    if [ -f "scripts/monitoring/$script" ]; then
        ok "$script exists"
        chmod +x "scripts/monitoring/$script"
        MONITOR_COUNT=$((MONITOR_COUNT + 1))
    else
        warn "scripts/monitoring/$script missing"
    fi
done

if [ -f "scripts/restore_and_sync.sh" ]; then
    ok "restore_and_sync.sh exists"
    chmod +x scripts/restore_and_sync.sh
else
    warn "scripts/restore_and_sync.sh missing (badge sync tool)"
fi

progress "🏷️  Verifying badge endpoints..."
badge_count=$(ls docs/badges/*.json 2>/dev/null | wc -l)
if [ "$badge_count" -ge 6 ]; then
    ok "Found $badge_count badge files"
else
    warn "Only $badge_count badge files found (expected 6+)"
    echo "     Creating placeholder badges..."
    
    # Create minimal badge set
    cat > docs/badges/latest.json << 'JSON'
{"schemaVersion": 1, "label": "latest", "message": "no file", "color": "lightgrey"}
JSON
    cat > docs/badges/downloads.json << 'JSON'
{"schemaVersion": 1, "label": "downloads", "message": "0", "color": "lightgrey"}
JSON
    cat > docs/badges/updated.json << 'JSON'
{"schemaVersion": 1, "label": "last updated", "message": "never", "color": "lightgrey"}
JSON
    cat > docs/badges/size.json << 'JSON'
{"schemaVersion": 1, "label": "size", "message": "0 MB", "color": "lightgrey"}
JSON
    cat > docs/badges/pdf-health.json << 'JSON'
{"schemaVersion": 1, "label": "PDF health", "message": "n/a", "color": "lightgrey"}
JSON
    cat > docs/badges/pages-deploy.json << 'JSON'
{"schemaVersion": 1, "label": "pages deploy", "message": "n/a", "color": "lightgrey"}
JSON
    ok "Created 6 placeholder badge files"
fi

progress "✅ Installation verification complete!"
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  📋 VERIFICATION SUMMARY                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Perfect! All components verified successfully.${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Installation OK with $WARNINGS warnings.${NC}"
else
    echo -e "${RED}❌ Installation incomplete: $ERRORS errors, $WARNINGS warnings.${NC}"
    echo ""
    echo "Missing files must be:"
    echo "  1. Created from templates/backups, or"
    echo "  2. Restored from a complete backup, or"
    echo "  3. Manually created following project documentation"
    echo ""
    if [ $ERRORS -gt 0 ]; then
        exit 1
    fi
fi

echo ""
echo "Installed/Verified components:"
echo ""
echo "  🛡️  Security Suite ($WORKFLOW_COUNT workflows)"
echo "      • Semgrep workflow (code scanning)"
echo "      • Security hardening workflow (subprocess protection)"
echo "      • .semgrep.yml (custom security rules)"
echo "      • patch_subprocess.py (auto-fix tool)"
echo ""
echo "  💾 Secure Build System"
echo "      • secure_build.py (backup + build + verify)"
echo "      • Automatic backups before builds"
echo "      • One-command rollback"
echo ""
echo "  📊 Monitoring Tools ($MONITOR_COUNT tools)"
echo "      • verify_pages.py (GitHub Pages verification)"
echo "      • pages_watch.sh (real-time monitoring)"
echo "      • restore_and_sync.sh (badge sync)"
echo ""
echo "  🏷️  Badge Infrastructure"
echo "      • $badge_count badge JSON files"
echo "      • Dynamic Flask API endpoints"
echo "      • Static GitHub Pages endpoints"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🚀 NEXT STEPS                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Test the installation:"
echo "   make semgrep              # Run security scan"
echo "   make harden-check         # Check for hardening issues"
echo "   make secure-build         # Create backup + build"
echo ""
echo "2. Configure GitHub remote (if not already done):"
echo "   git remote add origin https://github.com/USER/REPO.git"
echo "   make autofill-github      # Auto-fill user/repo in files"
echo ""
echo "3. Commit and push to GitHub:"
echo "   git add ."
echo "   git commit -m 'feat: install secure suite'"
echo "   git push origin main"
echo ""
echo "4. Deploy to Replit:"
echo "   Click 'Publish' → Select 'Autoscale'"
echo ""
echo "5. Monitor your deployment:"
echo "   make verify-pages         # Check GitHub Pages"
echo "   bash scripts/monitoring/pages_watch.sh  # Real-time monitoring"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""
