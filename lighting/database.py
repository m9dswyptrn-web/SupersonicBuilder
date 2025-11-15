#!/usr/bin/env python3
"""
Database module for RGB Lighting Controller
Manages scenes, presets, and user preferences
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / 'supersonic' / 'data' / 'supersonic.db'


class LightingDatabase:
    """Database interface for lighting controller."""
    
    def __init__(self):
        """Initialize database connection."""
        self.db_path = DB_PATH
        self._init_tables()
    
    def _init_tables(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lighting_scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scene_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    zone_colors TEXT NOT NULL,
                    mode TEXT DEFAULT 'static',
                    brightness INTEGER DEFAULT 100,
                    effect_intensity INTEGER DEFAULT 50,
                    is_favorite BOOLEAN DEFAULT 0,
                    is_builtin BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lighting_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lighting_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_name TEXT NOT NULL,
                    scene_id INTEGER,
                    trigger_time TEXT,
                    trigger_type TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scene_id) REFERENCES lighting_scenes(id)
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_scenes_name ON lighting_scenes(scene_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_scenes_favorite ON lighting_scenes(is_favorite)
            ''')
            
            conn.commit()
            
            self._create_builtin_scenes()
    
    def _create_builtin_scenes(self):
        """Create pre-built scenes if they don't exist."""
        builtin_scenes = [
            {
                'scene_name': 'Chill',
                'description': 'Relaxing blue and purple tones',
                'zone_colors': json.dumps({
                    'dashboard': {'r': 138, 'g': 43, 'b': 226},
                    'footwell_driver': {'r': 75, 'g': 0, 'b': 130},
                    'footwell_passenger': {'r': 75, 'g': 0, 'b': 130},
                    'door_left': {'r': 138, 'g': 43, 'b': 226},
                    'door_right': {'r': 138, 'g': 43, 'b': 226},
                    'cupholder': {'r': 100, 'g': 50, 'b': 200},
                    'trunk': {'r': 138, 'g': 43, 'b': 226}
                }),
                'mode': 'breathing',
                'brightness': 70,
                'effect_intensity': 30
            },
            {
                'scene_name': 'Party',
                'description': 'Energetic rainbow colors',
                'zone_colors': json.dumps({
                    'dashboard': {'r': 255, 'g': 0, 'b': 255},
                    'footwell_driver': {'r': 0, 'g': 255, 'b': 255},
                    'footwell_passenger': {'r': 255, 'g': 255, 'b': 0},
                    'door_left': {'r': 255, 'g': 0, 'b': 0},
                    'door_right': {'r': 0, 'g': 255, 'b': 0},
                    'cupholder': {'r': 0, 'g': 0, 'b': 255},
                    'trunk': {'r': 255, 'g': 128, 'b': 0}
                }),
                'mode': 'party',
                'brightness': 100,
                'effect_intensity': 90
            },
            {
                'scene_name': 'Drive',
                'description': 'Clean white lighting for driving',
                'zone_colors': json.dumps({
                    'dashboard': {'r': 255, 'g': 255, 'b': 255},
                    'footwell_driver': {'r': 255, 'g': 200, 'b': 150},
                    'footwell_passenger': {'r': 255, 'g': 200, 'b': 150},
                    'door_left': {'r': 255, 'g': 255, 'b': 255},
                    'door_right': {'r': 255, 'g': 255, 'b': 255},
                    'cupholder': {'r': 255, 'g': 255, 'b': 200},
                    'trunk': {'r': 255, 'g': 255, 'b': 255}
                }),
                'mode': 'static',
                'brightness': 80,
                'effect_intensity': 0
            },
            {
                'scene_name': 'Night',
                'description': 'Soft red lighting for night driving',
                'zone_colors': json.dumps({
                    'dashboard': {'r': 255, 'g': 0, 'b': 0},
                    'footwell_driver': {'r': 100, 'g': 0, 'b': 0},
                    'footwell_passenger': {'r': 100, 'g': 0, 'b': 0},
                    'door_left': {'r': 150, 'g': 0, 'b': 0},
                    'door_right': {'r': 150, 'g': 0, 'b': 0},
                    'cupholder': {'r': 80, 'g': 0, 'b': 0},
                    'trunk': {'r': 200, 'g': 0, 'b': 0}
                }),
                'mode': 'static',
                'brightness': 40,
                'effect_intensity': 0
            }
        ]
        
        for scene in builtin_scenes:
            scene['is_builtin'] = True
            self.save_scene(**scene, update_if_exists=False)
    
    def save_scene(self, scene_name: str, description: str, zone_colors: Dict,
                   mode: str = 'static', brightness: int = 100,
                   effect_intensity: int = 50, is_favorite: bool = False,
                   is_builtin: bool = False, update_if_exists: bool = True) -> int:
        """Save a lighting scene."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if isinstance(zone_colors, dict):
                zone_colors = json.dumps(zone_colors)
            
            if update_if_exists:
                cursor.execute('''
                    INSERT INTO lighting_scenes 
                    (scene_name, description, zone_colors, mode, brightness, 
                     effect_intensity, is_favorite, is_builtin, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(scene_name) DO UPDATE SET
                        description = excluded.description,
                        zone_colors = excluded.zone_colors,
                        mode = excluded.mode,
                        brightness = excluded.brightness,
                        effect_intensity = excluded.effect_intensity,
                        is_favorite = excluded.is_favorite,
                        updated_at = excluded.updated_at
                ''', (scene_name, description, zone_colors, mode, brightness,
                      effect_intensity, is_favorite, is_builtin,
                      datetime.now().isoformat()))
            else:
                cursor.execute('''
                    INSERT OR IGNORE INTO lighting_scenes 
                    (scene_name, description, zone_colors, mode, brightness, 
                     effect_intensity, is_favorite, is_builtin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (scene_name, description, zone_colors, mode, brightness,
                      effect_intensity, is_favorite, is_builtin))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_scene(self, scene_name: str) -> Optional[Dict]:
        """Get a scene by name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM lighting_scenes WHERE scene_name = ?
            ''', (scene_name,))
            
            row = cursor.fetchone()
            if row:
                scene = dict(row)
                scene['zone_colors'] = json.loads(scene['zone_colors'])
                return scene
            return None
    
    def get_all_scenes(self) -> List[Dict]:
        """Get all scenes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM lighting_scenes ORDER BY is_builtin DESC, scene_name ASC
            ''')
            
            scenes = []
            for row in cursor.fetchall():
                scene = dict(row)
                scene['zone_colors'] = json.loads(scene['zone_colors'])
                scenes.append(scene)
            
            return scenes
    
    def delete_scene(self, scene_name: str) -> bool:
        """Delete a scene (can't delete built-in scenes)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM lighting_scenes 
                WHERE scene_name = ? AND is_builtin = 0
            ''', (scene_name,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def set_favorite(self, scene_name: str, is_favorite: bool) -> bool:
        """Mark a scene as favorite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE lighting_scenes SET is_favorite = ? WHERE scene_name = ?
            ''', (is_favorite, scene_name))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value FROM lighting_preferences WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except:
                    return row[0]
            return default
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if not isinstance(value, str):
                value = json.dumps(value)
            
            cursor.execute('''
                INSERT INTO lighting_preferences (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            ''', (key, value, datetime.now().isoformat()))
            
            conn.commit()
    
    def get_all_preferences(self) -> Dict:
        """Get all user preferences."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM lighting_preferences')
            
            prefs = {}
            for row in cursor.fetchall():
                try:
                    prefs[row['key']] = json.loads(row['value'])
                except:
                    prefs[row['key']] = row['value']
            
            return prefs
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM lighting_scenes')
            scene_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM lighting_scenes WHERE is_builtin = 1')
            builtin_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM lighting_scenes WHERE is_favorite = 1')
            favorite_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM lighting_preferences')
            pref_count = cursor.fetchone()[0]
            
            return {
                'total_scenes': scene_count,
                'builtin_scenes': builtin_count,
                'custom_scenes': scene_count - builtin_count,
                'favorite_scenes': favorite_count,
                'preferences_stored': pref_count
            }
