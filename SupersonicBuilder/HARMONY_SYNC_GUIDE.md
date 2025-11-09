# 💓 SonicBuilder Harmony Sync Guide

## Overview

**Harmony** is a bidirectional synchronization system that creates a heartbeat between GitHub Actions and your Replit instance, ensuring continuous deployment even if one platform experiences issues.

---

## 🎯 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                  HARMONY SYNC FLOW                          │
└─────────────────────────────────────────────────────────────┘

     ┌──────────────┐                    ┌──────────────┐
     │   GitHub     │                    │    Replit    │
     │   Actions    │                    │   Instance   │
     └──────────────┘                    └──────────────┘
            │                                    │
            │  1. Hourly Workflow               │
            ├──────────────────────────>         │
            │   - Build docs                    │
            │   - Deploy Pages                  │
            │   - Update badges                 │
            │                                    │
            │  2. Send Heartbeat                │
            ├──────────────────────────>         │
            │   POST /founder_autodeploy/harmony│
            │                                    │
            │                          3. Store Timestamp
            │                            & Log Event
            │                                    │
            │  4. Harmony Watchdog Monitors     │
            │     If no heartbeat > 1.5 hours   │
            │     ◄──────────────────────────────┤
            │                          5. Trigger Local
            │                             Deploy
```

---

## 📦 Components

### **1. GitHub Actions Workflows**

#### **Eternal Loop** (`.github/workflows/eternal-loop.yaml`)
- **Trigger:** Every hour (cron: `0 * * * *`) + manual dispatch
- **Actions:**
  1. Rebuild documentation
  2. Generate Harmony badge
  3. Update all badges
  4. Export dashboard snapshot
  5. Deploy to GitHub Pages
  6. Commit metadata changes
  7. Verify deployment health

#### **Harmony Heartbeat** (`.github/workflows/harmony-heartbeat.yaml`)
- **Trigger:** After Eternal Loop completes
- **Actions:**
  1. Send POST request to Replit
  2. Include workflow status and metadata
  3. Log heartbeat confirmation

---

### **2. Replit Endpoints**

#### **Heartbeat Receiver** (`POST /founder_autodeploy/harmony`)
- Receives heartbeat from GitHub Actions
- Stores timestamp in `last_heartbeat.txt`
- Logs to security audit trail
- Sends Discord notification
- Returns JSON acknowledgment

**Example Request:**
```bash
curl -X POST "https://your-replit.repl.co/founder_autodeploy/harmony" \
  -d "status=success&workflow=Eternal Loop&run=42"
```

**Response:**
```json
{
  "status": "success",
  "message": "Harmony sync acknowledged",
  "timestamp": "2025-10-31T01:00:00Z"
}
```

---

#### **Status API** (`GET /status/harmony`)
- Returns current Harmony sync status
- Includes badge URL and timing data
- Public endpoint (no auth required)

**Example Request:**
```bash
curl "https://your-replit.repl.co/status/harmony"
```

**Response:**
```json
{
  "status": "Active",
  "color": "brightgreen",
  "badge_url": "https://img.shields.io/badge/Harmony-Active-brightgreen.svg",
  "last_heartbeat_age_sec": 1247.55,
  "last_update": "2025-10-31 01:00:00 UTC",
  "source": "Replit Harmony Sync Engine"
}
```

**Status States:**
- **Active** (green) - Last heartbeat < 1.5 hours
- **Late** (yellow) - Last heartbeat 1.5-2 hours
- **Desync** (red) - Last heartbeat > 2 hours

---

#### **Visual Dashboard** (`GET /status/dashboard`)
- Beautiful HTML dashboard with auto-refresh
- Animated status indicator
- Real-time heartbeat age display
- Links to other dashboards
- Updates every 60 seconds

**Features:**
- 🟢 Pulsing status light (color-coded)
- 📊 Statistics cards
- 🎨 Dynamic Shields.io badge display
- 🔗 Quick links to other dashboards

---

### **3. Harmony Watchdog**

Built into `autodeploy_api.py`, the watchdog monitors GitHub Actions heartbeat and triggers fallback deploys if needed.

**Behavior:**
- Runs in background thread
- Checks heartbeat every 10 minutes
- If no heartbeat for 1.5 hours → Triggers local deploy
- Prevents infinite loops by updating timestamp after trigger

**Startup:**
```python
# Started automatically with AutoDeploy API
watchdog_thread = threading.Thread(target=harmony_watchdog, daemon=True)
watchdog_thread.start()
```

---

### **4. Badge Generation**

#### **generate_heartbeat_badge.py**
- Reads `last_heartbeat.txt`
- Calculates heartbeat age
- Generates Shields.io badge URL
- Saves to `badges/heartbeat.json`

**Output Example:**
```json
{
  "status": "Active",
  "color": "brightgreen",
  "badge": "https://img.shields.io/badge/Harmony-Active-brightgreen.svg",
  "last_check": "2025-10-31 01:00 UTC",
  "delta_seconds": 1247.55
}
```

#### **Integration with update_badges.py**
Harmony badge automatically included in README badge block:
```markdown
![Harmony](https://img.shields.io/badge/Harmony-Active-brightgreen.svg)
```

---

### **5. Dashboard Export**

#### **export_dashboard_to_pages.py**
- Fetches current dashboard HTML from Replit
- Saves snapshot to `docs_build/status/dashboard.html`
- Deployed to GitHub Pages
- Accessible even when Replit is offline

**Usage:**
```bash
python3 export_dashboard_to_pages.py
```

---

### **6. Harmony Feed System**

The Harmony Feed provides a historical log of heartbeat events in both JSON and RSS formats, with automatic archiving to GitHub Pages.

#### **Feed Logging** (`harmony_feed.json`)
- Tracks last 50 heartbeat events
- Stores timestamp, status, color, and elapsed time
- Automatically rotates entries (FIFO)
- Updated on every heartbeat and status check

**Entry Format:**
```json
{
  "timestamp": "2025-10-31 01:00:00 UTC",
  "status": "Active",
  "color": "brightgreen",
  "elapsed_minutes": 21.7
}
```

#### **Feed Endpoint** (`GET /status/feed`)
Serves feed in JSON or RSS format.

**JSON Format** (default):
```bash
curl "https://your-replit.repl.co/status/feed"
# Returns array of last 50 heartbeat entries
```

**RSS Format:**
```bash
curl "https://your-replit.repl.co/status/feed?format=rss"
# Returns RSS 2.0 feed for feed readers
```

**RSS Example:**
```xml
<rss version="2.0">
  <channel>
    <title>SonicBuilder Harmony Feed</title>
    <link>https://sonicbuilder.replit.app/status/feed</link>
    <description>Live heartbeat log for SonicBuilder infrastructure.</description>
    <item>
      <title>Active at 2025-10-31 01:00:00 UTC</title>
      <description>Color: brightgreen | Elapsed: 21.7m</description>
      <pubDate>2025-10-31 01:00:00 UTC</pubDate>
    </item>
  </channel>
</rss>
```

#### **GitHub Pages Feed Mirroring**
Eternal Loop workflow automatically mirrors feeds to GitHub Pages:
- **Live JSON Feed:** `https://yourusername.github.io/SonicBuilder/status/feed.json`
- **Live RSS Feed:** `https://yourusername.github.io/SonicBuilder/status/feed.rss`

#### **Daily Feed Archiving**
- Archives saved daily as `feed_YYYYMMDD.json`
- Stored in `docs_build/status/archive/`
- Accessible via archive index: `https://yourusername.github.io/SonicBuilder/status/archive/`
- Auto-generated index page lists all archived snapshots

#### **Feed Health Badge** (`scripts/gen_feed_badge.py`)
Generates health badge based on feed freshness:
- **healthy** (green) - Last entry < 24 hours
- **desync** (red) - Last entry >= 24 hours
- **empty** (red) - Feed has no entries
- **missing** (gray) - Feed file doesn't exist

**Badge Format:**
```json
{
  "schemaVersion": 1,
  "label": "Feed",
  "message": "healthy",
  "color": "brightgreen"
}
```

**Usage in README:**
```markdown
[![Feed Health](https://img.shields.io/endpoint?url=https://yourusername.github.io/SonicBuilder/badges/feed_health.json)](https://yourusername.github.io/SonicBuilder/status/feed.json)
```

#### **Feed Badge Refresh Workflow**
`.github/workflows/feed-badge-refresh.yaml` runs every 12 hours to update feed health badge.

**Features:**
- Automatic 12-hour refresh cycle
- Manual trigger support
- Only commits if badge changes
- Minimal resource usage

---

### **7. Auto-Healer System**

The Auto-Healer is a self-healing background service that monitors feed and PDF health, automatically triggering rebuilds and GitHub Actions when issues are detected.

#### **Auto-Healer Script** (`replit_auto_healer.py`)
Comprehensive monitoring and healing service that runs in the background.

**Features:**
- Monitors Harmony feed freshness (checks every 15 minutes)
- Monitors PDF documentation age
- Triggers GitHub Actions if feed is stale (>24 hours)
- Attempts local PDF rebuild if needed
- Writes periodic heartbeat to GitHub Pages
- Updates auto-healer status badge
- Detailed logging with timestamps

**Healing Logic:**
```python
# Feed healing
if feed_age > 24 hours:
    trigger_github_action("stale_feed")

# PDF healing  
if pdf_age > 24 hours:
    rebuild_pdf()  # Try local rebuild first
    if failed:
        trigger_github_action("stale_pdf")  # Fallback to GitHub

# Heartbeat
every 1 hour:
    write_heartbeat()  # Update docs/status/heartbeat.json
```

**Usage:**
```bash
python3 replit_auto_healer.py
```

**Output:**
```
╔════════════════════════════════════════════════════════════════╗
║   🤖 SonicBuilder Auto-Healer v2.0.9 Started                  ║
╚════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Healing Cycle #1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Feed healthy (2.3h old)
✅ PDF healthy (1.5h old)
💓 Heartbeat written: 2025-10-31 02:15:00 UTC
💤 Sleeping 15 minutes until next check
```

#### **Feed Dashboard** (`replit_feed_dashboard.py`)
Interactive web UI for monitoring feed health with manual controls.

**Features:**
- Beautiful dark-themed dashboard
- Real-time status indicators (green/yellow/red)
- Manual GitHub Action trigger button
- PDF build status display
- Auto-refresh every 30 seconds
- Background monitoring thread
- Countdown timer for next check

**Access:**
```
https://your-replit.repl.co:8099/
```

**Dashboard Sections:**
1. **Feed Status Card** - Shows feed age and health status
2. **PDF Build Card** - Latest PDF info with download link
3. **GitHub Pages Card** - Deployment status and feed mirror links
4. **Auto-Refresh Card** - Countdown to next automatic check

**Manual Trigger:**
Click "🔁 Trigger GitHub Refresh Now" button to manually trigger feed badge refresh workflow.

#### **Auto-Healer Badge**
Auto-healer updates its own status badge to show operational state.

**Badge File:** `badges/auto_healer_status.json`

**States:**
- **active** (green) - Auto-healer is running
- **paused** (orange) - Auto-healer is stopped

**Badge Format:**
```json
{
  "schemaVersion": 1,
  "label": "Auto-Healer",
  "message": "active",
  "color": "green",
  "isError": false
}
```

**Usage in README:**
```markdown
[![Auto-Healer](https://img.shields.io/endpoint?url=https://yourusername.github.io/SonicBuilder/badges/auto_healer_status.json)](https://your-replit.repl.co:8099/)
```

#### **Heartbeat System**
Auto-healer writes periodic heartbeats that get deployed to GitHub Pages.

**Heartbeat File:** `docs/status/heartbeat.json`

**Format:**
```json
{
  "timestamp": "2025-10-31 02:15:00 UTC",
  "status": "alive",
  "source": "Replit Auto-Healer",
  "version": "2.0.9"
}
```

**Purpose:**
- Proves Replit instance is online
- Visible on GitHub Pages
- Can be monitored externally
- Updates hourly

#### **Uptime Logging System**
The auto-healer records uptime entries to a rolling 7-day log.

**Uptime Log File:** `docs/status/uptime_log.json`

**Format:**
```json
[
  {
    "timestamp": "2025-10-31 11:04:37 UTC",
    "status": "up",
    "source": "Auto-Healer"
  }
]
```

**Features:**
- Logs uptime entry every hour (with heartbeat)
- Automatic pruning of entries older than 7 days
- Rolling window keeps recent history
- Deployed to GitHub Pages for external monitoring

**Uptime Dashboard:**
Interactive visualization at `docs/dashboard/uptime.html`

Features:
- Chart.js bar graph showing 7-day activity
- Last ping timestamp
- System status indicator (🟢 Online / 🔴 Offline)
- Auto-adaptive dark/light theme
- Fetches data from uptime_log.json

**System Health Summary:**
Generate comprehensive health summary with `make system_json`

```bash
make system_json
```

Creates `docs/status/system.json` with:
- System version and branch
- Last heartbeat timestamp
- Last uptime entry
- Latest PDF info and checksum
- Overall health status

**Shields.io Badge Format:**
```json
{
  "schemaVersion": 1,
  "label": "System",
  "message": "healthy",
  "color": "brightgreen",
  "status": "healthy"
}
```

#### **Rollback Protection System**
Automatic rollback and notification system for system health deployments.

**Scripts:**
- `scripts/push_system_json.py` - Pushes system.json to GitHub Pages
- `scripts/rollback_system_json.py` - Rollback on corruption/failure
- `scripts/notify_rollback.py` - Discord/Slack notifications

**Features:**
- Automatic corruption detection
- Rollback to last known good state
- Discord/Slack webhook notifications
- Artifact archival (30-day retention)
- SHA256 integrity verification

**Workflow:** `.github/workflows/system-health-ci.yml`

Runs every 6 hours and:
1. Generates system.json
2. Pushes to gh-pages
3. Rolls back on failure
4. Sends notifications
5. Archives artifacts

**Required Secrets:**
```
ROLLBACK_WEBHOOK_URL - Discord webhook URL
SLACK_WEBHOOK_URL - Slack webhook URL (optional)
```

**Notification Types:**
- 🟢 Success (green) - Deployment successful
- 🔴 Rollback (red) - Corruption detected, rollback executed
- 🟡 Warning (yellow) - Unknown event

**Artifact Retention:**
- Success: 30 days (PDFs, system.json, badges)
- Failure: 14 days (logs, workflows, scripts)

---

## 🚀 Setup Instructions

### **Step 1: Configure GitHub Repository**

1. **Add Workflows:**
   - Workflows already created in `.github/workflows/`
   - Eternal Loop runs hourly automatically
   - Heartbeat runs after Eternal Loop

2. **Set Repository Secret:**
   ```
   Name:  REPLIT_HARMONY_URL
   Value: https://your-replit.repl.co/founder_autodeploy/harmony
   ```

   **How to add:**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add `REPLIT_HARMONY_URL` with your Replit URL

3. **Ensure `GITHUB_TOKEN` has permissions:**
   - Go to Settings → Actions → General
   - Under "Workflow permissions"
   - Select "Read and write permissions"
   - Save

---

### **Step 2: Configure Replit Instance**

1. **Start Services:**
   ```bash
   # Webhook listener (includes Harmony endpoints)
   python3 founder_webhook_listener_fortified_persist.py

   # AutoDeploy API (includes Harmony watchdog)
   python3 founder_infinity/services/autodeploy_api.py
   ```

2. **Or use unified startup:**
   ```bash
   ./start_infinity_suite.sh
   ```

3. **Verify Endpoints:**
   ```bash
   # Test heartbeat receiver (will create initial timestamp)
   curl -X POST "https://your-replit.repl.co/founder_autodeploy/harmony"

   # Check status
   curl "https://your-replit.repl.co/status/harmony"

   # View dashboard
   open "https://your-replit.repl.co/status/dashboard"
   ```

---

### **Step 3: Trigger First Workflow**

1. **Manual Trigger:**
   - Go to GitHub repository
   - Click "Actions" tab
   - Select "🧠 SonicBuilder Eternal Loop"
   - Click "Run workflow"

2. **Wait for Completion:**
   - Eternal Loop runs (5-10 minutes)
   - Heartbeat workflow triggers automatically
   - Check Replit for heartbeat confirmation

3. **Verify:**
   ```bash
   # Check if heartbeat file exists
   cat last_heartbeat.txt

   # Check badge
   python3 generate_heartbeat_badge.py

   # View status
   curl "https://your-replit.repl.co/status/harmony"
   ```

---

## 📊 Monitoring

### **Dashboard Access**

- **JSON API:** `https://your-replit.repl.co/status/harmony`
- **Visual Dashboard:** `https://your-replit.repl.co/status/dashboard`
- **GitHub Pages:** `https://your-github.github.io/SonicBuilder/status/dashboard.html`

### **Badge Display**

Add to README.md:
```markdown
![Harmony](https://img.shields.io/badge/Harmony-Active-brightgreen.svg)
```

Or use dynamic badge from API:
```markdown
![Harmony Status](https://your-replit.repl.co/badge/status.svg?key=YOUR_API_KEY)
```

### **Audit Trail**

All Harmony events logged to `security_audit.json`:
```json
{
  "timestamp": "2025-10-31T01:00:00Z",
  "ip": "140.82.115.x",
  "event": "harmony_ping",
  "detail": "GitHub Actions heartbeat received"
}
```

View via Command Deck:
`https://your-replit.repl.co/founder/command-deck`

---

## 🔧 Troubleshooting

### **Heartbeat Not Received**

**Symptom:** Status shows "Desync" or "Unknown"

**Checks:**
1. Verify `REPLIT_HARMONY_URL` secret is set correctly
2. Check GitHub Actions workflow logs
3. Ensure Replit webhook listener is running
4. Check firewall/network issues

**Test Manually:**
```bash
curl -X POST "https://your-replit.repl.co/founder_autodeploy/harmony" \
  -d "status=test"
```

---

### **Watchdog Not Triggering**

**Symptom:** No local deploys despite GitHub Actions failure

**Checks:**
1. Verify AutoDeploy API is running
2. Check `last_heartbeat.txt` exists and has valid timestamp
3. Review AutoDeploy API logs for watchdog status
4. Ensure timestamp is > 1.5 hours old

**Debug:**
```bash
# Check heartbeat age
python3 -c "import time; print(f'{(time.time() - float(open(\"last_heartbeat.txt\").read()))/3600:.2f} hours')"

# Force trigger (edit timestamp to old value)
echo "0" > last_heartbeat.txt

# Wait 10 minutes for watchdog check
```

---

### **Badge Shows "Unknown"**

**Symptom:** Harmony badge displays "Unknown" status

**Checks:**
1. Verify `badges/heartbeat.json` exists
2. Run badge generation manually:
   ```bash
   python3 generate_heartbeat_badge.py
   ```
3. Check `last_heartbeat.txt` exists and has valid timestamp
4. Update all badges:
   ```bash
   python3 founder_infinity/scripts/update_badges.py
   ```

---

### **Dashboard Shows Desync**

**Symptom:** Dashboard shows red status despite recent heartbeat

**Checks:**
1. Check system time synchronization
2. Verify timestamp in `last_heartbeat.txt`
3. Clear browser cache (dashboard may be cached)
4. Check for time zone issues

**Fix:**
```bash
# Manually update heartbeat
python3 -c "import time; open('last_heartbeat.txt', 'w').write(str(time.time()))"

# Refresh dashboard (auto-refreshes every 60s)
```

---

## 🎯 Use Cases

### **1. Continuous Deployment**
GitHub Actions handles primary deployments every hour, ensuring documentation stays fresh.

### **2. Failover Protection**
If GitHub Actions fails, Replit watchdog detects desync and triggers local deploy as backup.

### **3. Health Monitoring**
Visual dashboard and badges provide instant status visibility.

### **4. Audit Trail**
Complete log of all heartbeat events for compliance and debugging.

### **5. Offline Access**
Dashboard snapshot on GitHub Pages accessible even when Replit is down.

---

## 📈 Advanced Configuration

### **Adjust Heartbeat Interval**

Edit `.github/workflows/eternal-loop.yaml`:
```yaml
on:
  schedule:
    - cron: "0 */2 * * *"   # Every 2 hours instead of 1
```

Update thresholds in multiple files:
```python
# generate_heartbeat_badge.py
MAX_INTERVAL = 10800  # 3 hours (2x interval + buffer)

# founder_webhook_listener_fortified_persist.py
if delta < 10800:  # 3 hours
    status, color = "Active", "brightgreen"

# founder_infinity/services/autodeploy_api.py
if elapsed > 10800:  # 3 hours
    print("Triggering fallback...")
```

---

### **Add More Heartbeat Data**

Modify GitHub Actions to send additional metadata:
```yaml
- name: 💓 Send Harmony Heartbeat
  run: |
    curl -X POST "$REPLIT_HARMONY_URL" \
      -d "status=success" \
      -d "workflow=${{ github.workflow }}" \
      -d "run=${{ github.run_number }}" \
      -d "repo=${{ github.repository }}" \
      -d "commit=${{ github.sha }}"
```

Update webhook listener to parse and log this data.

---

### **Discord Notifications**

Harmony heartbeats already trigger Discord alerts if `DISCORD_WEBHOOK` is configured.

Customize message in `founder_webhook_listener_fortified_persist.py`:
```python
send_discord_alert(
    "💓 Harmony Sync", 
    f"GitHub Actions heartbeat received\nWorkflow: {workflow}\nRun: {run_number}",
    0x3498db
)
```

---

## 🔐 Security Considerations

### **Endpoint Protection**

The `/founder_autodeploy/harmony` endpoint is **intentionally public** (no API key required) because:
1. GitHub Actions needs easy access
2. Endpoint only stores timestamp (no sensitive operations)
3. All events are logged to audit trail
4. Receiving heartbeats is non-destructive

### **Rate Limiting**

The webhook listener's rate limiting applies to Harmony endpoints, preventing abuse.

### **Audit Logging**

Every heartbeat logged with:
- Source IP
- Timestamp
- Event type ("harmony_ping")
- Detail message

Review via `/audit` endpoint or Command Deck dashboard.

---

## 📊 Performance

### **Resource Usage**

- **GitHub Actions:** ~5-10 minutes per hour
- **Replit Watchdog:** Minimal (sleeps 10 minutes between checks)
- **API Calls:** 1 POST request per hour
- **Storage:** ~1 KB per heartbeat log entry

### **Reliability**

- **Uptime Target:** 99.9%
- **Recovery Time:** < 10 minutes (watchdog check interval)
- **Data Durability:** Audit log persisted to file + GitHub mirror

---

## 🎓 Best Practices

1. **Monitor Dashboard Regularly** - Check visual dashboard weekly
2. **Review Audit Logs** - Inspect harmony_ping events monthly
3. **Test Failover** - Manually disable GitHub Actions to verify watchdog
4. **Keep Secrets Updated** - Rotate `REPLIT_HARMONY_URL` if Replit URL changes
5. **Version Control** - Commit all workflow and script changes
6. **Backup Heartbeat Data** - Include `last_heartbeat.txt` in mirror sync

---

## 🔗 Related Documentation

- **Infinity Suite:** `founder_infinity/README.md`
- **Architecture:** `INFINITY_ARCHITECTURE.md`
- **Quick Reference:** `INFINITY_QUICK_REFERENCE.md`
- **Webhook Listener:** `WEBHOOK_LISTENER_GUIDE.md`

---

## 📞 Support

For issues or questions:

1. Check `/status/harmony` API for current status
2. Review workflow logs in GitHub Actions
3. Check Replit logs for webhook listener and AutoDeploy API
4. Inspect `security_audit.json` for harmony_ping events
5. Verify all endpoints accessible

---

**💓 Built with resilience by SonicBuilder v2.0.9 — Harmony Edition**

*Ensuring your documentation stays synchronized, no matter what.*
