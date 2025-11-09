# 🔔 Tier 2 Integration Guide - Sync Monitor + Alert Hooks

Complete guide for the **Sync Monitor Dashboard** and **Alert Hooks System**.

## 📋 Overview

**Tier 2 Files Installed:**
- ✅ `sync_monitor_dashboard.py` - Visual sync & health monitoring dashboard
- ✅ `alert_hooks.py` - Real-time health change notifications

## 🧭 Sync Monitor Dashboard

**Purpose:** Visual dashboard for monitoring Git sync status, health metrics, and system state in real-time.

### Features

- **Git Status Tracking** - Current branch and commit
- **Health Monitoring** - Reads from `docs/status/health.json`
- **Auto-Refresh** - Updates every 10 seconds
- **API Endpoint** - JSON API for programmatic access
- **Dark Theme** - Easy-to-read cyberpunk-style UI

### Usage

**Start Dashboard:**
```bash
python3 sync_monitor_dashboard.py
# Runs on http://localhost:8094
```

**Custom Port:**
```bash
export SYNC_MONITOR_PORT=9000
python3 sync_monitor_dashboard.py
```

**Access:**
- **Dashboard:** `http://localhost:8094/`
- **API:** `http://localhost:8094/api/status`

### Dashboard Display

```
🧭 SonicBuilder Sync Monitor
┌─────────────────────────────────────┐
│ Branch: main                        │
│ Commit: abc123d                     │
│ Last Pull: None                     │
│ Last Push: None                     │
│ Health: ✅ success                  │
│ Sync Active: 🟢 Yes                │
│ Last Updated: 2025-10-31 14:10 UTC │
└─────────────────────────────────────┘
Auto-refresh every 10s
```

### API Response

```json
{
  "last_pull": null,
  "last_push": null,
  "branch": "main",
  "health": {"status": "success"},
  "sync_active": true,
  "commit": "abc123d",
  "updated": "2025-10-31 14:10:37 UTC"
}
```

### Configuration

Edit `sync_monitor_dashboard.py`:

```python
CHECK_INTERVAL = 10  # Update frequency in seconds
```

Environment variables:
```bash
SYNC_MONITOR_PORT=8094  # Dashboard port (default: 8094)
```

## 🚨 Alert Hooks System

**Purpose:** Monitor health.json and send real-time alerts when status changes.

### Features

- **Continuous Monitoring** - Checks health every 30 seconds
- **Change Detection** - Only alerts on status changes
- **Dual Notifications** - Discord + Slack webhooks
- **Integration** - Uses existing ROLLBACK_WEBHOOK_URL
- **Color-Coded** - Green for success, red for failures
- **Detailed Logging** - Full console output

### Usage

**Start Alert Monitor:**
```bash
python3 alert_hooks.py
```

**With Webhooks:**
```bash
# Uses ROLLBACK_WEBHOOK_URL from Replit Secrets
# Or set DISCORD_WEBHOOK_URL or SLACK_WEBHOOK_URL
python3 alert_hooks.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════╗
║   🚨 SONICBUILDER ALERT HOOKS v2.0.9 ACTIVE                   ║
╚════════════════════════════════════════════════════════════════╝
📊 Monitoring: docs/status/health.json
⏱️  Check Interval: 30s
🔔 Discord: ✅ Configured
🔔 Slack: ❌ Not set

[2025-10-31T14:10:00] 🔄 Health status changed: initial → success
[2025-10-31T14:10:00] 📢 Sent Discord alert: success
```

### Discord Alert Format

```
┌───────────────────────────────────┐
│ 🚨 SonicBuilder Health Alert      │
│                                   │
│ Status: success                   │
│                                   │
│ 2025-10-31T14:10:00              │
│ SonicBuilder Alert Hooks v2.0.9  │
└───────────────────────────────────┘
```

### Slack Alert Format

```
✅ SonicBuilder Health Alert
Status: `success`
```

### Configuration

Edit `alert_hooks.py`:

```python
CHECK_INTERVAL = 30  # Check frequency in seconds
HEALTH_PATH = "docs/status/health.json"  # Health file to monitor
```

Environment variables (Replit Secrets):
```bash
ROLLBACK_WEBHOOK_URL=https://discord.com/api/webhooks/...  # Discord
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...     # Slack (optional)
```

### Status Detection

**Triggers Alert:**
- Status changes from one value to another
- Examples: `ok` → `failed`, `success` → `error`, `missing` → `success`

**Does Not Trigger:**
- Status remains the same
- File doesn't exist (logs warning, no alert)

**Recognized Success States:**
- `ok`
- `patched`
- `success`

**Other states considered failures** (red alert)

## 🔧 Integration Patterns

### With Auto-Healer

Auto-Healer writes `docs/status/health.json` → Alert Hooks monitors it → Sends notification on changes

### With CI Helper

CI Helper generates `health.json` → Dashboard displays it → Alert Hooks notifies if status changes

### With Existing Notifications

Alert Hooks uses `ROLLBACK_WEBHOOK_URL` (same as rollback system) → Unified notification channel

### Combined Deployment

Run both as background services:

```bash
# Terminal 1: Sync Monitor
python3 sync_monitor_dashboard.py &

# Terminal 2: Alert Hooks
python3 alert_hooks.py &
```

Or add as workflows:

```python
# Sync Monitor Workflow
workflows_set_run_config_tool(
    name="Sync Monitor",
    command="python3 sync_monitor_dashboard.py",
    output_type="console",
    wait_for_port=8094
)

# Alert Hooks Workflow
workflows_set_run_config_tool(
    name="Alert Hooks",
    command="python3 alert_hooks.py",
    output_type="console"
)
```

## 🎯 Use Cases

### Use Case 1: Visual Monitoring

**Scenario:** You want to see system status at a glance

**Solution:**
```bash
python3 sync_monitor_dashboard.py
# Open http://localhost:8094 in browser
```

### Use Case 2: Real-Time Alerts

**Scenario:** Get notified when health changes

**Solution:**
```bash
# Set up Discord webhook in Replit Secrets
# Run alert hooks
python3 alert_hooks.py
```

### Use Case 3: API Integration

**Scenario:** External monitoring wants to check status

**Solution:**
```bash
curl http://localhost:8094/api/status
# Returns JSON with current status
```

### Use Case 4: Combined Monitoring

**Scenario:** Full monitoring stack with visual + alerts

**Solution:**
```bash
python3 sync_monitor_dashboard.py &
python3 alert_hooks.py &
# Dashboard + real-time alerts
```

## 🔍 Troubleshooting

### Dashboard Port Conflict

**Problem:** Port 8094 already in use

**Solution:**
```bash
export SYNC_MONITOR_PORT=9000
python3 sync_monitor_dashboard.py
```

### No Health Data

**Problem:** Dashboard shows "missing" status

**Solution:**
- Ensure `docs/status/health.json` exists
- Run CI Helper or Auto-Healer to generate it
- Check file permissions

### Alerts Not Sending

**Problem:** No Discord/Slack notifications

**Solution:**
```bash
# Verify webhook is set
echo $ROLLBACK_WEBHOOK_URL

# Test webhook manually
curl -X POST $ROLLBACK_WEBHOOK_URL -H "Content-Type: application/json" \
  -d '{"content":"Test from SonicBuilder"}'
```

### Too Many Alerts

**Problem:** Getting alerts for every check

**Solution:**
- Alerts only fire on status *changes*
- If getting too many, health file is changing frequently
- Check what's writing to health.json
- Increase `CHECK_INTERVAL` in alert_hooks.py

## 📊 Integration with Full System

```
GitHub Actions
    │
    ├─ Builds & deploys
    ├─ Updates health.json
    │
    ↓
docs/status/health.json
    │
    ├─ Sync Monitor reads (every 10s)
    │   └─ Displays on http://localhost:8094
    │
    └─ Alert Hooks reads (every 30s)
        └─ Sends Discord/Slack on changes
```

## 📚 Complete File Structure

```
SonicBuilder/
├── sync_monitor_dashboard.py      # ← NEW (Tier 2)
├── alert_hooks.py                  # ← NEW (Tier 2)
│
├── docs/status/
│   └── health.json                 # Monitored by both
│
└── TIER2_INTEGRATION_GUIDE.md     # ← This file
```

## 🎉 Benefits

**Sync Monitor Dashboard:**
- ✅ Visual status overview
- ✅ Real-time updates
- ✅ API for automation
- ✅ Auto-refresh
- ✅ Clean UI

**Alert Hooks:**
- ✅ Instant notifications
- ✅ Change detection only
- ✅ Dual webhook support
- ✅ Detailed logging
- ✅ Low overhead

**Combined:**
- ✅ Visual + audible monitoring
- ✅ Historical + real-time tracking
- ✅ Local + remote notifications

---

**SonicBuilder v2.0.9 — Tier 2 Integration Complete**

*Visual Monitoring + Real-Time Alerts*
