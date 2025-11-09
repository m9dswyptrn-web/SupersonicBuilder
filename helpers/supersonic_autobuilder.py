#!/usr/bin/env python3
import os, zipfile, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "SonicBuilder_Supersonic_Overlays_MEGA_v2.zip"

INCLUDE = [
    ".github/workflows/docker-publish-supersonic.yml",
    ".github/workflows/docs-verify-supersonic.yml",
    ".github/workflows/pages-with-autofix-preview-supersonic.yml",
    ".github/workflows/pages-deploy-supersonic.yml",
    ".github/workflows/codeql-supersonic.yml",
    ".github/workflows/trivy-supersonic.yml",
    ".github/workflows/sbom-slsa-supersonic.yml",
    ".github/workflows/slsa-provenance-supersonic.yml",
    ".github/workflows/scorecard-supersonic.yml",
    ".github/workflows/release-signing-cosign-supersonic.yml",
    ".github/workflows/opa-policy-guard-supersonic.yml",
    "helpers/supersonic_voice_console.py",
    "helpers/supersonic_verify_pages_supersonic.py",
    "helpers/supersonic_verify_autofix_preview_supersonic.py",
    "helpers/supersonic_ai_reasoner.py",
    "policies/supersonic",
    "assets/audio",
    "docs/README_MEGA_v2.md",
    "docs/Supersonic_Overlays_MEGA_v2_ReleaseBody.md",
]

def build_zip():
    if ASSET.exists(): ASSET.unlink()
    with zipfile.ZipFile(ASSET, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            p = ROOT / item
            if p.is_file():
                z.write(p, arcname=item)
            elif p.is_dir():
                for sub in p.rglob("*"):
                    if sub.is_file():
                        z.write(sub, arcname=str(sub.relative_to(ROOT)))
    return ASSET

def make_release():
    mk = ROOT / "Makefile"
    if mk.exists():
        return subprocess.call(["make","release"]) == 0
    return build_zip().exists()

def git_autopush(msg="chore: supersonic auto-build"):
    try:
        subprocess.check_call(["git","add","-A"], cwd=str(ROOT))
        subprocess.check_call(["git","commit","-m", msg], cwd=str(ROOT))
        subprocess.check_call(["git","push"], cwd=str(ROOT))
        return True
    except subprocess.CalledProcessError:
        return False

if __name__=="__main__":
    ok = make_release()
    print("OK" if ok else "FAIL")
    sys.exit(0 if ok else 1)
