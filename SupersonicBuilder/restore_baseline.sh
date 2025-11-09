#!/bin/bash
set -e

echo "🔧 Restoring SonicBuilder baseline..."

# Restore requirements
if [ -f "requirements.txt" ]; then
    echo "  📦 Installing Python requirements..."
    pip install -r requirements.txt --quiet || echo "  ⚠️  Some requirements failed to install"
fi

# Restore directory structure
echo "  📁 Ensuring directory structure..."
mkdir -p scripts/{security,diagnostics,addons,monitoring,enhancements}
mkdir -p tools/{hardening,addons}
mkdir -p .github/workflows
mkdir -p docs/{badges,guides}
mkdir -p backups
mkdir -p downloads

# Set permissions
echo "  🔐 Setting permissions..."
chmod +x scripts/*.py 2>/dev/null || true
chmod +x scripts/monitoring/*.sh 2>/dev/null || true
chmod +x *.sh 2>/dev/null || true

echo "✅ Baseline restored successfully!"
echo ""
echo "Next steps:"
echo "  1. Run: make secure-install"
echo "  2. Run: make verify-pages"
echo "  3. Deploy to Replit"
