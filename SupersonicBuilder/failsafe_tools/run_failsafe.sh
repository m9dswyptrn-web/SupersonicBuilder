#!/bin/bash
echo "🧯 Activating Supersonic Failsafe Recovery..."
if [ -f restore_baseline.sh ]; then
    bash restore_baseline.sh
else
    echo "No baseline restore found; running minimal rebuild."
    pip install -r requirements.txt || true
fi
echo "✅ Recovery complete at $(date)"
