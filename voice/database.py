#!/usr/bin/env python3
"""
Voice Assistant Database
Stores command history, custom commands, macros, and voice profiles
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class VoiceDatabase:
    """Database for voice assistant service."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'supersonic' / 'data' / 'voice.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                raw_command TEXT NOT NULL,
                parsed_intent TEXT,
                entities TEXT,
                service_called TEXT,
                response TEXT,
                success BOOLEAN DEFAULT 1,
                processing_time_ms REAL,
                user_id TEXT,
                session_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_name TEXT UNIQUE NOT NULL,
                trigger_phrases TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_config TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_macros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                macro_name TEXT UNIQUE NOT NULL,
                trigger_phrase TEXT NOT NULL,
                actions TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                user_name TEXT,
                voice_samples TEXT,
                accent TEXT,
                training_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wake_word_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wake_word TEXT NOT NULL,
                sensitivity REAL DEFAULT 0.5,
                enabled BOOLEAN DEFAULT 1,
                training_samples TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS privacy_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_name TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_command_history_timestamp 
            ON command_history(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_command_history_intent 
            ON command_history(parsed_intent)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_custom_commands_enabled 
            ON custom_commands(enabled)
        ''')
        
        self.conn.commit()
        
        self._init_default_wake_word()
    
    def _init_default_wake_word(self):
        """Initialize default wake word if not exists."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM wake_word_settings')
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute('''
                INSERT INTO wake_word_settings (wake_word, sensitivity, enabled)
                VALUES (?, ?, ?)
            ''', ('Hey Sonic', 0.5, 1))
            self.conn.commit()
    
    def log_command(self, raw_command: str, parsed_intent: str = None, 
                   entities: Dict = None, service_called: str = None,
                   response: str = None, success: bool = True,
                   processing_time_ms: float = None, user_id: str = None,
                   session_id: str = None) -> int:
        """Log a voice command to history."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO command_history 
            (raw_command, parsed_intent, entities, service_called, response, 
             success, processing_time_ms, user_id, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            raw_command,
            parsed_intent,
            json.dumps(entities) if entities else None,
            service_called,
            response,
            success,
            processing_time_ms,
            user_id,
            session_id
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_command_history(self, limit: int = 50, user_id: str = None) -> List[Dict]:
        """Get command history."""
        cursor = self.conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT * FROM command_history 
                WHERE user_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM command_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def create_custom_command(self, command_name: str, trigger_phrases: List[str],
                             action_type: str, action_config: Dict,
                             user_id: str = None) -> int:
        """Create a custom voice command."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO custom_commands 
            (command_name, trigger_phrases, action_type, action_config, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            command_name,
            json.dumps(trigger_phrases),
            action_type,
            json.dumps(action_config),
            user_id
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_custom_commands(self, enabled_only: bool = True) -> List[Dict]:
        """Get all custom commands."""
        cursor = self.conn.cursor()
        
        if enabled_only:
            cursor.execute('SELECT * FROM custom_commands WHERE enabled = 1')
        else:
            cursor.execute('SELECT * FROM custom_commands')
        
        rows = cursor.fetchall()
        commands = []
        for row in rows:
            cmd = dict(row)
            cmd['trigger_phrases'] = json.loads(cmd['trigger_phrases'])
            cmd['action_config'] = json.loads(cmd['action_config'])
            commands.append(cmd)
        return commands
    
    def update_custom_command(self, command_id: int, updates: Dict) -> bool:
        """Update a custom command."""
        cursor = self.conn.cursor()
        
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ['trigger_phrases', 'action_config'] and isinstance(value, (dict, list)):
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(command_id)
        
        query = f"UPDATE custom_commands SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_custom_command(self, command_id: int) -> bool:
        """Delete a custom command."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM custom_commands WHERE id = ?', (command_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def create_macro(self, macro_name: str, trigger_phrase: str, actions: List[Dict]) -> int:
        """Create a voice macro."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO voice_macros (macro_name, trigger_phrase, actions)
            VALUES (?, ?, ?)
        ''', (macro_name, trigger_phrase, json.dumps(actions)))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_macros(self, enabled_only: bool = True) -> List[Dict]:
        """Get all voice macros."""
        cursor = self.conn.cursor()
        
        if enabled_only:
            cursor.execute('SELECT * FROM voice_macros WHERE enabled = 1')
        else:
            cursor.execute('SELECT * FROM voice_macros')
        
        rows = cursor.fetchall()
        macros = []
        for row in rows:
            macro = dict(row)
            macro['actions'] = json.loads(macro['actions'])
            macros.append(macro)
        return macros
    
    def update_macro(self, macro_id: int, updates: Dict) -> bool:
        """Update a voice macro."""
        cursor = self.conn.cursor()
        
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'actions' and isinstance(value, list):
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(macro_id)
        
        query = f"UPDATE voice_macros SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_macro(self, macro_id: int) -> bool:
        """Delete a voice macro."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM voice_macros WHERE id = ?', (macro_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_wake_word_settings(self) -> Dict:
        """Get wake word settings."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM wake_word_settings ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            settings = dict(row)
            if settings.get('training_samples'):
                settings['training_samples'] = json.loads(settings['training_samples'])
            return settings
        return {
            'wake_word': 'Hey Sonic',
            'sensitivity': 0.5,
            'enabled': True
        }
    
    def update_wake_word_settings(self, wake_word: str = None, 
                                  sensitivity: float = None,
                                  enabled: bool = None,
                                  training_samples: List = None) -> bool:
        """Update wake word settings."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM wake_word_settings')
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute('''
                INSERT INTO wake_word_settings (wake_word, sensitivity, enabled, training_samples)
                VALUES (?, ?, ?, ?)
            ''', (
                wake_word or 'Hey Sonic',
                sensitivity if sensitivity is not None else 0.5,
                enabled if enabled is not None else True,
                json.dumps(training_samples) if training_samples else None
            ))
        else:
            updates = []
            values = []
            
            if wake_word is not None:
                updates.append("wake_word = ?")
                values.append(wake_word)
            if sensitivity is not None:
                updates.append("sensitivity = ?")
                values.append(sensitivity)
            if enabled is not None:
                updates.append("enabled = ?")
                values.append(enabled)
            if training_samples is not None:
                updates.append("training_samples = ?")
                values.append(json.dumps(training_samples))
            
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            
            if updates:
                query = f"UPDATE wake_word_settings SET {', '.join(updates)}"
                cursor.execute(query, values)
        
        self.conn.commit()
        return True
    
    def get_privacy_setting(self, setting_name: str) -> Optional[str]:
        """Get a privacy setting value."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT setting_value FROM privacy_settings WHERE setting_name = ?', (setting_name,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def set_privacy_setting(self, setting_name: str, setting_value: str) -> bool:
        """Set a privacy setting."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO privacy_settings (setting_name, setting_value, updated_at)
            VALUES (?, ?, ?)
        ''', (setting_name, setting_value, datetime.now().isoformat()))
        self.conn.commit()
        return True
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM command_history')
        total_commands = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM command_history WHERE success = 1')
        successful_commands = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM custom_commands WHERE enabled = 1')
        active_custom_commands = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM voice_macros WHERE enabled = 1')
        active_macros = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(processing_time_ms) FROM command_history WHERE processing_time_ms IS NOT NULL')
        avg_processing_time = cursor.fetchone()[0] or 0
        
        return {
            'total_commands': total_commands,
            'successful_commands': successful_commands,
            'success_rate': (successful_commands / total_commands * 100) if total_commands > 0 else 0,
            'active_custom_commands': active_custom_commands,
            'active_macros': active_macros,
            'avg_processing_time_ms': round(avg_processing_time, 2)
        }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
