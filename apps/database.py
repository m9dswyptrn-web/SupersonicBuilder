#!/usr/bin/env python3
"""
Database handler for Android App Manager service
Stores app information, usage history, and actions
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class AppDatabase:
    """Database for app management tracking."""
    
    def __init__(self, db_path: str = 'data/apps.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS installed_apps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT UNIQUE NOT NULL,
                    app_name TEXT NOT NULL,
                    version_name TEXT,
                    version_code INTEGER,
                    app_size_mb REAL DEFAULT 0,
                    data_size_mb REAL DEFAULT 0,
                    cache_size_mb REAL DEFAULT 0,
                    total_size_mb REAL DEFAULT 0,
                    category TEXT DEFAULT 'other',
                    custom_category TEXT,
                    installation_date DATETIME,
                    last_used DATETIME,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_system_app BOOLEAN DEFAULT 0,
                    is_enabled BOOLEAN DEFAULT 1
                );
                
                CREATE TABLE IF NOT EXISTS app_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT NOT NULL,
                    permission_name TEXT NOT NULL,
                    permission_group TEXT,
                    is_granted BOOLEAN DEFAULT 0,
                    is_dangerous BOOLEAN DEFAULT 0,
                    privacy_concern_level TEXT DEFAULT 'low',
                    FOREIGN KEY (package_name) REFERENCES installed_apps(package_name) ON DELETE CASCADE,
                    UNIQUE(package_name, permission_name)
                );
                
                CREATE TABLE IF NOT EXISTS app_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT NOT NULL,
                    battery_usage_mah REAL DEFAULT 0,
                    battery_percent REAL DEFAULT 0,
                    cpu_usage_percent REAL DEFAULT 0,
                    ram_usage_mb REAL DEFAULT 0,
                    network_rx_mb REAL DEFAULT 0,
                    network_tx_mb REAL DEFAULT 0,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (package_name) REFERENCES installed_apps(package_name) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS app_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_details TEXT,
                    space_freed_mb REAL DEFAULT 0,
                    success BOOLEAN DEFAULT 1,
                    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS storage_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_storage_gb REAL NOT NULL,
                    used_storage_gb REAL NOT NULL,
                    free_storage_gb REAL NOT NULL,
                    apps_storage_gb REAL DEFAULT 0,
                    cache_storage_gb REAL DEFAULT 0,
                    data_storage_gb REAL DEFAULT 0,
                    snapshot_time DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS app_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recommendation_type TEXT NOT NULL,
                    recommendation_text TEXT NOT NULL,
                    app_suggestions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_apps_category ON installed_apps(category);
                CREATE INDEX IF NOT EXISTS idx_apps_size ON installed_apps(total_size_mb DESC);
                CREATE INDEX IF NOT EXISTS idx_apps_last_used ON installed_apps(last_used);
                CREATE INDEX IF NOT EXISTS idx_permissions_package ON app_permissions(package_name);
                CREATE INDEX IF NOT EXISTS idx_performance_package ON app_performance(package_name);
                CREATE INDEX IF NOT EXISTS idx_actions_package ON app_actions(package_name);
                CREATE INDEX IF NOT EXISTS idx_actions_time ON app_actions(performed_at);
            """)
    
    def upsert_app(self, app_data: Dict[str, Any]) -> int:
        """Insert or update app information."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO installed_apps 
                (package_name, app_name, version_name, version_code, app_size_mb, 
                 data_size_mb, cache_size_mb, total_size_mb, category, custom_category,
                 installation_date, last_used, is_system_app, is_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(package_name) DO UPDATE SET
                    app_name = excluded.app_name,
                    version_name = excluded.version_name,
                    version_code = excluded.version_code,
                    app_size_mb = excluded.app_size_mb,
                    data_size_mb = excluded.data_size_mb,
                    cache_size_mb = excluded.cache_size_mb,
                    total_size_mb = excluded.total_size_mb,
                    category = excluded.category,
                    last_used = excluded.last_used,
                    is_enabled = excluded.is_enabled,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                app_data['package_name'],
                app_data['app_name'],
                app_data.get('version_name'),
                app_data.get('version_code'),
                app_data.get('app_size_mb', 0),
                app_data.get('data_size_mb', 0),
                app_data.get('cache_size_mb', 0),
                app_data.get('total_size_mb', 0),
                app_data.get('category', 'other'),
                app_data.get('custom_category'),
                app_data.get('installation_date'),
                app_data.get('last_used'),
                app_data.get('is_system_app', False),
                app_data.get('is_enabled', True)
            ))
            return cursor.lastrowid
    
    def get_all_apps(self, include_system: bool = False) -> List[Dict[str, Any]]:
        """Get all installed apps."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM installed_apps"
            if not include_system:
                query += " WHERE is_system_app = 0"
            query += " ORDER BY total_size_mb DESC"
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_app_by_package(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get app by package name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM installed_apps WHERE package_name = ?", (package_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_apps_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get apps by category."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM installed_apps WHERE category = ? ORDER BY total_size_mb DESC",
                (category,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_top_apps_by_size(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top apps by total size."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM installed_apps ORDER BY total_size_mb DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_app_category(self, package_name: str, category: str, is_custom: bool = False):
        """Update app category."""
        with sqlite3.connect(self.db_path) as conn:
            if is_custom:
                conn.execute(
                    "UPDATE installed_apps SET custom_category = ? WHERE package_name = ?",
                    (category, package_name)
                )
            else:
                conn.execute(
                    "UPDATE installed_apps SET category = ? WHERE package_name = ?",
                    (category, package_name)
                )
    
    def delete_app(self, package_name: str):
        """Remove app from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM installed_apps WHERE package_name = ?", (package_name,))
    
    def upsert_permissions(self, package_name: str, permissions: List[Dict[str, Any]]):
        """Insert or update app permissions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for perm in permissions:
                cursor.execute("""
                    INSERT INTO app_permissions 
                    (package_name, permission_name, permission_group, is_granted, is_dangerous, privacy_concern_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(package_name, permission_name) DO UPDATE SET
                        is_granted = excluded.is_granted,
                        is_dangerous = excluded.is_dangerous,
                        privacy_concern_level = excluded.privacy_concern_level
                """, (
                    package_name,
                    perm['permission_name'],
                    perm.get('permission_group'),
                    perm.get('is_granted', False),
                    perm.get('is_dangerous', False),
                    perm.get('privacy_concern_level', 'low')
                ))
    
    def get_app_permissions(self, package_name: str) -> List[Dict[str, Any]]:
        """Get permissions for an app."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM app_permissions WHERE package_name = ?",
                (package_name,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def record_performance(self, package_name: str, perf_data: Dict[str, Any]):
        """Record app performance metrics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO app_performance
                (package_name, battery_usage_mah, battery_percent, cpu_usage_percent, 
                 ram_usage_mb, network_rx_mb, network_tx_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                package_name,
                perf_data.get('battery_usage_mah', 0),
                perf_data.get('battery_percent', 0),
                perf_data.get('cpu_usage_percent', 0),
                perf_data.get('ram_usage_mb', 0),
                perf_data.get('network_rx_mb', 0),
                perf_data.get('network_tx_mb', 0)
            ))
    
    def get_app_performance(self, package_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get performance history for an app."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM app_performance 
                   WHERE package_name = ? 
                   ORDER BY recorded_at DESC 
                   LIMIT ?""",
                (package_name, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def record_action(self, package_name: str, action_type: str, details: str = None, 
                     space_freed_mb: float = 0, success: bool = True):
        """Record an app management action."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO app_actions
                (package_name, action_type, action_details, space_freed_mb, success)
                VALUES (?, ?, ?, ?, ?)
            """, (package_name, action_type, details, space_freed_mb, success))
    
    def get_action_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent app actions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM app_actions ORDER BY performed_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def record_storage_snapshot(self, storage_data: Dict[str, Any]):
        """Record storage snapshot."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO storage_snapshots
                (total_storage_gb, used_storage_gb, free_storage_gb, apps_storage_gb, 
                 cache_storage_gb, data_storage_gb)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                storage_data['total_storage_gb'],
                storage_data['used_storage_gb'],
                storage_data['free_storage_gb'],
                storage_data.get('apps_storage_gb', 0),
                storage_data.get('cache_storage_gb', 0),
                storage_data.get('data_storage_gb', 0)
            ))
    
    def get_storage_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get storage history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM storage_snapshots 
                WHERE snapshot_time > datetime('now', '-' || ? || ' hours')
                ORDER BY snapshot_time DESC
            """, (hours,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM installed_apps WHERE is_system_app = 0")
            total_apps = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM installed_apps WHERE is_system_app = 1")
            system_apps = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(total_size_mb) FROM installed_apps")
            total_size_mb = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(cache_size_mb) FROM installed_apps")
            total_cache_mb = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM app_actions")
            total_actions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM app_permissions WHERE is_dangerous = 1")
            dangerous_permissions = cursor.fetchone()[0]
            
            return {
                'total_apps': total_apps,
                'system_apps': system_apps,
                'total_size_mb': round(total_size_mb, 2),
                'total_cache_mb': round(total_cache_mb, 2),
                'total_actions': total_actions,
                'dangerous_permissions': dangerous_permissions
            }
