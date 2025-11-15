#!/usr/bin/env python3
"""
Navigation Database Module
Handles saved locations, routes, POI cache, and navigation history
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

DB_PATH = Path(__file__).parent.parent.parent / 'supersonic' / 'data' / 'navigation.db'


class NavigationDatabase:
    """Database operations for navigation service."""
    
    def __init__(self):
        """Initialize database connection."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(DB_PATH)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                label TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                icon TEXT DEFAULT 'pin',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS route_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id TEXT UNIQUE NOT NULL,
                origin_lat REAL NOT NULL,
                origin_lng REAL NOT NULL,
                dest_lat REAL NOT NULL,
                dest_lng REAL NOT NULL,
                origin_address TEXT,
                dest_address TEXT,
                route_type TEXT DEFAULT 'fastest',
                distance_miles REAL,
                duration_minutes REAL,
                fuel_used_gallons REAL,
                avg_speed_mph REAL,
                waypoints TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS poi_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poi_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                address TEXT,
                rating REAL,
                distance_miles REAL,
                amenities TEXT,
                phone TEXT,
                hours TEXT,
                cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT UNIQUE NOT NULL,
                incident_type TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                severity TEXT DEFAULT 'medium',
                description TEXT,
                delay_minutes REAL,
                start_time DATETIME,
                end_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speed_limit_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                road_name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                speed_limit_mph INTEGER NOT NULL,
                road_type TEXT,
                cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS navigation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                route_id TEXT,
                destination_name TEXT,
                current_lat REAL,
                current_lng REAL,
                current_speed_mph REAL,
                current_speed_limit INTEGER,
                next_turn_distance_miles REAL,
                next_turn_instruction TEXT,
                eta_minutes REAL,
                fuel_consumed_gallons REAL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                FOREIGN KEY (route_id) REFERENCES route_history(route_id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_saved_locations_label ON saved_locations(label)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_history_created ON route_history(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_poi_cache_category ON poi_cache(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_incidents_type ON traffic_incidents(incident_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_speed_limit_cache_road ON speed_limit_cache(road_name)")
        
        conn.commit()
        conn.close()
    
    def save_location(self, location_id: str, name: str, label: str, latitude: float, 
                     longitude: float, address: str = None, icon: str = 'pin') -> bool:
        """Save a location (home, work, favorite)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO saved_locations 
                (location_id, name, label, latitude, longitude, address, icon)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (location_id, name, label, latitude, longitude, address, icon))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving location: {e}")
            return False
    
    def get_saved_locations(self) -> List[Dict[str, Any]]:
        """Get all saved locations."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM saved_locations 
            ORDER BY 
                CASE label
                    WHEN 'home' THEN 1
                    WHEN 'work' THEN 2
                    ELSE 3
                END,
                last_used DESC NULLS LAST,
                created_at DESC
        """)
        
        locations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return locations
    
    def get_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get a saved location by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM saved_locations WHERE location_id = ?", (location_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_location_last_used(self, location_id: str):
        """Update last used timestamp for a location."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE saved_locations 
            SET last_used = CURRENT_TIMESTAMP 
            WHERE location_id = ?
        """, (location_id,))
        
        conn.commit()
        conn.close()
    
    def delete_location(self, location_id: str) -> bool:
        """Delete a saved location."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM saved_locations WHERE location_id = ?", (location_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting location: {e}")
            return False
    
    def save_route(self, route_id: str, origin: Dict, destination: Dict, 
                   route_type: str, distance_miles: float, duration_minutes: float,
                   waypoints: List = None) -> bool:
        """Save route to history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            waypoints_json = json.dumps(waypoints) if waypoints else None
            
            cursor.execute("""
                INSERT INTO route_history 
                (route_id, origin_lat, origin_lng, dest_lat, dest_lng, 
                 origin_address, dest_address, route_type, distance_miles, 
                 duration_minutes, waypoints)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (route_id, origin['lat'], origin['lng'], destination['lat'], 
                  destination['lng'], origin.get('address'), destination.get('address'),
                  route_type, distance_miles, duration_minutes, waypoints_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving route: {e}")
            return False
    
    def get_recent_routes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent routes."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM route_history 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        routes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return routes
    
    def cache_poi(self, poi_id: str, name: str, category: str, latitude: float, 
                  longitude: float, address: str = None, rating: float = None,
                  distance_miles: float = None, amenities: List = None) -> bool:
        """Cache POI data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            amenities_json = json.dumps(amenities) if amenities else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO poi_cache 
                (poi_id, name, category, latitude, longitude, address, rating, 
                 distance_miles, amenities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (poi_id, name, category, latitude, longitude, address, rating,
                  distance_miles, amenities_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error caching POI: {e}")
            return False
    
    def get_cached_pois(self, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get cached POIs."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT * FROM poi_cache 
                WHERE category = ?
                ORDER BY distance_miles ASC
                LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
                SELECT * FROM poi_cache 
                ORDER BY distance_miles ASC
                LIMIT ?
            """, (limit,))
        
        pois = []
        for row in cursor.fetchall():
            poi = dict(row)
            if poi.get('amenities'):
                poi['amenities'] = json.loads(poi['amenities'])
            pois.append(poi)
        
        conn.close()
        return pois
    
    def add_traffic_incident(self, incident_id: str, incident_type: str, 
                            latitude: float, longitude: float, severity: str = 'medium',
                            description: str = None, delay_minutes: float = None) -> bool:
        """Add traffic incident."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO traffic_incidents 
                (incident_id, incident_type, latitude, longitude, severity, 
                 description, delay_minutes, start_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (incident_id, incident_type, latitude, longitude, severity,
                  description, delay_minutes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding traffic incident: {e}")
            return False
    
    def get_traffic_incidents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get traffic incidents."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT * FROM traffic_incidents 
                WHERE end_time IS NULL OR end_time > CURRENT_TIMESTAMP
                ORDER BY severity DESC, created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT * FROM traffic_incidents 
                ORDER BY created_at DESC
                LIMIT 100
            """)
        
        incidents = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return incidents
    
    def cache_speed_limit(self, road_name: str, latitude: float, longitude: float, 
                         speed_limit_mph: int, road_type: str = None) -> bool:
        """Cache speed limit data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO speed_limit_cache 
                (road_name, latitude, longitude, speed_limit_mph, road_type)
                VALUES (?, ?, ?, ?, ?)
            """, (road_name, latitude, longitude, speed_limit_mph, road_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error caching speed limit: {e}")
            return False
    
    def get_speed_limit(self, road_name: str) -> Optional[int]:
        """Get cached speed limit for a road."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT speed_limit_mph FROM speed_limit_cache 
            WHERE road_name = ?
            ORDER BY cached_at DESC
            LIMIT 1
        """, (road_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def create_navigation_session(self, session_id: str, route_id: str = None, 
                                 destination_name: str = None) -> bool:
        """Create a navigation session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO navigation_sessions 
                (session_id, route_id, destination_name)
                VALUES (?, ?, ?)
            """, (session_id, route_id, destination_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating navigation session: {e}")
            return False
    
    def update_navigation_session(self, session_id: str, data: Dict) -> bool:
        """Update navigation session data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            values = []
            
            for key in ['current_lat', 'current_lng', 'current_speed_mph', 
                       'current_speed_limit', 'next_turn_distance_miles', 
                       'next_turn_instruction', 'eta_minutes', 'fuel_consumed_gallons']:
                if key in data:
                    updates.append(f"{key} = ?")
                    values.append(data[key])
            
            if updates:
                values.append(session_id)
                query = f"UPDATE navigation_sessions SET {', '.join(updates)} WHERE session_id = ?"
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating navigation session: {e}")
            return False
    
    def end_navigation_session(self, session_id: str) -> bool:
        """End a navigation session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE navigation_sessions 
                SET ended_at = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            """, (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error ending navigation session: {e}")
            return False
