#!/usr/bin/env python3
"""
Command Center Database
Stores user preferences, dashboard layouts, and system state
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

DB_PATH = Path(__file__).parent.parent.parent / 'supersonic' / 'data' / 'command_center.db'


class CommandCenterDatabase:
    """Database for command center preferences and state."""
    
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pref_key TEXT UNIQUE NOT NULL,
                pref_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS dashboard_layouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                layout_name TEXT UNIQUE NOT NULL,
                layout_data TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS widget_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                layout_id INTEGER NOT NULL,
                widget_id TEXT NOT NULL,
                position_x INTEGER NOT NULL,
                position_y INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                is_visible BOOLEAN DEFAULT 1,
                FOREIGN KEY (layout_id) REFERENCES dashboard_layouts(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS service_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT UNIQUE NOT NULL,
                is_favorite BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                alert_level TEXT NOT NULL,
                alert_message TEXT NOT NULL,
                alert_data TEXT,
                is_acknowledged BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                acknowledged_at DATETIME
            );
            
            CREATE TABLE IF NOT EXISTS quick_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_name TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_data TEXT NOT NULL,
                is_enabled BOOLEAN DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_alerts_service ON system_alerts(service_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_level ON system_alerts(alert_level);
            CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON system_alerts(is_acknowledged);
        """)
        self.conn.commit()
        
        self._set_default_preferences()
    
    def _set_default_preferences(self):
        """Set default preferences if not already set."""
        defaults = {
            'theme': 'dark',
            'default_view': 'grid',
            'auto_refresh_interval': '5000',
            'show_offline_services': 'true',
            'enable_animations': 'true',
            'enable_sound': 'false',
            'temperature_unit': 'C',
            'pressure_unit': 'PSI',
            'distance_unit': 'MI'
        }
        
        for key, value in defaults.items():
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO user_preferences (pref_key, pref_value) VALUES (?, ?)",
                    (key, value)
                )
            except:
                pass
        
        self.conn.commit()
    
    def get_preference(self, key: str) -> Optional[str]:
        """Get user preference value."""
        row = self.conn.execute(
            "SELECT pref_value FROM user_preferences WHERE pref_key = ?",
            (key,)
        ).fetchone()
        
        return row['pref_value'] if row else None
    
    def set_preference(self, key: str, value: str):
        """Set user preference."""
        self.conn.execute("""
            INSERT INTO user_preferences (pref_key, pref_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(pref_key) DO UPDATE SET
                pref_value = excluded.pref_value,
                updated_at = CURRENT_TIMESTAMP
        """, (key, value))
        self.conn.commit()
    
    def get_all_preferences(self) -> Dict[str, str]:
        """Get all preferences."""
        rows = self.conn.execute("SELECT pref_key, pref_value FROM user_preferences").fetchall()
        return {row['pref_key']: row['pref_value'] for row in rows}
    
    def save_layout(self, name: str, layout_data: Dict[str, Any], set_active: bool = False):
        """Save dashboard layout."""
        layout_json = json.dumps(layout_data)
        
        if set_active:
            self.conn.execute("UPDATE dashboard_layouts SET is_active = 0")
        
        self.conn.execute("""
            INSERT INTO dashboard_layouts (layout_name, layout_data, is_active, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(layout_name) DO UPDATE SET
                layout_data = excluded.layout_data,
                is_active = excluded.is_active,
                updated_at = CURRENT_TIMESTAMP
        """, (name, layout_json, 1 if set_active else 0))
        self.conn.commit()
    
    def get_active_layout(self) -> Optional[Dict[str, Any]]:
        """Get active dashboard layout."""
        row = self.conn.execute(
            "SELECT layout_name, layout_data FROM dashboard_layouts WHERE is_active = 1"
        ).fetchone()
        
        if row:
            return {
                'name': row['layout_name'],
                'data': json.loads(row['layout_data'])
            }
        return None
    
    def get_all_layouts(self) -> List[Dict[str, Any]]:
        """Get all saved layouts."""
        rows = self.conn.execute("""
            SELECT layout_name, layout_data, is_active, created_at, updated_at
            FROM dashboard_layouts
            ORDER BY updated_at DESC
        """).fetchall()
        
        return [{
            'name': row['layout_name'],
            'data': json.loads(row['layout_data']),
            'is_active': bool(row['is_active']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        } for row in rows]
    
    def add_alert(self, service_id: str, level: str, message: str, data: Optional[Dict] = None):
        """Add system alert."""
        alert_data_json = json.dumps(data) if data else None
        
        self.conn.execute("""
            INSERT INTO system_alerts (service_id, alert_level, alert_message, alert_data)
            VALUES (?, ?, ?, ?)
        """, (service_id, level, message, alert_data_json))
        self.conn.commit()
    
    def get_active_alerts(self, service_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active (unacknowledged) alerts."""
        if service_id:
            rows = self.conn.execute("""
                SELECT id, service_id, alert_level, alert_message, alert_data, created_at
                FROM system_alerts
                WHERE is_acknowledged = 0 AND service_id = ?
                ORDER BY created_at DESC
            """, (service_id,)).fetchall()
        else:
            rows = self.conn.execute("""
                SELECT id, service_id, alert_level, alert_message, alert_data, created_at
                FROM system_alerts
                WHERE is_acknowledged = 0
                ORDER BY created_at DESC
            """).fetchall()
        
        return [{
            'id': row['id'],
            'service_id': row['service_id'],
            'level': row['alert_level'],
            'message': row['alert_message'],
            'data': json.loads(row['alert_data']) if row['alert_data'] else None,
            'created_at': row['created_at']
        } for row in rows]
    
    def acknowledge_alert(self, alert_id: int):
        """Acknowledge an alert."""
        self.conn.execute("""
            UPDATE system_alerts
            SET is_acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (alert_id,))
        self.conn.commit()
    
    def clear_old_alerts(self, days: int = 7):
        """Clear acknowledged alerts older than specified days."""
        self.conn.execute("""
            DELETE FROM system_alerts
            WHERE is_acknowledged = 1
            AND datetime(acknowledged_at) < datetime('now', ?)
        """, (f'-{days} days',))
        self.conn.commit()
    
    def add_favorite(self, service_id: str):
        """Add service to favorites."""
        self.conn.execute("""
            INSERT OR IGNORE INTO service_favorites (service_id)
            VALUES (?)
        """, (service_id,))
        self.conn.commit()
    
    def remove_favorite(self, service_id: str):
        """Remove service from favorites."""
        self.conn.execute("DELETE FROM service_favorites WHERE service_id = ?", (service_id,))
        self.conn.commit()
    
    def get_favorites(self) -> List[str]:
        """Get favorite services."""
        rows = self.conn.execute("""
            SELECT service_id FROM service_favorites
            WHERE is_favorite = 1
            ORDER BY sort_order, created_at
        """).fetchall()
        
        return [row['service_id'] for row in rows]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
