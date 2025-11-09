# 🔄 SonicBuilder Rollback & Notification System

Enterprise-grade rollback protection and notification system for system health monitoring.

## 📋 Overview

The rollback system provides automatic corruption detection, rollback to last known good state, and real-time notifications via Discord/Slack webhooks.

## 🏗️ Architecture

```
GitHub Actions (Every 6 hours)
    │
    ├─ Generate system.json
    │   └─ make system_json
    │
    ├─ Push to GitHub Pages
    │   └─ scripts/push_system_json.py
    │
    ├─ On Failure: Rollback
    │   ├─ Detect corruption
    │   ├─ Reset to HEAD~1
    │   └─ Force push to gh-pages
    │
    ├─ Send Notifications
    │   ├─ Success → 🟢 Discord
    │   └─ Rollback → 🔴 Discord
    │
    └─ Archive Artifacts
        ├─ Success → 30 days
        └─ Failure → 14 days
```

## 📦 Components

### 1. System Health Push (`scripts/push_system_json.py`)

Commits and pushes system.json to GitHub Pages.

**Features:**
- Auto-configured git identity
- Timestamp-based commit messages
- Smart change detection
- Environment variable support

**Usage:**
```bash
python3 scripts/push_system_json.py
```

**Environment:**
```bash
export PAGES_BRANCH=gh-pages
export REMOTE_NAME=origin
```

### 2. Rollback Script (`scripts/rollback_system_json.py`)

Automatically detects corruption and rolls back to last known good state.

**Features:**
- Corruption detection
- Automatic rollback to HEAD~1
- Force-push to restore state
- Detailed logging

**Usage:**
```bash
python3 scripts/rollback_system_json.py
```

**Triggers:**
- Commit failures
- System.json corruption
- GitHub Actions workflow failures

### 3. Notification Script (`scripts/notify_rollback.py`)

Sends rich Discord/Slack notifications for deployment events.

**Features:**
- Discord webhook integration
- Slack webhook support
- Color-coded embeds
- Timestamp tracking

**Usage:**
```bash
export ROLLBACK_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export ROLLBACK_STATUS="success"  # or "rollback"
export ROLLBACK_EVENT="system_json_push"
python3 scripts/notify_rollback.py
```

**Message Types:**
- 🟢 **Success** - Green embed, deployment successful
- 🔴 **Rollback** - Red embed, corruption detected
- 🟡 **Warning** - Yellow embed, unknown event

### 4. GitHub Actions Workflow (`.github/workflows/system-health-ci.yml`)

Complete CI/CD pipeline with rollback protection.

**Schedule:** Every 6 hours (`cron: '0 */6 * * *'`)

**Manual Trigger:** `workflow_dispatch`

**Steps:**
1. Generate system.json
2. Push to GitHub Pages
3. Rollback on failure
4. Send notifications
5. Verify integrity (SHA256)
6. Upload artifacts

## 🔐 Setup

### 1. Add Discord Webhook Secret

**Get Discord Webhook URL:**
1. Go to Discord Server Settings → Integrations
2. Click "Webhooks" → "New Webhook"
3. Name it "SonicBuilder Monitor"
4. Copy the webhook URL

**Add to GitHub:**
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `ROLLBACK_WEBHOOK_URL`
4. Value: Your Discord webhook URL
5. Click "Add secret"

### 2. (Optional) Add Slack Webhook

Same process but use `SLACK_WEBHOOK_URL` as the secret name.

### 3. Enable Workflow

1. Go to Actions tab
2. Find "System Health CI/CD Pipeline"
3. Click "Enable workflow" (if needed)

### 4. Test Manual Trigger

1. Actions → System Health CI/CD Pipeline
2. Run workflow → Run workflow
3. Check Discord/Slack for notification

## 📊 Workflow Execution

### Normal Flow

```
1. Generate system.json
   ↓
2. Push to gh-pages (success)
   ↓
3. Verify integrity (SHA256)
   ↓
4. Send success notification 🟢
   ↓
5. Upload artifacts (30-day retention)
```

### Failure Flow

```
1. Generate system.json
   ↓
2. Push to gh-pages (FAILS) ❌
   ↓
3. Detect failure
   ↓
4. Run rollback script
   ├─ Get previous commit (HEAD~1)
   ├─ Reset to previous commit
   └─ Force push to gh-pages
   ↓
5. Send rollback notification 🔴
   ↓
6. Upload failure logs (14-day retention)
```

## 📦 Artifact Archival

### Success Artifacts (30-day retention)

```
SonicBuilder-{run_number}-{commit_sha}
├── docs/**/*.pdf
├── docs/status/system.json
├── docs/status/uptime_log.json
├── docs/status/heartbeat.json
└── badges/*.json
```

### Failure Artifacts (14-day retention)

```
SonicBuilder-Failure-{run_number}-{commit_sha}
├── docs/status/*.json
├── .github/workflows/**/*.yml
└── scripts/**/*.py
```

**Access:**
GitHub Actions → Select workflow run → Artifacts section

## 📡 Notification Examples

### Success Notification

```
╔═══════════════════════════════════════════════╗
║ 🟢 SonicBuilder Deployment Update            ║
╠═══════════════════════════════════════════════╣
║                                               ║
║ ✅ Deployment Successful                     ║
║                                               ║
║ System.json successfully deployed to         ║
║ GitHub Pages                                  ║
║                                               ║
║ Event: system_json_push                       ║
║ Status: All systems operational               ║
║                                               ║
║ UTC 2025-10-31T11:30:00.000000               ║
╚═══════════════════════════════════════════════╝
```

### Rollback Notification

```
╔═══════════════════════════════════════════════╗
║ 🔴 SonicBuilder Deployment Update            ║
╠═══════════════════════════════════════════════╣
║                                               ║
║ ⚠️ Rollback Executed                         ║
║                                               ║
║ Reason: Failed commit or system.json         ║
║         corruption                            ║
║                                               ║
║ Event: system_json_push                       ║
║ Action: Reverted to last known good state    ║
║                                               ║
║ UTC 2025-10-31T11:30:00.000000               ║
╚═══════════════════════════════════════════════╝
```

## 🧪 Local Testing

### Test System JSON Generation

```bash
make system_json
```

### Test Push Script

```bash
python3 scripts/push_system_json.py
```

### Test Rollback Script

```bash
python3 scripts/rollback_system_json.py
```

### Test Notifications

```bash
export ROLLBACK_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export ROLLBACK_STATUS="success"
export ROLLBACK_EVENT="test"
python3 scripts/notify_rollback.py
```

## 🎨 Badges

Add these badges to your README.md:

```markdown
<!-- System Sync Status -->
[![System Sync](https://img.shields.io/github/actions/workflow/status/m9dswyptrn-web/SonicBuilder/system-health-ci.yml?label=System%20Sync&logo=github&color=00ccff)](https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/system-health-ci.yml)

<!-- Artifacts -->
[![Artifacts](https://github.com/m9dswyptrn-web/SonicBuilder/actions/workflows/system-health-ci.yml/badge.svg?event=schedule)](https://github.com/m9dswyptrn-web/SonicBuilder/actions)

<!-- Artifact Health -->
[![Artifact Health](https://img.shields.io/badge/Artifacts-Latest%20Uploaded-green)](https://github.com/m9dswyptrn-web/SonicBuilder/actions)
```

## 🔍 Troubleshooting

### Workflow Not Running

1. Check if workflow is enabled in Actions tab
2. Verify cron schedule is correct
3. Check repository permissions

### Notifications Not Sending

1. Verify webhook URL is correct
2. Check secret is named `ROLLBACK_WEBHOOK_URL`
3. Test webhook URL manually with curl

### Rollback Failing

1. Check git credentials in workflow
2. Verify gh-pages branch exists
3. Check force-push permissions

### Artifacts Not Uploading

1. Verify paths in workflow YAML
2. Check retention days setting
3. Ensure files exist before upload step

## 📚 Related Documentation

- `HARMONY_SYNC_GUIDE.md` - Harmony feed system
- `INFINITY_QUICK_REFERENCE.md` - Quick command reference
- Auto-Healer system documentation

## 🎯 Best Practices

1. **Monitor Discord notifications** - Set up a dedicated channel
2. **Review artifacts regularly** - Check for patterns in failures
3. **Test locally first** - Always test scripts before pushing
4. **Keep secrets secure** - Never commit webhook URLs
5. **Archive important artifacts** - Download before 30-day expiry

---

**SonicBuilder v2.0.9 — Enterprise-Grade Rollback Protection**
