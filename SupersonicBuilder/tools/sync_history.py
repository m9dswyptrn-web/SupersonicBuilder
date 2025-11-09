#!/usr/bin/env python3
"""
sync_history.py
Persistent history tracking for sync operations.

Stores sync metadata in JSONL format for analytics and debugging.
Provides query interface for metrics dashboard.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter

class SyncHistory:
    """Manages persistent sync operation history."""
    
    def __init__(self, history_file: str = ".cache/sync_history.jsonl", max_entries: int = 1000):
        self.history_file = Path(history_file)
        self.max_entries = max_entries
        self._ensure_dir()
    
    def _ensure_dir(self):
        """Ensure history file directory exists."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def record(self, event: Dict[str, Any]):
        """
        Record a sync event.
        
        Args:
            event: Dict with keys:
                - timestamp: ISO 8601 timestamp (auto-added if missing)
                - event_type: 'sync_start', 'sync_success', 'sync_failure', 'rate_limit_hit'
                - duration_sec: Time taken (for completed events)
                - files_changed: Number of files changed
                - commit_hash: Git commit SHA
                - error_msg: Error message (for failures)
                - throttled: Boolean if rate limited
        """
        if "timestamp" not in event:
            event["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        try:
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
            
            # Rotate if too large
            self._rotate_if_needed()
        except Exception as e:
            print(f"[WARN] Failed to record sync history: {e}")
    
    def _rotate_if_needed(self):
        """Keep only the last max_entries records."""
        try:
            if not self.history_file.exists():
                return
            
            # Read all entries
            entries = self.load_all()
            
            if len(entries) > self.max_entries:
                # Keep only the most recent max_entries
                recent = entries[-self.max_entries:]
                
                # Rewrite file
                with open(self.history_file, "w", encoding="utf-8") as f:
                    for entry in recent:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[WARN] Failed to rotate sync history: {e}")
    
    def load_all(self) -> List[Dict[str, Any]]:
        """Load all history entries."""
        if not self.history_file.exists():
            return []
        
        entries = []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            print(f"[WARN] Failed to load sync history: {e}")
        
        return entries
    
    def get_recent(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get entries from the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_iso = cutoff.isoformat() + "Z"
        
        entries = self.load_all()
        return [e for e in entries if e.get("timestamp", "") >= cutoff_iso]
    
    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate summary statistics for the last N hours.
        
        Returns:
            Dict with:
                - total_syncs: Total sync attempts
                - successful_syncs: Number of successful syncs
                - failed_syncs: Number of failed syncs
                - success_rate: Percentage (0-100)
                - avg_duration_sec: Average sync duration
                - total_files_changed: Sum of all files changed
                - rate_limit_hits: Number of times rate limited
                - last_success: ISO timestamp of last successful sync
                - last_failure: ISO timestamp of last failed sync
        """
        entries = self.get_recent(hours)
        
        successes = [e for e in entries if e.get("event_type") == "sync_success"]
        failures = [e for e in entries if e.get("event_type") == "sync_failure"]
        rate_limits = [e for e in entries if e.get("event_type") == "rate_limit_hit"]
        
        total = len(successes) + len(failures)
        success_count = len(successes)
        success_rate = (success_count / total * 100) if total > 0 else 0.0
        
        # Average duration (only for successful syncs)
        durations = [e.get("duration_sec", 0) for e in successes if "duration_sec" in e]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        # Total files changed
        files_changed = sum(e.get("files_changed", 0) for e in successes)
        
        # Last events
        last_success = successes[-1]["timestamp"] if successes else None
        last_failure = failures[-1]["timestamp"] if failures else None
        
        return {
            "total_syncs": total,
            "successful_syncs": success_count,
            "failed_syncs": len(failures),
            "success_rate": round(success_rate, 1),
            "avg_duration_sec": round(avg_duration, 2),
            "total_files_changed": files_changed,
            "rate_limit_hits": len(rate_limits),
            "last_success": last_success,
            "last_failure": last_failure,
        }
    
    def get_hourly_counts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get hourly sync counts for sparkline visualization.
        
        Returns:
            List of dicts with:
                - hour: ISO timestamp (hour precision)
                - total: Total syncs in that hour
                - successful: Successful syncs
                - failed: Failed syncs
        """
        entries = self.get_recent(hours)
        
        # Group by hour
        hourly_data = {}
        for entry in entries:
            ts = entry.get("timestamp", "")
            if not ts:
                continue
            
            # Truncate to hour
            hour = ts[:13] + ":00:00Z"
            
            if hour not in hourly_data:
                hourly_data[hour] = {"total": 0, "successful": 0, "failed": 0}
            
            event_type = entry.get("event_type", "")
            if event_type in ("sync_success", "sync_failure"):
                hourly_data[hour]["total"] += 1
                if event_type == "sync_success":
                    hourly_data[hour]["successful"] += 1
                else:
                    hourly_data[hour]["failed"] += 1
        
        # Convert to sorted list
        result = []
        for hour in sorted(hourly_data.keys()):
            result.append({
                "hour": hour,
                **hourly_data[hour]
            })
        
        return result


# Global singleton
_history_instance: SyncHistory | None = None

def get_history(history_file: str = ".cache/sync_history.jsonl", max_entries: int = 1000) -> SyncHistory:
    """Get the global history instance."""
    global _history_instance
    if _history_instance is None:
        _history_instance = SyncHistory(history_file, max_entries)
    return _history_instance


if __name__ == "__main__":
    # CLI test utility
    import sys
    history = get_history()
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats = history.get_stats(hours=24)
        print(json.dumps(stats, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "hourly":
        hourly = history.get_hourly_counts(hours=24)
        print(json.dumps(hourly, indent=2))
    else:
        entries = history.get_recent(hours=24)
        print(f"Last 24h: {len(entries)} entries")
        for e in entries[-10:]:
            print(json.dumps(e))
