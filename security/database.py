#!/usr/bin/env python3
"""
Security System Database
Handles storage of security events, alerts, GPS tracking, and system settings
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / 'supersonic' / 'data' / 'supersonic.db'


class SecurityDatabase:
    """Database interface for security system."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_schema(self):
        """Initialize database schema for security system."""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    location_lat REAL,
                    location_lng REAL,
                    camera_triggered TEXT,
                    video_recording_id TEXT,
                    snapshot_path TEXT,
                    metadata TEXT,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    alert_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    triggered_by TEXT,
                    notification_sent BOOLEAN DEFAULT 0,
                    notification_type TEXT,
                    acknowledged BOOLEAN DEFAULT 0,
                    acknowledged_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS gps_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_id TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    altitude REAL,
                    speed_kmh REAL,
                    heading REAL,
                    accuracy_meters REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS geofences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fence_id TEXT UNIQUE NOT NULL,
                    fence_name TEXT NOT NULL,
                    center_lat REAL NOT NULL,
                    center_lng REAL NOT NULL,
                    radius_meters REAL NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    alert_on_exit BOOLEAN DEFAULT 1,
                    alert_on_entry BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS security_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS motion_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_id TEXT UNIQUE NOT NULL,
                    camera_position TEXT NOT NULL,
                    detection_type TEXT NOT NULL,
                    confidence REAL,
                    person_detected BOOLEAN DEFAULT 0,
                    bounding_boxes TEXT,
                    snapshot_path TEXT,
                    system_armed BOOLEAN,
                    alert_triggered BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS battery_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    voltage REAL NOT NULL,
                    current_amps REAL,
                    state_of_charge REAL,
                    temperature_celsius REAL,
                    status TEXT,
                    alert_triggered BOOLEAN DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type);
                CREATE INDEX IF NOT EXISTS idx_security_events_created ON security_events(created_at);
                CREATE INDEX IF NOT EXISTS idx_security_alerts_type ON security_alerts(alert_type);
                CREATE INDEX IF NOT EXISTS idx_security_alerts_created ON security_alerts(created_at);
                CREATE INDEX IF NOT EXISTS idx_gps_tracking_track_id ON gps_tracking(track_id);
                CREATE INDEX IF NOT EXISTS idx_gps_tracking_timestamp ON gps_tracking(timestamp);
                CREATE INDEX IF NOT EXISTS idx_motion_detections_camera ON motion_detections(camera_position);
                CREATE INDEX IF NOT EXISTS idx_motion_detections_created ON motion_detections(created_at);
                CREATE INDEX IF NOT EXISTS idx_battery_monitoring_timestamp ON battery_monitoring(timestamp);
            """)
            conn.commit()
    
    def log_event(self, event_id: str, event_type: str, severity: str, 
                  description: str, location: Optional[tuple] = None,
                  camera_triggered: Optional[str] = None, 
                  video_recording_id: Optional[str] = None,
                  snapshot_path: Optional[str] = None,
                  metadata: Optional[dict] = None) -> int:
        """Log a security event."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            lat, lng = location if location else (None, None)
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO security_events 
                (event_id, event_type, severity, description, location_lat, location_lng,
                 camera_triggered, video_recording_id, snapshot_path, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_id, event_type, severity, description, lat, lng,
                  camera_triggered, video_recording_id, snapshot_path, metadata_json))
            
            conn.commit()
            return cursor.lastrowid
    
    def create_alert(self, alert_id: str, alert_type: str, title: str, 
                     message: str, severity: str, triggered_by: Optional[str] = None,
                     notification_sent: bool = False, notification_type: Optional[str] = None) -> int:
        """Create a security alert."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO security_alerts 
                (alert_id, alert_type, title, message, severity, triggered_by,
                 notification_sent, notification_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (alert_id, alert_type, title, message, severity, triggered_by,
                  notification_sent, notification_type))
            conn.commit()
            return cursor.lastrowid
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE security_alerts 
                SET acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP
                WHERE alert_id = ?
            """, (alert_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def log_gps_location(self, track_id: str, latitude: float, longitude: float,
                         altitude: Optional[float] = None, speed_kmh: Optional[float] = None,
                         heading: Optional[float] = None, accuracy_meters: Optional[float] = None) -> int:
        """Log GPS location."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO gps_tracking 
                (track_id, latitude, longitude, altitude, speed_kmh, heading, accuracy_meters)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (track_id, latitude, longitude, altitude, speed_kmh, heading, accuracy_meters))
            conn.commit()
            return cursor.lastrowid
    
    def get_gps_history(self, track_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get GPS tracking history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM gps_tracking 
                WHERE track_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (track_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def create_geofence(self, fence_id: str, fence_name: str, center_lat: float,
                       center_lng: float, radius_meters: float,
                       alert_on_exit: bool = True, alert_on_entry: bool = False) -> int:
        """Create a geofence."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO geofences 
                (fence_id, fence_name, center_lat, center_lng, radius_meters,
                 alert_on_exit, alert_on_entry)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (fence_id, fence_name, center_lat, center_lng, radius_meters,
                  alert_on_exit, alert_on_entry))
            conn.commit()
            return cursor.lastrowid
    
    def get_geofences(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get all geofences."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if enabled_only:
                cursor.execute("SELECT * FROM geofences WHERE enabled = 1")
            else:
                cursor.execute("SELECT * FROM geofences")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_geofence(self, fence_id: str, enabled: Optional[bool] = None,
                       alert_on_exit: Optional[bool] = None,
                       alert_on_entry: Optional[bool] = None) -> bool:
        """Update geofence settings."""
        updates = []
        params = []
        
        if enabled is not None:
            updates.append("enabled = ?")
            params.append(enabled)
        if alert_on_exit is not None:
            updates.append("alert_on_exit = ?")
            params.append(alert_on_exit)
        if alert_on_entry is not None:
            updates.append("alert_on_entry = ?")
            params.append(alert_on_entry)
        
        if not updates:
            return False
        
        params.append(fence_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE geofences 
                SET {', '.join(updates)}
                WHERE fence_id = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a security setting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM security_settings WHERE setting_key = ?", (key,))
            row = cursor.fetchone()
            return row['setting_value'] if row else None
    
    def set_setting(self, key: str, value: str) -> None:
        """Set a security setting."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO security_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET 
                    setting_value = excluded.setting_value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value))
            conn.commit()
    
    def log_motion_detection(self, detection_id: str, camera_position: str,
                            detection_type: str, confidence: float,
                            person_detected: bool = False,
                            bounding_boxes: Optional[list] = None,
                            snapshot_path: Optional[str] = None,
                            system_armed: bool = False,
                            alert_triggered: bool = False) -> int:
        """Log motion detection event."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            boxes_json = json.dumps(bounding_boxes) if bounding_boxes else None
            
            cursor.execute("""
                INSERT INTO motion_detections 
                (detection_id, camera_position, detection_type, confidence,
                 person_detected, bounding_boxes, snapshot_path, system_armed, alert_triggered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (detection_id, camera_position, detection_type, confidence,
                  person_detected, boxes_json, snapshot_path, system_armed, alert_triggered))
            
            conn.commit()
            return cursor.lastrowid
    
    def log_battery_status(self, voltage: float, current_amps: Optional[float] = None,
                          state_of_charge: Optional[float] = None,
                          temperature_celsius: Optional[float] = None,
                          status: Optional[str] = None,
                          alert_triggered: bool = False) -> int:
        """Log battery monitoring data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO battery_monitoring 
                (voltage, current_amps, state_of_charge, temperature_celsius, status, alert_triggered)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (voltage, current_amps, state_of_charge, temperature_celsius, status, alert_triggered))
            conn.commit()
            return cursor.lastrowid
    
    def get_recent_events(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent security events."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if event_type:
                cursor.execute("""
                    SELECT * FROM security_events 
                    WHERE event_type = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (event_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM security_events 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                if event['metadata']:
                    event['metadata'] = json.loads(event['metadata'])
                events.append(event)
            return events
    
    def get_recent_alerts(self, limit: int = 50, acknowledged: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get recent security alerts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if acknowledged is not None:
                cursor.execute("""
                    SELECT * FROM security_alerts 
                    WHERE acknowledged = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (acknowledged, limit))
            else:
                cursor.execute("""
                    SELECT * FROM security_alerts 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_battery_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get battery monitoring history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM battery_monitoring 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
