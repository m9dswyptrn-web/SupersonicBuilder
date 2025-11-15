import sqlite3
import json
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from contextlib import contextmanager


class SoundStageDatabase:
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
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS soundstage_presets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preset_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    speaker_positions TEXT NOT NULL,
                    balance_settings TEXT NOT NULL,
                    fader_settings TEXT NOT NULL,
                    acoustic_corrections TEXT,
                    time_alignment TEXT,
                    center_image_settings TEXT,
                    listening_position TEXT DEFAULT 'driver',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS soundstage_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id TEXT UNIQUE NOT NULL,
                    measurement_type TEXT NOT NULL,
                    frequency_response TEXT,
                    impulse_response TEXT,
                    rew_import_data TEXT,
                    speaker_position TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS soundstage_ai_tunings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tuning_id TEXT UNIQUE NOT NULL,
                    analysis TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    applied_settings TEXT,
                    model TEXT DEFAULT 'claude-sonnet-4',
                    tokens_used INTEGER,
                    confidence_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_soundstage_presets_position 
                    ON soundstage_presets(listening_position);
                CREATE INDEX IF NOT EXISTS idx_soundstage_measurements_type 
                    ON soundstage_measurements(measurement_type);
                CREATE INDEX IF NOT EXISTS idx_soundstage_ai_tunings_created 
                    ON soundstage_ai_tunings(created_at);
            """)
            conn.commit()
            
            self._initialized = True
    
    def save_preset(
        self,
        preset_name: str,
        speaker_positions: Dict,
        balance_settings: Dict,
        fader_settings: Dict,
        description: Optional[str] = None,
        acoustic_corrections: Optional[Dict] = None,
        time_alignment: Optional[Dict] = None,
        center_image_settings: Optional[Dict] = None,
        listening_position: str = 'driver'
    ) -> int:
        with self._transaction() as conn:
            cursor = conn.execute(
                """
                INSERT OR REPLACE INTO soundstage_presets (
                    preset_name, description, speaker_positions, balance_settings,
                    fader_settings, acoustic_corrections, time_alignment,
                    center_image_settings, listening_position, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    preset_name,
                    description,
                    json.dumps(speaker_positions),
                    json.dumps(balance_settings),
                    json.dumps(fader_settings),
                    json.dumps(acoustic_corrections) if acoustic_corrections else None,
                    json.dumps(time_alignment) if time_alignment else None,
                    json.dumps(center_image_settings) if center_image_settings else None,
                    listening_position,
                    datetime.utcnow().isoformat()
                )
            )
            return cursor.lastrowid
    
    def get_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM soundstage_presets WHERE preset_name = ?",
            (preset_name,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        preset = dict(row)
        for key in ['speaker_positions', 'balance_settings', 'fader_settings', 
                    'acoustic_corrections', 'time_alignment', 'center_image_settings']:
            if preset.get(key):
                preset[key] = json.loads(preset[key])
        
        return preset
    
    def list_presets(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT preset_name, description, listening_position, created_at, updated_at
            FROM soundstage_presets
            ORDER BY preset_name
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_preset(self, preset_name: str):
        with self._transaction() as conn:
            conn.execute("DELETE FROM soundstage_presets WHERE preset_name = ?", (preset_name,))
    
    def save_measurement(
        self,
        measurement_id: str,
        measurement_type: str,
        frequency_response: Optional[Dict] = None,
        impulse_response: Optional[Dict] = None,
        rew_import_data: Optional[Dict] = None,
        speaker_position: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        with self._transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO soundstage_measurements (
                    measurement_id, measurement_type, frequency_response,
                    impulse_response, rew_import_data, speaker_position, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    measurement_id,
                    measurement_type,
                    json.dumps(frequency_response) if frequency_response else None,
                    json.dumps(impulse_response) if impulse_response else None,
                    json.dumps(rew_import_data) if rew_import_data else None,
                    speaker_position,
                    notes
                )
            )
            return cursor.lastrowid
    
    def get_measurement(self, measurement_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM soundstage_measurements WHERE measurement_id = ?",
            (measurement_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        measurement = dict(row)
        for key in ['frequency_response', 'impulse_response', 'rew_import_data']:
            if measurement.get(key):
                measurement[key] = json.loads(measurement[key])
        
        return measurement
    
    def list_measurements(self, measurement_type: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        if measurement_type:
            cursor = conn.execute(
                """
                SELECT measurement_id, measurement_type, speaker_position, created_at
                FROM soundstage_measurements
                WHERE measurement_type = ?
                ORDER BY created_at DESC
                """,
                (measurement_type,)
            )
        else:
            cursor = conn.execute(
                """
                SELECT measurement_id, measurement_type, speaker_position, created_at
                FROM soundstage_measurements
                ORDER BY created_at DESC
                """
            )
        return [dict(row) for row in cursor.fetchall()]
    
    def save_ai_tuning(
        self,
        tuning_id: str,
        analysis: str,
        recommendations: Dict,
        applied_settings: Optional[Dict] = None,
        model: str = 'claude-sonnet-4',
        tokens_used: Optional[int] = None,
        confidence_score: Optional[float] = None
    ) -> int:
        with self._transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO soundstage_ai_tunings (
                    tuning_id, analysis, recommendations, applied_settings,
                    model, tokens_used, confidence_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tuning_id,
                    analysis,
                    json.dumps(recommendations),
                    json.dumps(applied_settings) if applied_settings else None,
                    model,
                    tokens_used,
                    confidence_score
                )
            )
            return cursor.lastrowid
    
    def get_ai_tuning(self, tuning_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM soundstage_ai_tunings WHERE tuning_id = ?",
            (tuning_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        tuning = dict(row)
        for key in ['recommendations', 'applied_settings']:
            if tuning.get(key):
                tuning[key] = json.loads(tuning[key])
        
        return tuning
    
    def list_ai_tunings(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT tuning_id, model, confidence_score, created_at
            FROM soundstage_ai_tunings
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        conn = self._get_connection()
        
        stats = {}
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM soundstage_presets")
        stats['total_presets'] = cursor.fetchone()['count']
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM soundstage_measurements")
        stats['total_measurements'] = cursor.fetchone()['count']
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM soundstage_ai_tunings")
        stats['total_ai_tunings'] = cursor.fetchone()['count']
        
        return stats
    
    def close(self):
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
