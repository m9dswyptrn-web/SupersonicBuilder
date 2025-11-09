# SETUP_PROJECTS_AUTOMATION.md

This guide is the quick, focused version Replit is asking for: GitHub Projects + automation.
It assumes you already committed the provided packs (labels, issue templates, projects, views, CI, release).

---

## 1) Create the Project and wire the URL
```bash
gh auth login
bash scripts/setup_project.sh <YOUR_ORG> "Sonic Kanban"
# Copy the printed URL: https://github.com/orgs/<YOUR_ORG>/projects/<PROJECT_NUMBER>

# Paste it into:
#   .github/project_config.json  ->  "project_url": "<PASTE_URL>"
```

Status field: Ensure your board has options: Backlog, In Progress, Review, Done.

---

## 2) Prefill Saved Views (optional but recommended)
```bash
# project_views.json already includes Bugs / Features / Ready for Review / Backlog
bash scripts/setup_project_views.sh .github/project_views.json
```

---

## 3) Sync Labels (if you have not already)
Choose one approach:

Python (REST)
```bash
export GITHUB_TOKEN=ghp_yourPATwithRepoScope   # repo scope
python scripts/setup_labels.py --repo <YOUR_ORG>/<YOUR_REPO> --labels .github/labels.yml
```

GitHub CLI
```bash
gh auth login
bash scripts/setup_labels_gh.sh <YOUR_ORG>/<YOUR_REPO>
```

Labels provided: bug, feature, chore, docs, build, good first issue.

---

## 4) Enable the Automation Workflows
Just commit and push the workflow files:
- .github/workflows/project-auto.yml  -> auto-add Issues/PRs to the board and set Status from labels
- .github/workflows/sonicbuilder-ci.yml -> verify + demos; uploads PDFs & bundles
- .github/workflows/version-badge.yml   -> updates badges/version.json
- .github/workflows/release.yml (optional) -> builds and attaches ZIP on tag v*

---

## 5) Verify it works
1. Open a new Issue; label it feature -> it appears in Backlog.
2. Add ready for review label -> it moves to Review.
3. Push to GitHub -> Actions runs verify + demos and uploads artifacts.
4. Run a release:
   ```bash
   make release        # default = patch; also: make minor | make major | make release PRE=rc.1
   ```
   The Release workflow (if enabled) publishes ZIPs; the Version badge updates.

---

## 6) Replit run command (keep parity with CI)
In .replit:
```ini
run = "make build_release && python serve_build.py --root output --port 8765"
env = ["THEME=dark","ANNOTATION_MODE=themed","WM_MODE=footer","WM_TEXT=LTZ RR2 GRZ","WM_FOOTER_POS=right","WM_OPACITY=0.55"]
```

---

## 7) Troubleshooting
- Item added but Status missing -> Confirm project URL in .github/project_config.json and that the Status field exists with the options above.
- Labels not mapping -> Check .github/project_config.json -> label_to_status keys match your labels exactly.
- CI did not upload PDFs -> See Actions logs for the demos step; artifacts appear under job summary when successful.
- Version badge not changing -> Ensure badges/version.json exists and the version-badge workflow ran.
