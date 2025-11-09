#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-5.0.0}"
RELEASE_ZIP="${2:-downloads/latest.pdf}"
OUT_DIR="${3:-docs/manifests}"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🎯 SONICBUILDER MANIFEST GENERATOR                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo
echo "Version: v$VERSION"
echo "Release: $RELEASE_ZIP"
echo "Output:  $OUT_DIR"
echo

python3 render_manifest.py \
  --version "$VERSION" \
  --release-zip "$RELEASE_ZIP" \
  --out "$OUT_DIR" \
  --all

echo
echo "✅ Manifest generation complete!"
echo "📁 Output directory: $OUT_DIR"
echo
ls -lh "$OUT_DIR"/*.zip 2>/dev/null || echo "No ZIP files created"
