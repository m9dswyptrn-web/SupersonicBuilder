#!/usr/bin/env python3
"""
Supersonic Clean & Export
-------------------------
One-click cleaner to trim Replit/git bloat and make a lean ZIP for GitHub deploy.

Usage (from project root):
    python3 clean_and_export.py
Optional flags:
    --zip-name SonicBuilderSupersonic_Clean.zip
    --dry-run      (show what would be removed/packed)
    --no-fresh     (keep existing .git history - NOT recommended)
    --keep-logs    (avoid deleting .log files)
    --include-ext ".pdf,.apk"  (extra file extensions to force-include)
    --exclude-ext ".mp4"       (extra file extensions to skip)
    --extra-exclude ".venv,.mypy_cache" (comma list of directories to skip)
Safe-by-default: never deletes your curated voice packs in assets/audio/* or docs/assets/*
"""
import argparse
import os
import shutil
from pathlib import Path
from typing import Set, Iterable
import zipfile

# -------- Configuration (safe defaults) --------
SAFE_KEEP_DIRS = {
    "assets/audio",            # curated voice packs
    "docs/assets",             # docs badges/gifs/voice pack previews
}
DEFAULT_DIR_EXCLUDES = {
    ".git", ".cache", ".replit", ".ruff_cache", ".pytest_cache",
    "__pycache__", ".mypy_cache", ".DS_Store", ".idea", ".vscode",
    "node_modules", ".venv", ".gradle", ".terraform", ".next", "dist",
    ".parcel-cache", ".tox", ".coverage", ".coverage_html"
}
DEFAULT_FILE_EXCLUDES = {
    ".DS_Store", ".env.local", ".envrc", ".coverage",
}
DEFAULT_EXT_EXCLUDES = {
    ".tmp", ".log", ".swp", ".swo", ".pyc",
}
DEFAULT_ZIP_NAME = "SonicBuilderSupersonic_Clean.zip"

def human_bytes(n: int) -> str:
    for unit in ("B","KB","MB","GB","TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

def dir_size(path: Path) -> int:
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except Exception:
                pass
    return total

def inside_any(child: Path, roots: Iterable[Path]) -> bool:
    child = child.resolve()
    for r in roots:
        try:
            r = r.resolve()
            if r in child.parents or r == child:
                return True
        except Exception:
            pass
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip-name", default=DEFAULT_ZIP_NAME)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-fresh", action="store_true", help="Keep .git history (not recommended)")
    ap.add_argument("--keep-logs", action="store_true")
    ap.add_argument("--include-ext", default="", help="Comma list of extra extensions to force-include")
    ap.add_argument("--exclude-ext", default="", help="Comma list of extra extensions to exclude")
    ap.add_argument("--extra-exclude", default="", help="Comma list of directories to exclude")
    args = ap.parse_args()

    project_root = Path(".").resolve()
    start_size = dir_size(project_root)

    # Resolve paths to keep protected
    protected_dirs = { (project_root / d).resolve() for d in SAFE_KEEP_DIRS if (project_root / d).exists() }

    # 1) Fresh init: remove .git and heavy caches (safe — never touches protected_dirs)
    to_remove_dirs = set(DEFAULT_DIR_EXCLUDES)
    to_remove_dirs |= set([d.strip() for d in args.extra_exclude.split(",") if d.strip()])

    actually_removed = []

    for dname in to_remove_dirs:
        p = (project_root / dname)
        if p.exists() and p.is_dir() and not inside_any(p, protected_dirs):
            if args.dry_run:
                print(f"[dry-run] would remove: {p}")
            else:
                try:
                    shutil.rmtree(p)
                    actually_removed.append(str(p))
                except Exception as e:
                    print(f"[warn] could not remove {p}: {e}")

    # Optionally remove .git
    if not args.no_fresh:
        g = project_root / ".git"
        if g.exists() and g.is_dir():
            if args.dry_run:
                print(f"[dry-run] would remove: {g}")
            else:
                try:
                    shutil.rmtree(g)
                    actually_removed.append(str(g))
                except Exception as e:
                    print(f"[warn] could not remove {g}: {e}")
    else:
        print("[info] Keeping .git history (requested by --no-fresh)")

    # 2) Prepare inclusion/exclusion sets for zipping
    ext_excludes: Set[str] = set(DEFAULT_EXT_EXCLUDES)
    if args.keep_logs:
        ext_excludes.discard(".log")

    if args.exclude_ext:
        for ext in args.exclude_ext.split(","):
            ext = ext.strip()
            if ext and not ext.startswith("."):
                ext = "." + ext
            if ext:
                ext_excludes.add(ext.lower())

    extra_include_ext = set()
    if args.include_ext:
        for ext in args.include_ext.split(","):
            ext = ext.strip()
            if ext and not ext.startswith("."):
                ext = "." + ext
            if ext:
                extra_include_ext.add(ext.lower())

    # 3) Create ZIP (skipping excluded dirs/files, but never skipping protected dirs)
    zip_path = project_root / args.zip_name
    if zip_path.exists():
        try:
            zip_path.unlink()
        except Exception:
            pass

    def should_skip(file_path: Path) -> bool:
        # Never skip protected dirs
        if inside_any(file_path, protected_dirs):
            return False
        # Skip excluded directories by name
        for dname in DEFAULT_DIR_EXCLUDES | set([d.strip() for d in args.extra_exclude.split(",") if d.strip()]):
            if dname and dname in file_path.parts:
                return True
        # Skip file names explicitly listed
        if file_path.name in DEFAULT_FILE_EXCLUDES:
            return True
        # Skip by extension
        ext = file_path.suffix.lower()
        if ext in ext_excludes and ext not in extra_include_ext:
            return True
        return False

    packed_count = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in project_root.rglob("*"):
            if p.is_file():
                if should_skip(p):
                    continue
                rel = p.relative_to(project_root)
                if args.dry_run:
                    print(f"[dry-run] would add: {rel}")
                else:
                    zf.write(p, arcname=rel)
                    packed_count += 1

    end_size = zip_path.stat().st_size if zip_path.exists() else 0

    print("\n=== Supersonic Clean & Export Summary ===")
    print(f" Project root: {project_root}")
    print(f" Removed items: {len(actually_removed)}")
    if actually_removed:
        for item in actually_removed:
            print(f"  - {item}")
    print(f" Original size on disk: {human_bytes(start_size)}")
    print(f" ZIP created: {zip_path.name} -> {human_bytes(end_size)} with {packed_count} files")
    print(" Status: SUCCESS (ready to upload to GitHub via deploy_to_github.py)")

if __name__ == "__main__":
    main()
