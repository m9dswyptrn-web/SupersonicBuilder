# 🚀 Quick Deploy - Supersonic v4 Ultimate Edition

Deploy your Supersonic v4 Ultimate Edition to **ChristopherElgin/SonicBuilderSupersonic** in minutes!

---

## ⚡ One-Command Deploy

```bash
python3 deploy_to_github.py \
  --owner ChristopherElgin \
  --repo SonicBuilderSupersonic \
  --version v1.0.0 \
  --public \
  --fresh
```

**What this does:**
- ✅ Fresh git init (removes old 3.7GB history → ~300MB)
- ✅ Sets up Git LFS for audio/image assets
- ✅ Commits all files
- ✅ Creates GitHub repository (if using `gh` CLI)
- ✅ Pushes code and creates v1.0.0 release
- ✅ Ready for GitHub Pages deployment

---

## 📋 Prerequisites

### macOS

```bash
brew install git git-lfs gh
git lfs install
gh auth login   # follow prompts (HTTPS + device code easiest)
```

### Windows

```bash
winget install Git.Git
winget install GitHub.GitLFS
winget install GitHub.cli
git lfs install
gh auth login
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y git git-lfs
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list
sudo apt update && sudo apt install -y gh
git lfs install
gh auth login
```

---

## 🎯 Deployment Steps

### Step 1: Download Project

Download this Replit project to your local machine:
- Click "Download as ZIP" in Replit
- Extract to a local directory

### Step 2: Navigate to Project

```bash
cd /path/to/SonicBuilderSupersonic
```

### Step 3: Deploy!

**Initial deployment (v1.0.0 with fresh git init):**

```bash
python3 deploy_to_github.py \
  --owner ChristopherElgin \
  --repo SonicBuilderSupersonic \
  --version v1.0.0 \
  --public \
  --fresh
```

**Subsequent releases (incremental updates):**

```bash
python3 deploy_to_github.py \
  --owner ChristopherElgin \
  --repo SonicBuilderSupersonic \
  --version v1.1.0 \
  --public
```

### Step 4: Generate Voice Packs

After deployment, generate remaining voice packs:

```bash
make -f make/ControlCore.mk ai-voicepacks
```

---

## 🔧 Advanced Options

### Deploy Private Repository

```bash
python3 deploy_to_github.py \
  --owner ChristopherElgin \
  --repo SonicBuilderSupersonic \
  --version v1.0.0 \
  --private \
  --fresh
```

### Deploy Without Git LFS

```bash
python3 deploy_to_github.py \
  --owner ChristopherElgin \
  --repo SonicBuilderSupersonic \
  --version v1.0.0 \
  --public \
  --fresh \
  --no-lfs
```

### Custom Commit Message

```bash
python3 deploy_to_github.py \
  --owner ChristopherElgin \
  --repo SonicBuilderSupersonic \
  --version v1.0.0 \
  --public \
  --fresh \
  --message "feat: Supersonic v4 Ultimate with all features"
```

### Update Last Known Good Tag

```bash
git tag -f lkg && git push -f origin lkg
```

---

## 📦 What Gets Deployed

### Supersonic v4 Ultimate Edition Features

✅ **LED Status Banner System**
- 4 animated GIF indicators (online/warn/fail/system)
- Auto-updating GitHub workflow
- Last Known Good recovery links

✅ **Voice Pack Management (5 Professional Packs)**
- Commander (185 WPM) - Included
- AIOps (205 WPM) - Included  
- FlightOps (170 WPM) - Generate on demand
- IndustrialOps (155 WPM) - Generate on demand
- ArcadeHUD (215 WPM) - Generate on demand

✅ **AI Mission Console**
- Interactive TUI for workflow dispatch
- Pipeline status monitoring
- Quick LKG access

✅ **Build Automation**
- 54 Make targets
- Complete voice/LED/console integration
- Self-healing asset generation

### Repository Size
- **Before:** 4.0GB (bloated git history)
- **After:** ~300MB (clean deployment with LFS)

---

## 🎯 Post-Deployment

After successful deployment:

### 1. Enable GitHub Pages

```
Settings → Pages → Branch: main / Folder: /docs → Save
```

Wait 2-5 minutes, then visit:
```
https://christopherelgin.github.io/SonicBuilderSupersonic/
```

### 2. Verify Workflows

Go to Actions tab and check:
- Status Banner Update workflow exists
- Workflows have proper permissions (Settings → Actions → General → Read & Write)

### 3. Generate Remaining Voice Packs

```bash
make -f make/ControlCore.mk ai-voicepacks
```

### 4. Test AI Console

```bash
make -f make/ControlCore.mk ai-console
```

### 5. Protect Main Branch

```
Settings → Branches → Add branch protection rule → main
```

Enable:
- Require pull request reviews
- Require status checks
- Include administrators

---

## 🚀 Makefile Shortcut (Optional)

Add to your root `Makefile` for quick deploys:

```makefile
# Makefile at repo root
ship:
	python3 deploy_to_github.py --owner ChristopherElgin --repo SonicBuilderSupersonic --version v1.0.0 --public --fresh

ship-update:
	python3 deploy_to_github.py --owner ChristopherElgin --repo SonicBuilderSupersonic --version v1.1.0 --public

.PHONY: ship ship-update
```

Then simply run:
```bash
make ship          # Initial deployment
make ship-update   # Update deployment
```

---

## 🐛 Troubleshooting

### "git-lfs not found"

**macOS:** `brew install git-lfs`  
**Windows:** `winget install GitHub.GitLFS`  
**Linux:** `sudo apt install git-lfs`

Then: `git lfs install`

### "gh not found"

**macOS:** `brew install gh`  
**Windows:** `winget install GitHub.cli`  
**Linux:** Follow instructions above

Then: `gh auth login`

### Script shows "⚠ git-lfs not installed"

The script will continue without LFS, but your repo will be larger. Install git-lfs and re-run with `--fresh`.

### "Repository already exists"

If deploying to existing repo, omit `--fresh` flag:

```bash
python3 deploy_to_github.py \
  --owner ChristopherElgin \
  --repo SonicBuilderSupersonic \
  --version v1.1.0 \
  --public
```

### LFS Quota Exceeded

Free GitHub accounts get 1GB LFS storage/month. Options:
1. Upgrade to GitHub Pro
2. Use `--no-lfs` flag (repo will be larger)
3. Reduce number of voice packs deployed

---

## 📚 Additional Documentation

- **DEPLOYMENT_GUIDE.md** - Complete deployment reference
- **docs/LED_VOICE_AI_CONSOLE_INTEGRATION.md** - Feature integration guide
- **docs/README_Supersonic_v4_Ultimate.md** - v4 documentation

---

## ✅ Deployment Checklist

Before deploying:

- [ ] Downloaded project to local machine
- [ ] Installed prerequisites (git, git-lfs, gh)
- [ ] Authenticated with GitHub (`gh auth login`)
- [ ] Navigated to project directory
- [ ] Ready to run deployment script

After deploying:

- [ ] Repository created on GitHub
- [ ] Tag v1.0.0 created
- [ ] Release published
- [ ] GitHub Pages enabled
- [ ] Workflows verified
- [ ] Voice packs generated
- [ ] AI Console tested
- [ ] Main branch protected

---

## 🎉 Success!

Your Supersonic v4 Ultimate Edition will be live at:

- **Repository:** https://github.com/ChristopherElgin/SonicBuilderSupersonic
- **Releases:** https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases
- **Pages:** https://christopherelgin.github.io/SonicBuilderSupersonic/

**All systems GO!** 🚀🎉🔒

---

_© 2025 Supersonic Systems — "Fast is fine. Supersonic is better."_
