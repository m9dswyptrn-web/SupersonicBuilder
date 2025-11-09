# Release Automation

Complete automation system for SonicBuilder releases with CHANGELOG generation, badge management, and one-command workflows.

## Overview

The release automation system provides:
1. **CHANGELOG automation** - Conventional Commits parser
2. **Badge management** - Automatic live/local switching
3. **One-command release** - Complete workflow in single make target
4. **Release checklists** - Pre-flight verification templates

---

## Quick Start

### One-Command Release

```bash
make release_tag VERSION=v2.0.15
```

**What it does:**
1. Switches badges to live endpoints
2. Generates CHANGELOG for new version
3. Prints next steps for you to review and execute

---

## CHANGELOG Automation

### Conventional Commits Format

The system parses git commits using [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(build): add modular makefile system

Separated 257 lines of targets into make/sonicbuilder.mk
for better organization and maintainability.

Closes #42
```

### Supported Types

| Type | Emoji | Section |
|------|-------|---------|
| `feat` | ✨ | Features |
| `fix` | 🐞 | Fixes |
| `perf` | ⚡ | Performance |
| `refactor` | ♻️ | Refactors |
| `docs` | 📝 | Docs |
| `build` | 🏗️ | Build |
| `ci` | 🧰 | CI |
| `test` | ✅ | Tests |
| `style` | 🎨 | Style |
| `chore` | 🧹 | Chore |
| `revert` | ⏪ | Reverts |
| other | 🔧 | Other |

### Example Commits

```bash
# Features
git commit -m "feat(badges): add dual badge system with completeness checking"

# Fixes
git commit -m "fix(docs): correct wiring diagram labels in Appendix C"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Build system
git commit -m "build(make): separate modular targets into make/sonicbuilder.mk"

# CI/CD
git commit -m "ci(workflow): add branch protection guard"
```

---

## Make Targets

### Preview CHANGELOG

```bash
make changelog_preview
```

**Output:** Shows what would be added to CHANGELOG.md (unreleased changes since last tag)

```markdown
## Unreleased — 2025-10-29

[Full Changelog](https://github.com/owner/repo/compare/v2.0.14...HEAD)

### ✨ Features

- add dual badge system ([e05247101a22](https://github.com/owner/repo/commit/e05247101a22))
- local completeness computation ([f1234567890a](https://github.com/owner/repo/commit/f1234567890a))

### 🐞 Fixes

- correct README badge URLs ([a0987654321b](https://github.com/owner/repo/commit/a0987654321b))

### 📝 Docs

- add DUAL_BADGE_SYSTEM.md guide ([b1234567890c](https://github.com/owner/repo/commit/b1234567890c))
```

### Write CHANGELOG

```bash
make changelog_update
```

**What it does:**
1. Generates CHANGELOG entry from git log (last tag → HEAD)
2. Prepends to CHANGELOG.md
3. Groups by commit type with emoji headers

### CHANGELOG for Specific Version

```bash
make changelog_for_tag VERSION=v2.0.15
```

**What it does:** Same as `changelog_update`, but uses VERSION in the heading

### Complete Release Tag Workflow

```bash
make release_tag VERSION=v2.0.15
```

**Steps:**
1. Run `badges_live_on` (switch to live endpoints)
2. Generate CHANGELOG for VERSION
3. Print next steps

**Output:**
```
🚀 Tagging SonicBuilder release v2.0.15...
>> Switching README badges to LIVE endpoints
✓ Live completeness badge activated.
📝 Updating CHANGELOG for v2.0.15...
✅ CHANGELOG.md updated with v2.0.15
✅ Release v2.0.15 ready. Review changes, then:
   git add CHANGELOG.md README.md
   git commit -m 'docs: prepare release v2.0.15'
   git tag v2.0.15
   git push && git push --tags
```

---

## Complete Release Workflow

### Step-by-Step

```bash
# 1. Ensure all work is committed
git status

# 2. Build and verify locally
make docs_release_local_strict

# 3. Check completeness
make badge_compute_complete_local

# 4. Preview CHANGELOG
make changelog_preview

# 5. Run release automation
make release_tag VERSION=v2.0.15

# 6. Review generated changes
git diff CHANGELOG.md README.md

# 7. Commit and tag
git add CHANGELOG.md README.md
git commit -m "docs: prepare release v2.0.15"
git tag v2.0.15
git push && git push --tags

# 8. CI automatically:
#    - Builds docs
#    - Stamps metadata
#    - Uploads to release
#    - Enriches notes
#    - Updates README
#    - Updates badges (both)
```

### Automated Workflow (Advanced)

Create a script `scripts/release.sh`:

```bash
#!/bin/bash
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/release.sh v2.0.15"
  exit 1
fi

echo "🚀 Releasing $VERSION"

# Build and verify
make docs_release_local_strict

# Check completeness
if ! make badge_compute_complete_local | grep -q '"complete"'; then
  echo "❌ Release incomplete. Fix missing assets first."
  exit 1
fi

# Generate CHANGELOG and prepare
make release_tag VERSION=$VERSION

# Commit and tag
git add CHANGELOG.md README.md .status/
git commit -m "docs: prepare release $VERSION"
git tag $VERSION
git push && git push --tags

echo "✅ Release $VERSION pushed!"
```

**Usage:**
```bash
chmod +x scripts/release.sh
./scripts/release.sh v2.0.15
```

---

## Release Checklist

### Use Template

A release checklist template is available at `templates/RELEASE_CHECKLIST.md`:

```markdown
# 📦 SonicBuilder — Documentation Release Checklist

✅ **Version**: `v2.0.15`  
🪪 **Commit**: `e05247101a22`  
📅 **Date**: `2025-10-29`

---

## 🚀 Preflight

- [ ] Run `make docs_release_local_strict`
- [ ] Run `make badge_compute_complete_local`
- [ ] Check for `complete`
- [ ] Review CHANGELOG: `make changelog_preview`

## 🏷️ Tag & Push

- [ ] `make release_tag VERSION=v2.0.15`
- [ ] Review: `git diff`
- [ ] Commit and tag
- [ ] Push

## 🧪 CI/CD Verification

- [ ] Docs Release badge ✅
- [ ] Docs Complete badge ✅

## 📎 Post-Release

- [ ] Verify assets
- [ ] Test downloads
- [ ] Celebrate 🍻
```

### Generate Filled Checklist

```bash
# Get current values
VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo v0.0.0)
COMMIT=$(git rev-parse --short=12 HEAD)
DATE=$(date -u +%Y-%m-%d)

# Create filled checklist
sed -e "s/{VERSION}/$VERSION/g" \
    -e "s/{COMMIT}/$COMMIT/g" \
    -e "s/{DATE}/$DATE/g" \
    templates/RELEASE_CHECKLIST.md > RELEASE_CHECKLIST_$VERSION.md

echo "✅ Created RELEASE_CHECKLIST_$VERSION.md"
```

---

## CHANGELOG Best Practices

### 1. Use Conventional Commits

```bash
# Good
git commit -m "feat(build): add modular makefile"

# Bad
git commit -m "updated makefile"
```

### 2. Include PR Numbers

```bash
git commit -m "fix(docs): correct diagram labels (#42)"
```

The CHANGELOG generator automatically links to PRs.

### 3. Write Descriptive Messages

```bash
# Good
git commit -m "feat(badges): add dual badge system with completeness

Implements separate badges for workflow status and asset completeness,
allowing clear visibility into both build health and release quality.

- Badge 1: Workflow status (pass/fail)
- Badge 2: Asset completeness (complete/incomplete)
- Local/live badge toggling for development workflow"

# Bad
git commit -m "feat: new badges"
```

### 4. Use Scopes Consistently

```bash
feat(build): ...
feat(docs): ...
feat(badges): ...
ci(workflow): ...
ci(guard): ...
```

---

## Example Generated CHANGELOG

```markdown
## v2.0.15 — 2025-10-29

[Full Changelog](https://github.com/owner/repo/compare/v2.0.14...v2.0.15)

### ✨ Features

- add dual badge system with completeness checking ([e05247101a22](https://github.com/owner/repo/commit/e05247101a22)) #42
- local completeness computation ([f1234567890a](https://github.com/owner/repo/commit/f1234567890a))
- CHANGELOG automation with Conventional Commits ([c2345678901b](https://github.com/owner/repo/commit/c2345678901b))

### 🏗️ Build

- separate modular targets into make/sonicbuilder.mk ([d3456789012c](https://github.com/owner/repo/commit/d3456789012c))
- add release automation helpers ([e4567890123d](https://github.com/owner/repo/commit/e4567890123d))

### 📝 Docs

- add DUAL_BADGE_SYSTEM.md guide ([a0987654321e](https://github.com/owner/repo/commit/a0987654321e))
- add RELEASE_AUTOMATION.md guide ([b0987654321f](https://github.com/owner/repo/commit/b0987654321f))

### 🐞 Fixes

- correct README badge URLs ([c0987654321g](https://github.com/owner/repo/commit/c0987654321g))

---
```

---

## Troubleshooting

### CHANGELOG shows no changes

**Cause:** No commits since last tag

**Solution:** Make some commits first:
```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### Commits not grouped correctly

**Cause:** Not using Conventional Commits format

**Solution:** Use proper format:
```bash
type(scope): subject
```

### PR numbers not detected

**Cause:** PR number not in parentheses

**Format:**
```bash
git commit -m "fix(docs): correct labels (#42)"
#                                        ^^^^
```

---

## Integration with CI/CD

### GitHub Actions Workflow

You can automate CHANGELOG updates in CI:

```yaml
name: changelog-on-release
on:
  release:
    types: [published]
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Update CHANGELOG
        run: |
          NEW_TAG=${{ github.event.release.tag_name }} python3 scripts/changelog_update.py --write
          git add CHANGELOG.md
          git commit -m "docs(changelog): update for ${{ github.event.release.tag_name }}"
          git push
```

---

## Related Documentation

- **[DUAL_BADGE_SYSTEM.md](DUAL_BADGE_SYSTEM.md)** - Badge management
- **[MODULAR_BUILD_SYSTEM.md](MODULAR_BUILD_SYSTEM.md)** - Build targets
- **[BADGE_SYSTEM.md](BADGE_SYSTEM.md)** - Badge configuration

---

## Version History

- **v2.0.15** - Release automation
  - CHANGELOG automation with Conventional Commits
  - One-command release workflow
  - Badge management integration
  - Release checklist templates
