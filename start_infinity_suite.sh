#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🚀 Starting SonicBuilder Infinity Suite v2.0.9               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check environment variables
echo "🔧 Checking configuration..."

if [ -z "$FOUNDER_API_KEY" ]; then
  echo "⚠️  WARNING: FOUNDER_API_KEY not set!"
fi

if [ -z "$GITHUB_TOKEN" ]; then
  echo "⚠️  WARNING: GITHUB_TOKEN not set!"
fi

if [ -z "$DISCORD_WEBHOOK" ]; then
  echo "⚠️  WARNING: DISCORD_WEBHOOK not set!"
fi

echo ""

# Start services
echo "🚀 Starting services..."
echo ""

# Main Webhook Listener (includes dashboards)
echo "  ▶️  Webhook Listener (Port 8080) + Dashboards"
python3 founder_webhook_listener_fortified_persist.py &
PID1=$!
sleep 2

# Badge Engine
echo "  ▶️  Badge Engine (Port 8081)"
python3 founder_infinity/services/badge_engine.py &
PID2=$!
sleep 1

# AutoDeploy API
echo "  ▶️  AutoDeploy API (Port 8082)"
python3 founder_infinity/services/autodeploy_api.py &
PID3=$!
sleep 1

# Mirror Sync (background)
echo "  ▶️  Mirror Sync Service (hourly)"
python3 founder_infinity/services/mirror_sync.py &
PID4=$!
sleep 1

# Scheduler ULTRA
echo "  ▶️  Scheduler ULTRA (autonomous deployment)"
python3 supersonic_scheduler_ultra.py &
PID5=$!
sleep 1

echo ""
echo "✅ All services started successfully!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  🖥️  DASHBOARD URLS"
echo "═══════════════════════════════════════════════════════════════"
echo "  Command Deck:      https://your-replit.repl.co/founder/command-deck"
echo "  Mirror Dashboard:  https://your-replit.repl.co/founder/mirror-dashboard"
echo "  Watchtower:        https://your-replit.repl.co/founder/watchtower"
echo "  Infinity Console:  https://your-replit.repl.co/founder/infinity-console"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  🔧  SERVICE STATUS"
echo "═══════════════════════════════════════════════════════════════"
echo "  Webhook Listener:  PID $PID1"
echo "  Badge Engine:      PID $PID2"
echo "  AutoDeploy API:    PID $PID3"
echo "  Mirror Sync:       PID $PID4"
echo "  Scheduler ULTRA:   PID $PID5"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Keep script running and handle Ctrl+C
trap "echo ''; echo '🛑 Stopping all services...'; kill $PID1 $PID2 $PID3 $PID4 $PID5 2>/dev/null; echo '✅ All services stopped'; exit" SIGINT SIGTERM

wait
