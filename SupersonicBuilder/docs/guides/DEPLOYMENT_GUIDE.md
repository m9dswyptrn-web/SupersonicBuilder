# SonicBuilder Deployment Guide

**Version:** v2.2.3+  
**Status:** ✅ Production Ready  
**Date:** October 29, 2025

---

## 🎯 Quick Start

### 1️⃣ **Setup (One Time)**

Add the following secrets in Replit (Secrets tab):

```bash
GH_TOKEN=<your_github_personal_access_token>
GITHUB_USER=m9dswyptrn-web
REPO_SLUG=SonicBuilder
```

**Optional webhooks:**
```bash
SLACK_WEBHOOK_URL=<your_slack_webhook>
# OR
DISCORD_WEBHOOK_URL=<your_discord_webhook>
```

**Initialize environment:**
```bash
make init
```

---

### 2️⃣ **Deploy**

#### Full Deployment (Recommended)
```bash
make ship
```
**This does:**
1. Commits and pushes all changes to GitHub
2. Creates/pushes version tag
3. Verifies GitHub Actions workflows
4. Sends webhook notification (if configured)

#### Docs-Only Deployment
```bash
make docs
```
Builds dark-themed docs, then deploys and verifies.

#### Manual Deployment
```bash
# Step by step
make deploy   # Push to GitHub
make verify   # Watch workflows
make notify   # Send notification
```

---

### 3️⃣ **Test Before Deploying**

```bash
make dryrun
```
Tests GitHub remote configuration without pushing.

---

## 📦 Deployment Scripts

### `deploy_all_to_github.py`
**Purpose:** Push all code and tag release

**Features:**
- Auto-commits if changes detected
- Reads VERSION file or generates timestamp tag
- Pushes to main branch
- Creates and pushes git tag

**Environment Variables:**
- `GITHUB_USER` - GitHub username (default: m9dswyptrn-web)
- `REPO_SLUG` - Repository name (default: SonicBuilder)

**Usage:**
```bash
python3 deploy_all_to_github.py
```

---

### `deploy_verify.py`
**Purpose:** Monitor GitHub Actions workflows

**Features:**
- Polls GitHub Actions API
- Shows real-time workflow status
- Waits for all workflows to complete
- Exits with error code if any fail

**Requirements:**
- `GH_TOKEN` environment variable (repo + workflow scopes)
- `requests` package

**Usage:**
```bash
python3 deploy_verify.py
```

**Output:**
```
🔍 Watching latest workflows… (Ctrl+C to stop)
------------------------------------------------------------------------------------
✅ Docs Release (Commit-Stamped)  SUCCESS    https://github.com/...
✅ Diagnostics (build)            SUCCESS    https://github.com/...
🕓 Release Support Bundle         IN_PROGRESS https://github.com/...
```

---

### `deploy_notify.py`
**Purpose:** Send deployment notifications

**Features:**
- Sends to Slack or Discord
- Gracefully skips if webhooks not configured
- Customizable message via `SB_NOTIFY_TEXT`

**Environment Variables:**
- `SLACK_WEBHOOK_URL` or `DISCORD_WEBHOOK_URL`
- `SB_NOTIFY_TEXT` (optional)

**Usage:**
```bash
export SB_NOTIFY_TEXT="🎉 Release v2.2.3 deployed!"
python3 deploy_notify.py
```

---

### `deploy_chain.sh`
**Purpose:** Run complete deployment pipeline

**Features:**
- Chains all three scripts
- Graceful fallbacks if tokens/webhooks missing
- Error handling for each step

**Usage:**
```bash
./deploy_chain.sh
```

---

## 🎯 Makefile Targets

| Target | Description |
|--------|-------------|
| `make ship` | **Full deployment pipeline** (deploy → verify → notify) |
| `make deploy` | Push code and tags to GitHub |
| `make verify` | Monitor GitHub Actions workflows |
| `make notify` | Send webhook notification |
| `make dryrun` | Test GitHub connection (no pushes) |
| `make docs` | Build docs with dark theme, then deploy |
| `make init` | Initialize deployment environment |
| `make clean-deploy` | Clean deployment artifacts |

---

## 🔐 GitHub Token Setup

### Create Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
4. Generate and copy token
5. Add to Replit Secrets as `GH_TOKEN`

### Verify Token
```bash
curl -H "Authorization: token $GH_TOKEN" \
  https://api.github.com/user
```

---

## 📊 Deployment Workflow

```
make ship
    ↓
┌─────────────────────┐
│  deploy_all_to_     │
│  github.py          │
│                     │
│  1. git add -A      │
│  2. git commit      │
│  3. git push        │
│  4. git tag vX.X.X  │
│  5. git push --tags │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  deploy_verify.py   │
│                     │
│  Polls GitHub       │
│  Actions every 45s  │
│  until all succeed  │
└─────────────────────┘
    ↓
┌─────────────────────┐
│  deploy_notify.py   │
│                     │
│  Sends webhook      │
│  notification       │
└─────────────────────┘
    ↓
✅ Complete!
```

---

## 🔔 Webhook Notifications

### Slack Setup
1. Create incoming webhook: https://api.slack.com/messaging/webhooks
2. Copy webhook URL
3. Add to Replit Secrets: `SLACK_WEBHOOK_URL`

### Discord Setup
1. Server Settings → Integrations → Webhooks
2. Create New Webhook
3. Copy webhook URL
4. Add to Replit Secrets: `DISCORD_WEBHOOK_URL`

### Custom Messages
```bash
export SB_NOTIFY_TEXT="🚀 SonicBuilder v2.2.3 deployed successfully!"
make notify
```

---

## 🧪 Testing

### Test Deployment Scripts
```bash
# Test GitHub connection
make dryrun

# Test deployment (without verify)
python3 deploy_all_to_github.py

# Test verification only
python3 deploy_verify.py

# Test notification only
python3 deploy_notify.py
```

### Test Complete Pipeline
```bash
# Full pipeline with all checks
make ship
```

---

## 🚨 Troubleshooting

### "Missing GH_TOKEN"
**Solution:** Add `GH_TOKEN` to Replit Secrets with repo + workflow scopes

### "Remote not configured"
**Solution:** 
```bash
git remote add origin https://github.com/m9dswyptrn-web/SonicBuilder.git
```

### "Verification failed"
**Check:**
1. GitHub Actions workflows enabled
2. Token has correct scopes
3. Workflows configured correctly

### "Push rejected"
**Solutions:**
```bash
# If main branch protected, temporarily disable or:
git push --force-with-lease origin main

# Or pull first:
git pull --rebase origin main
git push origin main
```

---

## 📋 Pre-Deployment Checklist

- [ ] All code changes committed locally
- [ ] Tests passing (if any)
- [ ] Documentation updated
- [ ] VERSION file updated (if applicable)
- [ ] GH_TOKEN configured in Replit Secrets
- [ ] Git remote configured
- [ ] Webhooks configured (optional)
- [ ] Run `make dryrun` to verify setup

---

## 🎯 Common Workflows

### Regular Development Deploy
```bash
# Make changes
git add .
git commit -m "feat: new feature"

# Deploy
make ship
```

### Documentation Update
```bash
# Update docs
make docs
```

### Emergency Hotfix
```bash
# Fix issue
git add .
git commit -m "fix: critical bug"

# Quick deploy (skip verification)
make deploy
```

### Tag-Only Update
```bash
# Update VERSION file
echo "v2.2.4" > VERSION

# Deploy
make ship
```

---

## 📊 Expected Timeline

| Step | Duration |
|------|----------|
| Deploy (push) | ~10-30 seconds |
| Workflows start | ~30 seconds |
| Docs build | ~2-5 minutes |
| Diagnostics | ~30 seconds |
| Support bundle | ~30 seconds |
| **Total** | **~4-7 minutes** |

---

## ✅ Success Indicators

After `make ship`:

1. ✅ Console shows "✅ SonicBuilder full deploy complete!"
2. ✅ GitHub Actions show green checkmarks
3. ✅ Release created on GitHub Releases page
4. ✅ Artifacts available for download
5. ✅ Webhook notification received (if configured)

---

## 📚 Related Documentation

- `docs/CI_CD_WORKFLOW_GUIDE.md` - Complete CI/CD documentation
- `docs/ENHANCED_DIAGNOSTICS_GUIDE.md` - Diagnostics system
- `FINAL_INTEGRATION_SUMMARY_v2.2.3.md` - Integration summary

---

**Your complete deployment automation system is ready! Use `make ship` to deploy everything to GitHub with automatic verification and notifications.** 🚀
