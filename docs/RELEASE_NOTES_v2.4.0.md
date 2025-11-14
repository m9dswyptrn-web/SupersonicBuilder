# Supersonic v2.4.0 – Deployment-Ready Release

## Highlights

- **Full health monitoring stack**
  - Port + file health probes (`./rs health`)
  - Metrics generator & badges (`./rs metrics`, `./rs metrics-plus`)
  - Log rotation & compression

- **Autonomy + Self-Heal Enhancements**
  - `./rs guard` loop with automatic restart on failure
  - Watchdog for RAM/CPU with webhook + email hooks
  - Doctor/Doctor-Plus orchestration (`./rs doctor`, `./rs doctor-plus`)

- **Car Install Mode (Chevy Sonic Integration)**
  - `./rs car-install on|off` – turn car mode on or off
  - Sonic install checklist (`./rs sonic-checklist show|export`)
  - Car metrics exporter (`./rs car-metrics` → `metrics/car_mode.json`)

- **Android 15 Board Map Integration**
  - Board photo pipeline ready for EOENKK Android 15 head unit
  - Placeholder doc: `docs/sonic/android15_board/BOARD_MAP_PLACEHOLDER.md`
  - CLI helper: `android15_board_setup.py` (used by build tools)

- **Docs & GitHub Readiness**
  - Expanded `README.md` & `replit.md`
  - Added `GITHUB_DEPLOYMENT.md` for deployment playbook
  - Security audit: .gitignore, env handling, basic secret hygiene

## New Commands (v2.4.0)

### Monitoring
- `./rs health`          – Probe ports/files → `logs/health.json`
- `./rs metrics`         – Refresh badges from health data
- `./rs metrics-plus`    – Full pipeline: health → metrics → Pages sync
- `./rs diag`            – Full diagnostic
- `./rs doctor-plus`     – Repo check + health + car install summary

### Autonomy + Guard
- `./rs launch-all`      – Start status server + shell bridge + board
- `./rs guard 5`         – 5s guard loop, auto heal on failure

### Car Install
- `./rs car-install on`  – Enable car install mode
- `./rs car-install off` – Disable car install mode
- `./rs sonic-checklist show`   – View Sonic install checklist
- `./rs sonic-checklist export` – Export to `metrics/sonic_checklist.json`
- `./rs car-metrics`     – Export car profile metrics

## GitHub Pages

- Metrics & health artifacts prepared for publication on GitHub Pages.
- See `.github/workflows/pages-metrics.yml` for automation.
- Default path: `gh-pages` branch → `/` site root.

## Upgrade Notes

- Existing configs are preserved wherever possible.
- Version file: `version.txt` set to `2.4.0`.
- If upgrading from pre-2.x:
  - Run `./rs doctor-plus` once after pulling.
  - Review `GITHUB_DEPLOYMENT.md` before first release.
