#!/usr/bin/env python3
"""Update README badges for CI and Pages workflows."""
import re
from pathlib import Path

README = Path("README.md")
OWNER_REPO = "ChristopherElgin/SonicBuilderSupersonic"

def update_badges():
    if not README.exists():
        print("README.md not found - creating basic template")
        README.write_text("""# SonicBuilder Supersonic

[![CI](https://github.com/{}/actions/workflows/ci.yml/badge.svg)](https://github.com/{}/actions/workflows/ci.yml)
[![Pages](https://github.com/{}/actions/workflows/pages.yml/badge.svg)](https://github.com/{}/actions/workflows/pages.yml)

Enterprise-grade PDF manual generator for 2014 Chevy Sonic LTZ Android head unit.

## Features
- v4 Ultimate Edition with AI-powered build automation
- LED status banner system
- 5 professional voice packs
- Multi-platform CI/CD
- Production-ready Replit Autoscale deployment

## Quick Start

```bash
make health-scan
make build_dark
make verify
```

## Documentation
- [Health Scan Guide](docs/SUPERSONIC_HEALTH_SCAN.md)
- [Replit Automation](docs/replit_automation/REPLIT_AUTOMATION_INTEGRATION.md)
""".format(OWNER_REPO, OWNER_REPO, OWNER_REPO, OWNER_REPO), encoding="utf-8")
        print("✅ Created README.md with badges")
        return

    content = README.read_text(encoding="utf-8")
    
    ci_badge = f"[![CI](https://github.com/{OWNER_REPO}/actions/workflows/ci.yml/badge.svg)](https://github.com/{OWNER_REPO}/actions/workflows/ci.yml)"
    pages_badge = f"[![Pages](https://github.com/{OWNER_REPO}/actions/workflows/pages.yml/badge.svg)](https://github.com/{OWNER_REPO}/actions/workflows/pages.yml)"
    
    if "[![CI]" not in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                lines.insert(i + 1, '')
                lines.insert(i + 2, ci_badge)
                lines.insert(i + 3, pages_badge)
                lines.insert(i + 4, '')
                break
        content = '\n'.join(lines)
        README.write_text(content, encoding="utf-8")
        print("✅ Added CI and Pages badges to README.md")
    else:
        print("ℹ️  Badges already present in README.md")

if __name__ == "__main__":
    update_badges()
