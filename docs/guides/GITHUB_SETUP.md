# GitHub Repository Setup Guide

Complete guide to setting up your Sonic Builder repository on GitHub.

---

## 📋 Complete GitHub Integration

Your repository now includes:

### ✅ Workflows (CI/CD)
- `.github/workflows/sonicbuilder-ci.yml` - Continuous integration
- `.github/workflows/release.yml` - Release automation

### ✅ Issue Templates
- `.github/ISSUE_TEMPLATE/bug_report.yml` - Bug reports
- `.github/ISSUE_TEMPLATE/feature_request.yml` - Feature requests
- `.github/ISSUE_TEMPLATE/chore.yml` - Maintenance tasks
- `.github/config.yml` - Issue configuration (disables blank issues)

### ✅ Repository Configuration
- `.github/CODEOWNERS` - Code ownership
- `.github/labels.yml` - Label definitions
- `.github/pull_request_template.md` - PR template
- `CONTRIBUTING.md` - Contribution guidelines

### ✅ Label Setup Scripts
- `scripts/setup_labels.py` - Python-based label setup
- `scripts/setup_labels_gh.sh` - GitHub CLI-based setup

---

## 🚀 Step-by-Step Setup

### 1. Update Repository References

**Edit `.github/CODEOWNERS`**:
```bash
vim .github/CODEOWNERS
# Replace @your-github-handle with your GitHub username
```

**Edit `.github/config.yml`**:
```bash
vim .github/config.yml
# Replace <YOUR_ORG>/<YOUR_REPO> with your repository path
```

---

### 2. Push to GitHub

```bash
# Stage all new files
git add .github/ scripts/ CONTRIBUTING.md CHANGELOG.md VERSION

# Commit
git commit -m "Add complete GitHub repository setup v2.0.7"

# Push
git push origin main
```

---

### 3. Setup Labels

#### Option A: GitHub CLI (Recommended)

```bash
# Login to GitHub CLI
gh auth login

# Run label setup script
bash scripts/setup_labels_gh.sh YOUR_ORG/YOUR_REPO
```

#### Option B: Python Script

```bash
# Set your GitHub Personal Access Token
export GITHUB_TOKEN=ghp_yourPersonalAccessToken

# Run Python setup script
python scripts/setup_labels.py --repo YOUR_ORG/YOUR_REPO --labels .github/labels.yml
```

**Creating a Personal Access Token**:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token and use it above

---

### 4. Verify Setup

#### Check Workflows
1. Go to your repository on GitHub
2. Click "Actions" tab
3. You should see "SonicBuilder CI" workflow
4. Push a commit to trigger it

#### Check Issue Templates
1. Go to "Issues" tab
2. Click "New Issue"
3. You should see 3 template options:
   - 🐞 Bug report
   - ✨ Feature request
   - 🧹 Chore

#### Check Labels
1. Go to "Issues" tab
2. Click "Labels"
3. Verify all labels from `labels.yml` are present

#### Check PR Template
1. Create a test branch
2. Open a pull request
3. Template should auto-fill

---

## 🏷️ Label System

### Type Labels
- **bug** (red) - Something isn't working
- **feature** (light blue) - New feature or enhancement
- **chore** (gray) - Maintenance, refactors, dependency bumps
- **docs** (blue) - Documentation-only changes
- **build** (purple) - Build system / CI

### Special Labels
- **good first issue** (purple) - Good for newcomers

All labels are defined in `.github/labels.yml` and can be customized.

---

## 🎫 Issue Templates

### Bug Report Template
Fields:
- Description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, etc.)
- Additional context

### Feature Request Template
Fields:
- Description
- Motivation/Rationale
- Proposal
- Additional context

### Chore Template
Fields:
- Description
- Type of maintenance
- Additional context

---

## 🤝 Contributing Workflow

### For Contributors

1. **Read CONTRIBUTING.md** first
2. **Fork** the repository
3. **Clone** your fork
4. **Create branch**: `git checkout -b feat/my-feature`
5. **Make changes**
6. **Test**: `make verify`
7. **Commit**: Follow conventional commit style
8. **Push**: `git push origin feat/my-feature`
9. **Open PR**: Template auto-fills
10. **Wait for review**: Code owners will be notified

### For Maintainers

1. **Review PRs**: Assigned automatically via CODEOWNERS
2. **Check CI**: Ensure all checks pass
3. **Review code**: Use GitHub review system
4. **Merge**: Squash and merge recommended
5. **Tag releases**: `git tag v2.0.7 && git push origin v2.0.7`

---

## 🤖 CI/CD Workflows

### Continuous Integration (sonicbuilder-ci.yml)

**Triggers**:
- Push to `main` or `master`
- Pull requests
- Manual dispatch

**Actions**:
1. Checkout code
2. Setup Python 3.11
3. Cache dependencies
4. Install dependencies
5. Run `make verify` (dark theme)
6. Run `make verify` (light theme)
7. Test annotation system
8. Upload artifacts

**Artifacts**:
- `output-pdfs` - All generated PDFs (7 day retention)

### Release Automation (release.yml)

**Triggers**:
- Git tags matching `v*` pattern

**Actions**:
1. Checkout code
2. Setup Python 3.11
3. Install dependencies
4. Run full build (`make clean && make build && make post && make package`)
5. Create GitHub Release
6. Attach PDF bundles

**Release Contents**:
- Versioned PDFs
- Field cards
- Complete bundle ZIPs

---

## 📊 Project Management

### Using Labels

**Triage new issues**:
```
Type: bug/feature/chore/docs
Priority: Add if critical/high
Area: annotations/build/ci-cd/docs
```

**Track progress**:
```
needs-review → in-progress → ready
```

**Mark blockers**:
```
Add "blocked" label
Link to blocking issue
```

### Using Milestones

Create milestones for versions:
```
v2.1.0 - Modular Build System
v2.2.0 - Advanced Features
```

### Using Projects

Create GitHub Projects for:
- Current sprint
- Backlog
- Long-term roadmap

---

## 🔧 Customization

### Add More Issue Templates

1. Create new `.yml` file in `.github/ISSUE_TEMPLATE/`
2. Follow existing template structure
3. Commit and push

Example structure:
```yaml
---
name: "🎨 Template Name"
about: Description
title: "[PREFIX] "
labels: ["label"]
assignees: []
---

## Section
<!-- Instructions -->
```

### Add More Labels

1. Edit `.github/labels.yml`
2. Add new labels:
```yaml
- name: new-label
  color: hexcolor
  description: Description
```
3. Run setup script again

### Modify Workflows

1. Edit workflow files in `.github/workflows/`
2. Test changes on a branch first
3. Monitor Actions tab for results

---

## 🎯 Best Practices

### Issue Management
- Use templates for all issues
- Apply labels immediately
- Link related issues
- Close stale issues

### PR Management
- Keep PRs focused (one feature/fix)
- Write clear descriptions
- Link to related issues
- Ensure CI passes
- Get code owner review

### Release Management
- Use semantic versioning (v2.0.7)
- Update CHANGELOG.md
- Tag after merge to main
- Monitor release workflow
- Verify artifacts

### Collaboration
- Review PRs promptly
- Provide constructive feedback
- Test changes locally
- Document decisions
- Celebrate contributions

---

## 📝 Maintenance

### Regular Tasks

**Weekly**:
- Review open issues
- Triage new issues
- Review open PRs
- Update labels as needed

**Monthly**:
- Update dependencies
- Review milestones
- Archive completed projects
- Update documentation

**Per Release**:
- Update CHANGELOG.md
- Update VERSION
- Tag release
- Verify artifacts
- Announce release

---

## 🆘 Troubleshooting

### Labels Not Created

**Issue**: Script fails to create labels

**Solution**:
```bash
# Verify GitHub token has repo scope
gh auth status

# Try GitHub CLI method instead
bash scripts/setup_labels_gh.sh YOUR_ORG/YOUR_REPO
```

### Workflows Not Running

**Issue**: CI doesn't trigger on push

**Solution**:
1. Check `.github/workflows/` files exist
2. Verify YAML syntax
3. Check branch protection rules
4. Review Actions tab for errors

### Issue Templates Not Showing

**Issue**: Templates don't appear when creating issue

**Solution**:
1. Verify files in `.github/ISSUE_TEMPLATE/`
2. Check `.github/config.yml` exists
3. Wait 5-10 minutes for GitHub to update
4. Clear browser cache

### CODEOWNERS Not Working

**Issue**: Reviews not auto-assigned

**Solution**:
1. Update username in `.github/CODEOWNERS`
2. Ensure user has write access
3. Check file is in root of `.github/`
4. Verify branch protection requires reviews

---

## 📚 Resources

### GitHub Documentation
- [About issue templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates)
- [Managing labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub Actions](https://docs.github.com/en/actions)

### Sonic Builder Documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [CI_CD_SETUP.md](../CI_CD_SETUP.md) - CI/CD details
- [COMPLETE_SYSTEM_v2.0.5.md](../COMPLETE_SYSTEM_v2.0.5.md) - System overview

---

**Version**: 2.0.7  
**Last Updated**: 2025-10-27  
**Status**: ✅ Complete GitHub Integration
