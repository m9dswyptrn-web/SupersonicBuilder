#!/bin/bash
# Start Advanced DSP Control Center on port 8100

cd "$(dirname "$0")"
export DSP_PORT=8100

echo "🎚️  Starting Advanced DSP Control Center on port 8100"
echo "🎧  Professional audio tuning for EOENKK Android 15"
echo "📊  31-band parametric EQ | Crossover | Time Alignment"
echo ""
echo "Service will be available at: http://localhost:8100"
echo "Health endpoint: http://localhost:8100/health"
echo ""

python3 app.py
