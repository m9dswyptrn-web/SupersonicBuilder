#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🚀 Supersonic Installer - SonicBuilder Edition            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check for Supersonic bundles
echo "🔍 Checking for Supersonic bundles..."

bundles=(
    "Supersonic_Core.zip"
    "Supersonic_Security.zip"
    "Supersonic_Diagnostics.zip"
    "Supersonic_Addons.zip"
    "Supersonic_Failsafe.zip"
)

found=0
for bundle in "${bundles[@]}"; do
    if [ -f "$bundle" ]; then
        echo "  ✅ Found: $bundle"
        found=$((found + 1))
    else
        echo "  ⚠️  Missing: $bundle"
    fi
done

if [ $found -eq 0 ]; then
    echo ""
    echo "❌ No Supersonic bundles found!"
    echo ""
    echo "To create bundles, run:"
    echo "  make package-all"
    echo ""
    exit 1
fi

echo ""
echo "Found $found bundle(s). Ready to install."
echo ""
echo "This installer will:"
echo "  1. Extract Supersonic bundles"
echo "  2. Restore baseline configuration"
echo "  3. Install dependencies"
echo "  4. Run secure installation"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting installation..."

# Extract bundles
for bundle in "${bundles[@]}"; do
    if [ -f "$bundle" ]; then
        echo "  📦 Extracting $bundle..."
        unzip -o -q "$bundle"
    fi
done

# Run baseline restore
if [ -f "restore_baseline.sh" ]; then
    echo "  🔧 Restoring baseline..."
    bash restore_baseline.sh
fi

# Run secure installation
if [ -f "install_secure_suite.sh" ]; then
    echo "  🛡️  Running secure installation..."
    bash install_secure_suite.sh
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                ✅ INSTALLATION COMPLETE                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Configure GitHub: make autofill-github"
echo "  2. Test locally: make pages-serve"
echo "  3. Deploy to Replit: Click 'Publish' → 'Autoscale'"
echo ""
