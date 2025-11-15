#!/usr/bin/env python3
"""
TPMS Database Module
Manages tire pressure monitoring data storage
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / 'supersonic' / 'data' / 'supersonic.db'


class TPMSDatabase:
    """Database operations for TPMS data."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        self.db_path = db_path or str(DB_PATH)
        self._init_tables()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Initialize TPMS database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tire pressure readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tpms_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tire_position TEXT NOT NULL,
                pressure_psi REAL NOT NULL,
                temperature_f REAL,
                sensor_id TEXT,
                sensor_battery REAL,
                signal_strength INTEGER,
                source TEXT DEFAULT 'simulated'
            )
        ''')
        
        # Tire rotation history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tire_rotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rotation_date DATE NOT NULL,
                odometer_reading INTEGER NOT NULL,
                rotation_pattern TEXT NOT NULL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # TPMS sensor calibration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tpms_sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT UNIQUE NOT NULL,
                tire_position TEXT NOT NULL,
                learn_date DATETIME,
                last_seen DATETIME,
                battery_voltage REAL,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # TPMS alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tpms_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                tire_position TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT DEFAULT 'warning',
                pressure_psi REAL,
                temperature_f REAL,
                message TEXT NOT NULL,
                is_dismissed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                dismissed_at DATETIME
            )
        ''')
        
        # Seasonal pressure settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tpms_seasonal_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                season TEXT NOT NULL,
                recommended_psi REAL NOT NULL,
                min_psi REAL NOT NULL,
                max_psi REAL NOT NULL,
                ambient_temp_f REAL,
                notes TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pressure history summary (hourly aggregates)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tpms_history_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hour_timestamp DATETIME NOT NULL,
                tire_position TEXT NOT NULL,
                avg_pressure_psi REAL NOT NULL,
                min_pressure_psi REAL NOT NULL,
                max_pressure_psi REAL NOT NULL,
                avg_temperature_f REAL,
                reading_count INTEGER DEFAULT 0,
                UNIQUE(hour_timestamp, tire_position)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tpms_readings_timestamp ON tpms_readings(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tpms_readings_position ON tpms_readings(tire_position)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tpms_alerts_active ON tpms_alerts(is_dismissed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tpms_sensors_position ON tpms_sensors(tire_position)')
        
        # Insert default seasonal settings if not exist
        cursor.execute('SELECT COUNT(*) FROM tpms_seasonal_settings')
        if cursor.fetchone()[0] == 0:
            default_seasons = [
                ('summer', 35.0, 32.0, 36.0, 75.0, 'Higher pressure for hot weather'),
                ('winter', 33.0, 30.0, 35.0, 32.0, 'Lower pressure for cold weather'),
                ('spring', 34.0, 31.0, 36.0, 55.0, 'Moderate pressure for mild weather'),
                ('fall', 34.0, 31.0, 36.0, 55.0, 'Moderate pressure for cooling weather')
            ]
            
            for season_data in default_seasons:
                cursor.execute('''
                    INSERT INTO tpms_seasonal_settings (season, recommended_psi, min_psi, max_psi, ambient_temp_f, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', season_data)
        
        conn.commit()
        conn.close()
    
    def log_reading(self, tire_position: str, pressure_psi: float, 
                    temperature_f: float = None, sensor_id: str = None,
                    sensor_battery: float = None, signal_strength: int = None,
                    source: str = 'simulated') -> int:
        """Log a tire pressure reading."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tpms_readings 
            (tire_position, pressure_psi, temperature_f, sensor_id, sensor_battery, signal_strength, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tire_position, pressure_psi, temperature_f, sensor_id, sensor_battery, signal_strength, source))
        
        reading_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reading_id
    
    def get_latest_readings(self) -> Dict[str, Dict]:
        """Get latest reading for each tire position."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        positions = ['front_left', 'front_right', 'rear_left', 'rear_right', 'spare']
        readings = {}
        
        for position in positions:
            cursor.execute('''
                SELECT * FROM tpms_readings
                WHERE tire_position = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (position,))
            
            row = cursor.fetchone()
            if row:
                readings[position] = dict(row)
        
        conn.close()
        return readings
    
    def get_pressure_history(self, tire_position: str, hours: int = 24) -> List[Dict]:
        """Get pressure history for a tire position."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, pressure_psi, temperature_f
            FROM tpms_readings
            WHERE tire_position = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        ''', (tire_position, since_time))
        
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return history
    
    def get_all_pressure_history(self, hours: int = 24) -> Dict[str, List[Dict]]:
        """Get pressure history for all tire positions."""
        positions = ['front_left', 'front_right', 'rear_left', 'rear_right', 'spare']
        history = {}
        
        for position in positions:
            history[position] = self.get_pressure_history(position, hours)
        
        return history
    
    def update_hourly_summary(self):
        """Update hourly pressure summaries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get the last hour's data
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0).isoformat()
        
        positions = ['front_left', 'front_right', 'rear_left', 'rear_right', 'spare']
        
        for position in positions:
            cursor.execute('''
                SELECT 
                    AVG(pressure_psi) as avg_pressure,
                    MIN(pressure_psi) as min_pressure,
                    MAX(pressure_psi) as max_pressure,
                    AVG(temperature_f) as avg_temp,
                    COUNT(*) as count
                FROM tpms_readings
                WHERE tire_position = ? AND timestamp >= ? AND timestamp < ?
            ''', (position, one_hour_ago, current_hour))
            
            result = cursor.fetchone()
            if result and result['count'] > 0:
                cursor.execute('''
                    INSERT OR REPLACE INTO tpms_history_summary
                    (hour_timestamp, tire_position, avg_pressure_psi, min_pressure_psi, 
                     max_pressure_psi, avg_temperature_f, reading_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (current_hour, position, result['avg_pressure'], result['min_pressure'],
                      result['max_pressure'], result['avg_temp'], result['count']))
        
        conn.commit()
        conn.close()
    
    def add_sensor(self, sensor_id: str, tire_position: str, 
                   battery_voltage: float = None, notes: str = None) -> int:
        """Add or update TPMS sensor."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tpms_sensors 
            (sensor_id, tire_position, learn_date, last_seen, battery_voltage, notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sensor_id, tire_position, now, now, battery_voltage, notes, now))
        
        sensor_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return sensor_db_id
    
    def get_sensors(self, active_only: bool = True) -> List[Dict]:
        """Get all TPMS sensors."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('SELECT * FROM tpms_sensors WHERE is_active = 1 ORDER BY tire_position')
        else:
            cursor.execute('SELECT * FROM tpms_sensors ORDER BY tire_position')
        
        sensors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return sensors
    
    def reset_sensors(self):
        """Reset all TPMS sensors (mark as inactive)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE tpms_sensors SET is_active = 0')
        
        conn.commit()
        conn.close()
    
    def log_rotation(self, rotation_date: str, odometer_reading: int, 
                     rotation_pattern: str, notes: str = None) -> int:
        """Log a tire rotation."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tire_rotations (rotation_date, odometer_reading, rotation_pattern, notes)
            VALUES (?, ?, ?, ?)
        ''', (rotation_date, odometer_reading, rotation_pattern, notes))
        
        rotation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return rotation_id
    
    def get_rotations(self, limit: int = 10) -> List[Dict]:
        """Get tire rotation history."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tire_rotations
            ORDER BY rotation_date DESC, odometer_reading DESC
            LIMIT ?
        ''', (limit,))
        
        rotations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return rotations
    
    def get_last_rotation_mileage(self) -> Optional[int]:
        """Get odometer reading of last tire rotation."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT odometer_reading FROM tire_rotations
            ORDER BY rotation_date DESC, odometer_reading DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return row['odometer_reading'] if row else None
    
    def add_alert(self, alert_id: str, tire_position: str, alert_type: str,
                  severity: str, message: str, pressure_psi: float = None,
                  temperature_f: float = None) -> int:
        """Add a TPMS alert."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tpms_alerts 
            (alert_id, tire_position, alert_type, severity, message, pressure_psi, temperature_f)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (alert_id, tire_position, alert_type, severity, message, pressure_psi, temperature_f))
        
        alert_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return alert_db_id
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active (non-dismissed) alerts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tpms_alerts
            WHERE is_dismissed = 0
            ORDER BY created_at DESC
        ''')
        
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return alerts
    
    def dismiss_alert(self, alert_id: str):
        """Dismiss an alert."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tpms_alerts
            SET is_dismissed = 1, dismissed_at = ?
            WHERE alert_id = ?
        ''', (datetime.now().isoformat(), alert_id))
        
        conn.commit()
        conn.close()
    
    def dismiss_all_alerts(self, tire_position: str = None):
        """Dismiss all alerts or all for a specific tire."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if tire_position:
            cursor.execute('''
                UPDATE tpms_alerts
                SET is_dismissed = 1, dismissed_at = ?
                WHERE tire_position = ? AND is_dismissed = 0
            ''', (datetime.now().isoformat(), tire_position))
        else:
            cursor.execute('''
                UPDATE tpms_alerts
                SET is_dismissed = 1, dismissed_at = ?
                WHERE is_dismissed = 0
            ''', (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()
    
    def get_seasonal_settings(self) -> List[Dict]:
        """Get all seasonal pressure settings."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tpms_seasonal_settings ORDER BY season')
        
        settings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return settings
    
    def get_active_seasonal_setting(self) -> Optional[Dict]:
        """Get active seasonal setting."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tpms_seasonal_settings WHERE is_active = 1 LIMIT 1')
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def set_active_season(self, season: str):
        """Set active season."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Deactivate all
        cursor.execute('UPDATE tpms_seasonal_settings SET is_active = 0')
        
        # Activate selected
        cursor.execute('UPDATE tpms_seasonal_settings SET is_active = 1 WHERE season = ?', (season,))
        
        conn.commit()
        conn.close()
    
    def detect_slow_leak(self, tire_position: str, hours: int = 72) -> Optional[Dict]:
        """Detect slow leaks by analyzing pressure trend."""
        history = self.get_pressure_history(tire_position, hours)
        
        if len(history) < 10:
            return None
        
        # Calculate pressure drop rate
        first_reading = history[0]['pressure_psi']
        last_reading = history[-1]['pressure_psi']
        pressure_drop = first_reading - last_reading
        
        # Time difference in hours
        time_diff = (datetime.fromisoformat(history[-1]['timestamp']) - 
                    datetime.fromisoformat(history[0]['timestamp'])).total_seconds() / 3600
        
        if time_diff > 0:
            drop_rate = pressure_drop / time_diff  # PSI per hour
            
            # If losing more than 0.5 PSI per day (0.02 PSI/hour)
            if drop_rate > 0.02:
                return {
                    'tire_position': tire_position,
                    'pressure_drop_psi': pressure_drop,
                    'time_period_hours': time_diff,
                    'drop_rate_psi_per_hour': drop_rate,
                    'drop_rate_psi_per_day': drop_rate * 24,
                    'severity': 'warning' if drop_rate < 0.05 else 'critical'
                }
        
        return None
