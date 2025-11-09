#!/usr/bin/env python3
"""
Supersonic Clean Export Kit
Removes Replit bloat, prepares clean deployment package
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Directories/files to remove
REMOVE_DIRS = [
    ".git",
    ".replit", 
    ".cache",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
]

REMOVE_FILES = [
    "*.log",
    "*.tmp",
    "*.pyc",
    ".DS_Store",
    "Thumbs.db",
]

# Large file patterns to remove (optional)
LARGE_AUDIO_THRESHOLD_MB = 10

# Exclude patterns for ZIP
ZIP_EXCLUDES = [
    "*.git*",
    "*.cache*", 
    "__pycache__*",
    "*.tmp",
    "*.log",
    "*.tar",
    "*.zip",
    ".replit*",
    "node_modules*",
    ".venv*",
]

def run(cmd, check=True):
    """Run shell command"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        print(f"⚠ Command failed with code {result.returncode}")
        if check:
            sys.exit(result.returncode)
    return result.returncode

def get_dir_size(path="."):
    """Get directory size in MB"""
    total = 0
    for entry in Path(path).rglob("*"):
        if entry.is_file():
            total += entry.stat().st_size
    return total / (1024 * 1024)

def remove_dirs(dry_run=False):
    """Remove bloat directories"""
    removed = []
    for dirname in REMOVE_DIRS:
        for path in Path(".").rglob(dirname):
            if path.is_dir():
                size = get_dir_size(str(path))
                if dry_run:
                    print(f"[DRY-RUN] Would remove: {path} ({size:.1f}MB)")
                else:
                    print(f"Removing: {path} ({size:.1f}MB)")
                    shutil.rmtree(path, ignore_errors=True)
                removed.append(str(path))
    return removed

def remove_files(dry_run=False):
    """Remove bloat files"""
    removed = []
    for pattern in REMOVE_FILES:
        for path in Path(".").rglob(pattern):
            if path.is_file():
                size = path.stat().st_size / 1024
                if dry_run:
                    print(f"[DRY-RUN] Would remove: {path} ({size:.1f}KB)")
                else:
                    print(f"Removing: {path} ({size:.1f}KB)")
                    path.unlink()
                removed.append(str(path))
    return removed

def remove_large_audio(threshold_mb=10, dry_run=False):
    """Remove large audio files (optional)"""
    removed = []
    for pattern in ["*.wav", "*.mp3", "*.flac"]:
        for path in Path(".").rglob(pattern):
            if path.is_file():
                size_mb = path.stat().st_size / (1024 * 1024)
                if size_mb > threshold_mb:
                    if dry_run:
                        print(f"[DRY-RUN] Would remove large audio: {path} ({size_mb:.1f}MB)")
                    else:
                        print(f"Removing large audio: {path} ({size_mb:.1f}MB)")
                        path.unlink()
                    removed.append(str(path))
    return removed

def create_zip(zip_name, dry_run=False):
    """Create clean ZIP archive"""
    exclude_args = " ".join([f'-x "{pattern}"' for pattern in ZIP_EXCLUDES])
    cmd = f'zip -r {zip_name} . {exclude_args}'
    
    if dry_run:
        print(f"[DRY-RUN] Would create: {zip_name}")
        print(f"[DRY-RUN] Command: {cmd}")
        return
    
    print(f"\nCreating ZIP archive: {zip_name}")
    run(cmd, check=False)
    
    if os.path.exists(zip_name):
        size_mb = os.path.getsize(zip_name) / (1024 * 1024)
        print(f"✅ Created: {zip_name} ({size_mb:.1f}MB)")
    else:
        print(f"❌ Failed to create {zip_name}")

def main():
    parser = argparse.ArgumentParser(description="Clean and export Supersonic project")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without doing it")
    parser.add_argument("--no-fresh", action="store_true", help="Don't remove .git (keep git history)")
    parser.add_argument("--keep-audio", action="store_true", help="Keep all audio files (don't remove large WAVs)")
    parser.add_argument("--zip-name", default="SonicBuilderSupersonic_Clean.zip", help="Output ZIP filename")
    args = parser.parse_args()

    print("=== Supersonic Clean Export Kit ===\n")
    
    # Detect Replit environment and skip protected directories
    is_replit = os.path.exists("/.replit") or os.getenv("REPL_ID") or os.getenv("REPLIT_DB_URL")
    if is_replit:
        print("⚠️  Replit environment detected - skipping protected directories")
        print("ℹ️  Protected files will be excluded via ZIP patterns instead\n")
        # Skip Replit-protected directories
        protected = [".git", ".replit", ".cache"]
        for d in protected:
            if d in REMOVE_DIRS:
                REMOVE_DIRS.remove(d)
    
    # Calculate initial size
    initial_size = get_dir_size(".")
    print(f"📊 Initial size: {initial_size:.1f}MB\n")

    # Optionally keep .git
    if args.no_fresh and ".git" in REMOVE_DIRS:
        REMOVE_DIRS.remove(".git")
        print("ℹ️  Keeping .git directory")

    # Remove directories
    print("🧹 Removing bloat directories...")
    removed_dirs = remove_dirs(args.dry_run)
    
    # Remove files
    print("\n🧹 Removing bloat files...")
    removed_files = remove_files(args.dry_run)
    
    # Remove large audio (optional)
    if not args.keep_audio:
        print(f"\n🧹 Removing large audio files (>{LARGE_AUDIO_THRESHOLD_MB}MB)...")
        removed_audio = remove_large_audio(LARGE_AUDIO_THRESHOLD_MB, args.dry_run)
    else:
        print("\nℹ️  Keeping all audio files")
        removed_audio = []

    # Calculate final size
    final_size = get_dir_size(".")
    saved = initial_size - final_size

    print(f"\n📊 Final size: {final_size:.1f}MB")
    print(f"💾 Space saved: {saved:.1f}MB ({(saved/initial_size*100):.1f}%)")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"   - Directories removed: {len(removed_dirs)}")
    print(f"   - Files removed: {len(removed_files)}")
    print(f"   - Large audio removed: {len(removed_audio)}")

    if args.dry_run:
        print("\n[DRY-RUN] No changes were made. Run without --dry-run to apply changes.")
        return

    # Create ZIP
    print(f"\n📦 Creating clean export package...")
    create_zip(args.zip_name, args.dry_run)

    print("\n✅ Export complete!")
    print(f"\n📦 Clean package: {args.zip_name}")
    print("\n🚀 Next steps:")
    print(f"   1. Extract: unzip {args.zip_name} -d SonicBuilderSupersonic")
    print(f"   2. Deploy: cd SonicBuilderSupersonic")
    print(f"   3. Run: python3 deploy_to_github.py --owner ChristopherElgin --repo SonicBuilderSupersonic --version v1.0.0 --public --fresh")

if __name__ == "__main__":
    main()
