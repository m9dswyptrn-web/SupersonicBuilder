#!/usr/bin/env python3
"""
Bass Management Database
Store bass settings, presets, and measurements
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

DB_PATH = ROOT / 'supersonic' / 'data' / 'builder.db'


class BassDatabase:
    """Database operations for bass management system."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        self.db_path = db_path or DB_PATH
        self._init_tables()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Initialize bass management tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bass_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_name TEXT NOT NULL,
                subwoofer_config TEXT NOT NULL,
                subsonic_filter TEXT,
                lowpass_crossover TEXT,
                bass_boost TEXT,
                phase_config TEXT,
                delay_config TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bass_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preset_name TEXT UNIQUE NOT NULL,
                preset_type TEXT NOT NULL,
                description TEXT,
                configuration TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bass_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id TEXT UNIQUE NOT NULL,
                measurement_type TEXT NOT NULL,
                frequency_hz REAL,
                spl_db REAL,
                phase_degrees REAL,
                coherence REAL,
                room_acoustics TEXT,
                measurement_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bass_calibration_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                vehicle_info TEXT,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                final_config TEXT,
                measurements_count INTEGER DEFAULT 0,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bass_config_name 
            ON bass_configurations(config_name)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bass_measurements_type 
            ON bass_measurements(measurement_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bass_calibration_start 
            ON bass_calibration_sessions(start_time)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_configuration(self, config_name: str, subwoofer_config: dict,
                          subsonic_filter: Optional[dict] = None,
                          lowpass_crossover: Optional[dict] = None,
                          bass_boost: Optional[dict] = None,
                          phase_config: Optional[dict] = None,
                          delay_config: Optional[dict] = None,
                          notes: Optional[str] = None) -> int:
        """Save bass configuration to database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bass_configurations 
            (config_name, subwoofer_config, subsonic_filter, lowpass_crossover, 
             bass_boost, phase_config, delay_config, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            config_name,
            json.dumps(subwoofer_config),
            json.dumps(subsonic_filter) if subsonic_filter else None,
            json.dumps(lowpass_crossover) if lowpass_crossover else None,
            json.dumps(bass_boost) if bass_boost else None,
            json.dumps(phase_config) if phase_config else None,
            json.dumps(delay_config) if delay_config else None,
            notes
        ))
        
        config_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return config_id
    
    def get_configuration(self, config_id: int) -> Optional[dict]:
        """Retrieve configuration by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bass_configurations WHERE id = ?
        ''', (config_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_config_dict(row)
        return None
    
    def get_configuration_by_name(self, config_name: str) -> Optional[dict]:
        """Retrieve configuration by name."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bass_configurations 
            WHERE config_name = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (config_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_config_dict(row)
        return None
    
    def list_configurations(self, limit: int = 50) -> List[dict]:
        """List all saved configurations."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bass_configurations 
            ORDER BY updated_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_config_dict(row) for row in rows]
    
    def update_configuration(self, config_id: int, **updates) -> bool:
        """Update existing configuration."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['config_name', 'subwoofer_config', 'subsonic_filter', 
                         'lowpass_crossover', 'bass_boost', 'phase_config', 
                         'delay_config', 'notes']
        
        update_fields = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                update_fields.append(f'{field} = ?')
                if isinstance(value, dict):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
        
        if not update_fields:
            conn.close()
            return False
        
        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        values.append(config_id)
        
        query = f'''
            UPDATE bass_configurations 
            SET {', '.join(update_fields)} 
            WHERE id = ?
        '''
        
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def delete_configuration(self, config_id: int) -> bool:
        """Delete configuration."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM bass_configurations WHERE id = ?', (config_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def save_preset(self, preset_name: str, preset_type: str, configuration: dict,
                   description: Optional[str] = None, is_default: bool = False) -> int:
        """Save bass preset."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bass_presets 
            (preset_name, preset_type, description, configuration, is_default)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            preset_name,
            preset_type,
            description,
            json.dumps(configuration),
            1 if is_default else 0
        ))
        
        preset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return preset_id
    
    def get_preset(self, preset_name: str) -> Optional[dict]:
        """Retrieve preset by name."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bass_presets WHERE preset_name = ?
        ''', (preset_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'preset_name': row['preset_name'],
                'preset_type': row['preset_type'],
                'description': row['description'],
                'configuration': json.loads(row['configuration']),
                'is_default': bool(row['is_default']),
                'created_at': row['created_at']
            }
        return None
    
    def list_presets(self, preset_type: Optional[str] = None) -> List[dict]:
        """List all presets, optionally filtered by type."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if preset_type:
            cursor.execute('''
                SELECT * FROM bass_presets 
                WHERE preset_type = ? 
                ORDER BY is_default DESC, preset_name
            ''', (preset_type,))
        else:
            cursor.execute('''
                SELECT * FROM bass_presets 
                ORDER BY is_default DESC, preset_name
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row['id'],
            'preset_name': row['preset_name'],
            'preset_type': row['preset_type'],
            'description': row['description'],
            'configuration': json.loads(row['configuration']),
            'is_default': bool(row['is_default']),
            'created_at': row['created_at']
        } for row in rows]
    
    def save_measurement(self, measurement_id: str, measurement_type: str,
                        measurement_data: dict, frequency_hz: Optional[float] = None,
                        spl_db: Optional[float] = None, phase_degrees: Optional[float] = None,
                        coherence: Optional[float] = None, room_acoustics: Optional[str] = None) -> int:
        """Save bass measurement."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bass_measurements 
            (measurement_id, measurement_type, frequency_hz, spl_db, phase_degrees,
             coherence, room_acoustics, measurement_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            measurement_id,
            measurement_type,
            frequency_hz,
            spl_db,
            phase_degrees,
            coherence,
            room_acoustics,
            json.dumps(measurement_data)
        ))
        
        meas_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return meas_id
    
    def get_measurements(self, measurement_type: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Get measurements, optionally filtered by type."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if measurement_type:
            cursor.execute('''
                SELECT * FROM bass_measurements 
                WHERE measurement_type = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (measurement_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM bass_measurements 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row['id'],
            'measurement_id': row['measurement_id'],
            'measurement_type': row['measurement_type'],
            'frequency_hz': row['frequency_hz'],
            'spl_db': row['spl_db'],
            'phase_degrees': row['phase_degrees'],
            'coherence': row['coherence'],
            'room_acoustics': row['room_acoustics'],
            'measurement_data': json.loads(row['measurement_data']) if row['measurement_data'] else {},
            'created_at': row['created_at']
        } for row in rows]
    
    def start_calibration_session(self, session_id: str, vehicle_info: Optional[dict] = None) -> int:
        """Start new calibration session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bass_calibration_sessions 
            (session_id, vehicle_info, start_time)
            VALUES (?, ?, ?)
        ''', (
            session_id,
            json.dumps(vehicle_info) if vehicle_info else None,
            datetime.now().isoformat()
        ))
        
        session_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_db_id
    
    def end_calibration_session(self, session_id: str, final_config: dict,
                               measurements_count: int, notes: Optional[str] = None) -> bool:
        """End calibration session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE bass_calibration_sessions 
            SET end_time = ?, final_config = ?, measurements_count = ?, notes = ?
            WHERE session_id = ?
        ''', (
            datetime.now().isoformat(),
            json.dumps(final_config),
            measurements_count,
            notes,
            session_id
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def get_calibration_sessions(self, limit: int = 50) -> List[dict]:
        """Get calibration sessions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bass_calibration_sessions 
            ORDER BY start_time DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row['id'],
            'session_id': row['session_id'],
            'vehicle_info': json.loads(row['vehicle_info']) if row['vehicle_info'] else None,
            'start_time': row['start_time'],
            'end_time': row['end_time'],
            'final_config': json.loads(row['final_config']) if row['final_config'] else None,
            'measurements_count': row['measurements_count'],
            'notes': row['notes'],
            'created_at': row['created_at']
        } for row in rows]
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM bass_configurations')
        configs_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM bass_presets')
        presets_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM bass_measurements')
        measurements_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM bass_calibration_sessions')
        sessions_count = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_configurations': configs_count,
            'total_presets': presets_count,
            'total_measurements': measurements_count,
            'total_calibration_sessions': sessions_count,
            'database_path': str(self.db_path)
        }
    
    def _row_to_config_dict(self, row) -> dict:
        """Convert database row to configuration dict."""
        return {
            'id': row['id'],
            'config_name': row['config_name'],
            'subwoofer_config': json.loads(row['subwoofer_config']),
            'subsonic_filter': json.loads(row['subsonic_filter']) if row['subsonic_filter'] else None,
            'lowpass_crossover': json.loads(row['lowpass_crossover']) if row['lowpass_crossover'] else None,
            'bass_boost': json.loads(row['bass_boost']) if row['bass_boost'] else None,
            'phase_config': json.loads(row['phase_config']) if row['phase_config'] else None,
            'delay_config': json.loads(row['delay_config']) if row['delay_config'] else None,
            'notes': row['notes'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
