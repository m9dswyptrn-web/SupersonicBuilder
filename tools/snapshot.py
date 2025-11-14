#!/usr/bin/env python3
"""
Supersonic Snapshot Engine

Creates a timestamped snapshot under snapshots/snapshot-YYYYmmdd-HHMMSS/

Each snapshot contains:
- logs/               (if present)
- metrics/            (if present)
- docs/sonic/         (if present)
- version.txt         (if present)
- any extra files we add later

Also writes:
- snapshot.json       (metadata for this snapshot)
- appends a line to snapshots/index.jsonl (snapshot index)
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAP_ROOT = ROOT / "snapshots"


def copy_if_exists(src: Path, dest: Path):
    if src.is_dir():
        # Copy directory tree, merge if already exists
        shutil.copytree(src, dest, dirs_exist_ok=True)
        return True
    if src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return True
    return False


def make_snapshot():
    SNAP_ROOT.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    snap_dir = SNAP_ROOT / f"snapshot-{ts}"
    snap_dir.mkdir(parents=True, exist_ok=True)

    copied = []

    # What we want to capture
    targets = [
        ("logs", ROOT / "logs", "logs"),
        ("metrics", ROOT / "metrics", "metrics"),
        ("docs/sonic", ROOT / "docs" / "sonic", "docs/sonic"),
        ("version.txt", ROOT / "version.txt", "version.txt"),
        # Add more here later as needed
    ]

    for label, path, dest_path in targets:
        dest = snap_dir / dest_path
        if copy_if_exists(path, dest):
            copied.append({
                "label": label,
                "src": str(path.relative_to(ROOT)),
                "dest": str(dest.relative_to(ROOT)),
                "type": "dir" if path.is_dir() else "file",
            })

    meta = {
        "snapshot_id": f"snapshot-{ts}",
        "created_utc": datetime.utcnow().isoformat() + "Z",
        "root": str(ROOT),
        "copied": copied,
        "env": {
            "GIT_BRANCH": os.environ.get("GIT_BRANCH") or "",
            "REPLIT_PROJECT": os.environ.get("REPL_SLUG") or "",
        },
    }

    # Write per-snapshot metadata
    meta_path = snap_dir / "snapshot.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Append to index.jsonl
    index_path = SNAP_ROOT / "index.jsonl"
    with index_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(meta) + "\n")

    return meta


def main():
    meta = make_snapshot()
    print("✅ Supersonic snapshot created")
    print(f"   ID:     {meta['snapshot_id']}")
    print(f"   Folder: snapshots/{meta['snapshot_id']}")
    print(f"   Files:  {len(meta['copied'])} items captured")
    if not meta["copied"]:
        print("⚠️  No snapshot sources were found. "
              "Create logs/ and metrics/ first or run ./rs health / ./rs metrics.")
    else:
        print("   Tip: commit snapshots/index.jsonl if you want a history journal,")
        print("        but you can .gitignore the snapshots/* folders if they get large.")


if __name__ == "__main__":
    main()
