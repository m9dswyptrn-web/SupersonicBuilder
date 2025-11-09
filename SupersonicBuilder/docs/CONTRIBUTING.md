# Contributing to SonicBuilder

Welcome! This repo builds printable install manuals for the **2014 Chevy Sonic LTZ Android head unit**.  
We use a Python + ReportLab toolchain with optional SVG rasterization and a flexible annotations system.

---

## 💻 Quick Start

1) **Install Python 3.11+**  
2) **Install dependencies** (includes extras used by our build packs):
   ```bash
   pip install -r requirements.txt || true
   pip install -r requirements.extras.txt || true
   pip install reportlab pypdf pdfrw pillow cairosvg watchdog
   ```

3) **Verify the project** (fast preflight + optional smoke build):
   ```bash
   make verify           # THEME=dark by default
   THEME=light make verify
   ```

4) **Build & package**:
   ```bash
   make build            # renders output/sonic_manual_dark.pdf (or light)
   make post             # versioned file + field cards + Two-Up PRO
   make package          # bundles output/ -> dist/
   make demos            # matrix of dark/light + modes, then bundle
   ```

> Replit users: the Run button can be set to `make build_release && python serve_build.py --root output --port 8765`.

---

## 🌲 Repo Layout (key pieces)

- `scripts/main_glue.py` — entrypoint (handles `--theme`, modes, manifest loop)
- `scripts/render_pages.py` — page drawing helpers (frame, images, tables)
- `scripts/render_pages_modes.py` — **mode-aware** photo page
- `templates/theme.sonic.json` — dark annotation theme
- `templates/theme.sonic.light.json` — light annotation theme
- `templates/annotations.sonic.json` — annotations (labels/arrows/boxes)
- `assets/` — images, SVGs, and tables (e.g., `tables/speakers.csv`)
- `config/manual.manifest.json` — page order & assets manifest

---

## 🧭 Build Modes & Themes

- **Themes:** `--theme dark|light` (picked by `scripts/main_glue.py`)
- **Annotation modes:** `ANNOTATION_MODE=basic|styled|themed|photo-only`  
  Set via environment variable at build time.

Examples:
```bash
ANNOTATION_MODE=photo-only make build
THEME=light ANNOTATION_MODE=themed make build
```

---

## 🏷️ Branches & Commits

- Branch from `main`:
  - feature: `feat/<short-topic>`
  - fix: `fix/<bug-name>`
  - docs: `docs/<area>`

- Commit style (conventional-ish):
  - `feat(annotations): add arrow styling`
  - `fix(build): ensure cairosvg error bubbles up`
  - `docs: update README with demos target`

Open a PR when ready; CI will run *verify + demos* and upload artifacts.

---

## ✅ PR Checklist

- [ ] `make verify` passes (dark & light if relevant)
- [ ] New/edited JSONs are valid (manifest, annotations, themes)
- [ ] Assets added to `assets/` and referenced in manifest
- [ ] `make demos` produces expected PDFs (spot-check `output/`)
- [ ] Screenshots or notes added to PR description for reviewers

---

## 🧪 CI

GitHub Actions:
- Runs `make verify` for **dark** and **light**
- Runs `make demos` and uploads `/output/**` and `/dist/**` as artifacts
- Optional `release` workflow: on tag `v*`, builds and attaches ZIP in Releases

Badge (update with your repo path):
```md
![SonicBuilder CI](https://github.com/<YOUR_ORG>/<YOUR_REPO>/actions/workflows/sonicbuilder-ci.yml/badge.svg)
```

---

## 🖼️ Assets & Annotations Guidelines

- Place images/SVGs under `assets/`. Keep names descriptive.
- For **SVGs**, install `cairosvg` to rasterize automatically; otherwise they're skipped.
- Update tables (like speakers) in `assets/tables/*.csv`.
- **Annotations** (`templates/annotations.sonic*.json`):
  - Coordinates are **normalized** `0..1` inside the inner panel.
  - Types: `"label"`, `"arrow"`, `"box"`
  - Per-item styling (v2): `arrow_color`, `box_fill`, `text_color`, `line_width`, `font_size`, etc.
  - **Theming** fills styles automatically via `templates/theme.sonic.json` (dark) or `.light.json` (light).

Tip: Use `overlays/*_grid.jpg` to estimate coordinates, or run:
```bash
python scripts/annotation_coords_helper.py --x_px 350 --y_px 420
```

---

## 🧰 Troubleshooting

- **"PDF didn't change"**
  - Use versioned files from `make post`, or open `/output/*.pdf?ts=<time>`
  - Ensure `scripts/main_glue.py` is the entrypoint used by your run command
  - Confirm you edited the right manifest/themes/annotations path

- **Missing SVGs in output**
  - Install `cairosvg` and re-run `make setup` or reinstall requirements

- **Two-Up PRO not generating**
  - Install `pdfrw`; verify `scripts/impose_two_up_pro.py` exists

- **Fonts/Alpha errors on Replit**
  - Ensure nix packages include `cairo`, `pango`, `freetype`, `fontconfig`

---

## 🚀 Release

1) Increment your version in release notes (if any).
2) Tag and push:
   ```bash
   git tag vX.Y.Z && git push origin vX.Y.Z
   ```
3) The `release` workflow builds and attaches `dist/*.zip` automatically.

---

## 🙌 Thanks

This project is powered by a dark/light page frame, annotation theming, and a robust Makefile pipeline.  
Run `make demos` to quickly QA everything before merging. Happy building!
