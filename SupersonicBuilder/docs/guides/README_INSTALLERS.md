# SonicBuilder Installation Scripts

This directory contains installer scripts for SonicBuilder's secure suite.

## Available Installers

### 1. install_secure_suite.sh (RECOMMENDED)
**One-shot installer** for the complete secure suite.

```bash
bash install_secure_suite.sh
# or
make secure-install
```

Installs:
- Security Suite (Semgrep + Hardening)
- Secure Build System (backup + restore)
- Monitoring Tools (Pages verification)
- Badge Infrastructure (8 endpoints)

### 2. autofill_github_info.sh
Auto-fills GitHub username and repository name in all files.

```bash
bash autofill_github_info.sh
# or
make autofill-github
```

### 3. install_addons.sh
Installs optional add-ons and enhancements.

```bash
bash install_addons.sh
```

## Quick Start

1. Install the secure suite:
   ```bash
   make secure-install
   ```

2. Configure GitHub info:
   ```bash
   make autofill-github
   ```

3. Test locally:
   ```bash
   make pages-serve
   ```

4. Deploy:
   - Click "Publish" in Replit → Select "Autoscale"
   - Or push to GitHub for Pages deployment

## Documentation

- [INSTALL_GUIDE.md](docs/INSTALL_GUIDE.md) - Complete installation guide
- [README.md](README.md) - Project overview
- [docs/guides/](docs/guides/) - Additional guides

