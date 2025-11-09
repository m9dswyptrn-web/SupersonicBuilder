#!/usr/bin/env python3
"""
Supersonic Full Project Snapshot Tool
Creates a comprehensive zip archive of the entire project.
"""
import os
import zipfile
import time
from pathlib import Path

def should_exclude(path):
    """Determine if a path should be excluded from snapshot"""
    exclude_patterns = [
        '.git',
        '__pycache__',
        '.pytest_cache',
        '.mypy_cache',
        'node_modules',
        '.venv',
        'venv',
        '*.pyc',
        '*.pyo',
        '.DS_Store',
        '.bak',
        'attached_assets',
        'tmp',
        '.reload'
    ]
    
    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str or path_str.endswith(pattern.replace('*', '')):
            return True
    return False

def create_snapshot(output_dir="docs"):
    """Create a full project snapshot"""
    timestamp = int(time.time())
    snapshot_name = f"Supersonic_Full_Project_Snapshot_{timestamp}.zip"
    snapshot_path = os.path.join(output_dir, snapshot_name)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating snapshot: {snapshot_path}")
    file_count = 0
    
    with zipfile.ZipFile(snapshot_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            for file in files:
                filepath = os.path.join(root, file)
                if should_exclude(filepath):
                    continue
                
                try:
                    arcname = filepath[2:] if filepath.startswith('./') else filepath
                    zipf.write(filepath, arcname)
                    file_count += 1
                    if file_count % 100 == 0:
                        print(f"  Added {file_count} files...")
                except Exception as e:
                    print(f"  ⚠️  Skipped {filepath}: {e}")
    
    size_mb = os.path.getsize(snapshot_path) / 1024 / 1024
    print(f"✅ Snapshot created: {snapshot_path}")
    print(f"   Files: {file_count}")
    print(f"   Size: {size_mb:.2f} MB")
    
    return snapshot_path

if __name__ == "__main__":
    create_snapshot()
