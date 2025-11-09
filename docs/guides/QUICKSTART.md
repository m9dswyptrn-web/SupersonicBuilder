# QUICKSTART.md

Your fastest path to a working SonicBuilder with GitHub automation.

## 1) Verify the toolchain
```bash
make verify
```

## 2) Choose your setup path

### Fast setup (recommended)
1. Open **SETUP_PROJECTS_AUTOMATION.md**
2. Follow the 7 short steps
3. Validate and push:
   ```bash
   make validate_setup
   git add -A && git commit -m "chore: projects wired" && git push
   ```

### Complete setup
1. Open **COMPLETE_GITHUB_SETUP.md**
2. Follow the TL;DR section
3. Test & verify with:
   ```bash
   make demos
   ```

## 3) Release (optional)
```bash
make release              # default patch bump; see README_RELEASE_BUMP.md
```

## 4) Where to look
- PDFs: output/
- Bundles: dist/
- GitHub -> Actions for verify/demos artifacts
- GitHub -> Projects for Kanban auto-triage
