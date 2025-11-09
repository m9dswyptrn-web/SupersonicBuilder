#!/usr/bin/env bash
set -euo pipefail
python3 clean_and_export.py "$@"
echo "✅ Done. Look for SonicBuilderSupersonic_Clean.zip"
