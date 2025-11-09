# COMPLETE_GITHUB_SETUP_v2.md

**Goal:** one-pass setup for GitHub Projects + CI + automated releases for SonicBuilder.

---

## TL;DR Quickstart (copy/paste)
Replace placeholders **<YOUR_ORG>** and **<YOUR_REPO>**:
```bash
# 0) Login & deps
gh auth login
pip install -r requirements.txt || true
pip install -r requirements.extras.txt || true
pip install reportlab pypdf pdfrw pillow cairosvg watchdog requests || true

# 1) Sync default labels
export GITHUB_TOKEN=ghp_yourPATwithRepoScope   # repo scope
python scripts/setup_labels.py --repo <YOUR_ORG>/<YOUR_REPO> --labels .github/labels.yml

# 2) Create the Project board (prints URL with number)
bash scripts/setup_project.sh <YOUR_ORG> "Sonic Kanban"

# 3) Update .github/project_config.json → "project_url": "https://github.com/orgs/<YOUR_ORG>/projects/<PROJECT_NUMBER>"
#    Ensure Status options exist: Backlog, In Progress, Review, Done

# 4) (Optional) Prefill saved views (Bugs/Features/Ready for Review/Backlog)
bash scripts/setup_project_views.sh .github/project_views.json

# 5) Commit and push
git add -A && git commit -m "docs: GitHub Projects wired + views" || true
git push

# 6) Verify + demo builds (CI parity)
make verify && make demos
```

---

## What you get
- **CI**: `sonicbuilder-ci.yml` (verify + demos), `project-auto.yml` (auto-triage), `version-badge.yml` (badge), optional `release.yml` (tagged releases)
- **Repo hygiene**: Issue templates + Labels
- **Projects**: Auto add items + label→Status mapping + saved views
- **Releases**: `make release` bumps version, tags, pushes; Actions publishes artifacts

---

## Release workflow
**Recommended flow**
```bash
# Patch bump (default). Also: make minor | make major | make release PRE=rc.1
make release
```
This updates `VERSION`, creates tag `vX.Y.Z`, pushes.  
If `release.yml` is enabled, a GitHub **Release** will be created with your ZIP bundle.  
The **version badge** updates automatically.

**Manual build alternative**
```bash
make build_release && make package
# Upload dist/*.zip manually if desired
```

---

## Replit run command (keep CI parity)
In `.replit`:
```ini
run = "make build_release && python serve_build.py --root output --port 8765"
env = ["THEME=dark","ANNOTATION_MODE=themed","WM_MODE=footer","WM_TEXT=LTZ RR2 GRZ","WM_FOOTER_POS=right","WM_OPACITY=0.55"]
```

---

## Troubleshooting
- **Project item didn’t get a Status** → Confirm project URL in `.github/project_config.json` and ensure the **Status** field has the options listed above.
- **Labels missing** → Re-run the label sync step.
- **Badge not updating** → Ensure `badges/version.json` is committed and `version-badge.yml` ran.
- **PDFs look unchanged** → Make sure you’re opening the latest in `/output/` or use `make post` to version filenames.
