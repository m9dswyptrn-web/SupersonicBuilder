#!/usr/bin/env python3
"""
SonicBuilder Secure Build Script
Provides backup, security scanning, and safe build execution with rollback capability.

Usage:
  python scripts/secure_build.py --backup          # Create backup only
  python scripts/secure_build.py --build           # Secure build with auto-backup
  python scripts/secure_build.py --restore BACKUP  # Restore from backup
  python scripts/secure_build.py --list            # List available backups
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "backups"
OUTPUT_DIRS = ["output", "out", "dist", "downloads"]

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log(msg, color=None):
    """Print colored log message."""
    if color:
        print(f"{color}{msg}{Colors.END}")
    else:
        print(msg)

def run_cmd(cmd, check=True, capture=False):
    """Run shell command safely."""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True, cwd=ROOT)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, check=check, cwd=ROOT)
            return result.returncode, None, None
    except subprocess.CalledProcessError as e:
        return e.returncode, None, str(e)

def create_backup(backup_name=None):
    """Create backup of all output directories."""
    log("\n🔒 Creating secure backup...", Colors.CYAN)
    
    # Generate backup name with timestamp
    if not backup_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], 
                              capture_output=True, text=True, cwd=ROOT)
        commit_hash = commit.stdout.strip() if commit.returncode == 0 else "unknown"
        backup_name = f"backup_{timestamp}_{commit_hash}"
    else:
        # If backup_name was provided, still get commit_hash for metadata
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], 
                              capture_output=True, text=True, cwd=ROOT)
        commit_hash = commit.stdout.strip() if commit.returncode == 0 else "unknown"
    
    backup_path = BACKUP_DIR / backup_name
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Backup metadata
    metadata = {
        "created": datetime.now().isoformat(),
        "commit": commit_hash,
        "backed_up": []
    }
    
    # Backup each output directory
    for dirname in OUTPUT_DIRS:
        src = ROOT / dirname
        if src.exists():
            dst = backup_path / dirname
            log(f"  📦 Backing up {dirname}/...", Colors.BLUE)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            
            # Count files
            file_count = sum(1 for _ in dst.rglob("*") if _.is_file())
            total_size = sum(f.stat().st_size for f in dst.rglob("*") if f.is_file())
            
            metadata["backed_up"].append({
                "directory": dirname,
                "files": file_count,
                "size_bytes": total_size
            })
            log(f"    ✅ {file_count} files ({total_size / 1024 / 1024:.1f} MB)", Colors.GREEN)
    
    # Save metadata
    with open(backup_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    log(f"\n✅ Backup created: {backup_name}", Colors.GREEN)
    log(f"   Location: {backup_path}", Colors.BLUE)
    
    return backup_name, backup_path

def list_backups():
    """List all available backups."""
    log("\n📦 Available backups:", Colors.CYAN)
    
    if not BACKUP_DIR.exists():
        log("  No backups found.", Colors.YELLOW)
        return []
    
    backups = sorted(BACKUP_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not backups:
        log("  No backups found.", Colors.YELLOW)
        return []
    
    for backup in backups:
        if backup.is_dir():
            meta_file = backup / "metadata.json"
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                created = meta.get("created", "unknown")
                commit = meta.get("commit", "unknown")
                dirs = len(meta.get("backed_up", []))
                log(f"  • {backup.name}", Colors.BOLD)
                log(f"    Created: {created}")
                log(f"    Commit:  {commit}")
                log(f"    Dirs:    {dirs} directories backed up")
            else:
                log(f"  • {backup.name} (no metadata)", Colors.YELLOW)
    
    return [b.name for b in backups if b.is_dir()]

def restore_backup(backup_name):
    """Restore from a backup."""
    backup_path = BACKUP_DIR / backup_name
    
    if not backup_path.exists():
        log(f"❌ Backup not found: {backup_name}", Colors.RED)
        return False
    
    log(f"\n🔄 Restoring from backup: {backup_name}", Colors.CYAN)
    
    # Load metadata
    meta_file = backup_path / "metadata.json"
    if meta_file.exists():
        with open(meta_file) as f:
            meta = json.load(f)
        log(f"   Created: {meta.get('created', 'unknown')}", Colors.BLUE)
    
    # Restore each directory
    for dirname in OUTPUT_DIRS:
        src = backup_path / dirname
        if src.exists():
            dst = ROOT / dirname
            log(f"  📦 Restoring {dirname}/...", Colors.BLUE)
            
            # Remove existing directory
            if dst.exists():
                shutil.rmtree(dst)
            
            # Copy from backup
            shutil.copytree(src, dst)
            file_count = sum(1 for _ in dst.rglob("*") if _.is_file())
            log(f"    ✅ Restored {file_count} files", Colors.GREEN)
    
    log(f"\n✅ Restore complete!", Colors.GREEN)
    return True

def run_security_checks():
    """Run security checks before building."""
    log("\n🔒 Running security checks...", Colors.CYAN)
    
    checks_passed = True
    
    # 1. Check for subprocess hardening issues
    log("  🔍 Checking subprocess security...", Colors.BLUE)
    code, stdout, stderr = run_cmd("python3 tools/hardening/patch_subprocess.py --check", 
                                   check=False, capture=True)
    
    if stdout:
        result = json.loads(stdout)
        if result.get("total_changes", 0) > 0:
            log(f"    ⚠️  Found {result['total_changes']} hardening issues", Colors.YELLOW)
            log("    Run: make harden", Colors.YELLOW)
            checks_passed = False
        else:
            log("    ✅ No subprocess issues found", Colors.GREEN)
    
    # 2. Run Semgrep (if available)
    log("  🔍 Running Semgrep scan...", Colors.BLUE)
    code, _, _ = run_cmd("semgrep --config .semgrep.yml --quiet --json", 
                        check=False, capture=True)
    
    if code == 0:
        log("    ✅ Semgrep scan passed", Colors.GREEN)
    elif code == 127:
        log("    ⚠️  Semgrep not installed (skipping)", Colors.YELLOW)
    else:
        log("    ⚠️  Semgrep found issues", Colors.YELLOW)
        checks_passed = False
    
    # 3. Check git status
    log("  🔍 Checking git status...", Colors.BLUE)
    code, stdout, _ = run_cmd("git status --porcelain", check=False, capture=True)
    if stdout and stdout.strip():
        log("    ⚠️  Uncommitted changes detected", Colors.YELLOW)
    else:
        log("    ✅ Clean working tree", Colors.GREEN)
    
    return checks_passed

def run_build():
    """Run the build process."""
    log("\n🔨 Running build process...", Colors.CYAN)
    
    # Run make build-all (or appropriate build command)
    log("  📄 Building documentation...", Colors.BLUE)
    code, _, stderr = run_cmd("make build-docs 2>&1", check=False, capture=True)
    
    if code == 0:
        log("    ✅ Build succeeded", Colors.GREEN)
        return True
    else:
        log("    ❌ Build failed", Colors.RED)
        if stderr:
            log(f"    Error: {stderr}", Colors.RED)
        return False

def verify_build():
    """Verify build output."""
    log("\n✅ Verifying build output...", Colors.CYAN)
    
    found_pdfs = []
    for dirname in OUTPUT_DIRS:
        dir_path = ROOT / dirname
        if dir_path.exists():
            pdfs = list(dir_path.glob("*.pdf"))
            if pdfs:
                log(f"  📄 {dirname}/:", Colors.BLUE)
                for pdf in pdfs:
                    size_mb = pdf.stat().st_size / 1024 / 1024
                    log(f"    • {pdf.name} ({size_mb:.1f} MB)", Colors.GREEN)
                    found_pdfs.append(pdf)
    
    if found_pdfs:
        log(f"\n✅ Found {len(found_pdfs)} PDF(s)", Colors.GREEN)
        return True
    else:
        log("\n⚠️  No PDFs found", Colors.YELLOW)
        return False

def main():
    parser = argparse.ArgumentParser(description="SonicBuilder Secure Build Tool")
    parser.add_argument("--backup", action="store_true", help="Create backup only")
    parser.add_argument("--build", action="store_true", help="Run secure build with auto-backup")
    parser.add_argument("--restore", metavar="NAME", help="Restore from backup")
    parser.add_argument("--list", action="store_true", help="List available backups")
    parser.add_argument("--skip-security", action="store_true", help="Skip security checks")
    parser.add_argument("--force", action="store_true", help="Force build even if checks fail")
    
    args = parser.parse_args()
    
    # Print header
    log("=" * 70, Colors.BOLD)
    log("  SonicBuilder Secure Build Tool", Colors.HEADER)
    log("=" * 70, Colors.BOLD)
    
    # Handle commands
    if args.list:
        list_backups()
        return 0
    
    if args.restore:
        success = restore_backup(args.restore)
        return 0 if success else 1
    
    if args.backup:
        create_backup()
        return 0
    
    if args.build:
        # 1. Create backup
        backup_name, backup_path = create_backup()
        
        # 2. Run security checks
        if not args.skip_security:
            checks_passed = run_security_checks()
            
            if not checks_passed and not args.force:
                log("\n⚠️  Security checks failed. Use --force to build anyway.", Colors.YELLOW)
                log(f"   Backup saved at: {backup_path}", Colors.BLUE)
                return 1
        
        # 3. Run build
        build_success = run_build()
        
        if not build_success:
            log("\n❌ Build failed. Restore backup with:", Colors.RED)
            log(f"   python scripts/secure_build.py --restore {backup_name}", Colors.YELLOW)
            return 1
        
        # 4. Verify output
        verify_build()
        
        log("\n" + "=" * 70, Colors.BOLD)
        log("✅ Secure build complete!", Colors.GREEN)
        log("=" * 70, Colors.BOLD)
        log(f"\n💾 Backup available: {backup_name}", Colors.BLUE)
        log(f"   Restore with: python scripts/secure_build.py --restore {backup_name}", Colors.BLUE)
        
        return 0
    
    # No command specified
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
