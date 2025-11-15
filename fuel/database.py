#!/usr/bin/env python3
"""
Fuel Economy Database
Manages fuel economy data, challenges, and lifetime statistics
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any


class FuelEconomyDatabase:
    """Database for fuel economy tracking and optimization."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path is None:
            ROOT = Path(__file__).parent.parent.parent
            db_path = ROOT / 'supersonic' / 'data' / 'supersonic.db'
        
        self.db_path = str(db_path)
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fuel_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                vehicle_year INTEGER,
                vehicle_make TEXT,
                vehicle_model TEXT,
                vehicle_engine TEXT,
                initial_odometer REAL,
                final_odometer REAL,
                distance_miles REAL,
                fuel_consumed_gallons REAL,
                avg_mpg REAL,
                instant_mpg_min REAL,
                instant_mpg_max REAL,
                avg_speed_mph REAL,
                max_speed_mph REAL,
                efficiency_score REAL,
                fuel_cost_per_gallon REAL,
                total_fuel_cost REAL,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fuel_data_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                speed_mph REAL,
                rpm INTEGER,
                throttle_percent REAL,
                fuel_rate_gph REAL,
                instant_mpg REAL,
                trip_mpg REAL,
                tank_avg_mpg REAL,
                latitude REAL,
                longitude REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES fuel_sessions(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fuel_tanks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tank_id TEXT UNIQUE NOT NULL,
                fill_date DATETIME NOT NULL,
                odometer_reading REAL NOT NULL,
                gallons_filled REAL NOT NULL,
                cost_per_gallon REAL,
                total_cost REAL,
                miles_driven REAL,
                calculated_mpg REAL,
                is_full_tank BOOLEAN DEFAULT 1,
                location TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fuel_lifetime_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT DEFAULT 'default',
                total_miles REAL DEFAULT 0,
                total_fuel_gallons REAL DEFAULT 0,
                lifetime_avg_mpg REAL DEFAULT 0,
                total_fuel_cost REAL DEFAULT 0,
                best_tank_mpg REAL DEFAULT 0,
                worst_tank_mpg REAL DEFAULT 0,
                best_trip_mpg REAL DEFAULT 0,
                total_trips INTEGER DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS driving_tips_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                tip_type TEXT NOT NULL,
                tip_message TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                speed_mph REAL,
                rpm INTEGER,
                throttle_percent REAL,
                potential_savings_mpg REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES fuel_sessions(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eco_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id TEXT UNIQUE NOT NULL,
                challenge_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                target_mpg REAL,
                target_duration_days INTEGER,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                reward_points INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eco_challenge_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                progress_percent REAL DEFAULT 0,
                current_mpg REAL,
                best_mpg REAL,
                miles_completed REAL,
                completed BOOLEAN DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (challenge_id) REFERENCES eco_challenges(challenge_id),
                FOREIGN KEY (session_id) REFERENCES fuel_sessions(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fuel_sessions_start ON fuel_sessions(start_time)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fuel_data_points_session ON fuel_data_points(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fuel_tanks_date ON fuel_tanks(fill_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_driving_tips_session ON driving_tips_log(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_eco_challenges_status ON eco_challenges(status)
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, vehicle_info: Dict[str, Any] = None) -> bool:
        """Create new fuel economy session."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            vehicle_info = vehicle_info or {}
            
            cursor.execute("""
                INSERT INTO fuel_sessions (
                    session_id, start_time, vehicle_year, vehicle_make, 
                    vehicle_model, vehicle_engine
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.now().isoformat(),
                vehicle_info.get('year', 2014),
                vehicle_info.get('make', 'Chevrolet'),
                vehicle_info.get('model', 'Sonic LTZ'),
                vehicle_info.get('engine', '1.4L Turbo')
            ))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def log_data_point(self, session_id: str, data: Dict[str, Any]):
        """Log fuel economy data point."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fuel_data_points (
                session_id, timestamp, speed_mph, rpm, throttle_percent,
                fuel_rate_gph, instant_mpg, trip_mpg, tank_avg_mpg,
                latitude, longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now().isoformat(),
            data.get('speed_mph', 0),
            data.get('rpm', 0),
            data.get('throttle_percent', 0),
            data.get('fuel_rate_gph', 0),
            data.get('instant_mpg', 0),
            data.get('trip_mpg', 0),
            data.get('tank_avg_mpg', 0),
            data.get('latitude'),
            data.get('longitude')
        ))
        
        conn.commit()
        conn.close()
    
    def log_driving_tip(self, session_id: str, tip_type: str, tip_message: str, 
                       severity: str = 'info', data: Dict[str, Any] = None):
        """Log a driving tip."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = data or {}
        
        cursor.execute("""
            INSERT INTO driving_tips_log (
                session_id, timestamp, tip_type, tip_message, severity,
                speed_mph, rpm, throttle_percent, potential_savings_mpg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now().isoformat(),
            tip_type,
            tip_message,
            severity,
            data.get('speed_mph'),
            data.get('rpm'),
            data.get('throttle_percent'),
            data.get('potential_savings_mpg')
        ))
        
        conn.commit()
        conn.close()
    
    def end_session(self, session_id: str, summary: Dict[str, Any]):
        """End fuel economy session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fuel_sessions SET
                end_time = ?,
                distance_miles = ?,
                fuel_consumed_gallons = ?,
                avg_mpg = ?,
                instant_mpg_min = ?,
                instant_mpg_max = ?,
                avg_speed_mph = ?,
                max_speed_mph = ?,
                efficiency_score = ?,
                fuel_cost_per_gallon = ?,
                total_fuel_cost = ?
            WHERE session_id = ?
        """, (
            datetime.now().isoformat(),
            summary.get('distance_miles', 0),
            summary.get('fuel_consumed_gallons', 0),
            summary.get('avg_mpg', 0),
            summary.get('instant_mpg_min', 0),
            summary.get('instant_mpg_max', 0),
            summary.get('avg_speed_mph', 0),
            summary.get('max_speed_mph', 0),
            summary.get('efficiency_score', 0),
            summary.get('fuel_cost_per_gallon', 3.50),
            summary.get('total_fuel_cost', 0),
            session_id
        ))
        
        conn.commit()
        conn.close()
        
        self.update_lifetime_stats(summary)
    
    def update_lifetime_stats(self, session_summary: Dict[str, Any]):
        """Update lifetime fuel economy statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fuel_lifetime_stats WHERE vehicle_id = 'default'")
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                INSERT INTO fuel_lifetime_stats (vehicle_id) VALUES ('default')
            """)
            cursor.execute("SELECT * FROM fuel_lifetime_stats WHERE vehicle_id = 'default'")
            row = cursor.fetchone()
        
        new_miles = row['total_miles'] + session_summary.get('distance_miles', 0)
        new_fuel = row['total_fuel_gallons'] + session_summary.get('fuel_consumed_gallons', 0)
        new_lifetime_mpg = new_miles / new_fuel if new_fuel > 0 else 0
        new_cost = row['total_fuel_cost'] + session_summary.get('total_fuel_cost', 0)
        new_trips = row['total_trips'] + 1
        
        trip_mpg = session_summary.get('avg_mpg', 0)
        best_trip = max(row['best_trip_mpg'], trip_mpg)
        
        cursor.execute("""
            UPDATE fuel_lifetime_stats SET
                total_miles = ?,
                total_fuel_gallons = ?,
                lifetime_avg_mpg = ?,
                total_fuel_cost = ?,
                best_trip_mpg = ?,
                total_trips = ?,
                updated_at = ?
            WHERE vehicle_id = 'default'
        """, (
            new_miles,
            new_fuel,
            new_lifetime_mpg,
            new_cost,
            best_trip,
            new_trips,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_lifetime_stats(self) -> Dict[str, Any]:
        """Get lifetime fuel economy statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fuel_lifetime_stats WHERE vehicle_id = 'default'")
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            return {
                'total_miles': 0,
                'total_fuel_gallons': 0,
                'lifetime_avg_mpg': 0,
                'total_fuel_cost': 0,
                'best_tank_mpg': 0,
                'worst_tank_mpg': 0,
                'best_trip_mpg': 0,
                'total_trips': 0
            }
        
        return dict(row)
    
    def add_fuel_tank(self, tank_data: Dict[str, Any]) -> str:
        """Add fuel tank fill-up record."""
        import uuid
        
        tank_id = f"tank_{uuid.uuid4().hex[:8]}"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fuel_tanks (
                tank_id, fill_date, odometer_reading, gallons_filled,
                cost_per_gallon, total_cost, miles_driven, calculated_mpg,
                is_full_tank, location, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tank_id,
            tank_data.get('fill_date', datetime.now().isoformat()),
            tank_data.get('odometer_reading', 0),
            tank_data.get('gallons_filled', 0),
            tank_data.get('cost_per_gallon', 3.50),
            tank_data.get('total_cost', 0),
            tank_data.get('miles_driven', 0),
            tank_data.get('calculated_mpg', 0),
            tank_data.get('is_full_tank', True),
            tank_data.get('location', ''),
            tank_data.get('notes', '')
        ))
        
        conn.commit()
        conn.close()
        
        return tank_id
    
    def get_tank_average_mpg(self, num_tanks: int = 3) -> float:
        """Get average MPG from recent tank fill-ups."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT AVG(calculated_mpg) as avg_mpg
            FROM (
                SELECT calculated_mpg
                FROM fuel_tanks
                WHERE calculated_mpg > 0 AND is_full_tank = 1
                ORDER BY fill_date DESC
                LIMIT ?
            )
        """, (num_tanks,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row['avg_mpg'] if row and row['avg_mpg'] else 0
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent fuel economy sessions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM fuel_sessions
            ORDER BY start_time DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_session_tips(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get driving tips for a session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM driving_tips_log
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def create_eco_challenge(self, challenge_data: Dict[str, Any]) -> str:
        """Create new eco challenge."""
        import uuid
        
        challenge_id = f"challenge_{uuid.uuid4().hex[:8]}"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO eco_challenges (
                challenge_id, challenge_type, title, description,
                target_mpg, target_duration_days, start_date, end_date,
                reward_points
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            challenge_id,
            challenge_data.get('challenge_type', 'daily'),
            challenge_data.get('title', ''),
            challenge_data.get('description', ''),
            challenge_data.get('target_mpg', 30.0),
            challenge_data.get('target_duration_days', 1),
            challenge_data.get('start_date', datetime.now().date().isoformat()),
            challenge_data.get('end_date', (datetime.now() + timedelta(days=1)).date().isoformat()),
            challenge_data.get('reward_points', 100)
        ))
        
        conn.commit()
        conn.close()
        
        return challenge_id
    
    def get_active_challenges(self) -> List[Dict[str, Any]]:
        """Get active eco challenges."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM eco_challenges
            WHERE status = 'active'
            AND end_date >= date('now')
            ORDER BY start_date DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
