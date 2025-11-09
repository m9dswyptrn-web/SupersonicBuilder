#!/usr/bin/env python3
import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(".")
IGNORE_DIRS = {'.git', '__pycache__', '.cache', '.pythonlibs', 'node_modules', 'venv', 'env'}
LARGE_FILE_THRESHOLD = 95 * 1024 * 1024  # 95 MB

def get_file_hash(filepath):
    """Get MD5 hash of file for duplicate detection."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None

def human_size(bytes):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def inventory_repository():
    """Create comprehensive repository inventory."""
    
    inventory = {
        'total_files': 0,
        'total_size': 0,
        'large_files': [],  # Files > 95 MB
        'duplicates': [],   # Duplicate files by hash
        'file_types': defaultdict(int),
        'directory_sizes': {},
        'errors': []
    }
    
    # Track files by hash for duplicate detection
    hash_map = defaultdict(list)
    
    print("📊 Scanning repository...")
    
    for root, dirs, files in os.walk(ROOT):
        # Remove ignored directories from traversal
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        root_path = Path(root)
        dir_size = 0
        
        for filename in files:
            filepath = root_path / filename
            
            try:
                size = filepath.stat().st_size
                inventory['total_files'] += 1
                inventory['total_size'] += size
                dir_size += size
                
                # Track file type
                ext = filepath.suffix.lower() or 'no_extension'
                inventory['file_types'][ext] += 1
                
                # Check for large files
                if size >= LARGE_FILE_THRESHOLD:
                    inventory['large_files'].append({
                        'path': str(filepath),
                        'size': size,
                        'size_mb': size / (1024 * 1024),
                        'size_human': human_size(size)
                    })
                
                # Check for duplicates (only for files > 1MB to save time)
                if size > 1024 * 1024:
                    file_hash = get_file_hash(filepath)
                    if file_hash:
                        hash_map[file_hash].append({
                            'path': str(filepath),
                            'size': size,
                            'size_human': human_size(size)
                        })
                        
            except Exception as e:
                inventory['errors'].append({
                    'path': str(filepath),
                    'error': str(e)
                })
        
        if dir_size > 0:
            inventory['directory_sizes'][str(root_path)] = {
                'size': dir_size,
                'size_human': human_size(dir_size)
            }
    
    # Find duplicates
    for file_hash, file_list in hash_map.items():
        if len(file_list) > 1:
            inventory['duplicates'].append({
                'hash': file_hash,
                'count': len(file_list),
                'files': file_list,
                'total_wasted': sum(f['size'] for f in file_list[1:]),
                'wasted_human': human_size(sum(f['size'] for f in file_list[1:]))
            })
    
    # Sort large files by size
    inventory['large_files'].sort(key=lambda x: x['size'], reverse=True)
    
    # Sort duplicates by wasted space
    inventory['duplicates'].sort(key=lambda x: x['total_wasted'], reverse=True)
    
    # Convert defaultdict to regular dict for JSON serialization
    inventory['file_types'] = dict(inventory['file_types'])
    
    return inventory

def generate_report(inventory):
    """Generate human-readable report."""
    
    print("\n" + "="*70)
    print("📊 REPOSITORY INVENTORY REPORT")
    print("="*70)
    
    print(f"\n📁 Total Files: {inventory['total_files']:,}")
    print(f"💾 Total Size: {human_size(inventory['total_size'])}")
    
    print(f"\n⚠️  Large Files (>{LARGE_FILE_THRESHOLD/(1024*1024):.0f} MB): {len(inventory['large_files'])}")
    if inventory['large_files']:
        print("\nTop 20 Largest Files:")
        for i, f in enumerate(inventory['large_files'][:20], 1):
            print(f"  {i:2d}. {f['size_human']:>10s}  {f['path']}")
    
    print(f"\n🔄 Duplicate File Groups: {len(inventory['duplicates'])}")
    if inventory['duplicates']:
        total_wasted = sum(d['total_wasted'] for d in inventory['duplicates'])
        print(f"   Total Wasted Space: {human_size(total_wasted)}")
        print("\nTop 10 Duplicate Groups:")
        for i, dup in enumerate(inventory['duplicates'][:10], 1):
            print(f"\n  {i}. {dup['wasted_human']} wasted ({dup['count']} copies):")
            for f in dup['files'][:3]:
                print(f"     - {f['path']}")
            if len(dup['files']) > 3:
                print(f"     ... and {len(dup['files'])-3} more")
    
    print(f"\n📋 File Types Distribution:")
    sorted_types = sorted(inventory['file_types'].items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_types[:15]:
        print(f"  {ext:20s}: {count:5d} files")
    
    print(f"\n📂 Largest Directories:")
    sorted_dirs = sorted(inventory['directory_sizes'].items(), 
                        key=lambda x: x[1]['size'], reverse=True)
    for path, info in sorted_dirs[:15]:
        print(f"  {info['size_human']:>10s}  {path}")
    
    if inventory['errors']:
        print(f"\n❌ Errors Encountered: {len(inventory['errors'])}")
        for err in inventory['errors'][:5]:
            print(f"  - {err['path']}: {err['error']}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    print("🔍 Starting repository audit...\n")
    inventory = inventory_repository()
    
    # Save to JSON
    with open('repository_inventory.json', 'w') as f:
        json.dump(inventory, f, indent=2)
    print("\n✅ Inventory saved to: repository_inventory.json")
    
    # Generate report
    generate_report(inventory)
    
    print("\n✅ Phase 1 Complete: Repository Inventory")
