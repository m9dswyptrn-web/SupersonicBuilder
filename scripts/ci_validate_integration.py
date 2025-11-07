#!/usr/bin/env python3
"""
CI Validation for Uploaded Content Integration
Performs duplicate-name scan, namespace-lint, and dry-run deployment checks
"""
import os
import sys
from pathlib import Path
from collections import defaultdict

class IntegrationValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def scan_duplicate_names(self):
        """Scan for duplicate filenames across the project"""
        print("🔍 Scanning for duplicate names...")
        files = defaultdict(list)
        
        for path in Path(".").rglob("*.py"):
            if "venv" not in str(path) and "__pycache__" not in str(path):
                files[path.name].append(str(path))
        
        duplicates = {name: paths for name, paths in files.items() if len(paths) > 1}
        
        if duplicates:
            self.warnings.append(f"Found {len(duplicates)} duplicate filenames")
            for name, paths in list(duplicates.items())[:5]:
                print(f"  ⚠️  {name}: {len(paths)} occurrences")
        else:
            print("  ✅ No critical duplicates found")
        
        return len(duplicates)
    
    def namespace_lint(self):
        """Check for namespace conflicts"""
        print("\n🔍 Checking namespace conflicts...")
        conflicts = []
        
        # Check for common naming conflicts
        reserved = ["test", "config", "main", "app", "build"]
        for name in reserved:
            files = list(Path(".").rglob(f"{name}.py"))
            if len(files) > 1:
                conflicts.append(f"{name}.py appears {len(files)} times")
        
        if conflicts:
            self.warnings.append(f"Found {len(conflicts)} namespace warnings")
            for conflict in conflicts[:5]:
                print(f"  ⚠️  {conflict}")
        else:
            print("  ✅ No namespace conflicts detected")
        
        return len(conflicts)
    
    def dry_run_check(self):
        """Perform dry-run deployment check"""
        print("\n🔍 Running dry-run deployment check...")
        
        # Check key components exist
        required = [
            "supersonic_autodeploy.py",
            "auto_orchestrator.py",
            "render_manifest.py",
            "Makefile"
        ]
        
        missing = []
        for req in required:
            if not Path(req).exists():
                missing.append(req)
                self.errors.append(f"Missing required file: {req}")
        
        if missing:
            print(f"  ❌ Missing {len(missing)} required files")
            for m in missing:
                print(f"     - {m}")
            return False
        else:
            print("  ✅ All required files present")
            return True
    
    def validate_package_integrity(self):
        """Validate integrated packages"""
        print("\n🔍 Validating package integrity...")
        
        pkg_dir = Path("packages")
        if not pkg_dir.exists():
            self.errors.append("packages/ directory not found")
            return False
        
        types = ["audio", "manifests", "exactfit"]
        found = 0
        for pkg_type in types:
            if (pkg_dir / pkg_type).exists():
                count = len(list((pkg_dir / pkg_type).rglob("*.py")))
                print(f"  ✅ {pkg_type}: {count} scripts")
                found += 1
        
        return found > 0
    
    def run_all(self):
        """Run all validation checks"""
        print("=" * 60)
        print("🚀 Integration Validation Suite")
        print("=" * 60)
        
        self.scan_duplicate_names()
        self.namespace_lint()
        self.dry_run_check()
        self.validate_package_integrity()
        
        print("\n" + "=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)
        print(f"  Errors:   {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\n❌ Validation FAILED")
            for err in self.errors:
                print(f"  - {err}")
            return False
        elif self.warnings:
            print("\n⚠️  Validation PASSED with warnings")
            return True
        else:
            print("\n✅ Validation PASSED")
            return True

if __name__ == "__main__":
    validator = IntegrationValidator()
    success = validator.run_all()
    sys.exit(0 if success else 1)
