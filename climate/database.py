#!/usr/bin/env python3
"""
Database Interface for Climate Control Service
Handles preset storage and climate history
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

DB_PATH = ROOT / 'supersonic' / 'data' / 'supersonic.db'


class ClimateDatabase:
    """Database interface for climate control presets and history."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or DB_PATH
        self._ensure_db()
    
    def _ensure_db(self):
        """Ensure database and tables exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS climate_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preset_name TEXT UNIQUE NOT NULL,
                    temp_driver REAL NOT NULL,
                    temp_passenger REAL,
                    temp_rear REAL,
                    fan_speed INTEGER NOT NULL,
                    mode TEXT NOT NULL,
                    ac_enabled BOOLEAN DEFAULT 0,
                    recirculation BOOLEAN DEFAULT 0,
                    defrost_front BOOLEAN DEFAULT 0,
                    defrost_rear BOOLEAN DEFAULT 0,
                    auto_mode BOOLEAN DEFAULT 0,
                    heated_seat_driver INTEGER DEFAULT 0,
                    heated_seat_passenger INTEGER DEFAULT 0,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS climate_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    temp_driver REAL,
                    temp_passenger REAL,
                    temp_outside REAL,
                    fan_speed INTEGER,
                    mode TEXT,
                    ac_enabled BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_climate_history_timestamp 
                ON climate_history(timestamp)
            ''')
            
            conn.commit()
            
            self._ensure_default_presets()
    
    def _ensure_default_presets(self):
        """Create default climate presets if they don't exist."""
        default_presets = [
            {
                'preset_name': 'Comfort',
                'temp_driver': 22.0,
                'temp_passenger': 22.0,
                'fan_speed': 7,
                'mode': 'auto',
                'ac_enabled': False,
                'recirculation': False,
                'auto_mode': True,
                'description': '72°F, auto fan - Perfect for daily driving'
            },
            {
                'preset_name': 'Cool',
                'temp_driver': 20.0,
                'temp_passenger': 20.0,
                'fan_speed': 5,
                'mode': 'face',
                'ac_enabled': True,
                'recirculation': True,
                'auto_mode': False,
                'description': '68°F, max AC - For hot summer days'
            },
            {
                'preset_name': 'Warm',
                'temp_driver': 24.5,
                'temp_passenger': 24.5,
                'fan_speed': 4,
                'mode': 'feet',
                'ac_enabled': False,
                'recirculation': False,
                'auto_mode': False,
                'heated_seat_driver': 2,
                'heated_seat_passenger': 2,
                'description': '76°F, feet mode - For cold winter days'
            },
            {
                'preset_name': 'Defrost',
                'temp_driver': 28.0,
                'temp_passenger': 28.0,
                'fan_speed': 6,
                'mode': 'defrost',
                'ac_enabled': True,
                'recirculation': False,
                'defrost_front': True,
                'defrost_rear': True,
                'auto_mode': False,
                'description': 'Max heat, defrost mode - Clear foggy windows fast'
            }
        ]
        
        for preset in default_presets:
            try:
                self.save_preset(preset)
            except:
                pass
    
    def save_preset(self, preset_data: Dict[str, Any]) -> int:
        """
        Save a climate preset.
        
        Args:
            preset_data: Preset configuration dictionary
        
        Returns:
            Preset ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT OR REPLACE INTO climate_presets 
                (preset_name, temp_driver, temp_passenger, temp_rear, fan_speed, 
                 mode, ac_enabled, recirculation, defrost_front, defrost_rear, 
                 auto_mode, heated_seat_driver, heated_seat_passenger, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                preset_data['preset_name'],
                preset_data['temp_driver'],
                preset_data.get('temp_passenger'),
                preset_data.get('temp_rear'),
                preset_data['fan_speed'],
                preset_data['mode'],
                preset_data.get('ac_enabled', False),
                preset_data.get('recirculation', False),
                preset_data.get('defrost_front', False),
                preset_data.get('defrost_rear', False),
                preset_data.get('auto_mode', False),
                preset_data.get('heated_seat_driver', 0),
                preset_data.get('heated_seat_passenger', 0),
                preset_data.get('description', '')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def load_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a preset by name.
        
        Args:
            preset_name: Name of the preset
        
        Returns:
            Preset dictionary or None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM climate_presets WHERE preset_name = ?
            ''', (preset_name,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """
        List all presets.
        
        Returns:
            List of preset dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM climate_presets
                ORDER BY preset_name
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_preset(self, preset_name: str) -> bool:
        """
        Delete a preset.
        
        Args:
            preset_name: Name of the preset to delete
        
        Returns:
            Success status
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM climate_presets WHERE preset_name = ?
            ''', (preset_name,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def log_climate_state(self, state: Dict[str, Any]):
        """
        Log current climate state to history.
        
        Args:
            state: Current climate state
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO climate_history 
                (temp_driver, temp_passenger, temp_outside, fan_speed, mode, ac_enabled)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                state.get('temp_driver'),
                state.get('temp_passenger'),
                state.get('temp_outside'),
                state.get('fan_speed'),
                state.get('mode'),
                state.get('ac_enabled', False)
            ))
            
            conn.commit()
    
    def get_history(self, hours: int = 24, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get climate history.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of records
        
        Returns:
            List of history records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM climate_history
                WHERE timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (hours, limit))
            
            return [dict(row) for row in cursor.fetchall()]
