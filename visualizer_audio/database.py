#!/usr/bin/env python3
"""
Audio Visualizer Settings Database
Stores user preferences, themes, and visualization settings
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class VisualizerDatabase:
    """Database for audio visualizer settings and preferences."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        if db_path is None:
            root = Path(__file__).parent.parent.parent
            db_path = root / 'supersonic' / 'data' / 'supersonic.db'
        
        self.db_path = str(db_path)
        self._init_tables()
    
    def _get_conn(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Create tables if they don't exist."""
        conn = self._get_conn()
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS visualizer_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS visualizer_themes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_name TEXT UNIQUE NOT NULL,
                    theme_data TEXT NOT NULL,
                    is_favorite BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audio_analysis_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_id TEXT UNIQUE NOT NULL,
                    fft_bands TEXT NOT NULL,
                    beat_detected BOOLEAN DEFAULT 0,
                    bpm REAL,
                    bass_level REAL,
                    mid_level REAL,
                    treble_level REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        finally:
            conn.close()
    
    def save_setting(self, key: str, value: any):
        """Save a setting."""
        conn = self._get_conn()
        try:
            value_json = json.dumps(value)
            conn.execute('''
                INSERT INTO visualizer_settings (setting_key, setting_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(setting_key) DO UPDATE SET
                    setting_value = excluded.setting_value,
                    updated_at = CURRENT_TIMESTAMP
            ''', (key, value_json))
            conn.commit()
        finally:
            conn.close()
    
    def get_setting(self, key: str, default=None):
        """Get a setting."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                'SELECT setting_value FROM visualizer_settings WHERE setting_key = ?',
                (key,)
            ).fetchone()
            
            if row:
                return json.loads(row['setting_value'])
            return default
        finally:
            conn.close()
    
    def save_theme(self, theme_name: str, theme_data: dict, is_favorite: bool = False):
        """Save a custom theme."""
        conn = self._get_conn()
        try:
            theme_json = json.dumps(theme_data)
            conn.execute('''
                INSERT INTO visualizer_themes (theme_name, theme_data, is_favorite)
                VALUES (?, ?, ?)
                ON CONFLICT(theme_name) DO UPDATE SET
                    theme_data = excluded.theme_data,
                    is_favorite = excluded.is_favorite
            ''', (theme_name, theme_json, is_favorite))
            conn.commit()
        finally:
            conn.close()
    
    def get_theme(self, theme_name: str) -> Optional[dict]:
        """Get a theme by name."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                'SELECT theme_data FROM visualizer_themes WHERE theme_name = ?',
                (theme_name,)
            ).fetchone()
            
            if row:
                return json.loads(row['theme_data'])
            return None
        finally:
            conn.close()
    
    def get_all_themes(self) -> List[dict]:
        """Get all saved themes."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                'SELECT theme_name, theme_data, is_favorite FROM visualizer_themes ORDER BY created_at DESC'
            ).fetchall()
            
            return [{
                'name': row['theme_name'],
                'data': json.loads(row['theme_data']),
                'is_favorite': bool(row['is_favorite'])
            } for row in rows]
        finally:
            conn.close()
    
    def mark_favorite(self, theme_name: str, is_favorite: bool = True):
        """Mark a theme as favorite."""
        conn = self._get_conn()
        try:
            conn.execute(
                'UPDATE visualizer_themes SET is_favorite = ? WHERE theme_name = ?',
                (is_favorite, theme_name)
            )
            conn.commit()
        finally:
            conn.close()
    
    def save_audio_snapshot(self, snapshot_id: str, fft_bands: List[float],
                           beat_detected: bool, bpm: float, bass: float,
                           mid: float, treble: float):
        """Save audio analysis snapshot."""
        conn = self._get_conn()
        try:
            fft_json = json.dumps(fft_bands)
            conn.execute('''
                INSERT INTO audio_analysis_snapshots
                (snapshot_id, fft_bands, beat_detected, bpm, bass_level, mid_level, treble_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (snapshot_id, fft_json, beat_detected, bpm, bass, mid, treble))
            conn.commit()
        finally:
            conn.close()
    
    def get_recent_snapshots(self, limit: int = 100) -> List[dict]:
        """Get recent audio snapshots."""
        conn = self._get_conn()
        try:
            rows = conn.execute('''
                SELECT * FROM audio_analysis_snapshots
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,)).fetchall()
            
            return [{
                'snapshot_id': row['snapshot_id'],
                'fft_bands': json.loads(row['fft_bands']),
                'beat_detected': bool(row['beat_detected']),
                'bpm': row['bpm'],
                'bass_level': row['bass_level'],
                'mid_level': row['mid_level'],
                'treble_level': row['treble_level'],
                'created_at': row['created_at']
            } for row in rows]
        finally:
            conn.close()
