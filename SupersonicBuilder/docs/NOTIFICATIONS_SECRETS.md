# GitHub Secrets & Variables Setup Guide

## Overview

This guide shows you how to configure GitHub Secrets and Variables for notifications, webhooks, and external integrations in your CI/CD workflows.

---

## 🔐 Secrets vs Variables

### Secrets (Encrypted)
- **Use for:** API keys, tokens, webhook URLs, passwords
- **Visibility:** Never shown in logs
- **Access:** `${{ secrets.SECRET_NAME }}`
- **Security:** Encrypted at rest

### Variables (Plain Text)
- **Use for:** Public configuration, URLs, usernames
- **Visibility:** Shown in logs
- **Access:** `${{ vars.VARIABLE_NAME }}`
- **Security:** Not encrypted

---

## 📋 Required Secrets

### SB_NOTIFY_WEBHOOK
**Purpose:** Webhook URL for build notifications (Slack, Discord, etc.)  
**Type:** Secret (encrypted)  
**Used by:** All CI workflows for notifications

**How to add:**
1. Go to repository Settings
2. Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `SB_NOTIFY_WEBHOOK`
5. Value: Your webhook URL
   - Slack: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`
   - Discord: `https://discord.com/api/webhooks/000000000000000000/XXXXXXXXXXXXXXXXXXXX`
   - Generic: Any HTTPS webhook endpoint

**Example workflow usage:**
```yaml
- name: Send notification
  if: always()
  run: |
    python scripts/notify.py \
      --webhook "${{ secrets.SB_NOTIFY_WEBHOOK }}" \
      --status "${{ job.status }}" \
      --message "Build completed"
```

---

## 📊 Optional Variables

### SB_NOTIFY_ENABLED
**Purpose:** Enable/disable notifications globally  
**Type:** Variable (plain text)  
**Default:** `true`

**Values:**
- `true` - Send notifications
- `false` - Skip notifications

**How to add:**
1. Go to repository Settings
2. Secrets and variables → Actions → Variables tab
3. Click "New repository variable"
4. Name: `SB_NOTIFY_ENABLED`
5. Value: `true` or `false`

**Example workflow usage:**
```yaml
- name: Send notification
  if: vars.SB_NOTIFY_ENABLED == 'true'
  run: python scripts/notify.py ...
```

### SB_NOTIFY_CHANNEL
**Purpose:** Override default notification channel  
**Type:** Variable (plain text)

**How to add:**
1. Settings → Secrets and variables → Actions → Variables
2. Name: `SB_NOTIFY_CHANNEL`
3. Value: Channel name or ID (e.g., `#builds`, `releases`)

---

## 🔧 Setting Up Webhooks

### Slack Webhook
1. Go to https://api.slack.com/apps
2. Create new app or select existing
3. Enable "Incoming Webhooks"
4. Click "Add New Webhook to Workspace"
5. Select channel
6. Copy webhook URL
7. Add as `SB_NOTIFY_WEBHOOK` secret

**Test:**
```bash
curl -X POST "$SB_NOTIFY_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from SonicBuilder"}'
```

### Discord Webhook
1. Go to Server Settings → Integrations
2. Click "Create Webhook"
3. Choose channel
4. Copy webhook URL
5. Add as `SB_NOTIFY_WEBHOOK` secret

**Test:**
```bash
curl -X POST "$SB_NOTIFY_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d '{"content":"Test from SonicBuilder"}'
```

### Generic Webhook
Any HTTPS endpoint that accepts POST requests with JSON body.

---

## 🧪 Local Testing

### Using .env.local
```bash
# Copy example file
cp .env.local.example .env.local

# Edit .env.local
SB_NOTIFY_WEBHOOK=https://your-webhook-url-here
SB_NOTIFY_ENABLED=true
SB_NOTIFY_CHANNEL=#builds

# Load and test
source .env.local
python scripts/notify.py --webhook "$SB_NOTIFY_WEBHOOK" --message "Local test"
```

**Important:** Add `.env.local` to `.gitignore` to prevent committing secrets!

---

## 📝 Complete Setup Checklist

### Secrets (Required)
- [ ] `SB_NOTIFY_WEBHOOK` - Your webhook URL

### Variables (Optional)
- [ ] `SB_NOTIFY_ENABLED` - Enable/disable notifications
- [ ] `SB_NOTIFY_CHANNEL` - Override channel

### Files
- [ ] `.env.local` created (from .env.local.example)
- [ ] `.env.local` added to `.gitignore`
- [ ] `scripts/notify.py` executable

### Testing
- [ ] Test webhook manually with curl
- [ ] Test with `scripts/notify.py` locally
- [ ] Trigger workflow and verify notification

---

## 🎯 Workflow Examples

### Simple Notification
```yaml
- name: Notify success
  if: success()
  run: |
    python scripts/notify.py \
      --webhook "${{ secrets.SB_NOTIFY_WEBHOOK }}" \
      --status "success" \
      --message "Build v${{ steps.version.outputs.VERSION }} completed"
```

### Conditional Notification
```yaml
- name: Notify on failure
  if: failure() && vars.SB_NOTIFY_ENABLED == 'true'
  run: |
    python scripts/notify.py \
      --webhook "${{ secrets.SB_NOTIFY_WEBHOOK }}" \
      --status "failure" \
      --message "Build failed: ${{ github.workflow }}"
```

### Rich Notification
```yaml
- name: Notify with details
  if: always()
  run: |
    python scripts/notify.py \
      --webhook "${{ secrets.SB_NOTIFY_WEBHOOK }}" \
      --status "${{ job.status }}" \
      --title "Release ${{ steps.version.outputs.VERSION }}" \
      --message "Files: AppendixC.zip, CoA #0007" \
      --url "${{ github.event.release.html_url }}"
```

---

## 🔒 Security Best Practices

### DO ✅
- Store webhook URLs as secrets
- Use HTTPS endpoints only
- Rotate webhooks periodically
- Use `.env.local` for local testing
- Add `.env.local` to `.gitignore`

### DON'T ❌
- Commit webhook URLs to repository
- Share secrets in public channels
- Use HTTP (non-encrypted) endpoints
- Log secret values in workflows
- Use secrets as variables (they're different!)

---

## 🐛 Troubleshooting

### Notification Not Sent
**Check:**
1. Secret exists: Settings → Secrets and variables → Actions
2. Secret name matches: `SB_NOTIFY_WEBHOOK` (exact)
3. Webhook URL is valid and active
4. Workflow has `if: always()` or `if: success()`
5. Check workflow logs for errors

### "Secret not found" Error
**Problem:** Workflow can't access secret  
**Solution:**
1. Verify secret name (case-sensitive)
2. Check repository Settings → Secrets
3. Ensure secret is at repository level (not environment)

### Webhook Receives Nothing
**Problem:** Notification sent but webhook not receiving  
**Solution:**
1. Test webhook manually with curl
2. Check webhook provider's status page
3. Verify webhook hasn't expired (Discord webhooks can expire)
4. Check channel permissions

### Local Testing Fails
**Problem:** `scripts/notify.py` doesn't work locally  
**Solution:**
1. Check `.env.local` exists and has webhook URL
2. Run `source .env.local` to load environment
3. Verify `SB_NOTIFY_WEBHOOK` is set: `echo $SB_NOTIFY_WEBHOOK`
4. Check Python dependencies: `pip install requests`

---

## 📚 Advanced Usage

### Multiple Webhooks
Store multiple webhooks for different purposes:
- `SB_NOTIFY_WEBHOOK_BUILDS` - Build notifications
- `SB_NOTIFY_WEBHOOK_RELEASES` - Release notifications
- `SB_NOTIFY_WEBHOOK_ERRORS` - Error alerts

### Environment-Specific Secrets
Use environments for different deployment stages:
- Production environment: Production webhook
- Staging environment: Staging webhook
- Development environment: Development webhook

### Conditional Notifications
```yaml
- name: Notify based on branch
  if: github.ref == 'refs/heads/main'
  run: python scripts/notify.py --webhook "${{ secrets.SB_NOTIFY_WEBHOOK }}" --message "Main branch updated"
```

---

## 📖 Reference

### GitHub Secrets Documentation
https://docs.github.com/en/actions/security-guides/encrypted-secrets

### GitHub Variables Documentation
https://docs.github.com/en/actions/learn-github-actions/variables

### Webhook Providers
- **Slack:** https://api.slack.com/messaging/webhooks
- **Discord:** https://support.discord.com/hc/en-us/articles/228383668
- **Microsoft Teams:** https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook

---

## ✅ Quick Setup (30 seconds)

```bash
# 1. Get your webhook URL from Slack/Discord

# 2. Add to GitHub
# Settings → Secrets and variables → Actions → New repository secret
# Name: SB_NOTIFY_WEBHOOK
# Value: [paste webhook URL]

# 3. Test locally
cp .env.local.example .env.local
echo "SB_NOTIFY_WEBHOOK=https://your-webhook-url" >> .env.local
source .env.local
python scripts/notify.py --webhook "$SB_NOTIFY_WEBHOOK" --message "Setup complete! 🎉"

# 4. Done! Your workflows will now send notifications
```

---

**Your CI/CD pipeline is now ready for professional notifications!** 🚀
