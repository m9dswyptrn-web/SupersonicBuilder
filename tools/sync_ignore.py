#!/usr/bin/env python3
"""
sync_ignore.py
Pattern-based exclusion for sync operations.

Supports .gitignore-style patterns for excluding files from auto-sync.
"""

import fnmatch
from pathlib import Path
from typing import List, Set

class SyncIgnore:
    """Manages file exclusion patterns for sync operations."""
    
    def __init__(self, patterns: List[str] | None = None, ignore_file: str = ".syncignore"):
        self.ignore_file = Path(ignore_file)
        self.patterns = patterns or []
        
        # Load patterns from file if it exists
        if self.ignore_file.exists():
            self.patterns.extend(self._load_patterns())
    
    def _load_patterns(self) -> List[str]:
        """Load patterns from .syncignore file."""
        patterns = []
        try:
            with open(self.ignore_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            print(f"[WARN] Failed to load {self.ignore_file}: {e}")
        
        return patterns
    
    def should_ignore(self, file_path: str) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            file_path: Path to check (relative to repo root)
        
        Returns:
            True if file should be ignored, False otherwise
        """
        if not self.patterns:
            return False
        
        # Normalize path (remove leading ./)
        path = file_path.lstrip("./")
        
        for pattern in self.patterns:
            # Handle negation (!)
            if pattern.startswith("!"):
                # Negation patterns mean "don't ignore"
                if self._matches_pattern(path, pattern[1:]):
                    return False
            else:
                # Normal patterns mean "ignore"
                if self._matches_pattern(path, pattern):
                    return True
        
        return False
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if path matches pattern (gitignore-style).
        
        Supports:
        - * (matches any characters except /)
        - ** (matches any characters including /)
        - / suffix (matches directories only)
        """
        # Directory-only pattern (ends with /)
        if pattern.endswith("/"):
            # Check if path is a directory or has this directory as prefix
            dir_pattern = pattern.rstrip("/")
            return path.startswith(dir_pattern + "/") or path == dir_pattern
        
        # Pattern with ** (recursive wildcard)
        if "**" in pattern:
            # Convert ** to regex-compatible pattern
            pattern = pattern.replace("**", "GLOBSTAR_PLACEHOLDER")
            pattern = pattern.replace("*", "[^/]*")  # * matches anything except /
            pattern = pattern.replace("GLOBSTAR_PLACEHOLDER", ".*")  # ** matches anything
            
            import re
            return re.match(f"^{pattern}$", path) is not None
        
        # Simple fnmatch for other patterns
        return fnmatch.fnmatch(path, pattern)
    
    def filter_files(self, files: List[str]) -> List[str]:
        """Filter a list of files, removing ignored ones."""
        return [f for f in files if not self.should_ignore(f)]
    
    def get_ignored_count(self, files: List[str]) -> int:
        """Count how many files would be ignored."""
        return len([f for f in files if self.should_ignore(f)])


def get_sync_ignore(config=None) -> SyncIgnore:
    """Get SyncIgnore instance from config."""
    if config is None:
        from tools.sync_config import get_config
        config = get_config()
    
    return SyncIgnore(patterns=config.exclude_patterns)


if __name__ == "__main__":
    # CLI test utility
    import subprocess
    
    # Get all tracked + untracked files
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, check=True
        )
        tracked = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, check=True
        )
        all_files = set(result.stdout.strip().split("\n") + tracked.stdout.strip().split("\n"))
        all_files = [f for f in all_files if f]
    except Exception:
        all_files = []
    
    ignore = get_sync_ignore()
    
    print(f"Total files: {len(all_files)}")
    print(f"Ignored: {ignore.get_ignored_count(all_files)}")
    print(f"Will sync: {len(ignore.filter_files(all_files))}")
    
    print("\n🚫 Ignored files (first 20):")
    ignored_files = [f for f in all_files if ignore.should_ignore(f)]
    for f in ignored_files[:20]:
        print(f"  - {f}")
    
    if len(ignored_files) > 20:
        print(f"  ... and {len(ignored_files) - 20} more")
