# SupersonicBuilder

**Comprehensive PDF Installation Manual Generator for Automotive Wiring Projects**

## Overview

SupersonicBuilder is a fully autonomous PDF installation manual generation system specifically designed for automotive wiring and integration projects. The flagship implementation targets a 2014 Chevrolet Sonic LTZ with EOENKK Android 15 head unit integration.

### Key Features

- **Professional PDF Generation**: Dark/light themed manuals with vector diagrams and installation photos
- **Autonomy Stack**: Self-healing monitoring infrastructure with health dashboards
- **Car Profile System**: Complete vehicle/hardware profiles with installation tracking
- **Android 15 Board Documentation**: 82 high-resolution circuit board photos with hardware atlas
- **Release Automation**: CI/CD workflows with badge generation and GitHub Pages deployment
- **RS CLI**: Unified command interface for all operations

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/m9dswyptrn-web/SupersonicBuilder.git
cd SupersonicBuilder

# Install dependencies (handled automatically on Replit)
# For local: pip install -r requirements.txt
```

### Generate a Manual

```bash
# Manual generation (interactive)
python3 main.py

# Production pack builder
python3 builder.py
```

### Autonomy Stack

```bash
# Start all services
make -f rs.mk start

# Or use RS CLI
./rs start

# Health check
./rs doctor

# View dashboard
# Navigate to http://localhost:8008
```

## Project Structure

```
SupersonicBuilder/
├── main.py                    # Manual PDF generator (entry point)
├── builder.py                 # Production pack builder
├── serve_pdfs.py              # PDF web server
├── rs                         # Unified CLI interface
├── rs.mk                      # Makefile automation
├── android15_board_setup.py   # Board photo documentation
│
├── scripts/                   # Organized automation
│   ├── ops/                   # Supersonic operational suite (30 files)
│   ├── active/                # Operational utilities (17 files)
│   ├── legacy/                # Archived scripts (9 files)
│   ├── deploy/                # Deployment scripts (7 files)
│   ├── monitoring/            # Monitoring/alerting (4 files)
│   └── tools/                 # General utilities (11 files)
│
├── tools/                     # Standalone tools
│   ├── support/               # Diagnostic utilities
│   ├── health_probe.py        # Port/file health checker
│   ├── metrics_refresh.py     # Badge generator
│   └── [130+ tools]
│
├── docs/                      # Documentation & GitHub Pages
│   ├── BUILD_ARCHITECTURE.md  # Build flow documentation
│   ├── sonic/                 # Vehicle-specific guides
│   └── assets/                # Web dashboard assets
│
├── profiles/                  # Car/hardware profiles
├── firmware/                  # DSP configurations
└── badges/                    # Status badges (JSON)
```

## RS CLI Commands

### Core Operations
```bash
./rs doctor           # Health check
./rs start           # Start autonomy services
./rs metrics         # Refresh badges
./rs diag            # Full diagnostic

# Car install workflows
./rs car-install     # Toggle install mode
./rs sonic-checklist # Installation tracking
./rs board-setup     # Android 15 board docs
```

### Advanced
```bash
./rs supersonic-preflight      # Git preflight checks
./rs supersonic-postinstall-v4 # Health pack installation
./rs metrics-plus              # Full metrics pipeline
```

## Documentation

- **[replit.md](replit.md)** - Comprehensive project documentation
- **[scripts/README.md](scripts/README.md)** - Scripts directory guide
- **[docs/BUILD_ARCHITECTURE.md](docs/BUILD_ARCHITECTURE.md)** - Build flow documentation
- **[REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md)** - Recent restructuring summary

## Key Technologies

- **PDF Generation**: ReportLab, PyPDF2, CairoSVG
- **Autonomy Stack**: Flask, psutil, FastAPI
- **Monitoring**: Health probes, badge generation, auto-healing
- **CI/CD**: GitHub Actions, automated workflows

## Recent Updates (November 2025)

### Evening Session - Comprehensive Audit
- ✅ **93.75% root directory cleanup** (80 → 5 files)
- ✅ **Supersonic tools integration** into RS CLI
- ✅ **Build architecture documentation**
- ✅ **Comprehensive testing and validation**

### Afternoon Session - Car Profile System
- ✅ **2014 Sonic LTZ profile** with Android 15 integration
- ✅ **82 circuit board photos** with hardware atlas
- ✅ **Install workflow automation** (pre/post-install sequences)

### Morning Session - Dashboard Enhancements
- ✅ **Interactive hotkeys widget** (D/H/R/L/S/G/K/?)
- ✅ **Real-time port latency monitoring**
- ✅ **Snapshot system** for archive creation
- ✅ **Guard mode auto-healing**

## Contributing

This is a personal automotive project, but contributions and suggestions are welcome via issues.

## License

Copyright © 2025 SupersonicBuilder Project

---

**Built with precision for automotive excellence** 🚗⚡

---

## Supersonic v2.4.0 – GitHub Deployment

This repository is wired for:

- ✅ Full health monitoring & self-heal
- ✅ Car Install Mode for a 2014 Chevy Sonic + EOENKK Android 15 head unit
- ✅ GitHub Pages metrics dashboard
- ✅ Release preflight GitHub Actions

Key docs:

- `docs/RELEASE_NOTES_v2.4.0.md`
- `GITHUB_DEPLOYMENT.md`
- `docs/sonic/android15_board/BOARD_MAP_PLACEHOLDER.md`

See **GITHUB_DEPLOYMENT.md** for a step-by-step deployment guide.
