#!/usr/bin/env python3
"""
Wireless Charger Database Module
Handles all database operations for charging sessions, history, and health tracking
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / 'supersonic' / 'data' / 'wireless_charger.db'


class WirelessChargerDatabase:
    """Database manager for wireless charger monitoring."""
    
    def __init__(self):
        """Initialize database connection and create tables."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(DB_PATH)
        self._init_tables()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS charging_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                phone_model TEXT,
                qi_compatible BOOLEAN DEFAULT 1,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                start_battery_percent INTEGER,
                end_battery_percent INTEGER,
                total_power_wh REAL DEFAULT 0.0,
                avg_power_w REAL DEFAULT 0.0,
                max_power_w REAL DEFAULT 0.0,
                avg_efficiency_percent REAL DEFAULT 0.0,
                max_temp_c REAL DEFAULT 0.0,
                misalignment_count INTEGER DEFAULT 0,
                overheating_count INTEGER DEFAULT 0,
                duration_minutes INTEGER,
                completed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS charging_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                phone_detected BOOLEAN DEFAULT 0,
                charging_active BOOLEAN DEFAULT 0,
                battery_percent INTEGER,
                charging_power_w REAL DEFAULT 0.0,
                input_power_w REAL DEFAULT 0.0,
                output_power_w REAL DEFAULT 0.0,
                efficiency_percent REAL DEFAULT 0.0,
                pad_temp_c REAL DEFAULT 0.0,
                phone_temp_c REAL DEFAULT 0.0,
                alignment_score INTEGER DEFAULT 100,
                FOREIGN KEY (session_id) REFERENCES charging_sessions(session_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS charging_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pad_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                status TEXT DEFAULT 'normal',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS charging_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_count INTEGER DEFAULT 0,
                total_power_delivered_wh REAL DEFAULT 0.0,
                coil_health_percent REAL DEFAULT 100.0,
                last_maintenance_date DATE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS battery_care_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tip_type TEXT NOT NULL,
                tip_message TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                shown_count INTEGER DEFAULT 0,
                last_shown DATETIME
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_start ON charging_sessions(start_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_phone ON charging_sessions(phone_model)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_session ON charging_metrics(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON charging_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_session ON charging_alerts(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_type ON charging_alerts(alert_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_metric ON pad_health(metric_name)')
        
        self._init_battery_care_tips(cursor)
        
        conn.commit()
        conn.close()
    
    def _init_battery_care_tips(self, cursor):
        """Initialize battery care tips."""
        tips = [
            ('optimal_range', "Keep your battery between 20-80% for optimal longevity", 1),
            ('avoid_100', "Avoid charging to 100% regularly - it stresses the battery", 2),
            ('heat_warning', "Heat is battery's enemy - remove thick cases while charging", 3),
            ('slow_charging', "Slow charging (5W) is better for battery health than fast charging", 2),
            ('full_cycles', "Perform a full 0-100% charge cycle once a month to calibrate", 1),
            ('overnight', "Avoid leaving phone on charger overnight - use automation to stop at 80%", 2),
            ('temperature', "Charge in moderate temperatures (15-25°C) for best results", 2),
            ('alignment', "Proper alignment reduces heat and improves efficiency", 3)
        ]
        
        for tip_type, tip_message, priority in tips:
            cursor.execute('''
                INSERT OR IGNORE INTO battery_care_tips (tip_type, tip_message, priority)
                VALUES (?, ?, ?)
            ''', (tip_type, tip_message, priority))
    
    def start_charging_session(self, phone_model: Optional[str] = None, 
                               qi_compatible: bool = True,
                               start_battery_percent: Optional[int] = None) -> str:
        """Start a new charging session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        session_id = f"CHG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO charging_sessions 
            (session_id, phone_model, qi_compatible, start_time, start_battery_percent)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, phone_model, qi_compatible, datetime.now(), start_battery_percent))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def end_charging_session(self, session_id: str, end_battery_percent: Optional[int] = None):
        """End a charging session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT start_time FROM charging_sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        if row:
            start_time = datetime.fromisoformat(row['start_time'])
            duration_minutes = int((datetime.now() - start_time).total_seconds() / 60)
            
            cursor.execute('''
                SELECT 
                    AVG(charging_power_w) as avg_power,
                    MAX(charging_power_w) as max_power,
                    AVG(efficiency_percent) as avg_efficiency,
                    MAX(pad_temp_c) as max_temp,
                    SUM(CASE WHEN alignment_score < 80 THEN 1 ELSE 0 END) as misalignment_count,
                    SUM(CASE WHEN pad_temp_c > 45 THEN 1 ELSE 0 END) as overheating_count
                FROM charging_metrics
                WHERE session_id = ?
            ''', (session_id,))
            
            metrics = cursor.fetchone()
            
            avg_power = metrics['avg_power'] or 0.0
            total_power_wh = (avg_power * duration_minutes) / 60.0
            
            cursor.execute('''
                UPDATE charging_sessions
                SET end_time = ?,
                    end_battery_percent = ?,
                    duration_minutes = ?,
                    total_power_wh = ?,
                    avg_power_w = ?,
                    max_power_w = ?,
                    avg_efficiency_percent = ?,
                    max_temp_c = ?,
                    misalignment_count = ?,
                    overheating_count = ?,
                    completed = 1
                WHERE session_id = ?
            ''', (datetime.now(), end_battery_percent, duration_minutes,
                  total_power_wh, avg_power, metrics['max_power'] or 0.0,
                  metrics['avg_efficiency'] or 0.0, metrics['max_temp'] or 0.0,
                  metrics['misalignment_count'] or 0, metrics['overheating_count'] or 0,
                  session_id))
        
        conn.commit()
        conn.close()
    
    def record_charging_metric(self, session_id: str, **kwargs):
        """Record a charging metric."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        fields = ['session_id']
        values = [session_id]
        placeholders = ['?']
        
        for key, value in kwargs.items():
            fields.append(key)
            values.append(value)
            placeholders.append('?')
        
        query = f'''
            INSERT INTO charging_metrics ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        '''
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def record_alert(self, session_id: Optional[str], alert_type: str, 
                    severity: str, message: str):
        """Record a charging alert."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO charging_alerts (session_id, alert_type, severity, message)
            VALUES (?, ?, ?, ?)
        ''', (session_id, alert_type, severity, message))
        
        conn.commit()
        conn.close()
    
    def resolve_alerts(self, alert_type: Optional[str] = None):
        """Mark alerts as resolved."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if alert_type:
            cursor.execute('''
                UPDATE charging_alerts 
                SET resolved = 1 
                WHERE alert_type = ? AND resolved = 0
            ''', (alert_type,))
        else:
            cursor.execute('UPDATE charging_alerts SET resolved = 1 WHERE resolved = 0')
        
        conn.commit()
        conn.close()
    
    def record_pad_health(self, metric_name: str, value: float, 
                         unit: str = '', status: str = 'normal'):
        """Record pad health metric."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pad_health (metric_name, value, unit, status)
            VALUES (?, ?, ?, ?)
        ''', (metric_name, value, unit, status))
        
        conn.commit()
        conn.close()
    
    def update_charging_cycles(self, power_delivered_wh: float, coil_health: float):
        """Update charging cycle count and coil health."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM charging_cycles ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            new_count = row['cycle_count'] + 1
            new_total_power = row['total_power_delivered_wh'] + power_delivered_wh
            
            cursor.execute('''
                INSERT INTO charging_cycles 
                (cycle_count, total_power_delivered_wh, coil_health_percent)
                VALUES (?, ?, ?)
            ''', (new_count, new_total_power, coil_health))
        else:
            cursor.execute('''
                INSERT INTO charging_cycles 
                (cycle_count, total_power_delivered_wh, coil_health_percent)
                VALUES (1, ?, ?)
            ''', (power_delivered_wh, coil_health))
        
        conn.commit()
        conn.close()
    
    def get_charging_sessions(self, limit: int = 50, 
                              completed_only: bool = False) -> List[Dict]:
        """Get charging session history."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM charging_sessions'
        if completed_only:
            query += ' WHERE completed = 1'
        query += ' ORDER BY start_time DESC LIMIT ?'
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_active_session(self) -> Optional[Dict]:
        """Get the current active charging session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM charging_sessions 
            WHERE completed = 0 
            ORDER BY start_time DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_session_metrics(self, session_id: str, limit: int = 100) -> List[Dict]:
        """Get metrics for a specific session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM charging_metrics
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_recent_alerts(self, limit: int = 20, 
                         unresolved_only: bool = False) -> List[Dict]:
        """Get recent charging alerts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM charging_alerts'
        if unresolved_only:
            query += ' WHERE resolved = 0'
        query += ' ORDER BY created_at DESC LIMIT ?'
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_pad_health_history(self, metric_name: Optional[str] = None,
                               hours: int = 24, limit: int = 500) -> List[Dict]:
        """Get pad health history."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        if metric_name:
            cursor.execute('''
                SELECT * FROM pad_health
                WHERE metric_name = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (metric_name, since, limit))
        else:
            cursor.execute('''
                SELECT * FROM pad_health
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (since, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_latest_charging_cycles(self) -> Optional[Dict]:
        """Get latest charging cycle data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM charging_cycles ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_battery_care_tip(self, tip_type: Optional[str] = None) -> Optional[Dict]:
        """Get a battery care tip."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if tip_type:
            cursor.execute('''
                SELECT * FROM battery_care_tips WHERE tip_type = ?
            ''', (tip_type,))
        else:
            cursor.execute('''
                SELECT * FROM battery_care_tips 
                ORDER BY priority DESC, shown_count ASC 
                LIMIT 1
            ''')
        
        row = cursor.fetchone()
        
        if row:
            cursor.execute('''
                UPDATE battery_care_tips 
                SET shown_count = shown_count + 1, last_shown = ?
                WHERE id = ?
            ''', (datetime.now(), row['id']))
            conn.commit()
        
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_battery_care_tips(self) -> List[Dict]:
        """Get all battery care tips."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM battery_care_tips ORDER BY priority DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_charging_statistics(self) -> Dict:
        """Get overall charging statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                AVG(duration_minutes) as avg_duration_min,
                SUM(total_power_wh) as total_power_wh,
                AVG(avg_efficiency_percent) as avg_efficiency,
                MAX(max_temp_c) as max_temp_ever,
                SUM(misalignment_count) as total_misalignments,
                SUM(overheating_count) as total_overheatings
            FROM charging_sessions
            WHERE completed = 1
        ''')
        
        stats = dict(cursor.fetchone())
        
        cursor.execute('''
            SELECT strftime('%H', start_time) as hour, COUNT(*) as count
            FROM charging_sessions
            WHERE completed = 1
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        stats['most_used_hour'] = row['hour'] if row else None
        
        cursor.execute('''
            SELECT phone_model, COUNT(*) as count
            FROM charging_sessions
            WHERE phone_model IS NOT NULL
            GROUP BY phone_model
            ORDER BY count DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        stats['most_common_phone'] = row['phone_model'] if row else None
        
        conn.close()
        
        return stats
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM charging_sessions')
        total_sessions = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM charging_metrics')
        total_metrics = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM charging_alerts')
        total_alerts = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM pad_health')
        total_health_records = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'total_charging_sessions': total_sessions,
            'total_metrics_recorded': total_metrics,
            'total_alerts': total_alerts,
            'total_health_records': total_health_records,
            'database_path': self.db_path
        }
