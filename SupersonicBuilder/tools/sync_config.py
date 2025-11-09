#!/usr/bin/env python3
"""
sync_config.py
Configuration loader for Supersonic Continuous Sync.

Loads settings from .supersonic-sync.conf (YAML) with env var overrides.
Provides sensible defaults for all settings.
"""

import os
import yaml
import copy
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "git": {
        "user": "SonicBuilder Bot",
        "email": "bot@sonicbuilder.local",
        "remote_url": None,
    },
    "sync": {
        "interval_sec": 300,
        "pull_enabled": True,
        "max_per_hour": 20,
        "backoff_enabled": True,
        "backoff_initial_sec": 60,
        "backoff_max_sec": 3600,
    },
    "exclude_patterns": [
        "build/",
        "*.pyc",
        "__pycache__/",
        ".cache/",
        "logs/*.log",
        "logs/archive/",
        "node_modules/",
        ".env",
        ".env.local",
    ],
    "metrics": {
        "history_enabled": True,
        "history_max_entries": 1000,
        "history_file": ".cache/sync_history.jsonl",
    },
    "webhooks": {
        "enabled": False,
        "urls": [],
        "events": ["sync_success", "sync_failure"],
        "timeout_sec": 5,
        "retry_enabled": True,
        "max_retries": 3,
    },
}

class SyncConfig:
    """Centralized configuration for sync operations."""
    
    def __init__(self, config_path: str = ".supersonic-sync.conf"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self) -> dict:
        """Load config from YAML file, falling back to defaults."""
        if not self.config_path.exists():
            return copy.deepcopy(DEFAULT_CONFIG)
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            
            # Deep merge with defaults (using deepcopy to prevent mutation)
            merged = copy.deepcopy(DEFAULT_CONFIG)
            for key, value in user_config.items():
                if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                    merged[key].update(value)
                else:
                    merged[key] = value
            
            return merged
        except Exception as e:
            print(f"[WARN] Failed to load {self.config_path}: {e}. Using defaults.")
            return copy.deepcopy(DEFAULT_CONFIG)
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides with validation."""
        # Git identity
        git_user = os.getenv("GIT_USER")
        if git_user:
            self.config["git"]["user"] = git_user
        
        git_email = os.getenv("GIT_EMAIL")
        if git_email:
            self.config["git"]["email"] = git_email
        
        repo_url = os.getenv("REPO_URL")
        if repo_url:
            self.config["git"]["remote_url"] = repo_url
        
        # Sync behavior (with error handling)
        interval_val = os.getenv("SYNC_INTERVAL_SEC")
        if interval_val:
            try:
                interval_int = int(interval_val)
                if interval_int > 0:
                    self.config["sync"]["interval_sec"] = interval_int
                else:
                    print(f"[WARN] SYNC_INTERVAL_SEC must be positive, got {interval_int}. Using default.")
            except ValueError:
                print(f"[WARN] Invalid SYNC_INTERVAL_SEC='{interval_val}'. Using default.")
        
        sync_pull = os.getenv("SYNC_PULL")
        if sync_pull:
            self.config["sync"]["pull_enabled"] = sync_pull == "1"
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get config value using dot notation (e.g., 'sync.interval_sec').
        Returns default if not found.
        """
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    @property
    def git_user(self) -> str:
        return self.get("git.user", "SonicBuilder Bot")
    
    @property
    def git_email(self) -> str:
        return self.get("git.email", "bot@sonicbuilder.local")
    
    @property
    def git_remote_url(self) -> str | None:
        return self.get("git.remote_url")
    
    @property
    def sync_interval_sec(self) -> int:
        return self.get("sync.interval_sec", 300)
    
    @property
    def pull_enabled(self) -> bool:
        return self.get("sync.pull_enabled", True)
    
    @property
    def max_per_hour(self) -> int:
        return self.get("sync.max_per_hour", 20)
    
    @property
    def backoff_enabled(self) -> bool:
        return self.get("sync.backoff_enabled", True)
    
    @property
    def backoff_initial_sec(self) -> int:
        return self.get("sync.backoff_initial_sec", 60)
    
    @property
    def backoff_max_sec(self) -> int:
        return self.get("sync.backoff_max_sec", 3600)
    
    @property
    def exclude_patterns(self) -> list[str]:
        return self.get("exclude_patterns", [])
    
    @property
    def history_enabled(self) -> bool:
        return self.get("metrics.history_enabled", True)
    
    @property
    def history_max_entries(self) -> int:
        return self.get("metrics.history_max_entries", 1000)
    
    @property
    def history_file(self) -> str:
        return self.get("metrics.history_file", ".cache/sync_history.jsonl")
    
    @property
    def webhooks_enabled(self) -> bool:
        return self.get("webhooks.enabled", False)
    
    @property
    def webhook_urls(self) -> list[str]:
        return self.get("webhooks.urls", [])
    
    @property
    def webhook_events(self) -> list[str]:
        return self.get("webhooks.events", ["sync_success", "sync_failure"])
    
    @property
    def webhook_timeout_sec(self) -> int:
        return self.get("webhooks.timeout_sec", 5)
    
    @property
    def webhook_retry_enabled(self) -> bool:
        return self.get("webhooks.retry_enabled", True)
    
    @property
    def webhook_max_retries(self) -> int:
        return self.get("webhooks.max_retries", 3)


# Global singleton instance
_config_instance: SyncConfig | None = None

def get_config(config_path: str = ".supersonic-sync.conf") -> SyncConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = SyncConfig(config_path)
    return _config_instance


if __name__ == "__main__":
    # CLI test utility
    import json
    config = get_config()
    print(json.dumps(config.config, indent=2))
