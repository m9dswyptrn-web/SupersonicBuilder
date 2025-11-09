# PR Automation System

Complete Pull Request automation for SonicBuilder with docs validation, artifact sharing, and merge gates.

---

## 🎯 System Overview

### Complete PR Automation Pipeline

1. **`docs-build`** - Builds PDFs on every push/PR
2. **`pr-docs-ready-label`** - Auto-labels PRs when build succeeds
3. **`pr-docs-comment`** - Posts artifact download links on PRs
4. **`pr-merge-guard`** - Blocks merges if docs changed but not validated
5. **`pr-docs-ready-command`** - `/docs-ready` maintainer override
6. **`pr-docs-reset-command`** - `/docs-reset` label removal
7. **`pr-docs-ready-autoreset`** - Auto-removes label on new commits

---

## 🔄 How It Works

### When You Open a PR

```
1. Developer pushes code to PR branch
   ↓
2. docs-build workflow runs
   - Builds dark + light PDFs
   - Generates checksums
   - Uploads artifacts (14-day retention)
   ↓
3. pr-docs-comment workflow triggers
   - Finds PR by commit SHA
   - Posts/updates comment with artifact download table
   - Cleans up duplicate comments
   ↓
4. pr-docs-ready-label workflow triggers
   - Creates 'docs:ready' label if needed
   - Applies label to PR
   ↓
5. pr-merge-guard workflow checks
   - If PR changes docs → requires 'docs:ready' label
   - If PR doesn't change docs → skips check
   - Blocks merge until label exists
```

---

## 📋 Workflows Details

### 1. `docs-build.yml`

**Triggers:** Push/PR to main branch

**Actions:**
- Install Python dependencies
- Run `make verify` preflight
- Build dark & light manuals
- Generate SHA256 checksums
- Upload artifacts

**Artifacts:**
- `output/*.pdf`
- `output/checksums/*.sha256`

**Retention:** 14 days

---

### 2. `pr-docs-ready-label.yml`

**Triggers:** After `docs-build` completes successfully

**Actions:**
- Find PRs by commit SHA
- Ensure `docs:ready` label exists in repo
- Apply label to all matching PRs

**Label Details:**
- **Name:** `docs:ready`
- **Color:** Green (`0e8a16`)
- **Description:** "Docs build passed for this PR"

---

### 3. `pr-docs-comment.yml`

**Triggers:** After `docs-build` completes successfully

**Actions:**
- Find PRs by commit SHA
- List workflow artifacts
- Post/update comment with download links
- Delete old duplicate comments

**Comment Format:**
```markdown
<!-- SB_DOCS_ARTIFACTS -->
**Docs Build** ✅

Run: [#123](link) on `feature-branch`

| Artifact | Link | Size |
|---|---|---|
| docs-build-abc123 | [download](link) | 5 MB |

> Links require GitHub login. Artifacts expire per repo retention settings.
```

**Features:**
- **Upsert behavior** - Updates existing comment instead of creating new ones
- **Cleanup** - Deletes older duplicate comments
- **Marker-based** - Uses `<!-- SB_DOCS_ARTIFACTS -->` to identify managed comments

---

### 4. `pr-docs-ready-command.yml`

**Triggers:** Comment `/docs-ready` on a PR

**Actions:**
- Validate commenter has maintainer permissions (admin/write)
- Apply `docs:ready` label to the PR
- Add rocket reaction to comment

**Purpose:** Manual override for maintainers to apply label after manual verification

---

### 5. `pr-docs-reset-command.yml`

**Triggers:** Comment `/docs-reset` on a PR

**Actions:**
- Validate commenter has maintainer permissions (admin/write)
- Remove `docs:ready` label from the PR

**Purpose:** Manual override to force re-validation

---

### 6. `pr-docs-ready-autoreset.yml`

**Triggers:** New commits pushed to PR (synchronize, reopen, etc.)

**Actions:**
- Check if `docs:ready` label exists
- Remove the label if present
- Post comment explaining auto-reset

**Purpose:** Ensure label is only valid for latest commit

**Comment Example:**
```
🔁 New commits detected — removed **docs:ready**. It will be re-applied 
automatically after the next successful _docs-build_, or a maintainer 
can comment `/docs-ready`.
```

---

### 7. `pr-merge-guard.yml`

**Triggers:** PR events (opened, sync, reopened, labeled, etc.)

**Actions:**
- Check which files changed in PR
- Determine if docs-related changes exist
- If yes → require `docs:ready` label
- If no → skip check

**Docs-Related Patterns:**
```javascript
/^docs\//                          // Any docs/ files
/^README\.md$/i                    // README file
/^assets\//                        // Asset files
/diagram|wiring|\.svg$|\.pdf$|\.png$|\.jpg$/i  // Media files
/^\.github\/workflows\/docs-/      // Docs workflows
```

**Behavior:**
- ✅ **Docs changed + label present** → Allow merge
- ❌ **Docs changed + no label** → Block merge
- ✅ **No docs changed** → Allow merge (skip check)

---

## 🚀 Usage Examples

### For Developers

#### Opening a PR with Docs Changes

```bash
# 1. Make changes to docs
git checkout -b feat/update-wiring-docs
# ... edit files ...
git add docs/wiring.md
git commit -m "docs: update wiring diagrams"
git push origin feat/update-wiring-docs

# 2. Open PR on GitHub
# 3. Wait for docs-build to run (automatic)
# 4. Check Actions tab for build status
# 5. When successful:
#    - PR gets 'docs:ready' label (automatic)
#    - Comment appears with artifact links (automatic)
#    - Merge guard passes (automatic)
# 6. Merge PR ✅
```

#### Opening a PR without Docs Changes

```bash
# 1. Make code-only changes
git checkout -b fix/update-script
# ... edit scripts/builder.py ...
git commit -m "fix: correct PDF metadata"
git push origin fix/update-script

# 2. Open PR on GitHub
# 3. docs-build still runs (builds artifacts)
# 4. Merge guard detects no docs changes → skips label check
# 5. Merge PR ✅ (no label required)
```

---

## 🔍 Maintainer Override Commands

### `/docs-ready` - Apply Label

**When to use:**
- Docs build succeeded but label wasn't auto-applied
- Manual verification of artifacts completed
- Override automated checks

**How to use:**
```
Just comment on the PR:
/docs-ready
```

**What happens:**
1. System validates you have maintainer permissions
2. Applies `docs:ready` label to PR
3. Adds 🚀 reaction to your comment
4. Merge guard passes (if this was blocking)

---

### `/docs-reset` - Remove Label

**When to use:**
- Need to force re-build and re-validation
- Label was applied incorrectly
- Changes made after label application

**How to use:**
```
Just comment on the PR:
/docs-reset
```

**What happens:**
1. System validates you have maintainer permissions
2. Removes `docs:ready` label from PR
3. Merge guard will block until label reapplied
4. Next successful build will auto-apply label again

---

### Manual Label Management (Alternative)

If slash commands aren't working:

```bash
# Via GitHub UI:
1. Go to PR page
2. Click "Labels" on right sidebar
3. Select/remove "docs:ready"

# Via GitHub CLI:
gh pr edit <PR_NUMBER> --add-label "docs:ready"
gh pr edit <PR_NUMBER> --remove-label "docs:ready"
```

---

## 📊 PR Template Integration

Updated `.github/pull_request_template.md` includes:

```markdown
## CI Requirements
- [ ] **Docs Build must pass** (PDFs + checksums) — see Actions tab → *docs-build*
- [ ] If this PR changes release docs, ensure **Latest Docs** block renders correctly
```

This reminds contributors to:
1. Check docs-build workflow status
2. Verify docs rendering if applicable

---

## 🛡️ Branch Protection Integration

### Recommended Settings

To enforce this system via branch protection:

1. **Required Status Checks:**
   - `pr-merge-guard`
   - `docs-build / build` (optional but recommended)

2. **Required Labels:**
   - Not applicable (handled by `pr-merge-guard` logic)

3. **Settings:**
   ```json
   {
     "required_status_checks": {
       "strict": true,
       "contexts": [
         "pr-merge-guard"
       ]
     },
     "enforce_admins": false,
     "required_pull_request_reviews": {
       "dismiss_stale_reviews": true,
       "require_code_owner_reviews": false,
       "required_approving_review_count": 1
     }
   }
   ```

---

## 🔧 Troubleshooting

### Label Not Applied

**Problem:** PR doesn't get `docs:ready` label after build succeeds

**Solutions:**
1. Check `pr-docs-ready-label` workflow run in Actions tab
2. Verify `docs-build` completed successfully
3. Check workflow permissions (needs `pull-requests: write`)
4. Manually apply label as workaround

---

### Comment Not Posted

**Problem:** Artifact comment doesn't appear on PR

**Solutions:**
1. Check `pr-docs-comment` workflow run in Actions tab
2. Verify PR was found by commit SHA search
3. Check workflow permissions (needs `pull-requests: write`)
4. Verify artifacts were uploaded in `docs-build`

---

### Merge Blocked Incorrectly

**Problem:** Merge guard blocks merge but shouldn't

**Solutions:**
1. Check which files changed: `gh pr view <PR> --json files`
2. Verify no docs-related patterns match
3. Check `pr-merge-guard` workflow logs
4. Manually apply `docs:ready` label if needed

---

## 🎛️ Configuration

### Adjust Docs Pattern Matching

Edit `.github/workflows/pr-merge-guard.yml`:

```javascript
const isDocsChange = names.some(n =>
  /^docs\//.test(n) ||
  /^README\.md$/i.test(n) ||
  /^assets\//.test(n) ||
  /diagram|wiring|\.svg$|\.pdf$|\.png$|\.jpg$/i.test(n) ||
  /^\.github\/workflows\/docs-/.test(n) ||
  /^YOUR_CUSTOM_PATTERN/.test(n)  // ← Add custom patterns here
);
```

### Change Artifact Retention

Edit `.github/workflows/docs-build.yml`:

```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v4
  with:
    retention-days: 30  # ← Change from 14 to desired days
```

### Change Label Name/Color

Edit `.github/workflows/pr-docs-ready-label.yml`:

```javascript
const labelName = 'my-custom-label';  // ← Change label name
// ...
await github.rest.issues.createLabel({
  color: 'ff0000',  // ← Change color (hex without #)
  description: 'Custom description'
});
```

---

## 📈 Benefits

### Developer Experience
✅ Automatic artifact sharing on every PR  
✅ No manual "docs passed" comments needed  
✅ Clear merge requirements in PR template  
✅ Self-service artifact downloads (no CI access needed)

### Quality Assurance
✅ Enforces docs validation before merge  
✅ Prevents broken docs from reaching main  
✅ Automatic cleanup of duplicate comments  
✅ Smart detection (only checks docs PRs)

### Visibility
✅ PR comments show build status instantly  
✅ Labels provide at-a-glance validation status  
✅ Artifact sizes shown for quick assessment  
✅ Direct links to workflow runs

---

## 🔗 Related Documentation

- [Dual Badge System](DUAL_BADGE_SYSTEM.md)
- [Release Automation](RELEASE_AUTOMATION.md)
- [CI Release Guide](CI_RELEASE_GUIDE.md)

---

**Your PR workflow is now fully automated!** 🎉
