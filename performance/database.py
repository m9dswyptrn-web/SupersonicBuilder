#!/usr/bin/env python3
"""
Performance Dashboard Database
Stores performance metrics, alerts, and optimization history
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / 'supersonic' / 'data' / 'performance.db'


class PerformanceDatabase:
    """Database for performance metrics and monitoring."""
    
    def __init__(self, db_path: Path = DB_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _get_conn(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database tables."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_category TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                status TEXT DEFAULT 'normal',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                metric_name TEXT,
                metric_value REAL,
                threshold_value REAL,
                acknowledged BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                details TEXT,
                before_state TEXT,
                after_state TEXT,
                success BOOLEAN DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS process_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_name TEXT NOT NULL,
                process_id INTEGER,
                cpu_percent REAL,
                memory_mb REAL,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
            ON performance_metrics(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metrics_category 
            ON performance_metrics(metric_category)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
            ON performance_alerts(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metric(self, category: str, name: str, value: float, 
                     unit: str = '', status: str = 'normal'):
        """Record a performance metric."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics 
            (metric_category, metric_name, value, unit, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (category, name, value, unit, status))
        
        conn.commit()
        conn.close()
    
    def record_alert(self, alert_type: str, severity: str, message: str,
                    metric_name: str = None, metric_value: float = None,
                    threshold_value: float = None):
        """Record a performance alert."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_alerts 
            (alert_type, severity, message, metric_name, metric_value, threshold_value)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert_type, severity, message, metric_name, metric_value, threshold_value))
        
        conn.commit()
        conn.close()
    
    def record_optimization(self, action_type: str, details: str = None,
                           before_state: Dict = None, after_state: Dict = None,
                           success: bool = True):
        """Record an optimization action."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        before_json = json.dumps(before_state) if before_state else None
        after_json = json.dumps(after_state) if after_state else None
        
        cursor.execute('''
            INSERT INTO optimization_history 
            (action_type, details, before_state, after_state, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (action_type, details, before_json, after_json, success))
        
        conn.commit()
        conn.close()
    
    def record_process_action(self, process_name: str, process_id: int = None,
                             cpu_percent: float = None, memory_mb: float = None,
                             action: str = 'monitored'):
        """Record a process action."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO process_history 
            (process_name, process_id, cpu_percent, memory_mb, action)
            VALUES (?, ?, ?, ?, ?)
        ''', (process_name, process_id, cpu_percent, memory_mb, action))
        
        conn.commit()
        conn.close()
    
    def get_metric_history(self, metric_name: str, hours: int = 1, 
                          limit: int = 1000) -> List[Dict]:
        """Get historical data for a metric."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT metric_category, metric_name, value, unit, status, timestamp
            FROM performance_metrics
            WHERE metric_name = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (metric_name, since.isoformat(), limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_latest_metrics(self, category: str = None) -> List[Dict]:
        """Get latest metrics for each metric name."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT m1.*
                FROM performance_metrics m1
                INNER JOIN (
                    SELECT metric_name, MAX(timestamp) as max_timestamp
                    FROM performance_metrics
                    WHERE metric_category = ?
                    GROUP BY metric_name
                ) m2 ON m1.metric_name = m2.metric_name 
                    AND m1.timestamp = m2.max_timestamp
                ORDER BY m1.timestamp DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT m1.*
                FROM performance_metrics m1
                INNER JOIN (
                    SELECT metric_name, MAX(timestamp) as max_timestamp
                    FROM performance_metrics
                    GROUP BY metric_name
                ) m2 ON m1.metric_name = m2.metric_name 
                    AND m1.timestamp = m2.max_timestamp
                ORDER BY m1.timestamp DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_alerts(self, limit: int = 100, severity: str = None) -> List[Dict]:
        """Get recent alerts."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if severity:
            cursor.execute('''
                SELECT * FROM performance_alerts
                WHERE severity = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (severity, limit))
        else:
            cursor.execute('''
                SELECT * FROM performance_alerts
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_optimization_history(self, limit: int = 50) -> List[Dict]:
        """Get optimization history."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM optimization_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            item = dict(row)
            if item.get('before_state'):
                item['before_state'] = json.loads(item['before_state'])
            if item.get('after_state'):
                item['after_state'] = json.loads(item['after_state'])
            history.append(item)
        
        return history
    
    def get_process_history(self, limit: int = 100) -> List[Dict]:
        """Get process monitoring history."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM process_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM performance_metrics')
        total_metrics = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM performance_alerts')
        total_alerts = cursor.fetchone()['total']
        
        cursor.execute('''
            SELECT COUNT(*) as total FROM performance_alerts 
            WHERE acknowledged = 0
        ''')
        unacknowledged_alerts = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM optimization_history')
        total_optimizations = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            'total_metrics': total_metrics,
            'total_alerts': total_alerts,
            'unacknowledged_alerts': unacknowledged_alerts,
            'total_optimizations': total_optimizations,
            'database_path': str(self.db_path)
        }
    
    def cleanup_old_metrics(self, days: int = 7):
        """Clean up old metrics to save space."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            DELETE FROM performance_metrics
            WHERE timestamp < ?
        ''', (cutoff.isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
