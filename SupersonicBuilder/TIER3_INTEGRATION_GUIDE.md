# 📊 Tier 3 Integration Guide - Charts, Secrets & Automation

Complete guide for **5 advanced SonicBuilder tools** that add visualization, secrets management, continuous sync, auto-patching, and PDF appendix generation.

## 📋 Overview

**Tier 3 Files Installed:**
- ✅ `fusion_live_charts.py` - Real-time Chart.js visualization dashboard
- ✅ `secrets_configurator.py` - Interactive secrets validator & configurator
- ✅ `smart_pair_sync.py` - Continuous Replit ↔ GitHub synchronization
- ✅ `local_autopatch.py` - Local mirror of GitHub QuickFix logic
- ✅ `fusion_appendix_injector.py` - PDF health appendix generator

---

## 📈 1. Fusion Live Charts

**Purpose:** Real-time telemetry visualization with Chart.js graphs showing health metrics over time.

### Features

- **Chart.js Visualization** - Beautiful line charts for health trends
- **Auto-Refresh** - Updates every 15 seconds
- **500-Point History** - Displays last 500 health checks
- **JSON API** - Programmatic access to metrics
- **Dark Theme** - Cyberpunk-style UI matching other dashboards

### Usage

**Start Charts Server:**
```bash
python3 fusion_live_charts.py
# Runs on http://localhost:8092
```

**Custom Port:**
```bash
export FUSION_CHARTS_PORT=9092
python3 fusion_live_charts.py
```

**Access:**
- **Dashboard:** `http://localhost:8092/charts`
- **API:** `http://localhost:8092/charts/data.json`

### Dashboard Display

```
🧠 Fusion Live Telemetry Charts
Uptime: 95.0% | Failures: 3

[Interactive Chart.js Line Graph]
- Green line showing health index over time
- X-axis: Timestamps
- Y-axis: Health level (0-1)
- Auto-refreshes every 15 seconds
```

### API Response

```json
{
  "uptime": 95.0,
  "failures": 3,
  "avg_delay": 0,
  "data": [
    {
      "time": "2025-10-31T14:00:00Z",
      "status": "green",
      "color": "#00e676"
    },
    {
      "time": "2025-10-31T14:15:00Z",
      "status": "green",
      "color": "#00e676"
    }
  ]
}
```

### Data Source

Reads from **Auto-Healer uptime logs** (`logs/uptime/*.json`)

Each log file:
```json
{
  "timestamp": "2025-10-31T14:00:00Z",
  "status": "success"
}
```

Charts converts `success` → green line, anything else → red line

### Configuration

Edit `fusion_live_charts.py`:

```python
LOG_DIR = "logs/uptime"  # Data source
PORT = 8092              # Server port
```

Environment variables:
```bash
FUSION_CHARTS_PORT=8092  # Custom port
```

---

## 🔐 2. Secrets Configurator

**Purpose:** Interactive tool to validate and configure all required Replit Secrets with automated testing.

### Features

- **Interactive Prompts** - Guides you through each secret
- **Validation** - Tests GitHub tokens and webhooks
- **Smart Detection** - Checks if secrets already exist
- **Safe Storage** - Uses Replit Secrets vault
- **Guided Setup** - Shows next steps after configuration

### Usage

**Run Configurator:**
```bash
python3 secrets_configurator.py
```

**Interactive Session:**
```
🚀 SonicBuilder Secrets Auto-Configurator
======================================================================

🔐 GITHUB_TOKEN — Used for authenticated pushes and GitHub API actions
❓ Paste or type your GITHUB_TOKEN value: [paste token]
🧪 Verifying GitHub token...
✅ GitHub token valid for user: m9dswyptrn-web

🔐 ROLLBACK_WEBHOOK_URL — Discord webhook for rollback and health alerts
✅ Already found in Replit Secrets (length 120).

🔐 SLACK_WEBHOOK_URL — Slack webhook for notifications (optional)
❓ Paste or type your SLACK_WEBHOOK_URL value: [skip]
⚠️ Skipped — no value provided.

🔐 SESSION_SECRET — Flask session security key
✅ Already found in Replit Secrets (length 32).

======================================================================
✅ All required secrets checked or configured.
💾 Saved securely in Replit Secrets vault.

🚀 You can now safely run all SonicBuilder services:
   python3 auto_orchestrator.py        # Full build automation
   python3 alert_hooks.py              # Health alerts
   python3 sync_monitor_dashboard.py   # Visual dashboard
   python3 smart_pair_sync.py          # Continuous GitHub sync
```

### Required Secrets

| Secret | Purpose | Required? |
|--------|---------|-----------|
| `GITHUB_TOKEN` | GitHub API authentication | ✅ Yes |
| `ROLLBACK_WEBHOOK_URL` | Discord rollback/health alerts | ✅ Yes |
| `SLACK_WEBHOOK_URL` | Slack notifications | ❌ Optional |
| `SESSION_SECRET` | Flask session security | ✅ Yes |

### Validation Tests

**GitHub Token Test:**
```bash
GET https://api.github.com/user
# Verifies token validity and shows username
```

**Discord Webhook Test:**
```bash
POST [webhook_url]
# Sends test message: "✅ SonicBuilder webhook connected successfully!"
```

### Manual Secret Setup

If you prefer manual setup:

```bash
# In Replit Secrets tab:
GITHUB_TOKEN=ghp_your_token_here
ROLLBACK_WEBHOOK_URL=https://discord.com/api/webhooks/...
SESSION_SECRET=your-random-32-char-string
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...  # optional
```

---

## 🔄 3. Smart Pair Sync

**Purpose:** Continuous bidirectional synchronization between Replit workspace and GitHub repository.

### Features

- **Automatic Pull** - Fetches latest changes from GitHub
- **Automatic Push** - Commits and pushes local changes
- **3-Minute Cycles** - Configurable sync interval
- **Rebase Strategy** - Clean linear history
- **Auto-Commit** - Timestamps every sync
- **Background Service** - Runs continuously

### Usage

**Start Sync Service:**
```bash
python3 smart_pair_sync.py
```

**Expected Output:**
```
[2025-10-31T14:00:00] 🚀 SonicBuilder Smart Pair Sync engaged.
[2025-10-31T14:00:00] 🔍 Checking Git remote...
[2025-10-31T14:00:00] ✅ Remote origin already configured.
[2025-10-31T14:00:00] 🔁 Starting sync cycle...
[2025-10-31T14:00:00] ⬇️ Pulling latest changes from GitHub...
[2025-10-31T14:00:01] Already up to date.
[2025-10-31T14:00:01] ⬆️ Pushing local Replit changes to GitHub...
[2025-10-31T14:00:01] Nothing to commit
[2025-10-31T14:00:01] ⏳ Waiting 3 minutes for next cycle...
```

### Configuration

Edit `smart_pair_sync.py`:

```python
SYNC_INTERVAL = 180  # Seconds (default: 3 minutes)
```

Adjust sync frequency:
```python
SYNC_INTERVAL = 60   # Every 1 minute (aggressive)
SYNC_INTERVAL = 300  # Every 5 minutes (moderate)
SYNC_INTERVAL = 600  # Every 10 minutes (conservative)
```

### Git Remote Setup

Smart Pair Sync auto-configures the GitHub remote:

```bash
git remote add origin https://github.com/m9dswyptrn-web/SonicBuilder.git
```

To change repository:

Edit `smart_pair_sync.py`:
```python
def ensure_remote():
    run("git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git")
```

### Comparison with Harmony Sync

| Feature | Smart Pair Sync | Harmony Sync |
|---------|----------------|--------------|
| Direction | Bidirectional | GitHub → Replit |
| Trigger | Time-based (3 min) | Webhook-based |
| Auto-commit | Yes | No |
| Setup | Simple | Requires webhooks |
| Use case | Active development | Production updates |

**Recommendation:** Use both together for complete coverage!

---

## 🩹 4. Local Auto-Patch Mirror

**Purpose:** Matches GitHub QuickFix logic to repair missing artifacts locally before they trigger CI failures.

### Features

- **Health.json Creation** - Creates missing health files
- **Badge Insertion** - Adds CI badges to README
- **Dummy PDF Trigger** - Generates rebuild triggers
- **Auto-Commit** - Commits repairs to Git
- **GitHub CLI Integration** - Triggers remote workflows
- **[skip ci] Tags** - Prevents infinite loops

### Usage

**Run Auto-Patch:**
```bash
python3 local_autopatch.py
```

**Expected Output:**
```
[2025-10-31T14:00:00] 🧩 Starting SonicBuilder Local Auto-Patch Mirror...
[2025-10-31T14:00:00] ✅ health.json already present.
[2025-10-31T14:00:00] ✅ Added preflight badge to README.md
[2025-10-31T14:00:00] ✅ Added QuickFix badge to README.md
[2025-10-31T14:00:01] ✅ Added dummy rebuild trigger PDF.
[2025-10-31T14:00:02] 🚀 Local auto-patch committed and pushed.
[2025-10-31T14:00:02] 🔁 Triggered remote preflight re-run via GH CLI.
[2025-10-31T14:00:02] ✅ Local Auto-Patch cycle complete.
```

### What It Fixes

**1. Missing health.json:**
```bash
# Creates: docs/status/health.json
{
  "status": "patched-local",
  "timestamp": "2025-10-31T14:00:00Z"
}
```

**2. Missing Badges in README:**
```markdown
[![Smart CI Preflight](badge-url)]
[![QuickFix Auto-Patch](badge-url)]
```

**3. Missing PDF Triggers:**
```bash
# Creates: docs/DUMMY_REBUILD_TRIGGER.pdf
```

### When to Use

- **Before CI runs** - Prevent failures
- **After clean clone** - Restore artifacts
- **Manual repairs** - Fix broken state
- **Testing** - Validate QuickFix logic

### GitHub CLI Requirement

For remote workflow triggering:

```bash
# Install GitHub CLI (if not present)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

Without `gh`, auto-patch still works but won't trigger remote workflows.

---

## 📄 5. Fusion Appendix Injector

**Purpose:** Appends system health summary as final pages to generated PDF manuals.

### Features

- **PDF Merging** - Combines base manual + health appendix
- **PyPDF2 Integration** - Preserves original formatting
- **FPDF Generation** - Creates health pages
- **Markdown Support** - Reads appendix from .md files
- **Auto-Directory Creation** - Creates output folders

### Usage

**Generate PDF with Appendix:**
```bash
python3 fusion_appendix_injector.py
```

**Expected Output:**
```
✅ Fusion Appendix attached → output/SonicBuilder_Manual_With_Health.pdf
```

### Required Files

**Input:**
- `output/SonicBuilder_Manual_Final.pdf` (base manual)
- `docs/appendix_system_health.md` (health summary)

**Output:**
- `output/SonicBuilder_Manual_With_Health.pdf` (merged PDF)

### Appendix Format

Create `docs/appendix_system_health.md`:

```markdown
# System Health Summary

**Build Date:** 2025-10-31
**Health Status:** Excellent (95.0%)

## Metrics
- Uptime: 95.0%
- Failures: 3
- Health Index: 0.95

## Component Status
- Auto-Healer: ✅ Running
- Harmony Sync: ✅ Active
- Rollback Protection: ✅ Enabled
```

This gets appended as final PDF pages with headers and formatting.

### Integration with Auto Orchestrator

Add to orchestration pipeline:

```python
# In auto_orchestrator.py
def step_appendix():
    run_cmd("python3 fusion_appendix_injector.py", "Appending health to PDF")
```

Full chain:
```
Build PDF → Generate Health → Append Health → Deploy
```

### Dependencies

**Already Installed** in SonicBuilder (via packager_tool):
- ✅ `PyPDF2` - PDF reading and manipulation
- ✅ `fpdf2` - PDF generation
- ✅ `fpdf` - Legacy PDF support

**Manual Installation** (if needed):
```bash
pip install PyPDF2 fpdf2 fpdf
```

Or add to `requirements.txt`:
```
PyPDF2
fpdf2
fpdf
```

**Verification:**
```bash
python3 -c "import PyPDF2, fpdf; print('✅ Dependencies installed')"
```

---

## 🔧 Integration Patterns

### Pattern 1: Full Monitoring Stack

```bash
# Terminal 1: Visual monitoring
python3 sync_monitor_dashboard.py &  # Port 8094

# Terminal 2: Chart visualization
python3 fusion_live_charts.py &      # Port 8092

# Terminal 3: Alert notifications
python3 alert_hooks.py &             # Background

# Terminal 4: Continuous sync
python3 smart_pair_sync.py &         # Background
```

### Pattern 2: One-Time Setup

```bash
# Step 1: Configure secrets
python3 secrets_configurator.py

# Step 2: Repair any issues
python3 local_autopatch.py

# Step 3: Start services
python3 auto_orchestrator.py
```

### Pattern 3: Build Pipeline

```bash
# Full orchestration with appendix
python3 auto_orchestrator.py          # Build PDF
python3 generate_fusion_summary.py    # Generate health
python3 fusion_appendix_injector.py   # Append to PDF
```

### Pattern 4: Development Workflow

```bash
# Morning startup
python3 secrets_configurator.py       # Verify secrets
python3 smart_pair_sync.py &          # Start sync
python3 fusion_live_charts.py &       # Start charts

# Work on code...

# Evening shutdown
pkill -f "smart_pair_sync"
pkill -f "fusion_live_charts"
```

---

## 📊 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TIER 3 COMPONENTS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Fusion Live Charts (8092)                                  │
│      │                                                       │
│      ├── Reads: logs/uptime/*.json                          │
│      ├── Displays: Chart.js graphs                          │
│      └── Updates: Every 15 seconds                          │
│                                                              │
│  Secrets Configurator                                       │
│      │                                                       │
│      ├── Validates: GITHUB_TOKEN                            │
│      ├── Tests: ROLLBACK_WEBHOOK_URL                        │
│      └── Stores: Replit Secrets vault                       │
│                                                              │
│  Smart Pair Sync                                            │
│      │                                                       │
│      ├── Pull: GitHub → Replit (every 3 min)               │
│      ├── Push: Replit → GitHub (every 3 min)               │
│      └── Strategy: Rebase for clean history                 │
│                                                              │
│  Local Auto-Patch                                           │
│      │                                                       │
│      ├── Creates: health.json, badges, PDFs                 │
│      ├── Commits: Auto-repairs with [skip ci]               │
│      └── Triggers: Remote workflows via GH CLI              │
│                                                              │
│  Fusion Appendix Injector                                   │
│      │                                                       │
│      ├── Reads: base PDF + health.md                        │
│      ├── Merges: PyPDF2 + FPDF                              │
│      └── Outputs: Manual with health appendix               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Use Cases

### Use Case 1: Initial Setup

**Scenario:** Setting up SonicBuilder for the first time

**Solution:**
```bash
# 1. Configure all secrets
python3 secrets_configurator.py

# 2. Repair any missing files
python3 local_autopatch.py

# 3. Start continuous sync
python3 smart_pair_sync.py &

# 4. Start monitoring
python3 fusion_live_charts.py &
```

### Use Case 2: Visual Health Monitoring

**Scenario:** Want to see health trends over time

**Solution:**
```bash
# Start charts dashboard
python3 fusion_live_charts.py

# Open browser
http://localhost:8092/charts

# See beautiful Chart.js graphs showing health over time
```

### Use Case 3: Continuous GitHub Sync

**Scenario:** Working actively, want automatic sync

**Solution:**
```bash
# Start smart pair sync
python3 smart_pair_sync.py &

# Work normally
# Every 3 minutes: auto-pull + auto-push

# No manual git commands needed!
```

### Use Case 4: PDF with Health Report

**Scenario:** Want manual PDF to include system health

**Solution:**
```bash
# 1. Build base manual
python3 generate_manual.py

# 2. Generate health summary
python3 generate_fusion_summary.py

# 3. Append health to PDF
python3 fusion_appendix_injector.py

# Result: output/SonicBuilder_Manual_With_Health.pdf
```

### Use Case 5: Validate All Secrets

**Scenario:** Not sure if secrets are configured correctly

**Solution:**
```bash
# Run secrets configurator
python3 secrets_configurator.py

# It will:
# - Check each secret
# - Test GitHub token
# - Test Discord webhook
# - Guide you through fixes
```

---

## 🔍 Troubleshooting

### Charts Show Empty Data

**Problem:** Fusion Live Charts shows no data

**Solution:**
```bash
# Ensure Auto-Healer is running
ps aux | grep replit_auto_healer

# Check uptime logs exist
ls -la logs/uptime/

# Auto-Healer creates logs over time
# Charts will populate as logs accumulate
```

### Smart Pair Sync Fails

**Problem:** Git push/pull errors

**Solution:**
```bash
# Check GITHUB_TOKEN
echo $GITHUB_TOKEN

# Verify remote
git remote -v

# Test credentials
git pull origin main

# Reconfigure if needed
git remote set-url origin https://YOUR_TOKEN@github.com/USER/REPO.git
```

### Secrets Configurator Can't Add Secrets

**Problem:** `replit secrets add` command fails

**Solution:**
- Use Replit UI instead (Secrets tab in sidebar)
- Manually add secrets through web interface
- Configurator will detect them automatically

### Auto-Patch Creates Conflicts

**Problem:** Local autopatch conflicts with GitHub

**Solution:**
```bash
# Pull first
git pull origin main --rebase

# Then run autopatch
python3 local_autopatch.py

# Use [skip ci] to avoid loops
```

### PDF Appendix Missing Pages

**Problem:** Fusion appendix injector skips content

**Solution:**
```bash
# Check appendix file exists
cat docs/appendix_system_health.md

# Verify base PDF exists
ls -la output/SonicBuilder_Manual_Final.pdf

# Check dependencies
pip install PyPDF2 fpdf
```

---

## 📚 File Summary

```
SonicBuilder/
├── fusion_live_charts.py         # ← NEW (Tier 3) - Chart.js dashboard
├── secrets_configurator.py       # ← NEW (Tier 3) - Secrets validator
├── smart_pair_sync.py            # ← NEW (Tier 3) - Continuous sync
├── local_autopatch.py            # ← NEW (Tier 3) - Local QuickFix
├── fusion_appendix_injector.py   # ← NEW (Tier 3) - PDF appendix
│
├── logs/uptime/                   # Data source for charts
├── docs/status/health.json       # Created by autopatch
├── docs/appendix_system_health.md # Appendix content
│
└── TIER3_INTEGRATION_GUIDE.md    # ← This file
```

---

## 🎉 Benefits

**Fusion Live Charts:**
- ✅ Beautiful visualizations
- ✅ Real-time updates
- ✅ 500-point history
- ✅ Chart.js graphs
- ✅ JSON API

**Secrets Configurator:**
- ✅ Interactive setup
- ✅ Automated validation
- ✅ Safe storage
- ✅ Guided workflow
- ✅ Test webhooks

**Smart Pair Sync:**
- ✅ Automatic sync
- ✅ Bidirectional
- ✅ No manual git
- ✅ Clean history
- ✅ Background service

**Local Auto-Patch:**
- ✅ Prevent CI failures
- ✅ Auto-repair artifacts
- ✅ Mirror GitHub logic
- ✅ Trigger workflows
- ✅ Badge management

**Fusion Appendix Injector:**
- ✅ PDF merging
- ✅ Health reports
- ✅ Professional output
- ✅ Markdown support
- ✅ Auto-formatting

---

## 🚀 Quick Reference

**Start All Tier 3 Services:**
```bash
python3 fusion_live_charts.py &       # Charts on 8092
python3 smart_pair_sync.py &          # Continuous sync
python3 alert_hooks.py &              # Health alerts (Tier 2)
python3 sync_monitor_dashboard.py &   # Dashboard on 8094 (Tier 2)
```

**One-Time Setup:**
```bash
python3 secrets_configurator.py       # Configure secrets
python3 local_autopatch.py            # Repair artifacts
```

**Build with Health Appendix:**
```bash
python3 auto_orchestrator.py && python3 fusion_appendix_injector.py
```

**Access Dashboards:**
- Charts: http://localhost:8092/charts
- Sync Monitor: http://localhost:8094/
- Fusion Summary: http://localhost:8093/charts/summary/view

---

**SonicBuilder v2.0.9 — Tier 3 Integration Complete**

*Charts • Secrets • Sync • Auto-Patch • PDF Appendix*
