# SonicBuilder Preflight & Artifact Checks

**Purpose:** Pre-deployment validation to catch issues before pushing to GitHub

---

## 🔎 Preflight Checks

### What It Does

The preflight target verifies:
- ✅ Git is installed
- ✅ Python 3 is installed
- ✅ Git user identity is configured
- ✅ Environment is ready for deployment

### Usage

```bash
make -f Makefile.preflight preflight
```

**Output:**
```
🔎 Preflight: checking required tools and files...
✅ Preflight OK
```

### Auto-Configuration

If git identity is not set, preflight automatically configures:
- `user.name` = "SonicBuilder AutoDeploy"
- `user.email` = "autodeploy@users.noreply.github.com"

---

## 📦 Artifact Inventory

### What It Does

Lists all PDFs and checksums in:
- `out/` directory (build outputs)
- `dist/` directory (release artifacts)

### Usage

```bash
make -f Makefile.preflight artifact-inventory
```

**Output:**
```
📦 Artifact inventory (out/ and dist/):
-rw-r--r-- 1 user user  11K Oct 29 17:49 out/field_cards_four_up.pdf
-rw-r--r-- 1 user user  12K Oct 29 17:49 out/field_cards_two_up.pdf
-rw-r--r-- 1 user user  28K Oct 29 17:19 out/NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf
...
```

---

## 🚀 Integration with Deployment

### Recommended Workflow

```bash
# 1. Run preflight
make -f Makefile.preflight preflight

# 2. Check artifacts
make -f Makefile.preflight artifact-inventory

# 3. Test connection
make dryrun

# 4. Deploy
make ship
```

### Automated Preflight

The `make ship` and `make docs` targets now automatically run preflight checks first:

```makefile
ship: preflight deploy verify notify
docs: preflight build_dark deploy verify notify
```

---

## ✅ Preflight Checklist

Before deploying, verify:

- [ ] `make -f Makefile.preflight preflight` succeeds
- [ ] Git identity configured
- [ ] Python 3 available
- [ ] Required PDFs exist in `out/` or `dist/`
- [ ] `make dryrun` shows correct GitHub remote
- [ ] GH_TOKEN configured in Replit Secrets

---

## 🔧 Troubleshooting

### "git missing"

**Install git:**
```bash
sudo apt-get update
sudo apt-get install git
```

### "python3 missing"

**Install Python:**
```bash
sudo apt-get update
sudo apt-get install python3
```

### Git identity not set

**Preflight auto-fixes this**, but you can manually set:
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### No artifacts found

**Build docs first:**
```bash
make build-all
```

Then check again:
```bash
make -f Makefile.preflight artifact-inventory
```

---

## 📋 Makefile.preflight Reference

### Available Targets

| Target | Description |
|--------|-------------|
| `preflight` | Verify git, python3, git identity |
| `artifact-inventory` | List all PDFs and checksums |

### File Location

The preflight targets are in a standalone file:
- **Makefile.preflight** - Can be used independently

### Include in Main Makefile (Optional)

To integrate into main Makefile:

```makefile
-include Makefile.preflight
```

Then use directly:
```bash
make preflight
make artifact-inventory
```

---

## ✨ Benefits

### Pre-Deployment Validation
- ✅ Catch environment issues early
- ✅ Verify tools before pushing
- ✅ Auto-configure git identity

### Artifact Verification
- ✅ Confirm PDFs exist before release
- ✅ Check file sizes
- ✅ Verify build outputs

### CI/CD Integration
- ✅ Can be added to workflows
- ✅ Validates CI environment
- ✅ Documents artifact state

---

## 🎯 Quick Reference

```bash
# Preflight only
make -f Makefile.preflight preflight

# Artifacts only
make -f Makefile.preflight artifact-inventory

# Both
make -f Makefile.preflight preflight artifact-inventory

# Full deployment with preflight
make ship
```

---

**Use preflight checks before every deployment to ensure a smooth release!** ✅
