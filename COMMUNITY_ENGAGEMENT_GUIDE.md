# 📢 Community Engagement & Notifications Guide

Automated release announcements for your community.

---

## 🎯 What This Does

Your release system now includes **automated community engagement**:

1. ✅ **GitHub Discussions** - Auto-create release announcements
2. ✅ **Slack Notifications** - Post to your team channel
3. ✅ **Discord Webhooks** - Notify your community server
4. ✅ **Release Summaries** - Beautiful formatted announcements

---

## 📢 GitHub Discussions Integration

### Features

- ✅ Automatically creates Discussion for each release
- ✅ Posts to "Announcements" category (if available)
- ✅ Includes CHANGELOG + RELEASE_SUMMARY
- ✅ Links back to GitHub Release

### Setup

**1. Enable Discussions on your repository**

```bash
# Go to repository Settings
open https://github.com/ChristopherElgin/SonicBuilderSupersonic/settings

# Scroll to "Features"
# Check "Discussions"
# Click "Set up discussions"
```

**2. Create "Announcements" category** (recommended)

- Go to Discussions tab
- Click "Categories"
- Create category named "Announcements"
- Set format to "Announcement" (not Q&A)

**3. The script runs automatically**

The `create_release_discussion.js` script triggers on every release via your workflow.

### Manual Testing

```bash
# Install GitHub CLI
gh auth login

# Set environment
export RELEASE_TAG="v1.0.0"

# Run the script (requires Node.js)
node -e "
const script = require('./tools/create_release_discussion.js');
const { Octokit } = require('@octokit/rest');
const github = new Octokit({ auth: process.env.GITHUB_TOKEN });
const core = { info: console.log };
const context = { repo: { owner: 'ChristopherElgin', repo: 'SonicBuilderSupersonic' }};
script({ github, core, context });
"
```

---

## 💬 Slack Webhook Notifications

### Setup Slack Webhook

**1. Create Incoming Webhook**

1. Go to: https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "Supersonic Release Bot"
4. Select your workspace
5. Click "Incoming Webhooks"
6. Activate Incoming Webhooks: ON
7. "Add New Webhook to Workspace"
8. Choose channel (e.g., `#releases`)
9. Copy the webhook URL

**2. Add to GitHub Secrets**

```bash
# Go to repository secrets
open https://github.com/ChristopherElgin/SonicBuilderSupersonic/settings/secrets/actions

# Add new secret:
# Name: SLACK_WEBHOOK_URL
# Value: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

**3. Test locally**

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

python3 tools/notify_webhooks.py \
  --status success \
  --title "Test Release v1.0.0" \
  --text "Testing Slack notifications from Supersonic v4" \
  --url "https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases/tag/v1.0.0"
```

### Slack Message Format

```
📦 Release v1.0.0 published
━━━━━━━━━━━━━━━━━━━━━━
Changelog updated, assets attached.
Repo: https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases/tag/v1.0.0

Status: success
```

---

## 🎮 Discord Integration

### Option 1: Discord Webhooks (Simple)

**Setup Discord Webhook**

**1. Create Webhook in Discord**

1. Go to your Discord server
2. Right-click channel (e.g., `#announcements`)
3. Edit Channel → Integrations → Webhooks
4. "New Webhook"
5. Name: "Supersonic Releases"
6. Avatar: Upload logo (optional)
7. Copy Webhook URL

**2. Add to GitHub Secrets**

```bash
# Go to repository secrets
open https://github.com/ChristopherElgin/SonicBuilderSupersonic/settings/secrets/actions

# Add new secret:
# Name: DISCORD_WEBHOOK_URL
# Value: https://discord.com/api/webhooks/123456789/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**3. Test locally**

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK/ID"

python3 tools/notify_webhooks.py \
  --status success \
  --title "Test Release v1.0.0" \
  --text "Testing Discord notifications from Supersonic v4" \
  --url "https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases/tag/v1.0.0"
```

### Discord Message Format

Rich embed with:
- ✅ Title (clickable link)
- ✅ Description (markdown text)
- ✅ Color-coded status (green/red/yellow)
- ✅ Release URL

---

### Option 2: Discord Forum Threads (Advanced)

**Create discussion threads in Discord forum channels**

**1. Create Discord Bot**

1. Go to: https://discord.com/developers/applications
2. Click "New Application"
3. Name: "Supersonic Release Bot"
4. Go to "Bot" section
5. Click "Reset Token" → Copy the token
6. Enable these intents:
   - ✅ Message Content Intent
   - ✅ Guild Messages

**2. Add Bot to Your Server**

1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - ✅ `bot`
3. Select permissions:
   - ✅ Send Messages
   - ✅ Create Public Threads
   - ✅ Send Messages in Threads
4. Copy generated URL and open in browser
5. Add bot to your server

**3. Get Forum Channel ID**

1. Enable Developer Mode in Discord (User Settings → Advanced)
2. Right-click your forum channel
3. "Copy Channel ID"

**4. Add to GitHub Secrets**

```bash
# Add these secrets to GitHub:
# DISCORD_BOT_TOKEN = Your bot token from step 1
# DISCORD_FORUM_CHANNEL_ID = Channel ID from step 3
```

**5. Test Locally**

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
export DISCORD_FORUM_CHANNEL_ID="your-channel-id"

python3 tools/mirror_discussion_to_discord.py \
  --title "Release v1.0.0" \
  --content "Release discussion for Supersonic v4 Ultimate
  
Features:
- Health scan system
- Cryptographic signing
- Automated workflows

Download: https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases/tag/v1.0.0"
```

**Forum Thread Features**:
- ✅ Auto-creates thread in forum channel
- ✅ 7-day auto-archive
- ✅ Persistent discussion space
- ✅ Better than ephemeral webhook messages

---

## 🔧 Webhook Notification Tool

### Usage

```bash
python3 tools/notify_webhooks.py \
  --status <success|failure|warning> \
  --title "Short title" \
  --text "Longer description with details" \
  --url "https://link.to/resource"
```

### Status Colors

| Status | Slack | Discord | Meaning |
|--------|-------|---------|---------|
| `success` | 🟢 Green | `#2eb886` | Release successful |
| `failure` | 🔴 Red | `#e01e5a` | Release failed |
| `warning` | 🟡 Yellow | `#ecb22e` | Warnings present |

### Environment Variables

```bash
# Set in GitHub Secrets (for Actions)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Or export locally for testing
export SLACK_WEBHOOK_URL="..."
export DISCORD_WEBHOOK_URL="..."
```

---

## 🔄 Workflow Integration

Your `.github/workflows/release.yml` should include:

```yaml
env:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}

jobs:
  release:
    steps:
      # ... build and release steps ...

      # Create GitHub Discussion
      - name: Create release discussion
        if: always()
        uses: actions/github-script@v7
        env:
          RELEASE_TAG: ${{ steps.ver.outputs.version }}
        with:
          script: |
            const skr = require('fs').readFileSync('tools/create_release_discussion.js', 'utf8');
            const fn = new Function('module','exports','require',skr);
            const mod = {exports:{}};
            fn(mod, mod.exports, require);
            await mod.exports({github, core, context});

      # Send webhook notifications
      - name: Notify webhooks
        if: always()
        run: |
          python3 tools/notify_webhooks.py \
            --status "success" \
            --title "Release ${{ steps.ver.outputs.version }} published" \
            --text "Changelog updated, assets attached.\nRepo: https://github.com/${{ github.repository }}/releases/tag/${{ steps.ver.outputs.version }}" \
            --url "https://github.com/${{ github.repository }}/releases/tag/${{ steps.ver.outputs.version }}"
```

---

## 📊 Notification Matrix

| Event | GitHub Discussion | Slack | Discord |
|-------|------------------|-------|---------|
| Release Published | ✅ Auto-create | ✅ Send | ✅ Send |
| Release Failed | ❌ Skip | ✅ Send (red) | ✅ Send (red) |
| Build Warning | ❌ Skip | ✅ Send (yellow) | ✅ Send (yellow) |

---

## 🎨 Customization

### Custom Slack Message

Edit `tools/notify_webhooks.py`:

```python
payload = {
    "attachments": [
        {
            "color": slack_color(status),
            "title": title,
            "title_link": url or None,
            "text": text or "",
            "footer": f"Status: {status}",
            # Add custom fields:
            "fields": [
                {"title": "Version", "value": "v1.0.0", "short": True},
                {"title": "Platform", "value": "Supersonic v4", "short": True}
            ]
        }
    ]
}
```

### Custom Discord Embed

```python
payload = {
    "embeds": [
        {
            "title": title,
            "url": url or None,
            "description": text[:4000],
            "color": color,
            # Add thumbnail:
            "thumbnail": {"url": "https://your-logo.png"},
            # Add footer:
            "footer": {"text": "Supersonic v4 Ultimate"}
        }
    ]
}
```

---

## 🧪 Testing

### Test All Notifications

```bash
# Set all webhooks
export SLACK_WEBHOOK_URL="your-slack-webhook"
export DISCORD_WEBHOOK_URL="your-discord-webhook"

# Test success
python3 tools/notify_webhooks.py \
  --status success \
  --title "✅ Release v1.0.0 Published" \
  --text "All tests passed. Assets attached to release." \
  --url "https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases/tag/v1.0.0"

# Test failure
python3 tools/notify_webhooks.py \
  --status failure \
  --title "❌ Release v1.0.1 Failed" \
  --text "Build failed: compilation error in module X" \
  --url "https://github.com/ChristopherElgin/SonicBuilderSupersonic/actions"

# Test warning
python3 tools/notify_webhooks.py \
  --status warning \
  --title "⚠️ Release v1.0.2 - Warnings" \
  --text "Released with 3 warnings. Review recommended." \
  --url "https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases"
```

---

## 🚨 Troubleshooting

### "No webhooks configured"

```bash
# Check environment variables are set
echo $SLACK_WEBHOOK_URL
echo $DISCORD_WEBHOOK_URL

# Ensure they're added to GitHub Secrets
```

### Slack: "Invalid payload"

```bash
# Test webhook directly
curl -X POST "$SLACK_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test message"}'
```

### Discord: "Unknown Webhook"

```bash
# Verify webhook URL format
# Should be: https://discord.com/api/webhooks/ID/TOKEN

# Test directly
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message"}'
```

### Discussion: "Discussions not enabled"

```bash
# Enable in repository settings
open https://github.com/ChristopherElgin/SonicBuilderSupersonic/settings

# Check "Discussions" under Features
```

---

## 📈 Best Practices

### Security

- ✅ **Never commit webhooks** to git
- ✅ **Use GitHub Secrets** for webhook URLs
- ✅ **Rotate webhooks** if exposed
- ✅ **Use HTTPS only**

### Content

- ✅ **Be concise** in titles (< 50 chars)
- ✅ **Include links** to release/runs
- ✅ **Use emoji** for visual clarity
- ✅ **Provide context** in text field

### Timing

- ✅ **Notify on success** (celebrate releases!)
- ✅ **Alert on failures** (quick response)
- ✅ **Warn on issues** (transparency)

---

## 🎯 Example Workflow

```yaml
name: Release with Notifications

on:
  push:
    tags: ['v*']

env:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # ... build steps ...
      
      - name: Create Discussion
        uses: actions/github-script@v7
        env:
          RELEASE_TAG: ${{ github.ref_name }}
        with:
          script: |
            const script = require('./tools/create_release_discussion.js');
            await script({github, core, context});
      
      - name: Notify Success
        if: success()
        run: |
          python3 tools/notify_webhooks.py \
            --status success \
            --title "🚀 Release ${{ github.ref_name }} Published" \
            --text "View release: https://github.com/${{ github.repository }}/releases/tag/${{ github.ref_name }}"
      
      - name: Notify Failure
        if: failure()
        run: |
          python3 tools/notify_webhooks.py \
            --status failure \
            --title "❌ Release ${{ github.ref_name }} Failed" \
            --text "Check workflow: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

---

## 📊 Release Size Tracking

**Track artifact size changes between releases**

### Setup

The `release_size_diff.py` tool automatically:
- ✅ Compares current artifacts to previous release
- ✅ Shows size differences per file
- ✅ Generates markdown report
- ✅ Appends to RELEASE_SUMMARY.md

### Usage

```bash
# In GitHub Actions (automatic)
python3 tools/release_size_diff.py \
  --globs "dist/**
build/**
**/*.zip
!**/node_modules/**" \
  --tag "v1.0.1" \
  --out RELEASE_SIZE_DIFF.md
```

### Example Output

```markdown
## Artifact Size Diff — v1.0.1

Prev: **v1.0.0** total **45.32 MB** → Now: **47.18 MB**  (**+1.86 MB**)

| File | Current | Previous | Δ |
|------|---------:|---------:|----:|
| `sonic_manual.pdf` | 23.45 MB | 22.10 MB | +1.35 MB |
| `build.zip` | 15.23 MB | 14.98 MB | +250.00 KB |
| `assets.tar.gz` | 8.50 MB | 8.24 MB | +260.00 KB |
```

### Integration

The diff is automatically:
1. ✅ Generated during release workflow
2. ✅ Appended to RELEASE_SUMMARY.md
3. ✅ Included in webhook notifications
4. ✅ Posted to GitHub Discussions

---

## ✅ Checklist

After setup:

- [ ] GitHub Discussions enabled
- [ ] "Announcements" category created
- [ ] Slack webhook created & added to secrets
- [ ] Discord webhook created & added to secrets
- [ ] Discord bot created (optional, for forum threads)
- [ ] Discord forum channel ID copied (optional)
- [ ] Test notifications sent successfully
- [ ] Test size diff generated
- [ ] Workflow updated with notification steps
- [ ] First release creates Discussion ✅
- [ ] Slack receives notification ✅
- [ ] Discord receives notification ✅
- [ ] Discord forum thread created ✅ (if using bot)
- [ ] Size diff included in notifications ✅

---

## 📚 Resources

- **GitHub Discussions API**: https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions
- **Slack Webhooks**: https://api.slack.com/messaging/webhooks
- **Discord Webhooks**: https://discord.com/developers/docs/resources/webhook

---

## ✨ You're Connected!

Your releases now automatically notify:
- ✅ GitHub community (Discussions)
- ✅ Team (Slack)
- ✅ Community (Discord)

**Build in public, engage your community!** 📢
