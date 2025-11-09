#!/usr/bin/env python3
"""
SONICBUILDER AUTO ORCHESTRATOR v5.0 🚀
One-command automation for:
- Telemetry refresh
- Health summary
- Manual PDF build
- Fusion appendix injection
- Metadata stamping
- Auto-deploy to GitHub Pages
"""

import os, subprocess, datetime, sys

# === CONFIG ===
SUMMARY_SCRIPT = "generate_fusion_summary.py"   # Standalone summary generator
APPENDIX_SCRIPT = "fusion_appendix_injector.py" # NEW: Tier 3 appendix injector
PDF_BUILDER = "supersonic_autodeploy.py"        # SonicBuilder PDF generator
DEPLOY_SCRIPT = "scripts/deploy_pages.sh"       # Deploy to GitHub Pages
SYSTEM_HEALTH = "scripts/gen_system_json.py"    # System health generator
FINAL_PDF = "downloads/latest.pdf"              # SonicBuilder output path

def run_step(name, cmd):
    print(f"\n🔹 Running: {name}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Step failed: {name}")
        sys.exit(1)
    else:
        print(f"✅ Step complete: {name}")

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║   🧠 SONICBUILDER AUTO ORCHESTRATOR v5.0                      ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    start_time = datetime.datetime.now()

    # 1️⃣ Generate system health summary
    if os.path.exists(SYSTEM_HEALTH):
        run_step("Generate System Health", f"python3 {SYSTEM_HEALTH}")
    else:
        print("⚠️  No system health generator found – skipping")

    # 2️⃣ Update telemetry + fusion summary
    if os.path.exists(SUMMARY_SCRIPT):
        run_step("Generate Fusion Summary", f"python3 {SUMMARY_SCRIPT}")
    else:
        print("⚠️  Fusion summary not found – skipping telemetry")

    # 3️⃣ Build base PDF manual
    if os.path.exists(PDF_BUILDER):
        run_step("Generate PDF Manual", f"python3 {PDF_BUILDER}")
    else:
        print("⚠️  PDF builder not found – skipping PDF build")

    # 4️⃣ Append system health (if appendix script exists)
    if os.path.exists(APPENDIX_SCRIPT):
        run_step("Inject System Health Appendix", f"python3 {APPENDIX_SCRIPT}")
    else:
        print("ℹ️   Appendix script not found – PDF has no health appendix")

    # 5️⃣ Stamp metadata (timestamp + version)
    os.makedirs("docs/status", exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    metadata = {
        "last_build": stamp,
        "orchestrator_version": "5.0",
        "pdf_path": FINAL_PDF,
        "status": "completed" if os.path.exists(FINAL_PDF) else "no_pdf"
    }
    with open("docs/status/build_metadata.json", "w") as f:
        import json
        json.dump(metadata, f, indent=2)
    print(f"\n🕓 Metadata stamped at {stamp}")

    # 6️⃣ Deploy to GitHub Pages if configured
    if os.path.exists(DEPLOY_SCRIPT):
        run_step("Deploy to GitHub Pages", f"bash {DEPLOY_SCRIPT}")
    else:
        print("ℹ️   Deployment script not found — skipping deploy")

    end_time = datetime.datetime.now()
    elapsed = round((end_time - start_time).total_seconds(), 2)
    
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print(f"║   🚀 ORCHESTRATION COMPLETE in {elapsed}s")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    if os.path.exists(FINAL_PDF):
        size = os.path.getsize(FINAL_PDF) / 1024
        print(f"\n📘 Final manual: {FINAL_PDF} ({size:.1f} KB)")
    else:
        print(f"\n⚠️  PDF not found at {FINAL_PDF}")
    
    print(f"📊 Metadata: docs/status/build_metadata.json")

if __name__ == "__main__":
    main()