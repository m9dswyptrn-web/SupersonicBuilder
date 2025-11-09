#!/usr/bin/env python3
"""
validate_github_setup.py - quick local sanity check for Projects + Automation files.
Does NOT call the network; it only checks files and obvious pitfalls.
"""
import json, sys
from pathlib import Path

def check_file(path):
    p = Path(path)
    ok = p.exists()
    print(("OK" if ok else "MISSING"), path)
    return ok

def looks_like_url(url: str) -> bool:
    return url.startswith("https://github.com/orgs/") and "/projects/" in url

def main():
    ok = True
    ok &= check_file(".github/workflows/project-auto.yml")
    ok &= check_file(".github/workflows/sonicbuilder-ci.yml")
    ok &= check_file(".github/workflows/version-badge.yml")
    ok &= check_file(".github/project_config.json")
    ok &= check_file(".github/ISSUE_TEMPLATE/bug_report.yml")
    ok &= check_file(".github/labels.yml")

    pj = Path(".github/project_config.json")
    if pj.exists():
        try:
            cfg = json.loads(pj.read_text(encoding="utf-8"))
            url = cfg.get("project_url","")
            if not looks_like_url(url):
                print("WARN .github/project_config.json -> 'project_url' looks empty or invalid:", url)
                ok = False
            mapping = cfg.get("label_to_status", {})
            required = ["feature","bug","chore","docs","build","ready for review","done"]
            missing = [k for k in required if k not in mapping]
            if missing:
                print("WARN missing label mappings:", ", ".join(missing))
                ok = False
        except Exception as e:
            print("ERROR Failed to parse .github/project_config.json:", e)
            ok = False

    if not ok:
        print("\nSome checks failed. Open SETUP_PROJECTS_AUTOMATION.md and complete missing steps.")
        sys.exit(2)
    print("\nAll local checks passed. Push to GitHub and watch Actions + your Project board.")
    sys.exit(0)

if __name__ == "__main__":
    main()
