#!/usr/bin/env bash
set -euo pipefail

VER="${1:-}"
if [[ -z "$VER" ]]; then
  echo "Usage: $0 vMAJOR.MINOR.PATCH" >&2
  exit 2
fi

OUT="build/Supersonic_Release_${VER}.zip"
TMP="build/_release_${VER}"
rm -rf "$TMP"; mkdir -p "$TMP"

# What to include (add anything else you want)
mkdir -p "$TMP/docs/installer" "$TMP/docs/status" "$TMP/build"
cp -f docs/installer/*.pdf "$TMP/docs/installer/" 2>/dev/null || true
cp -f docs/status/* "$TMP/docs/status/" 2>/dev/null || true
cp -f build/*.zip "$TMP/build/" 2>/dev/null || true

# Manifest
cat > "$TMP/manifest.json" <<JSON
{
  "name": "SupersonicBuilder",
  "version": "${VER}",
  "generated_at_utc": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "contents": [
    "docs/installer/*.pdf",
    "docs/status/*",
    "build/*.zip"
  ]
}
JSON

# Zip it
( cd "$TMP" && zip -r "../Supersonic_Release_${VER}.zip" . >/dev/null )

# Checksums
( cd build && sha256sum "Supersonic_Release_${VER}.zip" > "Supersonic_Release_${VER}.zip.sha256" )

echo "Created: $OUT"
echo "SHA256:  $(cut -d' ' -f1 build/Supersonic_Release_${VER}.zip.sha256)"
