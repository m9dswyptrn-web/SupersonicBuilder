#!/bin/bash
#
# SonicBuilder Autodeploy
# Orchestrates complete deployment pipeline:
#   1. setup_supersonic.py → Environment & bundles
#   2. security_patch.py → Security checks
#   3. publish_to_pages.py → GitHub Pages publishing
#   4. founder_autodeploy.py → Git commit & push
#

set -e  # Exit on error

VERSION="2.0.9"
SILENT=${SILENT:-0}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    if [ "$SILENT" != "1" ]; then
        echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
    fi
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Header
if [ "$SILENT" != "1" ]; then
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║       🚀 SonicBuilder Autodeploy System                       ║
╚════════════════════════════════════════════════════════════════╝

EOF
fi

log "Starting autodeploy pipeline v${VERSION}..."

# Phase 1: Setup & Environment
log ""
log "Phase 1/4: Supersonic Setup"
log "→ Running setup_supersonic.py..."

if python3 supersonic/setup_supersonic.py --skip-secrets --skip-deps; then
    log_success "Setup complete"
else
    log_error "Setup failed"
    exit 1
fi

# Phase 2: Security Patch
log ""
log "Phase 2/4: Security Patch"
log "→ Running security_patch.py..."

if python3 supersonic/security_patch.py; then
    log_success "Security checks passed"
else
    log_warning "Security checks had warnings (non-fatal)"
fi

# Phase 3: Publish to Pages
log ""
log "Phase 3/4: GitHub Pages Publishing"
log "→ Running publish_to_pages.py..."

if python3 supersonic/publish_to_pages.py; then
    log_success "Publishing complete"
else
    log_error "Publishing failed"
    exit 1
fi

# Phase 4: Git Autodeploy (optional - requires GITHUB_TOKEN)
if [ -n "$GITHUB_TOKEN" ] || [ -n "$SKIP_GIT_PUSH" ]; then
    log ""
    log "Phase 4/4: Git Autodeploy"
    
    if [ -n "$SKIP_GIT_PUSH" ]; then
        log_warning "Git push skipped (SKIP_GIT_PUSH set)"
    else
        log "→ Running founder_autodeploy.py..."
        
        if python3 founder_autodeploy/founder_autodeploy.py; then
            log_success "Git push complete"
        else
            log_error "Git push failed (rollback initiated)"
            exit 1
        fi
    fi
else
    log ""
    log "Phase 4/4: Git Autodeploy"
    log_warning "Skipping git push (GITHUB_TOKEN not set)"
    log "Set GITHUB_TOKEN in Replit Secrets to enable auto-push"
fi

# Display results
if [ "$SILENT" != "1" ]; then
    echo ""
    cat verify.log 2>/dev/null || true
fi

log_success "Autodeploy complete!"

exit 0
