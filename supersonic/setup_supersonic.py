#!/usr/bin/env python3
"""
SonicBuilder Supersonic Setup
Ultimate installer that orchestrates all setup phases:
- Environment detection and validation
- Secret verification
- Dependency installation
- Bundle packaging
- Failsafe deployment
"""

import os
import sys
import subprocess
import argparse
import json
from datetime import datetime
from pathlib import Path

VERSION = "2.0.9"
REQUIRED_SECRETS = ["GITHUB_TOKEN"]
SETUP_DIR = Path("setup")
FAILSAFE_DIR = Path("failsafe_tools")

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log(msg, level="INFO"):
    """Structured logging with colors"""
    colors = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED
    }
    color = colors.get(level, "")
    timestamp = datetime.utcnow().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {level}: {msg}{Colors.END}")

def run_cmd(cmd, check=True, silent=False):
    """Execute command with optional output suppression"""
    if not silent:
        log(f"→ {cmd}", "INFO")
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 and check:
        log(f"Command failed: {cmd}", "ERROR")
        log(result.stderr, "ERROR")
        sys.exit(1)
    
    return result

def check_environment():
    """Validate Replit/system environment"""
    log("Checking environment...", "INFO")
    
    # Check Python version
    py_version = sys.version_info
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
        log(f"Python 3.8+ required, found {py_version.major}.{py_version.minor}", "ERROR")
        sys.exit(1)
    
    log(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}", "SUCCESS")
    
    # Check Git
    result = run_cmd("git --version", check=False, silent=True)
    if result.returncode == 0:
        log(f"Git: {result.stdout.strip()}", "SUCCESS")
    else:
        log("Git not found", "WARNING")
    
    # Check required directories
    for dir_path in [SETUP_DIR, FAILSAFE_DIR]:
        if dir_path.exists():
            log(f"Found: {dir_path}/", "SUCCESS")
        else:
            log(f"Missing: {dir_path}/", "WARNING")

def verify_secrets():
    """Check for required environment secrets"""
    log("Verifying secrets...", "INFO")
    
    missing = []
    for secret in REQUIRED_SECRETS:
        if not os.getenv(secret):
            missing.append(secret)
            log(f"Missing: {secret}", "WARNING")
        else:
            log(f"Found: {secret}", "SUCCESS")
    
    if missing:
        log("\nRequired secrets missing. Add them to Replit Secrets:", "ERROR")
        for secret in missing:
            log(f"  - {secret}", "ERROR")
        return False
    
    return True

def install_dependencies():
    """Install required Python packages"""
    log("Checking dependencies...", "INFO")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        log("No requirements.txt found", "WARNING")
        return
    
    log("Installing from requirements.txt...", "INFO")
    run_cmd("pip install -q -r requirements.txt", silent=True)
    log("Dependencies installed", "SUCCESS")

def build_bundles(bundle_type="all"):
    """Build Supersonic bundle packages"""
    log(f"Building bundles: {bundle_type}", "INFO")
    
    bundle_scripts = {
        "core": SETUP_DIR / "build_supersonic_core.py",
        "security": SETUP_DIR / "build_supersonic_security.py",
        "diagnostics": SETUP_DIR / "build_supersonic_diagnostics.py",
        "addons": SETUP_DIR / "build_supersonic_addons.py",
        "failsafe": SETUP_DIR / "build_supersonic_failsafe.py",
        "all": SETUP_DIR / "package_all.py"
    }
    
    script = bundle_scripts.get(bundle_type)
    if not script or not script.exists():
        log(f"Bundle script not found: {script}", "ERROR")
        return False
    
    run_cmd(f"python3 {script}")
    log(f"Bundle '{bundle_type}' built successfully", "SUCCESS")
    return True

def deploy_failsafe():
    """Deploy failsafe recovery system"""
    log("Deploying failsafe system...", "INFO")
    
    failsafe_script = FAILSAFE_DIR / "run_failsafe.sh"
    if not failsafe_script.exists():
        log("Failsafe script not found", "WARNING")
        return False
    
    # Verify failsafe bundle exists
    if not Path("Supersonic_Failsafe.zip").exists():
        log("Building failsafe bundle first...", "INFO")
        build_bundles("failsafe")
    
    log("Failsafe system ready", "SUCCESS")
    return True

def generate_status_report():
    """Generate setup status JSON for founder_console"""
    status = {
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        },
        "secrets": {
            "verified": all(os.getenv(s) for s in REQUIRED_SECRETS),
            "missing": [s for s in REQUIRED_SECRETS if not os.getenv(s)]
        },
        "bundles": {
            "core": Path("Supersonic_Core.zip").exists(),
            "security": Path("Supersonic_Security.zip").exists(),
            "diagnostics": Path("Supersonic_Diagnostics.zip").exists(),
            "addons": Path("Supersonic_Addons.zip").exists(),
            "failsafe": Path("Supersonic_Failsafe.zip").exists()
        }
    }
    
    output_file = Path("founder_console/health_status.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(status, f, indent=2)
    
    log(f"Status report: {output_file}", "SUCCESS")
    return status

def main():
    parser = argparse.ArgumentParser(
        description="SonicBuilder Supersonic Setup - Ultimate Installer"
    )
    parser.add_argument(
        "--bundle",
        choices=["core", "security", "diagnostics", "addons", "failsafe", "all"],
        default="all",
        help="Bundle type to build"
    )
    parser.add_argument(
        "--skip-secrets",
        action="store_true",
        help="Skip secret verification (for local testing)"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency installation"
    )
    parser.add_argument(
        "--failsafe-only",
        action="store_true",
        help="Only deploy failsafe system"
    )
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}╔════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}║   🚀 SonicBuilder Supersonic Setup v{VERSION}                  ║{Colors.END}")
    print(f"{Colors.BOLD}╚════════════════════════════════════════════════════════════════╝{Colors.END}\n")
    
    try:
        # Phase 1: Environment Check
        log("Phase 1/5: Environment Validation", "INFO")
        check_environment()
        
        # Phase 2: Secret Verification
        if not args.skip_secrets:
            log("\nPhase 2/5: Secret Verification", "INFO")
            if not verify_secrets():
                log("Setup incomplete - secrets required", "ERROR")
                sys.exit(1)
        else:
            log("\nPhase 2/5: Secret Verification (SKIPPED)", "WARNING")
        
        # Phase 3: Dependencies
        if not args.skip_deps:
            log("\nPhase 3/5: Dependency Installation", "INFO")
            install_dependencies()
        else:
            log("\nPhase 3/5: Dependency Installation (SKIPPED)", "WARNING")
        
        # Phase 4: Bundle Building or Failsafe Deployment
        if args.failsafe_only:
            log("\nPhase 4/5: Failsafe Deployment", "INFO")
            deploy_failsafe()
        else:
            log(f"\nPhase 4/5: Bundle Building ({args.bundle})", "INFO")
            build_bundles(args.bundle)
        
        # Phase 5: Status Report
        log("\nPhase 5/5: Status Report Generation", "INFO")
        status = generate_status_report()
        
        # Summary
        print(f"\n{Colors.BOLD}╔════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}║              ✅ SUPERSONIC SETUP COMPLETE                      ║{Colors.END}")
        print(f"{Colors.BOLD}╚════════════════════════════════════════════════════════════════╝{Colors.END}\n")
        
        log(f"Version: {VERSION}", "SUCCESS")
        log(f"Secrets: {'✅ Verified' if status['secrets']['verified'] else '⚠️  Missing'}", "INFO")
        
        bundles_count = sum(1 for v in status['bundles'].values() if v)
        log(f"Bundles: {bundles_count}/5 built", "SUCCESS" if bundles_count > 0 else "WARNING")
        
        log(f"Status: founder_console/health_status.json", "INFO")
        
        print(f"\n{Colors.GREEN}Ready for autodeploy!{Colors.END}")
        print(f"{Colors.BLUE}Run: bash autodeploy.sh{Colors.END}\n")
        
        return 0
        
    except Exception as e:
        log(f"Setup failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
