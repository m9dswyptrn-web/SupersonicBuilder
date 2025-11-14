# 2014 Chevy Sonic LTZ — Automotive Wiring Manual Generator

## Overview
This project generates comprehensive PDF installation manuals for automotive wiring and integration, specifically for a 2014 Chevrolet Sonic LTZ. It supports an Android head unit, Maestro RR2/GM2 primary gateway, and G-RZ overlay system. The primary purpose is to create professional dark and light-themed PDF manuals from YAML configuration files, including detailed wiring diagrams, pinout documentation, and parts lists. The system aims to streamline the creation and distribution of complex automotive installation documentation through automation and a web interface.

## User Preferences
None documented yet. This is a new project.

## Recent Integrations (v2.4.0)

### Supersonic Snapshot Engine (November 14, 2025)
**Timestamped Snapshot System for Logs, Metrics, and Documentation**

Creates immutable snapshots of critical system state for historical tracking and debugging.

**Usage:**
```bash
# Via RS CLI (recommended)
./rs snapshot

# Or directly
./rs-snapshot
python3 tools/snapshot.py
```

**Features:**
- Timestamped snapshot directories: `snapshots/snapshot-YYYYmmdd-HHMMSS/`
- Captures: logs/, metrics/, docs/sonic/, version.txt
- Creates snapshot.json metadata for each snapshot
- Maintains index.jsonl journal for snapshot history
- Idempotent and safe to run multiple times

**Files:**
- `tools/snapshot.py` - Main snapshot engine (120 lines)
- `rs-snapshot` - Standalone wrapper script
- `rs` - Integrated as `./rs snapshot` command (lines 466-469)
- `snapshots/index.jsonl` - Snapshot history journal

**Typical Workflow:**
```bash
./rs health         # Generate health data
./rs metrics        # Refresh metrics
./rs snapshot       # Capture snapshot
```

### Console Bridge System (November 13, 2025)
**Bidirectional Console-to-Shell-Root Command Executor**

Allows execution of ANY shell command from either the Replit Agent console OR the repo shell root, providing seamless bidirectional communication.

**Usage:**
```bash
# Single command mode
./rs console "cat version.txt"
./rs console "git status --short"
./rs console "ls -la docs/"

# Interactive mode (REPL)
./rs console
# Then type commands interactively, 'exit' to quit
```

**Features:**
- Real-time output streaming with colored status indicators
- Command logging to `logs/console_bridge.log`
- Graceful error handling and exit code reporting
- Interactive REPL mode with command history
- Full integration with RS CLI

**Files:**
- `tools/console_bridge.py` - Main console bridge script (150 lines)
- `rs` - Integrated console command (lines 522-529)
- `logs/console_bridge.log` - Command history and audit trail

### v2.4.0 Release Bundle (November 13, 2025)
**GitHub Deployment Preparation**

Complete release bundle generation system for GitHub deployment with CI/CD workflows.

**Generated Files:**
- `docs/RELEASE_NOTES_v2.4.0.md` - Comprehensive release notes
- `docs/sonic/android15_board/BOARD_MAP_PLACEHOLDER.md` - Board mapping guide
- `.github/workflows/release-preflight.yml` - CI preflight checks
- `.github/workflows/pages-metrics.yml` - GitHub Pages automation
- `version.txt` - Updated to 2.4.0

**Generator:** `tools/gen_release_bundle_v2_4_0.sh` (idempotent, safe to re-run)

## System Architecture

### UI/UX Decisions
The system features a "Supersonic Commander" web control panel (http://localhost:5000) for managing operations, offering live settings management, streaming consoles with real-time output, and a system telemetry dashboard. It includes thematic voice packs for audible feedback. Generated PDFs offer both dark and light themes, interactive bookmarks, QR code generation, version/timestamp footers, and printable job cards with signal icons. Diagrams utilize a DUAL-DIAGRAM SYSTEM, combining vector diagrams with real installation photos.

### Technical Implementations
- **PDF Generation**: Uses `main.py` to generate PDFs from YAML configurations, supporting SVG vector graphics (CairoSVG) and multi-image layouts.
- **Autonomy Stack**: Core services (`autonomy_manager.py`, `status_server.py`, `shell_bridge.py`, `healthboard.py`) orchestrate system health APIs, secure shell command execution, and live dashboards.
- **Release Automation System**: Includes scripts for version management (`tools/version_tag.sh`), local release creation (`tools/make-release-local.sh`), and an automated nightly CI/CD workflow (`.github/workflows/ultra-nightly.yml`).
- **Monitoring & Auto-Healing**: Features a unified `rs` CLI for health probes, metrics generation, log rotation, and alert notifications (Discord, email). `tools/zap_heal.py` provides lock-protected auto-healing for critical services, and `tools/watchdog_monitor.py` monitors the file system.
- **Configuration**: Manuals are generated from 12 YAML configuration sections.
- **Asset Handling**: `AssetResolver` for robust image rendering (SVG, PNG, JPG) with auto-optimization.
- **GitHub Pages Deployment**: `supersonic_deploy_pages.py` copies assets to the `/docs` directory for publishing.
- **Car Profile System**: Manages vehicle-specific data (`profiles/sonic_2014.json`) and provides tools for installation checklists, mode toggling, and firmware profiles.
- **Android 15 Board Setup**: Extracts and documents circuit board photos, generating a hardware atlas and organizing assets.

### System Design Choices
- **Modular Design**: Core functionalities are separated into Python modules.
- **Data-Driven Configuration**: YAML files define manual content for easy updates.
- **Three-Phase Integration**: Foundation (isolated tools) → Wiring (conditional integration) → Validation (testing).
- **Port Strategy**: Dedicated ports for Status (6000), Bridge (6800), Healthboard (8008), and Badge Server (7000).
- **Lock-Based Protection**: PID files prevent duplicate instances of monitors.
- **DRY-RUN Mode**: All release tools support dry-run for safe testing.
- **Secret Guards**: GitHub operations require `GITHUB_TOKEN`, and optional secrets for notifications.
- **Version Control Integration**: Automated version management via `version.txt` and `CHANGELOG.md`.
- **Security**: Path traversal prevention, backup validation, token authentication, and secure secret storage.
- **Hotkeys Widget**: Enhanced healthboard with interactive dashboard, real-time latency sparklines, theme toggles, and snapshot system.

## External Dependencies

### Python Packages
- **PDF Generation**: `reportlab`, `PyPDF2`, `PyYAML`, `Pillow`, `svglib`, `cairosvg`, `qrcode[pil]`, `tinycss2`, `cssselect2`.
- **Autonomy Stack**: `Flask`, `psutil`.
- **Release Automation**: `fastapi`, `uvicorn`.
- **Monitoring**: `watchdog`, `pyserial`.

### System Dependencies
- `cairo`
- `pkg-config`
- `zip`, `unzip`

### Optional Dependencies
- **OpenAI API**: For `supersonic_doc_updater.py`.