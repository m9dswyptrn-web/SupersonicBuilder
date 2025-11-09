#!/usr/bin/env python3
"""
Package Orchestrator - Toggleable Integration System
Manages optional addon packages from uploaded content
"""
import os
import sys
from pathlib import Path

class PackageOrchestrator:
    def __init__(self):
        self.packages_dir = Path("packages")
        self.audio_enabled = os.getenv("ENABLE_AUDIO_ADDONS", "false").lower() == "true"
        self.manifest_enabled = os.getenv("ENABLE_MANIFEST_ADDONS", "false").lower() == "true"
        self.exactfit_enabled = os.getenv("ENABLE_EXACTFIT_ADDONS", "false").lower() == "true"
    
    def list_available_packages(self):
        """List all available addon packages"""
        packages = {}
        for pkg_type in ["audio", "manifests", "exactfit"]:
            pkg_dir = self.packages_dir / pkg_type
            if pkg_dir.exists():
                scripts = list(pkg_dir.rglob("*.py")) + list(pkg_dir.rglob("*.sh"))
                packages[pkg_type] = len(scripts)
        return packages
    
    def get_enabled_packages(self):
        """Return list of currently enabled packages"""
        enabled = []
        if self.audio_enabled:
            enabled.append("audio")
        if self.manifest_enabled:
            enabled.append("manifests")
        if self.exactfit_enabled:
            enabled.append("exactfit")
        return enabled
    
    def execute_package_scripts(self, package_type):
        """Execute scripts from a specific package"""
        pkg_dir = self.packages_dir / package_type
        if not pkg_dir.exists():
            print(f"⚠️  Package {package_type} not found")
            return False
        
        scripts = sorted(pkg_dir.rglob("*.py"))
        executed = 0
        for script in scripts:
            if "apply" in script.name or "install" in script.name:
                print(f"🔧 Executing: {script}")
                os.system(f"python3 {script}")
                executed += 1
        
        print(f"✅ Executed {executed} scripts from {package_type}")
        return True
    
    def status(self):
        """Print current package orchestrator status"""
        print("📦 Package Orchestrator Status")
        print("=" * 60)
        available = self.list_available_packages()
        for pkg, count in available.items():
            enabled = "✅ ENABLED" if pkg in self.get_enabled_packages() else "⚠️  DISABLED"
            print(f"  {pkg.ljust(15)} {str(count).rjust(3)} scripts  {enabled}")
        print("=" * 60)
        print(f"\nTo enable packages, set environment variables:")
        print(f"  export ENABLE_AUDIO_ADDONS=true")
        print(f"  export ENABLE_MANIFEST_ADDONS=true")
        print(f"  export ENABLE_EXACTFIT_ADDONS=true")

if __name__ == "__main__":
    orchestrator = PackageOrchestrator()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            orchestrator.status()
        elif cmd == "list":
            print(orchestrator.list_available_packages())
        elif cmd == "execute":
            if len(sys.argv) > 2:
                orchestrator.execute_package_scripts(sys.argv[2])
            else:
                print("Usage: package_orchestrator.py execute <audio|manifests|exactfit>")
        else:
            print("Commands: status, list, execute")
    else:
        orchestrator.status()
