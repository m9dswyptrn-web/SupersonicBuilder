#!/usr/bin/env python3
"""
Maintenance Reminder Database
Handles all database operations for vehicle maintenance tracking
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / 'supersonic' / 'data' / 'supersonic.db'


class MaintenanceDatabase:
    """Database operations for maintenance tracking."""
    
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
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_name TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                mile_interval INTEGER,
                month_interval INTEGER,
                description TEXT,
                parts_needed TEXT,
                estimated_cost REAL,
                is_active BOOLEAN DEFAULT 1,
                is_custom BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT UNIQUE NOT NULL,
                schedule_id INTEGER,
                service_type TEXT NOT NULL,
                service_date DATE NOT NULL,
                odometer_reading INTEGER NOT NULL,
                service_provider TEXT,
                service_category TEXT DEFAULT 'shop',
                labor_hours REAL DEFAULT 0,
                parts_used TEXT,
                parts_cost REAL DEFAULT 0,
                labor_cost REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                receipt_path TEXT,
                photo_paths TEXT,
                notes TEXT,
                next_service_miles INTEGER,
                next_service_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (schedule_id) REFERENCES maintenance_schedules(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_mileage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                odometer_reading INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'manual'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE NOT NULL,
                schedule_id INTEGER,
                alert_type TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                miles_until_due INTEGER,
                days_until_due INTEGER,
                is_overdue BOOLEAN DEFAULT 0,
                is_dismissed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                dismissed_at DATETIME,
                FOREIGN KEY (schedule_id) REFERENCES maintenance_schedules(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_name TEXT NOT NULL,
                budget_period TEXT DEFAULT 'annual',
                budget_amount REAL NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER,
                part_name TEXT NOT NULL,
                part_number TEXT,
                part_type TEXT DEFAULT 'OEM',
                estimated_price REAL,
                supplier TEXT,
                supplier_url TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (schedule_id) REFERENCES maintenance_schedules(id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_records_date ON maintenance_records(service_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_records_odometer ON maintenance_records(odometer_reading)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_alerts_dismissed ON maintenance_alerts(is_dismissed)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicle_mileage_timestamp ON vehicle_mileage(timestamp)')
        
        conn.commit()
        conn.close()
        
        self._init_default_schedules()
    
    def _init_default_schedules(self):
        """Initialize default maintenance schedules."""
        default_schedules = [
            {
                'name': 'Oil Change',
                'type': 'engine',
                'mile_interval': 5000,
                'month_interval': 6,
                'description': 'Engine oil and filter replacement',
                'parts': 'Engine oil (5qt), Oil filter',
                'estimated_cost': 45.0
            },
            {
                'name': 'Tire Rotation',
                'type': 'tires',
                'mile_interval': 7500,
                'month_interval': None,
                'description': 'Rotate tires and check tire pressure',
                'parts': None,
                'estimated_cost': 25.0
            },
            {
                'name': 'Air Filter Replacement',
                'type': 'engine',
                'mile_interval': 15000,
                'month_interval': None,
                'description': 'Replace engine air filter',
                'parts': 'Engine air filter',
                'estimated_cost': 30.0
            },
            {
                'name': 'Cabin Filter Replacement',
                'type': 'hvac',
                'mile_interval': 15000,
                'month_interval': None,
                'description': 'Replace cabin air filter',
                'parts': 'Cabin air filter',
                'estimated_cost': 25.0
            },
            {
                'name': 'Spark Plugs Replacement',
                'type': 'engine',
                'mile_interval': 30000,
                'month_interval': None,
                'description': 'Replace spark plugs',
                'parts': 'Spark plugs (set of 4-8)',
                'estimated_cost': 120.0
            },
            {
                'name': 'Brake Fluid Flush',
                'type': 'brakes',
                'mile_interval': 30000,
                'month_interval': 24,
                'description': 'Flush and replace brake fluid',
                'parts': 'Brake fluid (1qt)',
                'estimated_cost': 80.0
            },
            {
                'name': 'Transmission Fluid Service',
                'type': 'transmission',
                'mile_interval': 60000,
                'month_interval': None,
                'description': 'Drain and fill transmission fluid',
                'parts': 'Transmission fluid (4-6qt)',
                'estimated_cost': 150.0
            },
            {
                'name': 'Coolant Flush',
                'type': 'cooling',
                'mile_interval': 60000,
                'month_interval': 60,
                'description': 'Flush cooling system and replace coolant',
                'parts': 'Coolant/antifreeze (2gal)',
                'estimated_cost': 100.0
            }
        ]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for schedule in default_schedules:
            cursor.execute('''
                INSERT OR IGNORE INTO maintenance_schedules 
                (schedule_name, schedule_type, mile_interval, month_interval, description, parts_needed, estimated_cost, is_custom)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                schedule['name'],
                schedule['type'],
                schedule['mile_interval'],
                schedule['month_interval'],
                schedule['description'],
                schedule['parts'],
                schedule['estimated_cost']
            ))
        
        conn.commit()
        conn.close()
    
    def get_current_mileage(self) -> Optional[int]:
        """Get current odometer reading."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT odometer_reading 
            FROM vehicle_mileage 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return row['odometer_reading'] if row else None
    
    def update_mileage(self, odometer: int, source: str = 'manual') -> bool:
        """Update current mileage."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO vehicle_mileage (odometer_reading, source)
                VALUES (?, ?)
            ''', (odometer, source))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating mileage: {e}")
            return False
    
    def get_schedules(self, active_only: bool = True) -> List[Dict]:
        """Get maintenance schedules."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM maintenance_schedules'
        if active_only:
            query += ' WHERE is_active = 1'
        query += ' ORDER BY mile_interval ASC'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_schedule(self, name: str, schedule_type: str, mile_interval: int = None,
                    month_interval: int = None, description: str = None,
                    parts_needed: str = None, estimated_cost: float = 0) -> Optional[int]:
        """Add custom maintenance schedule."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO maintenance_schedules 
                (schedule_name, schedule_type, mile_interval, month_interval, description, parts_needed, estimated_cost, is_custom)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (name, schedule_type, mile_interval, month_interval, description, parts_needed, estimated_cost))
            
            schedule_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return schedule_id
        except Exception as e:
            print(f"Error adding schedule: {e}")
            return None
    
    def add_maintenance_record(self, service_type: str, service_date: str, odometer: int,
                               schedule_id: int = None, service_provider: str = None,
                               service_category: str = 'shop', labor_hours: float = 0,
                               parts_used: str = None, parts_cost: float = 0,
                               labor_cost: float = 0, receipt_path: str = None,
                               photo_paths: List[str] = None, notes: str = None) -> Optional[str]:
        """Add maintenance record."""
        try:
            import uuid
            record_id = f"maint_{uuid.uuid4().hex[:12]}"
            total_cost = parts_cost + labor_cost
            
            photo_json = json.dumps(photo_paths) if photo_paths else None
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO maintenance_records 
                (record_id, schedule_id, service_type, service_date, odometer_reading, 
                 service_provider, service_category, labor_hours, parts_used, parts_cost, 
                 labor_cost, total_cost, receipt_path, photo_paths, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, schedule_id, service_type, service_date, odometer, 
                  service_provider, service_category, labor_hours, parts_used, parts_cost,
                  labor_cost, total_cost, receipt_path, photo_json, notes))
            
            conn.commit()
            conn.close()
            
            self.update_mileage(odometer, 'service_record')
            
            return record_id
        except Exception as e:
            print(f"Error adding maintenance record: {e}")
            return None
    
    def get_maintenance_records(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get maintenance records."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mr.*, ms.schedule_name, ms.schedule_type
            FROM maintenance_records mr
            LEFT JOIN maintenance_schedules ms ON mr.schedule_id = ms.id
            ORDER BY mr.service_date DESC, mr.created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            record = dict(row)
            if record.get('photo_paths'):
                try:
                    record['photo_paths'] = json.loads(record['photo_paths'])
                except:
                    record['photo_paths'] = []
            records.append(record)
        
        return records
    
    def get_record(self, record_id: str) -> Optional[Dict]:
        """Get single maintenance record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mr.*, ms.schedule_name, ms.schedule_type
            FROM maintenance_records mr
            LEFT JOIN maintenance_schedules ms ON mr.schedule_id = ms.id
            WHERE mr.record_id = ?
        ''', (record_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            record = dict(row)
            if record.get('photo_paths'):
                try:
                    record['photo_paths'] = json.loads(record['photo_paths'])
                except:
                    record['photo_paths'] = []
            return record
        return None
    
    def create_alert(self, schedule_id: int, alert_type: str, severity: str,
                    title: str, message: str, miles_until_due: int = None,
                    days_until_due: int = None, is_overdue: bool = False) -> Optional[str]:
        """Create maintenance alert."""
        try:
            import uuid
            alert_id = f"alert_{uuid.uuid4().hex[:8]}"
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO maintenance_alerts 
                (alert_id, schedule_id, alert_type, severity, title, message, 
                 miles_until_due, days_until_due, is_overdue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (alert_id, schedule_id, alert_type, severity, title, message,
                  miles_until_due, days_until_due, is_overdue))
            
            conn.commit()
            conn.close()
            return alert_id
        except Exception as e:
            print(f"Error creating alert: {e}")
            return None
    
    def get_active_alerts(self) -> List[Dict]:
        """Get active alerts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ma.*, ms.schedule_name, ms.schedule_type
            FROM maintenance_alerts ma
            LEFT JOIN maintenance_schedules ms ON ma.schedule_id = ms.id
            WHERE ma.is_dismissed = 0
            ORDER BY ma.severity DESC, ma.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss an alert."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE maintenance_alerts 
                SET is_dismissed = 1, dismissed_at = CURRENT_TIMESTAMP
                WHERE alert_id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error dismissing alert: {e}")
            return False
    
    def get_cost_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get cost summary for a period."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                COUNT(*) as total_services,
                SUM(total_cost) as total_spent,
                SUM(parts_cost) as total_parts,
                SUM(labor_cost) as total_labor,
                SUM(CASE WHEN service_category = 'diy' THEN 1 ELSE 0 END) as diy_count,
                SUM(CASE WHEN service_category = 'shop' THEN 1 ELSE 0 END) as shop_count,
                AVG(total_cost) as avg_cost
            FROM maintenance_records
            WHERE 1=1
        '''
        
        params = []
        if start_date:
            query += ' AND service_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND service_date <= ?'
            params.append(end_date)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}
    
    def get_cost_by_category(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get costs grouped by service category."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                service_category,
                COUNT(*) as service_count,
                SUM(total_cost) as total_cost,
                AVG(total_cost) as avg_cost
            FROM maintenance_records
            WHERE 1=1
        '''
        
        params = []
        if start_date:
            query += ' AND service_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND service_date <= ?'
            params.append(end_date)
        
        query += ' GROUP BY service_category'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def add_parts_recommendation(self, schedule_id: int, part_name: str,
                                part_number: str = None, part_type: str = 'OEM',
                                estimated_price: float = None, supplier: str = None,
                                supplier_url: str = None, notes: str = None) -> Optional[int]:
        """Add parts recommendation."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO parts_recommendations 
                (schedule_id, part_name, part_number, part_type, estimated_price, supplier, supplier_url, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (schedule_id, part_name, part_number, part_type, estimated_price, supplier, supplier_url, notes))
            
            rec_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return rec_id
        except Exception as e:
            print(f"Error adding parts recommendation: {e}")
            return None
    
    def get_parts_recommendations(self, schedule_id: int = None) -> List[Dict]:
        """Get parts recommendations."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if schedule_id:
            cursor.execute('SELECT * FROM parts_recommendations WHERE schedule_id = ?', (schedule_id,))
        else:
            cursor.execute('SELECT * FROM parts_recommendations')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
