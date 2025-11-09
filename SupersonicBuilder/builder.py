#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
builder.py — Supersonic Production Pack Builder
Scaffold or regenerate the complete Supersonic Commander system.

Usage:
    python builder.py                   # scaffold files into current repo
    python builder.py --zip             # also create Supersonic_Production_Pack_v1.zip
    python builder.py --clean           # remove generated pack files
    python builder.py --requirements    # generate requirements.txt
"""

from __future__ import annotations
from pathlib import Path
import argparse, sys, textwrap, json, shutil, time

ROOT = Path(".").resolve()
FILES: dict[str, str] = {}

def add(path: str, content: str):
    """Register a file to be written"""
    FILES[path] = textwrap.dedent(content).lstrip("\n")

def banner(msg: str):
    print(f"\n{'='*70}\n{msg}\n{'='*70}")

# ============================================================
# SETTINGS & CONFIGURATION
# ============================================================
add("supersonic_settings.json", """
{
  "voice_pack": "ArcadeHUD",
  "volume": 1.0,
  "rate": 185,
  "dashboard_auto_refresh": true,
  "telemetry_interval_sec": 30,
  "theme": "dark",
  "show_changelog_cards": true,
  "advanced_tools": false
}
""")

add("supersonic_settings.py", r"""
#!/usr/bin/env python3
from pathlib import Path
import json

SETTINGS_FILE = Path("supersonic_settings.json")
DEFAULTS = {
  "voice_pack": "FlightOps",
  "volume": 1.0,
  "rate": 185,
  "dashboard_auto_refresh": True,
  "telemetry_interval_sec": 30,
  "theme": "dark",
  "show_changelog_cards": True,
  "advanced_tools": False
}

def load_settings()->dict:
    data = DEFAULTS.copy()
    if SETTINGS_FILE.exists():
        try:
            data.update(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"⚠️ settings read error: {e}")
    return data

def save_settings(cfg:dict):
    SETTINGS_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
""")

# ============================================================
# VOICE SYSTEM (4 packs + commander)
# ============================================================
add("supersonic_voice_packs.py", r"""
#!/usr/bin/env python3
VOICE_PACKS = {
  "FlightOps": {
    "meta": {"rate":185, "volume":1.0, "voice_pref":"female"},
    "phrases":{
      "online":"Flight Ops online. Systems green.",
      "start":"Pre-flight checks complete. Ignition.",
      "success":"Mission complete. All systems nominal.",
      "warn":"Caution. Anomaly detected. Review advisories.",
      "fail":"Abort. Mission failed verification.",
      "offline":"Flight Ops standing by.",
      "signing":"Authenticity signing in progress.",
      "signed":"Signature complete. Identity verified.",
      "tagging":"Applying release tag.",
      "tagged":"Release tag confirmed.",
      "release":"Package released. Ready for deployment.",
      "rollback":"Rollback complete. System restored."
    }
  },
  "SciFiControl": {
    "meta": {"rate":170, "volume":0.95, "voice_pref":"Zira|Samantha|Google US"},
    "phrases":{
      "online":"Control nexus online.",
      "start":"Compilation lattice engaged.",
      "success":"Operation complete. Integrity affirmed.",
      "warn":"Advisory. Non-fatal deviations present.",
      "fail":"Critical fault. Integrity breach detected.",
      "offline":"Nexus offline.",
      "signing":"Initiating cryptographic attestation.",
      "signed":"Attestation complete. Trust anchor locked.",
      "tagging":"Version anchor requested.",
      "tagged":"Version anchor secured.",
      "release":"Distribution channel open. Release propagated.",
      "rollback":"State restored to last checkpoint."
    }
  },
  "IndustrialOps": {
    "meta": {"rate":160, "volume":1.0, "voice_pref":"male|David|Alex"},
    "phrases":{
      "online":"Industrial Ops ready.",
      "start":"Spin-up sequence started.",
      "success":"Job finished. Output verified.",
      "warn":"Heads up. Check the logs.",
      "fail":"Stop work. Build failed checks.",
      "offline":"Industrial Ops idle.",
      "signing":"Signing artifacts.",
      "signed":"Signature applied.",
      "tagging":"Tagging version.",
      "tagged":"Tag recorded.",
      "release":"Release published.",
      "rollback":"Rollback finished. Previous version live."
    }
  },
  "ArcadeHUD": {
    "meta": {"rate":190, "volume":1.0, "voice_pref":"Samantha|Zira|Alex|David"},
    "phrases":{
      "online":"Player one ready.",
      "start":"Level start — good luck!",
      "success":"Stage clear! High score!",
      "warn":"Caution — bonus time running low.",
      "fail":"Game over — insert coin to retry.",
      "offline":"Arcade idle. Press start.",
      "signing":"Authenticity power-up engaged.",
      "signed":"Epic! Signature unlocked.",
      "tagging":"New level tag incoming.",
      "tagged":"Level tag locked in.",
      "release":"Drop complete — claim your loot.",
      "rollback":"Rewind complete. Back in the fight."
    }
  }
}
DEFAULT_PACK="FlightOps"

def get_pack(name:str|None)->dict:
    return VOICE_PACKS.get(name or DEFAULT_PACK, VOICE_PACKS[DEFAULT_PACK])

def list_packs()->list[str]:
    return sorted(VOICE_PACKS.keys())
""")

add("supersonic_voice_commander.py", r"""
#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, threading, time, os
try:
    import pyttsx3
except Exception:
    pyttsx3 = None
from supersonic_voice_packs import get_pack, list_packs
from supersonic_settings import load_settings

EVENTS=("online","start","success","warn","fail","offline","signing","signed","tagging","tagged","release","rollback")

def _pick_voice(engine, pref:str|None):
    if not pref or not engine: return
    tokens=[t.strip().lower() for t in re.split(r"[|,/]+", pref)]
    try:
        for v in engine.getProperty("voices"):
            name=(v.name or "").lower()
            if any(t in name for t in tokens):
                engine.setProperty("voice", v.id); return
    except Exception: pass

class VoiceCommander:
    def __init__(self, pack_name:str|None=None):
        cfg=load_settings()
        pack_name=pack_name or cfg.get("voice_pack")
        self.pack=get_pack(pack_name)
        self.engine=None
        if pyttsx3:
            try:
                self.engine=pyttsx3.init()
                self.engine.setProperty("rate", cfg.get("rate", self.pack["meta"].get("rate",185)))
                self.engine.setProperty("volume", cfg.get("volume", self.pack["meta"].get("volume",1.0)))
                _pick_voice(self.engine, self.pack["meta"].get("voice_pref"))
            except Exception as e:
                print(f"⚠️  TTS initialization failed: {e}")
                self.engine=None
        self._lock=threading.Lock()
    
    def speak(self, text:str):
        if not self.engine:
            print(f"🔊 [TTS disabled] {text}"); return
        def _run():
            with self._lock:
                self.engine.say(text); self.engine.runAndWait()
        threading.Thread(target=_run, daemon=True).start()
    
    def speak_event(self, event:str):
        phrase=self.pack["phrases"].get(event, f"{event.title()}."); self.speak(phrase)

def _cli():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pack"); ap.add_argument("--say"); ap.add_argument("--event", choices=EVENTS)
    ap.add_argument("--list", action="store_true"); ap.add_argument("--preview", action="store_true")
    a=ap.parse_args()
    if a.list: print("Available packs:", ", ".join(list_packs())); return
    vc=VoiceCommander(a.pack)
    if a.preview:
        for ev in EVENTS: vc.speak_event(ev); time.sleep(1.1); return
    if a.event: vc.speak_event(a.event); time.sleep(1.0); return
    if a.say: vc.speak(a.say); time.sleep(max(1.0,len(a.say.split())/3)); return
    vc.speak_event("online"); time.sleep(1.0)

if __name__=="__main__": _cli()
""")

# ============================================================
# README
# ============================================================
add("SUPERSONIC_README.md", """
# Supersonic Production Pack

Enterprise-grade automation and control panel for the SonicBuilder PDF manual system.

## Features

- 🎙️ **Voice Commander** - 4 voice packs with 12 events
- 🎮 **6 Streaming Consoles** - Rebuild, Deploy, Verify, Auto-Fix, Promote, Rollback
- 📋 **Operations Audit Log** - Track all operations with timestamps
- 🛟 **Emergency Rollback** - One-click restore from timestamped backups
- 🔧 **Makefile Integration** - All operations available via make targets

## Quick Start

```bash
# Install dependencies
pip install flask pyttsx3 beautifulsoup4 requests

# Launch the control panel (port 5000)
python supersonic_settings_server.py

# Or use Make targets
make supersonic-serve       # Launch control panel
make supersonic-rebuild     # Rebuild all PDFs
make supersonic-deploy      # Deploy to /docs
make supersonic-verify      # Verify links
make supersonic-audit       # View operations log
```

## Voice Packs

1. **FlightOps** - Military flight operations style
2. **SciFiControl** - Futuristic control nexus
3. **IndustrialOps** - Factory floor operations
4. **ArcadeHUD** - Retro gaming arcade

## Voice Events

- online, offline - System startup/shutdown
- start - Operation beginning
- success, warn, fail - Operation outcomes
- signing, signed - Code signing
- tagging, tagged - Version tagging
- release - Package deployment
- rollback - System restoration

## Architecture

- **Flask server** (port 5000) with streaming consoles
- **LogBuffer** class for thread-safe log management
- **Audit logging** to docs/_ops_log.txt (JSON format)
- **Voice feedback** via pyttsx3 (optional, falls back to console)
- **Timestamped backups** for rollback capability

## Advanced Tools

Toggle "Advanced Tools" in settings to show:
- **Auto-Fix Preview** - Scan HTML and suggest fixes
- **Promote** - Move preview fixes to production
- **Rollback** - Restore from backups

## Security

- Path traversal protection in rollback
- Backup name validation
- Pre-rollback safety snapshots
- Recursive HTML scanning

## Production Deployment

System runs on port 5000 and is designed for 24/7 operation with:
- Thread-safe operations
- Graceful error handling
- Complete audit trail
- Voice feedback on all operations
""")

add("requirements.txt", """
# PDF Generation
reportlab
Pillow
pypdf
PyPDF2
PyYAML
qrcode[pil]
svglib
pdf2image
pikepdf

# Serial & Monitoring
pyserial
watchdog
psutil

# Web Framework
Flask>=3.0.0
flask-cors
fpdf
fpdf2

# Verify / Auto-fix
beautifulsoup4>=4.12.0
requests>=2.32.0

# Voice Commander
pyttsx3>=2.90

# Production Server
gunicorn>=21.2
""")

# ============================================================
# DEPLOYMENT CONFIGURATIONS
# ============================================================
add("Procfile", """
web: gunicorn supersonic_settings_server:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
""")

add("Dockerfile", """
# ---- Base (slim) ----
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# System deps (for pyttsx3 backends + basic TTS capability)
RUN apt-get update && apt-get install -y --no-install-recommends \\
    libespeak-ng1 libasound2 libasound2-data libasound2-plugins \\
    build-essential curl ca-certificates \\
  && rm -rf /var/lib/apt/lists/*

# ---- Deps ----
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn

# ---- App ----
COPY . .

# Expose panel port; Render/Heroku pass $PORT
EXPOSE 5055

# Default: gunicorn serve panel
CMD ["sh", "-c", "gunicorn supersonic_settings_server:app --bind 0.0.0.0:${PORT:-5055} --workers 2 --threads 4 --timeout 120"]
""")

add(".dockerignore", """
__pycache__/
*.pyc
*.pyo
*.pyd
*.log
.venv/
env/
.build/
dist/
*.zip
.git/
.gitignore
.github/
ci-logs/
docs/_backup_*/
docs/_fixed_preview/
.Python
*.so
*.egg
*.egg-info
.DS_Store
.vscode
.idea
*.swp
*.swo
*~
.replit
replit.nix
Makefile.backup
attached_assets
backups
downloads
exports
build
artifacts
""")

add("render.yaml", """
services:
  - type: web
    name: supersonic-commander
    env: python
    plan: starter
    region: oregon
    runtime: docker
    autoDeploy: true
    healthCheckPath: /
    envVars:
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: FLASK_ENV
        value: production
    # If you prefer Render's native Python runtime, comment 'runtime: docker'
    # and uncomment below:
    # buildCommand: pip install -r requirements.txt
    # startCommand: gunicorn supersonic_settings_server:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
""")

add("docker-compose.yml", """
version: "3.9"
services:
  # Option 1: Build locally
  commander:
    build: .
    ports:
      - "5055:5055"
    environment:
      - PORT=5055
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    volumes:
      - ./docs:/app/docs
    restart: unless-stopped

  # Option 2: Pull from GitHub Container Registry (after CI publishes)
  # Uncomment to use pre-built image instead of local build
  # commander-ghcr:
  #   image: ghcr.io/OWNER/supersonic-commander:latest
  #   ports:
  #     - "5055:5055"
  #   environment:
  #     - PORT=5055
  #     - FLASK_ENV=production
  #   restart: unless-stopped
""")

add(".github/workflows/release-drafter.yml", """
name: Release Drafter

on:
  push:
    branches: [ main ]
  pull_request:
    types: [opened, edited, reopened, synchronize, closed]

permissions:
  contents: write
  pull-requests: write

jobs:
  update_release_draft:
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
""")

add(".github/release-drafter.yml", """
name-template: "v$NEXT_PATCH_VERSION"
tag-template: "v$NEXT_PATCH_VERSION"
categories:
  - title: "🚀 Features"
    labels: ["feature", "enhancement"]
  - title: "🛠 Fixes"
    labels: ["fix", "bug", "bugfix"]
  - title: "🧹 Maintenance"
    labels: ["chore", "refactor", "docs", "ci", "build"]
  - title: "🔒 Security"
    labels: ["security"]
change-template: "- $TITLE (#$NUMBER) by @$AUTHOR"
exclude-labels: ["skip-changelog"]
autolabeler:
  - label: "docs"
    title:
      - "/docs/i"
    files:
      - "docs/**"
  - label: "ci"
    files:
      - ".github/**"
template: |
  ## What's New
  $CHANGES

  ## Install / Upgrade
  - Docker: `docker pull ghcr.io/$OWNER/supersonic-commander:$NEXT_PATCH_VERSION`
  - Py: `pip install -r requirements.txt`

  _Generated by Release Drafter._
""")

add(".github/dependabot.yml", """
version: 2
updates:
  # Keep GitHub Actions up to date
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "08:00"
    open-pull-requests-limit: 5
    groups:
      actions-minor:
        patterns: ["*"]
        update-types: ["minor", "patch"]

  # Python (pip) dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "08:15"
    open-pull-requests-limit: 10
    allow:
      - dependency-type: "direct"
    ignore:
      - dependency-name: "flask"
        versions: ["<3.0.0"]
    groups:
      bs4-requests:
        patterns: ["beautifulsoup4", "requests"]
      tts:
        patterns: ["pyttsx3"]
      server:
        patterns: ["gunicorn"]

  # Docker base image
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "monthly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 2
""")

add(".github/CODEOWNERS", """
# CODEOWNERS
# Default owner for everything in the repo
* @OWNER

# CI/CD and workflows
/.github/ @OWNER

# Deployment configurations
/Dockerfile @OWNER
/docker-compose.yml @OWNER
/Procfile @OWNER
/render.yaml @OWNER

# Core application
/supersonic_*.py @OWNER
/builder.py @OWNER
/requirements.txt @OWNER
""")

def scaffold_files():
    """Write all registered files to disk"""
    banner("📦 Scaffolding Supersonic Production Pack")
    created = []
    
    for path_str, content in FILES.items():
        path = ROOT / path_str
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.exists():
            print(f"⚠️  Skipping {path_str} (already exists)")
            continue
        
        path.write_text(content, encoding="utf-8")
        print(f"✅ Created {path_str}")
        created.append(path_str)
    
    if created:
        banner(f"✨ Scaffolded {len(created)} files")
        print("\nNext steps:")
        print("  pip install -r requirements.txt")
        print("  python supersonic_settings_server.py")
    else:
        print("\n✅ All files already exist")

def create_zip():
    """Create distributable ZIP"""
    banner("📦 Creating Supersonic_Production_Pack_v1.zip")
    
    # Write files to temp directory
    temp_dir = ROOT / "Supersonic_Pack_Temp"
    temp_dir.mkdir(exist_ok=True)
    
    for path_str, content in FILES.items():
        dest = temp_dir / path_str
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    
    # Create ZIP
    zip_path = ROOT / "Supersonic_Production_Pack_v1"
    shutil.make_archive(str(zip_path), 'zip', temp_dir)
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    print(f"✅ Created {zip_path}.zip")
    print(f"   Size: {(zip_path.with_suffix('.zip').stat().st_size / 1024):.1f} KB")

def clean_files():
    """Remove generated files"""
    banner("🧹 Cleaning generated files")
    
    removed = []
    for path_str in FILES.keys():
        path = ROOT / path_str
        if path.exists():
            path.unlink()
            print(f"🗑️  Removed {path_str}")
            removed.append(path_str)
    
    # Remove ZIP if exists
    zip_path = ROOT / "Supersonic_Production_Pack_v1.zip"
    if zip_path.exists():
        zip_path.unlink()
        print(f"🗑️  Removed {zip_path.name}")
        removed.append(zip_path.name)
    
    if removed:
        banner(f"✨ Cleaned {len(removed)} files")
    else:
        print("✅ No generated files to remove")

def main():
    ap = argparse.ArgumentParser(description="Supersonic Production Pack Builder")
    ap.add_argument("--zip", action="store_true", help="Create ZIP distribution")
    ap.add_argument("--clean", action="store_true", help="Remove generated files")
    ap.add_argument("--requirements", action="store_true", help="Generate requirements.txt only")
    args = ap.parse_args()
    
    if args.clean:
        clean_files()
        return
    
    if args.requirements:
        req_path = ROOT / "requirements.txt"
        req_path.write_text(FILES["requirements.txt"], encoding="utf-8")
        print(f"✅ Created requirements.txt")
        return
    
    scaffold_files()
    
    if args.zip:
        create_zip()
    
    banner("🚀 Supersonic Production Pack ready")
    print("\n🎮 Launch the control panel:")
    print("   python supersonic_settings_server.py")
    print("\n📚 Documentation:")
    print("   cat SUPERSONIC_README.md")

if __name__ == "__main__":
    main()
