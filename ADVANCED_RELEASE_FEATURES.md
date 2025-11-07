# 🚀 Advanced Release Features

Additional enterprise features for your release automation.

---

## 📊 Release Size Tracking

**Automatically track artifact size changes between releases.**

### What It Does

The `release_size_diff.py` tool:
- ✅ Compares current build artifacts to previous release
- ✅ Shows per-file size changes
- ✅ Generates markdown report
- ✅ Helps track bloat and optimization

### Setup

**Already installed!** No configuration needed.

### Usage in Workflows

```yaml
- name: Artifact size diff
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python3 tools/release_size_diff.py \
      --globs "${{ env.ARTIFACT_GLOBS }}" \
      --tag "$VERSION" \
      --out RELEASE_SIZE_DIFF.md
    
    # Append to release summary
    cat RELEASE_SIZE_DIFF.md >> RELEASE_SUMMARY.md
```

### Example Report

```markdown
## Artifact Size Diff — v1.0.1

Prev: **v1.0.0** total **45.32 MB** → Now: **47.18 MB**  (**+1.86 MB**)

| File | Current | Previous | Δ |
|------|---------:|---------:|----:|
| `sonic_manual.pdf` | 23.45 MB | 22.10 MB | +1.35 MB |
| `build.zip` | 15.23 MB | 14.98 MB | +250.00 KB |
| `assets.tar.gz` | 8.50 MB | 8.24 MB | +260.00 KB |
```

### Benefits

- ✅ **Track bloat** - Spot unexpected size increases
- ✅ **Verify optimization** - Confirm size reductions
- ✅ **Transparency** - Users see what changed
- ✅ **Budget compliance** - Stay within limits

---

## 🎮 Discord Forum Threads

**Create persistent discussion threads in Discord forum channels.**

### Why Forum Threads?

**Webhooks**: Ephemeral messages, lost in chat history  
**Forum Threads**: Persistent discussions, organized by release

### Setup Discord Bot

**1. Create Application**

```
1. Visit: https://discord.com/developers/applications
2. Click "New Application"
3. Name: "Supersonic Release Bot"
4. Save
```

**2. Create Bot**

```
1. Go to "Bot" section
2. Click "Reset Token"
3. Copy the token (save securely!)
4. Enable intents:
   ✅ Message Content Intent
   ✅ Guild Messages
```

**3. Add to Server**

```
1. Go to "OAuth2" → "URL Generator"
2. Scopes: bot
3. Permissions:
   ✅ Send Messages
   ✅ Create Public Threads
   ✅ Send Messages in Threads
4. Copy URL and open in browser
5. Select your server and authorize
```

**4. Get Channel ID**

```
1. Enable Developer Mode (User Settings → Advanced → Developer Mode)
2. Right-click your forum channel
3. "Copy Channel ID"
```

**5. Add GitHub Secrets**

```bash
# Go to repository secrets
open https://github.com/ChristopherElgin/SonicBuilderSupersonic/settings/secrets/actions

# Add:
# Name: DISCORD_BOT_TOKEN
# Value: (your bot token from step 2)

# Name: DISCORD_FORUM_CHANNEL_ID
# Value: (channel ID from step 4)
```

### Usage

**In Workflow:**

```yaml
- name: Mirror discussion to Discord forum
  if: always()
  env:
    DISCORD_BOT_TOKEN: ${{ secrets.DISCORD_BOT_TOKEN }}
    DISCORD_FORUM_CHANNEL_ID: ${{ secrets.DISCORD_FORUM_CHANNEL_ID }}
  run: |
    python3 tools/mirror_discussion_to_discord.py \
      --title "Release ${{ steps.ver.outputs.version }}" \
      --content "Release discussion opened.
      https://github.com/${{ github.repository }}/releases/tag/${{ steps.ver.outputs.version }}"
```

**Local Testing:**

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
export DISCORD_FORUM_CHANNEL_ID="123456789012345678"

python3 tools/mirror_discussion_to_discord.py \
  --title "Test Release v1.0.0" \
  --content "Testing Discord forum thread creation.

Features:
- Health scan system
- Cryptographic signing
- Release automation

Download: https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases/tag/v1.0.0"
```

### Thread Properties

- **Auto-archive**: 7 days (10080 minutes)
- **Rate limit**: None (0 seconds)
- **Max title**: 95 characters
- **Max content**: 1900 characters

### Benefits

- ✅ **Persistent** - Doesn't get lost in chat
- ✅ **Organized** - One thread per release
- ✅ **Searchable** - Easy to find past releases
- ✅ **Threaded** - Discussions stay on topic

---

## 🔔 Enhanced Notifications

**Include size diff in webhook notifications**

### Updated Webhook Call

```yaml
- name: Notify webhooks (with size diff)
  if: always()
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
  run: |
    # Extract size delta from diff report
    DELTA=$(sed -n '2p' RELEASE_SIZE_DIFF.md | sed 's/^Prev: //')
    
    python3 tools/notify_webhooks.py \
      --status "success" \
      --title "Release ${{ steps.ver.outputs.version }} published" \
      --text "Artifacts: ${DELTA}
Changelog & assets:
https://github.com/${{ github.repository }}/releases/tag/${{ steps.ver.outputs.version }}" \
      --url "https://github.com/${{ github.repository }}/releases/tag/${{ steps.ver.outputs.version }}"
```

### Example Notification

**Slack/Discord message:**
```
🚀 Release v1.0.1 published
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Artifacts: v1.0.0 total 45.32 MB → Now: 47.18 MB (+1.86 MB)

Changelog & assets:
https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases/tag/v1.0.1
```

---

## 🔄 Complete Integration Example

### Workflow with All Features

```yaml
name: Advanced Release

on:
  push:
    tags: ['v*']

env:
  ARTIFACT_GLOBS: |
    dist/**
    build/**
    **/*.zip
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
  DISCORD_BOT_TOKEN: ${{ secrets.DISCORD_BOT_TOKEN }}
  DISCORD_FORUM_CHANNEL_ID: ${{ secrets.DISCORD_FORUM_CHANNEL_ID }}

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # ... build steps ...
      
      # Size tracking
      - name: Generate size diff
        run: |
          python3 tools/release_size_diff.py \
            --globs "${{ env.ARTIFACT_GLOBS }}" \
            --tag "${{ github.ref_name }}" \
            --out RELEASE_SIZE_DIFF.md
          cat RELEASE_SIZE_DIFF.md >> RELEASE_SUMMARY.md
      
      # GitHub Discussion
      - name: Create discussion
        uses: actions/github-script@v7
        env:
          RELEASE_TAG: ${{ github.ref_name }}
        with:
          script: |
            const script = require('./tools/create_release_discussion.js');
            await script({github, core, context});
      
      # Discord Forum Thread
      - name: Discord forum thread
        run: |
          python3 tools/mirror_discussion_to_discord.py \
            --title "Release ${{ github.ref_name }}" \
            --content "$(cat RELEASE_SUMMARY.md | head -500)"
      
      # Webhook Notifications (with size)
      - name: Notify webhooks
        run: |
          DELTA=$(sed -n '2p' RELEASE_SIZE_DIFF.md | sed 's/^Prev: //')
          python3 tools/notify_webhooks.py \
            --status "success" \
            --title "Release ${{ github.ref_name }} published" \
            --text "Artifacts: ${DELTA}" \
            --url "https://github.com/${{ github.repository }}/releases/tag/${{ github.ref_name }}"
```

---

## 📊 Feature Matrix

| Feature | Tool | Secrets Required | Optional? |
|---------|------|------------------|-----------|
| Size Diff | `release_size_diff.py` | `GITHUB_TOKEN` | No |
| GitHub Discussion | `create_release_discussion.js` | None | Yes |
| Slack Webhook | `notify_webhooks.py` | `SLACK_WEBHOOK_URL` | Yes |
| Discord Webhook | `notify_webhooks.py` | `DISCORD_WEBHOOK_URL` | Yes |
| Discord Forum | `mirror_discussion_to_discord.py` | `DISCORD_BOT_TOKEN`, `DISCORD_FORUM_CHANNEL_ID` | Yes |

---

## 🧪 Testing

### Test Size Diff

```bash
# Requires previous release to exist
export GITHUB_REPOSITORY="ChristopherElgin/SonicBuilderSupersonic"
export GITHUB_TOKEN="your-token"

python3 tools/release_size_diff.py \
  --globs "dist/**" \
  --tag "v1.0.1" \
  --out test_diff.md

cat test_diff.md
```

### Test Discord Forum Thread

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
export DISCORD_FORUM_CHANNEL_ID="your-channel-id"

python3 tools/mirror_discussion_to_discord.py \
  --title "Test Release v0.0.1" \
  --content "Testing forum thread creation"

# Check Discord - should see new thread in forum channel
```

---

## ✅ Setup Checklist

Advanced features setup:

- [ ] Size diff tested locally
- [ ] Discord bot created
- [ ] Bot added to Discord server
- [ ] Forum channel ID copied
- [ ] `DISCORD_BOT_TOKEN` secret added
- [ ] `DISCORD_FORUM_CHANNEL_ID` secret added
- [ ] Forum thread tested locally
- [ ] Workflow updated with all features
- [ ] First release tests all integrations

---

## 🎯 Benefits Summary

**Size Tracking**:
- Track bloat and optimization
- Transparency for users
- Budget compliance

**Discord Forum**:
- Persistent discussions
- Better organization
- Searchable history

**Enhanced Notifications**:
- Richer context
- Size changes visible
- Multi-channel engagement

---

## 📚 Tool Reference

| Tool | Purpose | Exit Code |
|------|---------|-----------|
| `release_size_diff.py` | Compare artifact sizes | 1 (error) |
| `mirror_discussion_to_discord.py` | Create Discord thread | 1 (missing token) |

---

## ✨ Complete System

With these advanced features, you have:

1. ✅ **Health scanning** - Project audit
2. ✅ **Release automation** - One-command deploy
3. ✅ **Cryptographic security** - GPG + SHA-256
4. ✅ **Post-release verification** - Automated checks
5. ✅ **GitHub Discussions** - Community engagement
6. ✅ **Slack notifications** - Team alerts
7. ✅ **Discord webhooks** - Community updates
8. ✅ **Discord forum threads** - Persistent discussions 🆕
9. ✅ **Size tracking** - Artifact monitoring 🆕

**Enterprise-grade release infrastructure!** 🚀

---

## 💰 Per-Asset Size Budgets

**Enforce size limits on individual artifacts with delta tracking.**

### What It Does

The `size_budget_check.py` tool:
- ✅ Checks each artifact against configured budgets
- ✅ Enforces **max size** per file pattern
- ✅ Enforces **max delta** (growth from previous release)
- ✅ Can **annotate** (warn) or **enforce** (fail build)
- ✅ Color-coded status indicators

### Configuration

Edit `.github/artifact_budgets.json`:

```json
[
  { "pattern": "dist/*.zip",                 "max_mb": 300, "max_delta_mb": 50 },
  { "pattern": "build/**/*.zip",             "max_mb": 300, "max_delta_mb": 50 },
  { "pattern": "SonicBuilder_*_ProPack.zip", "max_mb": 500, "max_delta_mb": 75 },
  { "pattern": "**/*.whl",                   "max_mb": 150, "max_delta_mb": 25 },
  { "pattern": "**/*.tar.gz",                "max_mb": 400, "max_delta_mb": 75 }
]
```

**Pattern matching**: Uses `fnmatch` (glob patterns)
**Units**: MB (megabytes)

### Usage

**Annotate mode** (warn only):
```bash
python3 tools/size_budget_check.py \
  --globs "dist/**
build/**" \
  --budgets ".github/artifact_budgets.json" \
  --tag "v1.0.1" \
  --out "RELEASE_BUDGETS.md"
```

**Enforce mode** (fail on violations):
```bash
python3 tools/size_budget_check.py \
  --globs "dist/**" \
  --budgets ".github/artifact_budgets.json" \
  --tag "v1.0.1" \
  --out "RELEASE_BUDGETS.md" \
  --enforce  # Exit code 49 on violations
```

### Example Report

```markdown
## Per-asset Budgets — v1.0.1

Compared against: **v1.0.0**

| File | Size | Δ vs prev | Budget | Δ Budget | Status |
|------|-----:|----------:|-------:|---------:|:------:|
| `sonic_manual.pdf` | 23.45 MB | +1.35 MB | 300 MB | 50 MB | 🟢 |
| `build.zip` | 155.00 MB | +60.00 MB | 300 MB | 50 MB | 🟡 |
| `ProPack.zip` | 520.00 MB | +20.00 MB | 500 MB | 75 MB | 🟠 |
```

### Status Indicators

| Icon | Meaning | Condition |
|------|---------|-----------|
| 🟢 | **OK** | Within budget and delta |
| 🟡 | **Delta Warning** | Size OK, but delta exceeded |
| 🟠 | **Size Warning** | Exceeded max_mb |
| 🔴 | **Critical** | Both max_mb and max_delta_mb exceeded |

### Workflow Integration

```yaml
env:
  ART_ENFORCE_BUDGETS: "true"   # "false" to annotate only

steps:
  - name: Per-asset size budgets
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      ENFORCE_FLAG=$([ "${{ env.ART_ENFORCE_BUDGETS }}" = "true" ] && echo "--enforce" || echo "")
      python3 tools/size_budget_check.py \
        --globs "${{ env.ARTIFACT_GLOBS }}" \
        --budgets ".github/artifact_budgets.json" \
        --tag "$VERSION" \
        --out "RELEASE_BUDGETS.md" \
        $ENFORCE_FLAG
      cat RELEASE_BUDGETS.md >> RELEASE_SUMMARY.md
```

### Benefits

- ✅ **Prevent bloat** - Fail builds that exceed limits
- ✅ **Track growth** - Monitor incremental changes
- ✅ **Per-file control** - Different budgets for different artifacts
- ✅ **Flexible enforcement** - Annotate or enforce modes
- ✅ **Pattern matching** - Glob patterns for flexible rules

### Use Cases

**Development Phase** (`ART_ENFORCE_BUDGETS: "false"`):
- Warnings only
- Track trends
- Don't block releases

**Production Phase** (`ART_ENFORCE_BUDGETS: "true"`):
- Enforce limits
- Prevent bloat
- Fail builds on violations

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All budgets OK |
| 49 | Budget violations (when `--enforce` is set) |

---

## 📈 Budget History & Sparklines

**Visualize size trends across releases with automatic sparkline generation.**

### What It Does

Two complementary tools track historical artifact sizes:

**1. `budgets_history.py`** - Total release size sparkline
- ✅ Fetches last N releases from GitHub
- ✅ Sums all asset sizes per release
- ✅ Generates SVG sparkline chart
- ✅ Outputs JSON history data

**2. `budgets_asset_history.py`** - Per-asset history tracking
- ✅ Tracks each asset across releases
- ✅ Creates time-series data per file
- ✅ Enables inline sparklines in budget reports
- ✅ Shows growth trends at a glance

### Generated Files

```
docs/budgets_sparkline.svg        # Full-width sparkline chart (20 releases)
docs/budgets_history.json         # { "v1.0.0": 45000000, ... }
docs/budgets_asset_history.json   # { "file.zip": [42MB, 43MB, ...], ... }
docs/budgets.html                 # Enhanced with sparklines
```

### Usage

**Manual Generation:**
```bash
# Set environment variables
export GITHUB_REPOSITORY="owner/repo"
export GITHUB_TOKEN="ghp_..."  # or GH_TOKEN
export HISTORY_COUNT="20"      # optional, default 20

# Generate release totals sparkline
python3 tools/budgets_history.py

# Generate per-asset history
export HISTORY_COUNT="12"      # smaller window for per-asset
python3 tools/budgets_asset_history.py

# Generate enhanced budget report
python3 tools/budgets_report.py
```

**With Makefile:**
```bash
export GH_TOKEN=ghp_...   # repo scope
make budgets-history      # Both history tools
make budgets-report       # Enhanced report with sparklines
```

### GitHub Actions Integration

Add these steps to your release workflow **before** the budget report:

```yaml
      - name: Build per-asset history (last 12 releases)
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          HISTORY_COUNT: "12"
        run: |
          python3 tools/budgets_asset_history.py
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/budgets_asset_history.json || true
          git commit -m "docs(budgets-asset-history): update" || true
          git push || true

      - name: Build history sparkline (latest 20 releases)
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          HISTORY_COUNT: "20"
          TOTAL_WARN_MB: "900"     # Yellow warning threshold
          TOTAL_HARD_MB: "1200"    # Red hard limit
        run: |
          python3 tools/budgets_history.py
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/budgets_history.json docs/budgets_sparkline.svg || true
          git commit -m "docs(budgets-history): update" || true
          git push || true

      - name: Generate budgets dashboard (docs/budgets.html)
        env:
          ARTIFACT_GLOBS: ${{ env.ARTIFACT_GLOBS }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          VERSION: ${{ steps.ver.outputs.version }}
          HISTORY_COUNT: "20"
        run: |
          python3 tools/budgets_report.py
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add docs/budgets.html
          git commit -m "docs(budgets): $VERSION" || true
          git push || true

      - name: Annotate release with budget status
        id: totals
        env:
          TOTAL_WARN_MB: "900"
          TOTAL_HARD_MB: "1200"
        run: |
          echo "Checking overall size status..."
          latest_bytes=$(jq -r 'to_entries[-1].value' docs/budgets_history.json)
          latest_tag=$(jq -r 'to_entries[-1].key' docs/budgets_history.json)
          latest_mb=$(awk "BEGIN {printf \"%.0f\", $latest_bytes/1024/1024}")
          warn=${TOTAL_WARN_MB:-900}
          hard=${TOTAL_HARD_MB:-1200}
          if [ "$latest_mb" -ge "$hard" ]; then
            emoji="🔴"; msg="HARD limit exceeded ($latest_mb MB ≥ $hard MB)"
          elif [ "$latest_mb" -ge "$warn" ]; then
            emoji="🟡"; msg="Warning: near limit ($latest_mb MB ≥ $warn MB)"
          else
            emoji="🟢"; msg="OK — $latest_mb MB < $warn MB"
          fi
          echo "RELEASE STATUS: $emoji $msg"
          echo "tag=$latest_tag" >> $GITHUB_OUTPUT
          echo "line=$emoji Release size status: $msg" >> $GITHUB_OUTPUT

      - name: Update Release notes with status badge + legend
        uses: actions/github-script@v7
        with:
          script: |
            const { owner, repo } = context.repo;
            const tag   = "${{ steps.totals.outputs.tag }}" || "${{ steps.ver.outputs.version }}";
            const badge = "${{ steps.totals.outputs.line }}";
            const warn  = process.env.TOTAL_WARN_MB || "900";
            const hard  = process.env.TOTAL_HARD_MB || "1200";

            const legend = `Legend: 🟢 OK (< ${warn} MB) • 🟡 Warn (≥ ${warn} MB) • 🔴 Hard (≥ ${hard} MB)`;

            const rel = await github.rest.repos.getReleaseByTag({ owner, repo, tag });
            const body = rel.data.body || "";

            const header = `${badge}\n${legend}\n\n`;
            const cleaned = body.replace(/^([🟢🟡🔴].*Release size status:[^]*?Legend:[^\n]*\n\n)/, "");

            await github.rest.repos.updateRelease({
              owner, repo,
              release_id: rel.data.id,
              body: header + cleaned
            });

            console.log(`✅ Updated release ${tag} with badge + emoji legend`);
        env:
          TOTAL_WARN_MB: "900"
          TOTAL_HARD_MB: "1200"
```

**Optional: Add status to webhook notifications:**

```yaml
      - name: Notify webhooks (release published)
        if: always()
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          TOTAL_WARN_MB: "900"
          TOTAL_HARD_MB: "1200"
        run: |
          BADGE="${{ steps.totals.outputs.line }}"
          DELTA=$(sed -n '2p' RELEASE_SIZE_DIFF.md | sed 's/^Prev: //')
          LEGEND="Legend: 🟢 OK (< ${TOTAL_WARN_MB} MB) • 🟡 Warn (≥ ${TOTAL_WARN_MB} MB) • 🔴 Hard (≥ ${TOTAL_HARD_MB} MB)"
          python3 tools/notify_webhooks.py \
            --status "${{ job.status == 'success' && 'success' || 'failure' }}" \
            --title "Release ${{ steps.ver.outputs.version }} published" \
            --text "${BADGE}\n${LEGEND}\nArtifacts: ${DELTA}\nhttps://github.com/${{ github.repository }}/releases/tag/${{ steps.ver.outputs.version }}" \
            --url "https://github.com/${{ github.repository }}/releases/tag/${{ steps.ver.outputs.version }}"
```

### Enhanced Budget Dashboard

The `budgets_report.py` now includes:

**1. Release Total Sparkline with Thresholds**
- Full-width chart showing total artifact size trends
- Last 20 releases (configurable)
- **Threshold-based coloring**: Blue (OK) / Yellow (Warning) / Red (Hard limit)
- **Interactive tooltips**: Hover over points to see tag + size
- **Status legend**: Shows current status in top-right corner

**2. Per-Asset Inline Sparklines with Tooltips**
- Mini sparkline next to each artifact
- **Interactive tooltips**: Hover to see release tag + size per point
- Shows growth/shrinkage trends
- Base64-encoded SVG (no external files)
- Graceful fallback ("—") when no history

**3. Updated Table Columns:**

| File | Size | Prev | Δ | Budget | Δ Budget | **History** | Status |
|------|-----:|-----:|---:|-------:|---------:|:-----------:|:------:|
| file.zip | 45 MB | 43 MB | +2 MB | 50 MB | 10 MB | 📈 sparkline | 🟢 OK |

**4. Automatic Release Annotations**
- Releases automatically get status badge at the top
- Color-coded emoji: 🟢 OK / 🟡 Warning / 🔴 Hard limit
- Legend shows thresholds for transparency
- Visible to all users viewing the release

### Benefits

- ✅ **Interactive tooltips** - Hover to see exact size per release
- ✅ **Threshold coloring** - Instant visual status (green/yellow/red)
- ✅ **Trend visibility** - See size evolution at a glance
- ✅ **Early warning** - Spot gradual bloat before it's critical
- ✅ **Historical context** - Understand if current size is anomaly
- ✅ **Release annotations** - Status badge auto-added to releases
- ✅ **Visual reporting** - Beautiful charts in HTML dashboard
- ✅ **Automated** - Runs automatically in CI/CD
- ✅ **Lightweight** - Inline SVG, no external dependencies

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_REPOSITORY` | - | Required: `owner/repo` |
| `GITHUB_TOKEN` or `GH_TOKEN` | - | Required: GitHub API token |
| `HISTORY_COUNT` | `20` for totals, `12` for assets | Number of releases to track |
| `TOTAL_WARN_MB` | `900` | Yellow warning threshold (MB) |
| `TOTAL_HARD_MB` | `1200` | Red hard limit threshold (MB) |

### Example Dashboard

The enhanced budget report includes:

```markdown
## Artifact Budgets v1.0.5

Generated 2025-11-04T06:00:00Z · Repo: owner/repo · Compared to v1.0.4

┌──────────────────────────────────────────────────────────────┐
│ Release totals (last 20)          [🟡 987 MB ≥ 900 MB (WARN)]│
│ [Yellow/orange sparkline showing upward trend with tooltips] │
│  ↑ Hover over points to see: "v1.0.4 — 975.23 MB"          │
└──────────────────────────────────────────────────────────────┘

Current total: 145.23 MB
Previous total: 142.10 MB
Δ total: +3.13 MB

File              Size      History (hover for details!)    Status
──────────────────────────────────────────────────────────────────
sonic_pro.zip     45 MB    📊 [sparkline with tooltips]    🟢 OK
sonic_mega.zip    98 MB    📊 [sparkline with tooltips]    🟢 OK
```

**Example Release Notes (auto-generated):**

```markdown
🟡 Release size status: Warning — near limit (987 MB ≥ 900 MB)
Legend: 🟢 OK (< 900 MB) • 🟡 Warn (≥ 900 MB) • 🔴 Hard (≥ 1200 MB)

## What's Changed
- Feature: Added new voice packs
- Fix: Improved PDF generation performance

[...rest of changelog...]
```

### Interactive Features

**Tooltip Behavior:**
- Hover over any point on sparklines to see details
- Total sparkline shows: "v1.0.4 — 975.23 MB"
- Asset sparklines show: "v1.0.3 — 45.67 MB" or "v1.0.2 — not present"
- Works in all modern browsers
- Accessible via screen readers

**Color Coding:**
- 🟢 **Green/Blue**: Total < TOTAL_WARN_MB (healthy)
- 🟡 **Yellow**: TOTAL_WARN_MB ≤ Total < TOTAL_HARD_MB (warning)
- 🔴 **Red**: Total ≥ TOTAL_HARD_MB (critical)

**Release Status Badges:**
- Automatically added to top of release notes
- Updates on every release
- Includes threshold legend for transparency
- Optionally sent to Slack/Discord webhooks

### Troubleshooting

**No sparklines appearing:**
- Ensure `budgets_asset_history.json` exists
- Check `HISTORY_COUNT` is set appropriately
- Verify GitHub API rate limits not exceeded

**Tooltips not showing:**
- Ensure SVG is not blocked by browser extensions
- Check browser supports SVG `<title>` elements
- Test in incognito/private mode

**Missing total sparkline:**
- Ensure `budgets_history.py` ran successfully
- Check `docs/budgets_sparkline.svg` exists
- Verify `GITHUB_TOKEN` has repo access

**Wrong colors on sparkline:**
- Check `TOTAL_WARN_MB` and `TOTAL_HARD_MB` environment variables
- Verify thresholds are set correctly in workflow
- Re-run `budgets_history.py` with correct values

**Release badge not appearing:**
- Ensure `actions/github-script@v7` step runs
- Check `docs/budgets_history.json` exists
- Verify workflow has release write permissions

**GitHub API limits:**
- Default limit: 60 requests/hour (unauthenticated)
- Authenticated: 5,000 requests/hour
- Each history fetch = 1 API call

---

