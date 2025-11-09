#!/usr/bin/env bash
set -euo pipefail

echo "🚀 SonicBuilder Deployment Chain Starting..."

# Deploy to GitHub
python3 deploy_all_to_github.py

# Verify workflows (optional - requires GH_TOKEN)
if [[ -n "${GH_TOKEN:-}" ]]; then
    echo "🔍 Verifying workflows..."
    python3 -m pip install --quiet requests 2>/dev/null || true
    python3 deploy_verify.py
else
    echo "⚠️ GH_TOKEN not set, skipping workflow verification"
fi

# Send notifications (optional - requires webhook)
if [[ -n "${SLACK_WEBHOOK_URL:-}" ]] || [[ -n "${DISCORD_WEBHOOK_URL:-}" ]]; then
    echo "📣 Sending notifications..."
    python3 deploy_notify.py
else
    echo "ℹ️ No webhooks configured, skipping notifications"
fi

echo "✅ Deployment chain complete!"
