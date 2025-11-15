import sqlite3
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from contextlib import contextmanager


class ParkingDatabase:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            data_dir = Path(__file__).parent.parent.parent / "supersonic" / "data"
            db_path = data_dir / "builds.db"
        
        self.db_path = str(db_path)
        self._local = threading.local()
        self._lock = threading.Lock()
        self._initialized = False
        
        self._ensure_initialized()
    
    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            self._local.connection = conn
        return self._local.connection
    
    @contextmanager
    def _transaction(self):
        conn = self._get_connection()
        try:
            conn.execute("BEGIN")
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    
    def _ensure_initialized(self):
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            conn = self._get_connection()
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS parking_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    duration_seconds REAL,
                    location_gps TEXT,
                    location_name TEXT,
                    closest_object_cm REAL,
                    min_distance_front REAL,
                    min_distance_rear REAL,
                    min_distance_left REAL,
                    min_distance_right REAL,
                    ai_detections TEXT,
                    alerts_triggered INTEGER DEFAULT 0,
                    close_calls INTEGER DEFAULT 0,
                    recording_id TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS parking_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    event_id TEXT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    distance_cm REAL,
                    camera_position TEXT,
                    object_detected TEXT,
                    ai_analysis TEXT,
                    auto_recorded BOOLEAN DEFAULT 0,
                    recording_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES parking_events(event_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS distance_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT,
                    sensor_position TEXT NOT NULL,
                    distance_cm REAL NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES parking_events(event_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS object_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT,
                    alert_id TEXT,
                    camera_position TEXT NOT NULL,
                    object_type TEXT NOT NULL,
                    confidence REAL,
                    distance_estimate_cm REAL,
                    position_x REAL,
                    position_y REAL,
                    ai_model TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES parking_events(event_id),
                    FOREIGN KEY (alert_id) REFERENCES parking_alerts(alert_id)
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_parking_events_type ON parking_events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_parking_events_created ON parking_events(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_parking_alerts_event ON parking_alerts(event_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_parking_alerts_type ON parking_alerts(alert_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_distance_measurements_event ON distance_measurements(event_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_object_detections_event ON object_detections(event_id)")
            
            conn.commit()
            self._initialized = True
    
    def create_parking_event(
        self,
        event_id: str,
        event_type: str,
        location_gps: Optional[str] = None,
        location_name: Optional[str] = None
    ) -> int:
        start_time = datetime.utcnow().isoformat()
        
        with self._transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO parking_events (
                    event_id, event_type, start_time, location_gps, location_name
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (event_id, event_type, start_time, location_gps, location_name)
            )
            return cursor.lastrowid
    
    def update_parking_event(
        self,
        event_id: str,
        end_time: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        closest_object_cm: Optional[float] = None,
        min_distances: Optional[Dict[str, float]] = None,
        ai_detections: Optional[str] = None,
        alerts_triggered: Optional[int] = None,
        close_calls: Optional[int] = None,
        recording_id: Optional[str] = None,
        notes: Optional[str] = None
    ):
        updates = []
        params = []
        
        if end_time is not None:
            updates.append("end_time = ?")
            params.append(end_time)
        if duration_seconds is not None:
            updates.append("duration_seconds = ?")
            params.append(duration_seconds)
        if closest_object_cm is not None:
            updates.append("closest_object_cm = ?")
            params.append(closest_object_cm)
        if min_distances:
            if 'front' in min_distances:
                updates.append("min_distance_front = ?")
                params.append(min_distances['front'])
            if 'rear' in min_distances:
                updates.append("min_distance_rear = ?")
                params.append(min_distances['rear'])
            if 'left' in min_distances:
                updates.append("min_distance_left = ?")
                params.append(min_distances['left'])
            if 'right' in min_distances:
                updates.append("min_distance_right = ?")
                params.append(min_distances['right'])
        if ai_detections is not None:
            updates.append("ai_detections = ?")
            params.append(ai_detections)
        if alerts_triggered is not None:
            updates.append("alerts_triggered = ?")
            params.append(alerts_triggered)
        if close_calls is not None:
            updates.append("close_calls = ?")
            params.append(close_calls)
        if recording_id is not None:
            updates.append("recording_id = ?")
            params.append(recording_id)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        if updates:
            params.append(event_id)
            with self._transaction() as conn:
                conn.execute(
                    f"UPDATE parking_events SET {', '.join(updates)} WHERE event_id = ?",
                    tuple(params)
                )
    
    def create_alert(
        self,
        alert_id: str,
        alert_type: str,
        severity: str,
        message: str,
        event_id: Optional[str] = None,
        distance_cm: Optional[float] = None,
        camera_position: Optional[str] = None,
        object_detected: Optional[str] = None,
        ai_analysis: Optional[str] = None,
        auto_recorded: bool = False,
        recording_id: Optional[str] = None
    ) -> int:
        timestamp = datetime.utcnow().isoformat()
        
        with self._transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO parking_alerts (
                    alert_id, event_id, alert_type, severity, message,
                    distance_cm, camera_position, object_detected, ai_analysis,
                    auto_recorded, recording_id, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (alert_id, event_id, alert_type, severity, message,
                 distance_cm, camera_position, object_detected, ai_analysis,
                 auto_recorded, recording_id, timestamp)
            )
            return cursor.lastrowid
    
    def log_distance_measurement(
        self,
        sensor_position: str,
        distance_cm: float,
        status: str,
        event_id: Optional[str] = None
    ):
        timestamp = datetime.utcnow().isoformat()
        
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO distance_measurements (
                    event_id, sensor_position, distance_cm, status, timestamp
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (event_id, sensor_position, distance_cm, status, timestamp)
            )
    
    def log_object_detection(
        self,
        camera_position: str,
        object_type: str,
        confidence: float,
        distance_estimate_cm: Optional[float] = None,
        position_x: Optional[float] = None,
        position_y: Optional[float] = None,
        ai_model: Optional[str] = None,
        event_id: Optional[str] = None,
        alert_id: Optional[str] = None
    ):
        timestamp = datetime.utcnow().isoformat()
        
        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO object_detections (
                    event_id, alert_id, camera_position, object_type,
                    confidence, distance_estimate_cm, position_x, position_y,
                    ai_model, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (event_id, alert_id, camera_position, object_type,
                 confidence, distance_estimate_cm, position_x, position_y,
                 ai_model, timestamp)
            )
    
    def get_parking_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM parking_events WHERE event_id = ?",
            (event_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM parking_events 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_events_by_type(self, event_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM parking_events 
            WHERE event_type = ?
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (event_type, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_alerts_for_event(self, event_id: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM parking_alerts 
            WHERE event_id = ? 
            ORDER BY timestamp DESC
            """,
            (event_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM parking_alerts 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_detections_for_event(self, event_id: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM object_detections 
            WHERE event_id = ? 
            ORDER BY timestamp DESC
            """,
            (event_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_parking_statistics(self) -> Dict[str, Any]:
        conn = self._get_connection()
        
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_events,
                AVG(duration_seconds) as avg_duration,
                AVG(closest_object_cm) as avg_closest_distance,
                MIN(closest_object_cm) as min_distance_ever,
                SUM(alerts_triggered) as total_alerts,
                SUM(close_calls) as total_close_calls
            FROM parking_events
            WHERE end_time IS NOT NULL
        """)
        row = cursor.fetchone()
        stats = dict(row) if row else {}
        
        cursor = conn.execute("""
            SELECT event_type, COUNT(*) as count
            FROM parking_events
            GROUP BY event_type
            ORDER BY count DESC
        """)
        stats['events_by_type'] = {row['event_type']: row['count'] for row in cursor.fetchall()}
        
        cursor = conn.execute("""
            SELECT alert_type, COUNT(*) as count
            FROM parking_alerts
            GROUP BY alert_type
            ORDER BY count DESC
        """)
        stats['alerts_by_type'] = {row['alert_type']: row['count'] for row in cursor.fetchall()}
        
        cursor = conn.execute("""
            SELECT object_type, COUNT(*) as count, AVG(confidence) as avg_confidence
            FROM object_detections
            GROUP BY object_type
            ORDER BY count DESC
        """)
        stats['detections_by_type'] = {
            row['object_type']: {
                'count': row['count'],
                'avg_confidence': row['avg_confidence']
            }
            for row in cursor.fetchall()
        }
        
        return stats
    
    def close(self):
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
