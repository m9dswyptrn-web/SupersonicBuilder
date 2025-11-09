# 2014 Chevy Sonic LTZ — Automotive Wiring Manual Generator

## Overview
This project generates comprehensive PDF installation manuals for automotive wiring and integration projects, specifically for a 2014 Chevrolet Sonic LTZ with an Android head unit, Maestro RR2/GM2 primary gateway, and G-RZ overlay system. The purpose is to create professional dark and light themed PDF manuals from YAML configuration files, including complete wiring diagrams, pinout documentation, and parts lists. The system is fully operational and configured to generate and serve these manuals via a web interface.

## User Preferences
None documented yet. This is a new project.

## System Architecture

### UI/UX Decisions
The system features a "Supersonic Commander" web control panel (http://localhost:5000) for managing operations. This panel includes:
- Live settings management (voice pack, volume, rate, theme, advanced tools toggle).
- Six streaming consoles (Rebuild, Deploy, Verify, Auto-Fix, Promote, Rollback) with live output.
- A system telemetry dashboard (CPU, memory, disk usage) with auto-refresh.
- Thematic voice packs (FlightOps, SciFiControl, IndustrialOps, ArcadeHUD) for audible feedback on system events.
- Generated PDFs offer both dark and light themes, interactive bookmarks, and printable job cards with signal icons.
- Diagrams leverage a DUAL-DIAGRAM SYSTEM, displaying vector diagrams alongside real installation photos.

### Technical Implementations
- **PDF Generation**: Uses `main.py` to generate PDFs from YAML configurations. Supports SVG vector graphics with high-DPI raster fallback (CairoSVG) and multi-image layouts. Includes features like PDF bookmarks, QR code generation, and version/timestamp footers.
- **Web Servers**:
    - `supersonic_settings_server.py` (Flask) hosts the Supersonic Commander control panel on port 5000.
    - `serve_pdfs.py` serves generated PDF downloads on port 8000, tracking download statistics.
- **Automation**: Extensive Makefile targets automate building, deploying, verifying, fixing, and rolling back changes.
- **Monitoring & Diagnostics**: Includes a health and logging system with FastAPI/Flask health endpoints, rotating log files, and a comprehensive diagnostic suite (`supersonic_doctor.py`) for system health reports and project scanning.
- **Configuration**: Manuals are generated from 12 YAML configuration sections covering main technical details, professional add-on sections, and printable job cards.
- **Asset Handling**: Employs an `AssetResolver` for robust image rendering, supporting SVG, PNG, and JPG with error placeholders and auto-optimization.
- **Workflow Orchestration**: `supersonic_commander_system` provides a unified interface for build, deployment, verification, and automated fixing and rollback processes.

### System Design Choices
- **Modular Design**: Core functionalities are separated into Python modules (e.g., `toc_jobcards.py`, `img_tools.py`, `qr_tools.py`).
- **Data-Driven Configuration**: YAML files are central to defining manual content, allowing for easy updates and customization.
- **Version Control Integration**: Includes version management via `version.txt` and `CHANGELOG.md`, along with Makefile targets for version bumping and release management.
- **Security**: Implements path traversal prevention and backup name validation for rollback features.

## External Dependencies

### Python Packages
- **PDF Generation**: `reportlab`, `PyPDF2`, `PyYAML`, `Pillow`, `svglib`, `cairosvg`, `qrcode[pil]`, `tinycss2`, `cssselect2`.
- **Supersonic Commander**: `Flask`, `pyttsx3`, `psutil`, `beautifulsoup4`, `requests`, `simpleaudio`.
- **Diagnostics & Watchdog**: `watchdog`, `pyserial`.

### System Dependencies
- `cairo` (C library for graphics rendering)
- `pkg-config` (helps Python find C libraries)
- `zip`, `unzip` (for package creation)

### Optional Dependencies
- **OpenAI API**: For `supersonic_doc_updater.py` (AI documentation updater).