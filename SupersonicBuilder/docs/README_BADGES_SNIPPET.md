# GitHub README Badges

Copy/paste these Shields.io badges into your README.md to show CI/CD status and version.

---

## 🏷️ Quick Copy (All Badges)

```markdown
[![Build Appendix C](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=main&label=Build%20Appendix%20C&logo=github)](https://github.com/OWNER/REPO/actions/workflows/build-appendixC.yml)
[![Release Appendix C](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/release-appendixC.yml?label=Release%20Appendix%20C&logo=github)](https://github.com/OWNER/REPO/actions/workflows/release-appendixC.yml)
[![Enrich Release Notes](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/release-notes-enricher.yml?label=Release%20Notes&logo=github)](https://github.com/OWNER/REPO/actions/workflows/release-notes-enricher.yml)
[![Version](https://img.shields.io/github/v/release/OWNER/REPO?label=Version&logo=semver)](https://github.com/OWNER/REPO/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
```

**Replace `OWNER/REPO` with your repository path** (e.g., `username/sonicbuilder`)

---

## 📊 Individual Badges

### Build Status
```markdown
[![Build Appendix C](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=main&label=Build%20Appendix%20C&logo=github)](https://github.com/OWNER/REPO/actions/workflows/build-appendixC.yml)
```

### Release Status
```markdown
[![Release Appendix C](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/release-appendixC.yml?label=Release%20Appendix%20C&logo=github)](https://github.com/OWNER/REPO/actions/workflows/release-appendixC.yml)
```

### Release Notes Enricher
```markdown
[![Enrich Release Notes](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/release-notes-enricher.yml?label=Release%20Notes&logo=github)](https://github.com/OWNER/REPO/actions/workflows/release-notes-enricher.yml)
```

### Version Badge
```markdown
[![Version](https://img.shields.io/github/v/release/OWNER/REPO?label=Version&logo=semver)](https://github.com/OWNER/REPO/releases/latest)
```

### CoA Workflow
```markdown
[![CoA Generation](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/coa-on-release.yml?label=CoA%20Generation&logo=github)](https://github.com/OWNER/REPO/actions/workflows/coa-on-release.yml)
```

### CI Pipeline
```markdown
[![CI](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/sonicbuilder-ci.yml?branch=main&label=CI&logo=github)](https://github.com/OWNER/REPO/actions/workflows/sonicbuilder-ci.yml)
```

---

## 🎨 Badge Styles

### Default (Flat)
```markdown
![Badge](https://img.shields.io/badge/Build-Passing-success)
```

### Flat Square
```markdown
![Badge](https://img.shields.io/badge/Build-Passing-success?style=flat-square)
```

### Plastic
```markdown
![Badge](https://img.shields.io/badge/Build-Passing-success?style=plastic)
```

### For the Badge
```markdown
![Badge](https://img.shields.io/badge/Build-Passing-success?style=for-the-badge)
```

---

## 🌈 Custom Colors

```markdown
<!-- Blue -->
![Badge](https://img.shields.io/badge/Status-Active-blue)

<!-- Green -->
![Badge](https://img.shields.io/badge/Build-Passing-success)

<!-- Red -->
![Badge](https://img.shields.io/badge/Build-Failing-critical)

<!-- Orange -->
![Badge](https://img.shields.io/badge/Status-Beta-orange)

<!-- Yellow -->
![Badge](https://img.shields.io/badge/Docs-Complete-yellow)

<!-- Custom Hex -->
![Badge](https://img.shields.io/badge/Custom-Color-ff69b4)
```

---

## 📦 Release & Download Badges

### Latest Release
```markdown
[![Latest Release](https://img.shields.io/github/v/release/OWNER/REPO)](https://github.com/OWNER/REPO/releases/latest)
```

### Release Date
```markdown
[![Release Date](https://img.shields.io/github/release-date/OWNER/REPO)](https://github.com/OWNER/REPO/releases)
```

### Downloads
```markdown
[![Downloads](https://img.shields.io/github/downloads/OWNER/REPO/total)](https://github.com/OWNER/REPO/releases)
```

### Release Count
```markdown
[![Releases](https://img.shields.io/github/v/release/OWNER/REPO?include_prereleases&label=releases)](https://github.com/OWNER/REPO/releases)
```

---

## 🔧 Repository Stats

### Repo Size
```markdown
[![Repo Size](https://img.shields.io/github/repo-size/OWNER/REPO)](https://github.com/OWNER/REPO)
```

### Code Size
```markdown
[![Code Size](https://img.shields.io/github/languages/code-size/OWNER/REPO)](https://github.com/OWNER/REPO)
```

### Last Commit
```markdown
[![Last Commit](https://img.shields.io/github/last-commit/OWNER/REPO)](https://github.com/OWNER/REPO/commits)
```

### Issues
```markdown
[![Issues](https://img.shields.io/github/issues/OWNER/REPO)](https://github.com/OWNER/REPO/issues)
```

---

## 📝 Example README Section

```markdown
# SonicBuilder

[![Build Appendix C](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=main&label=Build&logo=github)](https://github.com/OWNER/REPO/actions/workflows/build-appendixC.yml)
[![Release](https://img.shields.io/github/v/release/OWNER/REPO?label=Version)](https://github.com/OWNER/REPO/releases/latest)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/OWNER/REPO/total)](https://github.com/OWNER/REPO/releases)

Professional PDF manual generator for 2014 Chevy Sonic LTZ Android head unit installation.

## Features
- ✅ Auto-indexed PCB photos and I²S tap diagrams
- ✅ QR galleries for installer reference
- ✅ Professional dark-mode PDFs
- ✅ Complete CI/CD automation
- ✅ Certificate of Authenticity generation

## Quick Start
\`\`\`bash
make all VERSION=v2.0.9
\`\`\`

## Documentation
See [Complete Integration Guide](docs/COMPLETE_INTEGRATION_GUIDE.md)
```

---

## 🚀 Advanced Shields

### Dynamic Version from File
```markdown
![Version](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/OWNER/REPO/main/package.json&query=$.version&label=Version)
```

### Workflow Status with Event
```markdown
![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?event=push)
```

### Multiple Branches
```markdown
<!-- Main branch -->
![Main](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=main&label=main)

<!-- Dev branch -->
![Dev](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=dev&label=dev)
```

---

## 🎯 Recommended Badge Set

**Minimal (3 badges):**
```markdown
[![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=main)](https://github.com/OWNER/REPO/actions)
[![Version](https://img.shields.io/github/v/release/OWNER/REPO)](https://github.com/OWNER/REPO/releases)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
```

**Standard (5 badges):**
```markdown
[![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=main&label=Build)](https://github.com/OWNER/REPO/actions)
[![Release](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/release-appendixC.yml?label=Release)](https://github.com/OWNER/REPO/actions)
[![Version](https://img.shields.io/github/v/release/OWNER/REPO)](https://github.com/OWNER/REPO/releases)
[![Downloads](https://img.shields.io/github/downloads/OWNER/REPO/total)](https://github.com/OWNER/REPO/releases)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
```

**Complete (8 badges):**
```markdown
[![Build](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/build-appendixC.yml?branch=main)](https://github.com/OWNER/REPO/actions)
[![Release](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/release-appendixC.yml)](https://github.com/OWNER/REPO/actions)
[![Enricher](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/release-notes-enricher.yml)](https://github.com/OWNER/REPO/actions)
[![CoA](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/coa-on-release.yml)](https://github.com/OWNER/REPO/actions)
[![Version](https://img.shields.io/github/v/release/OWNER/REPO)](https://github.com/OWNER/REPO/releases)
[![Downloads](https://img.shields.io/github/downloads/OWNER/REPO/total)](https://github.com/OWNER/REPO/releases)
[![Last Commit](https://img.shields.io/github/last-commit/OWNER/REPO)](https://github.com/OWNER/REPO/commits)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
```

---

## 📖 Reference

- **Shields.io:** https://shields.io/
- **GitHub Badges:** https://shields.io/category/build
- **Custom Badges:** https://shields.io/badges/static-badge

---

## ✅ Setup Steps

1. Choose badge style from above
2. Replace `OWNER/REPO` with your repository
3. Copy markdown snippet
4. Paste into your README.md (usually at the top after the title)
5. Commit and push
6. Badges will update automatically!

**Your README will look professional with live CI/CD status!** 🎉
