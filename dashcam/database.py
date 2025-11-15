#!/usr/bin/env python3
"""
Dash Cam Database Interface
Manages recordings, incidents, settings, and storage
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class DashcamDatabase:
    """Database interface for dashcam service."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        if db_path is None:
            root = Path(__file__).parent.parent.parent
            db_path = root / "supersonic" / "data" / "supersonic.db"
        
        self.db_path = str(db_path)
        self._init_db()
    
    def _init_db(self):
        """Ensure database and tables exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashcam_recordings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recording_id TEXT UNIQUE NOT NULL,
                camera_layout TEXT NOT NULL,
                recording_type TEXT DEFAULT 'continuous',
                video_path TEXT NOT NULL,
                duration_seconds REAL,
                file_size_mb REAL,
                quality TEXT DEFAULT '1080p',
                protected BOOLEAN DEFAULT 0,
                loop_recording BOOLEAN DEFAULT 1,
                gps_data TEXT,
                timestamp_overlay BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashcam_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT UNIQUE NOT NULL,
                incident_type TEXT NOT NULL,
                recording_id TEXT,
                severity TEXT DEFAULT 'medium',
                g_force_value REAL,
                speed_kmh REAL,
                location_lat REAL,
                location_lng REAL,
                thumbnail_path TEXT,
                video_clip_path TEXT,
                protected BOOLEAN DEFAULT 1,
                cloud_uploaded BOOLEAN DEFAULT 0,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recording_id) REFERENCES dashcam_recordings(recording_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashcam_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashcam_storage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_storage_gb REAL,
                used_storage_gb REAL,
                available_storage_gb REAL,
                recording_count INTEGER,
                protected_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dashcam_cloud_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id TEXT UNIQUE NOT NULL,
                incident_id TEXT,
                file_path TEXT NOT NULL,
                file_size_mb REAL,
                upload_status TEXT DEFAULT 'pending',
                wifi_connected BOOLEAN DEFAULT 0,
                cloud_url TEXT,
                uploaded_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES dashcam_incidents(incident_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dashcam_recordings_created 
            ON dashcam_recordings(created_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dashcam_recordings_protected 
            ON dashcam_recordings(protected)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dashcam_incidents_created 
            ON dashcam_incidents(created_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dashcam_incidents_type 
            ON dashcam_incidents(incident_type)
        """)
        
        self._init_default_settings(cursor)
        
        conn.commit()
        conn.close()
    
    def _init_default_settings(self, cursor):
        """Initialize default settings."""
        default_settings = {
            'recording_quality': '1080p',
            'loop_recording_enabled': 'true',
            'parking_mode_enabled': 'false',
            'parking_mode_sensitivity': '0.7',
            'battery_cutoff_voltage': '11.8',
            'g_sensor_sensitivity': '0.5',
            'auto_snapshot_on_honk': 'true',
            'cloud_backup_enabled': 'true',
            'cloud_auto_upload_wifi': 'true',
            'storage_max_gb': '128',
            'storage_alert_threshold_gb': '10',
            'timestamp_overlay': 'true',
            'gps_overlay': 'true',
            'continuous_recording': 'true'
        }
        
        for key, value in default_settings.items():
            cursor.execute("""
                INSERT OR IGNORE INTO dashcam_settings (key, value)
                VALUES (?, ?)
            """, (key, value))
    
    def create_recording(self, recording_id: str, camera_layout: str,
                        video_path: str, recording_type: str = 'continuous',
                        quality: str = '1080p', protected: bool = False,
                        gps_data: dict = None) -> int:
        """Create a new recording entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        gps_json = json.dumps(gps_data) if gps_data else None
        
        cursor.execute("""
            INSERT INTO dashcam_recordings 
            (recording_id, camera_layout, recording_type, video_path, quality,
             protected, gps_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (recording_id, camera_layout, recording_type, video_path, quality,
              protected, gps_json, datetime.now().isoformat()))
        
        recording_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return recording_db_id
    
    def update_recording(self, recording_id: str, duration_seconds: float = None,
                        file_size_mb: float = None):
        """Update recording with duration and file size."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if duration_seconds is not None:
            updates.append("duration_seconds = ?")
            params.append(duration_seconds)
        
        if file_size_mb is not None:
            updates.append("file_size_mb = ?")
            params.append(file_size_mb)
        
        if updates:
            params.append(recording_id)
            query = f"UPDATE dashcam_recordings SET {', '.join(updates)} WHERE recording_id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def set_recording_protected(self, recording_id: str, protected: bool = True) -> bool:
        """Mark/unmark recording as protected."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE dashcam_recordings SET protected = ? WHERE recording_id = ?
        """, (protected, recording_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def create_incident(self, incident_id: str, incident_type: str,
                       recording_id: str = None, severity: str = 'medium',
                       g_force_value: float = None, speed_kmh: float = None,
                       location_lat: float = None, location_lng: float = None,
                       thumbnail_path: str = None, video_clip_path: str = None,
                       metadata: dict = None) -> int:
        """Create a new incident entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO dashcam_incidents 
            (incident_id, incident_type, recording_id, severity, g_force_value,
             speed_kmh, location_lat, location_lng, thumbnail_path,
             video_clip_path, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (incident_id, incident_type, recording_id, severity, g_force_value,
              speed_kmh, location_lat, location_lng, thumbnail_path,
              video_clip_path, metadata_json, datetime.now().isoformat()))
        
        incident_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return incident_db_id
    
    def mark_incident_uploaded(self, incident_id: str, cloud_url: str = None) -> bool:
        """Mark incident as uploaded to cloud."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE dashcam_incidents 
            SET cloud_uploaded = 1
            WHERE incident_id = ?
        """, (incident_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_incidents(self, limit: int = 100, incident_type: str = None) -> List[Dict]:
        """Get incidents, optionally filtered by type."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if incident_type:
            cursor.execute("""
                SELECT * FROM dashcam_incidents 
                WHERE incident_type = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (incident_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM dashcam_incidents 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_incident(self, incident_id: str) -> Optional[Dict]:
        """Get a specific incident."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM dashcam_incidents WHERE incident_id = ?
        """, (incident_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_recordings(self, limit: int = 100, protected_only: bool = False) -> List[Dict]:
        """Get recordings."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if protected_only:
            cursor.execute("""
                SELECT * FROM dashcam_recordings 
                WHERE protected = 1
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        else:
            cursor.execute("""
                SELECT * FROM dashcam_recordings 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_recording(self, recording_id: str) -> Optional[Dict]:
        """Get a specific recording."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM dashcam_recordings WHERE recording_id = ?
        """, (recording_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording (only if not protected)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM dashcam_recordings 
            WHERE recording_id = ? AND protected = 0
        """, (recording_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def delete_old_recordings(self, keep_count: int = 100) -> int:
        """Delete old unprotected recordings, keeping only recent ones."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM dashcam_recordings 
            WHERE protected = 0 
            AND id NOT IN (
                SELECT id FROM dashcam_recordings 
                WHERE protected = 0 
                ORDER BY created_at DESC 
                LIMIT ?
            )
        """, (keep_count,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def log_storage_status(self, total_gb: float, used_gb: float,
                          available_gb: float, recording_count: int,
                          protected_count: int):
        """Log storage status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO dashcam_storage_logs 
            (total_storage_gb, used_storage_gb, available_storage_gb,
             recording_count, protected_count, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (total_gb, used_gb, available_gb, recording_count,
              protected_count, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def create_cloud_upload(self, upload_id: str, incident_id: str,
                           file_path: str, file_size_mb: float,
                           wifi_connected: bool = False) -> int:
        """Create cloud upload entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO dashcam_cloud_uploads 
            (upload_id, incident_id, file_path, file_size_mb, wifi_connected,
             upload_status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (upload_id, incident_id, file_path, file_size_mb, wifi_connected,
              datetime.now().isoformat()))
        
        upload_db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return upload_db_id
    
    def update_cloud_upload(self, upload_id: str, status: str,
                           cloud_url: str = None):
        """Update cloud upload status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if cloud_url:
            cursor.execute("""
                UPDATE dashcam_cloud_uploads 
                SET upload_status = ?, cloud_url = ?, uploaded_at = ?
                WHERE upload_id = ?
            """, (status, cloud_url, datetime.now().isoformat(), upload_id))
        else:
            cursor.execute("""
                UPDATE dashcam_cloud_uploads 
                SET upload_status = ?
                WHERE upload_id = ?
            """, (status, upload_id))
        
        conn.commit()
        conn.close()
    
    def get_pending_uploads(self, wifi_only: bool = False) -> List[Dict]:
        """Get pending cloud uploads."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if wifi_only:
            cursor.execute("""
                SELECT * FROM dashcam_cloud_uploads 
                WHERE upload_status = 'pending' AND wifi_connected = 1
                ORDER BY created_at ASC
            """)
        else:
            cursor.execute("""
                SELECT * FROM dashcam_cloud_uploads 
                WHERE upload_status = 'pending'
                ORDER BY created_at ASC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM dashcam_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set a setting value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO dashcam_settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM dashcam_settings")
        rows = cursor.fetchall()
        conn.close()
        
        return {row['key']: row['value'] for row in rows}
    
    def get_stats(self) -> Dict:
        """Get dashcam statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM dashcam_recordings")
        total_recordings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dashcam_recordings WHERE protected = 1")
        protected_recordings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dashcam_incidents")
        total_incidents = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT SUM(file_size_mb) FROM dashcam_recordings
        """)
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT incident_type, COUNT(*) FROM dashcam_incidents 
            GROUP BY incident_type
        """)
        incidents_by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT COUNT(*) FROM dashcam_cloud_uploads 
            WHERE upload_status = 'completed'
        """)
        cloud_uploads = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_recordings': total_recordings,
            'protected_recordings': protected_recordings,
            'total_incidents': total_incidents,
            'total_size_mb': total_size,
            'incidents_by_type': incidents_by_type,
            'cloud_uploads_completed': cloud_uploads
        }
