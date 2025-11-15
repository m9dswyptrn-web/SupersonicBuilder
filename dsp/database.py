#!/usr/bin/env python3
"""
DSP Database Interface
Store presets, user profiles, and DSP settings
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DSPDatabase:
    """Database interface for DSP service."""
    
    def __init__(self, db_path: str = 'supersonic/data/supersonic.db'):
        """Initialize database connection."""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def _init_schema(self):
        """Initialize DSP tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dsp_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preset_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                author TEXT,
                preset_type TEXT DEFAULT 'user',
                eq_settings TEXT,
                crossover_settings TEXT,
                time_alignment_settings TEXT,
                bass_settings TEXT,
                loudness_settings TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dsp_user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT UNIQUE NOT NULL,
                vehicle_info TEXT,
                active_preset_id TEXT,
                listening_position TEXT DEFAULT 'driver',
                preferences TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dsp_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id TEXT UNIQUE NOT NULL,
                measurement_type TEXT NOT NULL,
                profile_id INTEGER,
                spectrum_data TEXT,
                frequency_response TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES dsp_user_profiles(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dsp_presets_type 
            ON dsp_presets(preset_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dsp_measurements_type 
            ON dsp_measurements(measurement_type)
        """)
        
        conn.commit()
        conn.close()
        
    def save_preset(
        self,
        preset_id: str,
        name: str,
        eq_settings: Dict = None,
        crossover_settings: Dict = None,
        time_alignment_settings: Dict = None,
        bass_settings: Dict = None,
        loudness_settings: Dict = None,
        description: str = None,
        author: str = 'User'
    ) -> Dict:
        """Save DSP preset to database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO dsp_presets (
                    preset_id, name, description, author, preset_type,
                    eq_settings, crossover_settings, time_alignment_settings,
                    bass_settings, loudness_settings, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                preset_id,
                name,
                description,
                author,
                'user',
                json.dumps(eq_settings) if eq_settings else None,
                json.dumps(crossover_settings) if crossover_settings else None,
                json.dumps(time_alignment_settings) if time_alignment_settings else None,
                json.dumps(bass_settings) if bass_settings else None,
                json.dumps(loudness_settings) if loudness_settings else None,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            preset_db_id = cursor.lastrowid
            
            return {
                'ok': True,
                'preset_id': preset_id,
                'db_id': preset_db_id
            }
        except sqlite3.Error as e:
            return {
                'ok': False,
                'error': str(e)
            }
        finally:
            conn.close()
            
    def get_preset(self, preset_id: str) -> Optional[Dict]:
        """Get preset from database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM dsp_presets WHERE preset_id = ?
        """, (preset_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'preset_id': row['preset_id'],
                'name': row['name'],
                'description': row['description'],
                'author': row['author'],
                'preset_type': row['preset_type'],
                'eq_settings': json.loads(row['eq_settings']) if row['eq_settings'] else None,
                'crossover_settings': json.loads(row['crossover_settings']) if row['crossover_settings'] else None,
                'time_alignment_settings': json.loads(row['time_alignment_settings']) if row['time_alignment_settings'] else None,
                'bass_settings': json.loads(row['bass_settings']) if row['bass_settings'] else None,
                'loudness_settings': json.loads(row['loudness_settings']) if row['loudness_settings'] else None,
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
        
    def list_presets(self, preset_type: str = None) -> List[Dict]:
        """List all presets."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if preset_type:
            cursor.execute("""
                SELECT preset_id, name, description, author, preset_type, created_at
                FROM dsp_presets WHERE preset_type = ?
                ORDER BY created_at DESC
            """, (preset_type,))
        else:
            cursor.execute("""
                SELECT preset_id, name, description, author, preset_type, created_at
                FROM dsp_presets
                ORDER BY created_at DESC
            """)
            
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    def delete_preset(self, preset_id: str) -> Dict:
        """Delete preset from database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM dsp_presets WHERE preset_id = ?", (preset_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return {'ok': True, 'preset_id': preset_id}
            else:
                return {'ok': False, 'error': 'Preset not found'}
        except sqlite3.Error as e:
            return {'ok': False, 'error': str(e)}
        finally:
            conn.close()
            
    def create_user_profile(
        self,
        profile_name: str,
        vehicle_info: Dict = None,
        listening_position: str = 'driver',
        preferences: Dict = None
    ) -> Dict:
        """Create user profile."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO dsp_user_profiles (
                    profile_name, vehicle_info, listening_position, preferences
                ) VALUES (?, ?, ?, ?)
            """, (
                profile_name,
                json.dumps(vehicle_info) if vehicle_info else None,
                listening_position,
                json.dumps(preferences) if preferences else None
            ))
            
            conn.commit()
            profile_id = cursor.lastrowid
            
            return {
                'ok': True,
                'profile_id': profile_id,
                'profile_name': profile_name
            }
        except sqlite3.Error as e:
            return {'ok': False, 'error': str(e)}
        finally:
            conn.close()
            
    def save_measurement(
        self,
        measurement_id: str,
        measurement_type: str,
        spectrum_data: Dict = None,
        frequency_response: Dict = None,
        profile_id: int = None,
        notes: str = None
    ) -> Dict:
        """Save spectrum analyzer measurement."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO dsp_measurements (
                    measurement_id, measurement_type, profile_id,
                    spectrum_data, frequency_response, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                measurement_id,
                measurement_type,
                profile_id,
                json.dumps(spectrum_data) if spectrum_data else None,
                json.dumps(frequency_response) if frequency_response else None,
                notes
            ))
            
            conn.commit()
            return {'ok': True, 'measurement_id': measurement_id}
        except sqlite3.Error as e:
            return {'ok': False, 'error': str(e)}
        finally:
            conn.close()
