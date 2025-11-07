#!/usr/bin/env python3
"""
sync_throttle.py
Smart rate limiting with exponential backoff for sync operations.

Prevents excessive sync operations and repository spam.
"""

import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple

class SyncThrottle:
    """Rate limiter with exponential backoff."""
    
    def __init__(self, 
                 max_per_hour: int = 20,
                 backoff_enabled: bool = True,
                 backoff_initial_sec: int = 60,
                 backoff_max_sec: int = 3600,
                 state_file: str = ".cache/sync_throttle.json"):
        self.max_per_hour = max_per_hour
        self.backoff_enabled = backoff_enabled
        self.backoff_initial_sec = backoff_initial_sec
        self.backoff_max_sec = backoff_max_sec
        self.state_file = Path(state_file)
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load throttle state from disk."""
        if not self.state_file.exists():
            return {
                "sync_times": [],
                "consecutive_failures": 0,
                "last_failure_time": None,
            }
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "sync_times": [],
                "consecutive_failures": 0,
                "last_failure_time": None,
            }
    
    def _save_state(self):
        """Save throttle state to disk."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to save throttle state: {e}")
    
    def can_sync(self) -> Tuple[bool, str]:
        """
        Check if sync is allowed.
        
        Returns:
            (allowed: bool, reason: str)
        """
        now = time.time()
        
        # Clean up old sync times (older than 1 hour)
        cutoff = now - 3600
        self.state["sync_times"] = [t for t in self.state["sync_times"] if t > cutoff]
        
        # Check rate limit
        if len(self.state["sync_times"]) >= self.max_per_hour:
            return False, f"Rate limit: {len(self.state['sync_times'])}/{self.max_per_hour} syncs in last hour"
        
        # Check backoff after failures
        if self.backoff_enabled and self.state["consecutive_failures"] > 0:
            last_failure = self.state.get("last_failure_time")
            if last_failure:
                # Calculate backoff delay (exponential)
                backoff_delay = min(
                    self.backoff_initial_sec * (2 ** (self.state["consecutive_failures"] - 1)),
                    self.backoff_max_sec
                )
                
                time_since_failure = now - last_failure
                if time_since_failure < backoff_delay:
                    remaining = int(backoff_delay - time_since_failure)
                    return False, f"Backoff: {remaining}s remaining after {self.state['consecutive_failures']} failures"
        
        return True, "OK"
    
    def record_sync_start(self):
        """Record a sync attempt."""
        self.state["sync_times"].append(time.time())
        self._save_state()
    
    def record_sync_success(self):
        """Record a successful sync (resets backoff)."""
        self.state["consecutive_failures"] = 0
        self.state["last_failure_time"] = None
        self._save_state()
    
    def record_sync_failure(self):
        """Record a failed sync (increases backoff)."""
        self.state["consecutive_failures"] += 1
        self.state["last_failure_time"] = time.time()
        self._save_state()
    
    def get_status(self) -> dict:
        """Get current throttle status."""
        now = time.time()
        cutoff = now - 3600
        recent_syncs = [t for t in self.state["sync_times"] if t > cutoff]
        
        allowed, reason = self.can_sync()
        
        # Calculate backoff info
        backoff_info = None
        if self.state["consecutive_failures"] > 0:
            backoff_delay = min(
                self.backoff_initial_sec * (2 ** (self.state["consecutive_failures"] - 1)),
                self.backoff_max_sec
            )
            last_failure = self.state.get("last_failure_time", now)
            time_since_failure = now - last_failure
            remaining = max(0, int(backoff_delay - time_since_failure))
            
            backoff_info = {
                "active": remaining > 0,
                "failures": self.state["consecutive_failures"],
                "delay_sec": backoff_delay,
                "remaining_sec": remaining,
            }
        
        return {
            "allowed": allowed,
            "reason": reason,
            "syncs_last_hour": len(recent_syncs),
            "max_per_hour": self.max_per_hour,
            "backoff": backoff_info,
        }


def get_throttle(config=None) -> SyncThrottle:
    """Get throttle instance from config."""
    if config is None:
        from tools.sync_config import get_config
        config = get_config()
    
    return SyncThrottle(
        max_per_hour=config.max_per_hour,
        backoff_enabled=config.backoff_enabled,
        backoff_initial_sec=config.backoff_initial_sec,
        backoff_max_sec=config.backoff_max_sec,
    )


if __name__ == "__main__":
    # CLI test utility
    import sys
    throttle = get_throttle()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status = throttle.get_status()
        print(json.dumps(status, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "can-sync":
        allowed, reason = throttle.can_sync()
        print(f"Allowed: {allowed}")
        print(f"Reason: {reason}")
    else:
        print("Usage: python sync_throttle.py [status|can-sync]")
