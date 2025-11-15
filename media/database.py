#!/usr/bin/env python3
"""
Media Center Pro - Database Module
Handles all database operations for media library
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class MediaDatabase:
    """Database handler for media library."""
    
    def __init__(self, db_path: str = 'data/media_center.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS music_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT,
                title TEXT,
                artist TEXT,
                album TEXT,
                album_artist TEXT,
                year INTEGER,
                genre TEXT,
                track_number INTEGER,
                disc_number INTEGER,
                duration_seconds REAL,
                bitrate INTEGER,
                sample_rate INTEGER,
                channels INTEGER,
                format TEXT,
                album_art_path TEXT,
                play_count INTEGER DEFAULT 0,
                last_played DATETIME,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_modified DATETIME,
                rating INTEGER DEFAULT 0,
                favorite BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT,
                title TEXT,
                duration_seconds REAL,
                width INTEGER,
                height INTEGER,
                fps REAL,
                codec TEXT,
                bitrate INTEGER,
                format TEXT,
                thumbnail_path TEXT,
                play_count INTEGER DEFAULT 0,
                last_played DATETIME,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_modified DATETIME,
                rating INTEGER DEFAULT 0,
                favorite BOOLEAN DEFAULT 0,
                folder_path TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT DEFAULT 'manual',
                auto_criteria TEXT,
                track_count INTEGER DEFAULT 0,
                duration_seconds REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (track_id) REFERENCES music_tracks(id) ON DELETE CASCADE,
                UNIQUE(playlist_id, track_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS play_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES music_tracks(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS now_playing (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                track_id INTEGER,
                position_seconds REAL DEFAULT 0,
                state TEXT DEFAULT 'stopped',
                volume INTEGER DEFAULT 75,
                shuffle BOOLEAN DEFAULT 0,
                repeat TEXT DEFAULT 'off',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES music_tracks(id) ON DELETE SET NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS storage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_size_gb REAL,
                music_size_gb REAL,
                video_size_gb REAL,
                other_size_gb REAL,
                free_size_gb REAL,
                scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id_1 INTEGER NOT NULL,
                track_id_2 INTEGER NOT NULL,
                similarity_score REAL,
                match_type TEXT,
                resolved BOOLEAN DEFAULT 0,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id_1) REFERENCES music_tracks(id) ON DELETE CASCADE,
                FOREIGN KEY (track_id_2) REFERENCES music_tracks(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                files_synced INTEGER DEFAULT 0,
                files_failed INTEGER DEFAULT 0,
                bytes_transferred INTEGER DEFAULT 0,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                status TEXT DEFAULT 'in_progress'
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_artist ON music_tracks(artist)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_album ON music_tracks(album)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_genre ON music_tracks(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_year ON music_tracks(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_favorite ON music_tracks(favorite)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_added ON music_tracks(date_added)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_folder ON video_files(folder_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_playlist_type ON playlists(type)')
        
        cursor.execute('INSERT OR IGNORE INTO now_playing (id) VALUES (1)')
        
        conn.commit()
        conn.close()
    
    def add_music_track(self, track_data: Dict[str, Any]) -> int:
        """Add or update a music track."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO music_tracks 
            (file_path, file_name, file_size, file_hash, title, artist, album, album_artist,
             year, genre, track_number, disc_number, duration_seconds, bitrate, sample_rate,
             channels, format, album_art_path, date_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            track_data.get('file_path'),
            track_data.get('file_name'),
            track_data.get('file_size'),
            track_data.get('file_hash'),
            track_data.get('title'),
            track_data.get('artist'),
            track_data.get('album'),
            track_data.get('album_artist'),
            track_data.get('year'),
            track_data.get('genre'),
            track_data.get('track_number'),
            track_data.get('disc_number'),
            track_data.get('duration_seconds'),
            track_data.get('bitrate'),
            track_data.get('sample_rate'),
            track_data.get('channels'),
            track_data.get('format'),
            track_data.get('album_art_path'),
            datetime.now().isoformat()
        ))
        
        track_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return track_id
    
    def add_video_file(self, video_data: Dict[str, Any]) -> int:
        """Add or update a video file."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO video_files 
            (file_path, file_name, file_size, file_hash, title, duration_seconds,
             width, height, fps, codec, bitrate, format, thumbnail_path, folder_path, date_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_data.get('file_path'),
            video_data.get('file_name'),
            video_data.get('file_size'),
            video_data.get('file_hash'),
            video_data.get('title'),
            video_data.get('duration_seconds'),
            video_data.get('width'),
            video_data.get('height'),
            video_data.get('fps'),
            video_data.get('codec'),
            video_data.get('bitrate'),
            video_data.get('format'),
            video_data.get('thumbnail_path'),
            video_data.get('folder_path'),
            datetime.now().isoformat()
        ))
        
        video_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return video_id
    
    def search_music(self, query: str, limit: int = 100) -> List[Dict]:
        """Search music tracks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        search_query = f'%{query}%'
        cursor.execute('''
            SELECT * FROM music_tracks
            WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR genre LIKE ?
            ORDER BY play_count DESC, date_added DESC
            LIMIT ?
        ''', (search_query, search_query, search_query, search_query, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_all_music(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """Get all music tracks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM music_tracks
            ORDER BY date_added DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_all_videos(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """Get all video files."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM video_files
            ORDER BY date_added DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_artists(self) -> List[Dict]:
        """Get all artists with track counts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT artist, COUNT(*) as track_count, 
                   COUNT(DISTINCT album) as album_count
            FROM music_tracks
            WHERE artist IS NOT NULL AND artist != ''
            GROUP BY artist
            ORDER BY artist
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_albums(self, artist: Optional[str] = None) -> List[Dict]:
        """Get all albums, optionally filtered by artist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if artist:
            cursor.execute('''
                SELECT album, artist, album_artist, year, 
                       COUNT(*) as track_count,
                       MAX(album_art_path) as album_art_path
                FROM music_tracks
                WHERE album IS NOT NULL AND album != '' AND artist = ?
                GROUP BY album, artist
                ORDER BY year DESC, album
            ''', (artist,))
        else:
            cursor.execute('''
                SELECT album, artist, album_artist, year, 
                       COUNT(*) as track_count,
                       MAX(album_art_path) as album_art_path
                FROM music_tracks
                WHERE album IS NOT NULL AND album != ''
                GROUP BY album, artist
                ORDER BY year DESC, album
            ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_genres(self) -> List[Dict]:
        """Get all genres with track counts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT genre, COUNT(*) as track_count
            FROM music_tracks
            WHERE genre IS NOT NULL AND genre != ''
            GROUP BY genre
            ORDER BY track_count DESC
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def create_playlist(self, name: str, description: str = '', playlist_type: str = 'manual',
                       auto_criteria: Optional[str] = None) -> int:
        """Create a new playlist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO playlists (name, description, type, auto_criteria)
            VALUES (?, ?, ?, ?)
        ''', (name, description, playlist_type, auto_criteria))
        
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return playlist_id
    
    def add_to_playlist(self, playlist_id: int, track_id: int) -> bool:
        """Add track to playlist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT MAX(position) FROM playlist_tracks WHERE playlist_id = ?
        ''', (playlist_id,))
        
        max_pos = cursor.fetchone()[0]
        position = (max_pos or 0) + 1
        
        try:
            cursor.execute('''
                INSERT INTO playlist_tracks (playlist_id, track_id, position)
                VALUES (?, ?, ?)
            ''', (playlist_id, track_id, position))
            
            cursor.execute('''
                UPDATE playlists SET track_count = track_count + 1, updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), playlist_id))
            
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        
        conn.close()
        return success
    
    def get_playlists(self) -> List[Dict]:
        """Get all playlists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM playlists ORDER BY created_at DESC')
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_playlist_tracks(self, playlist_id: int) -> List[Dict]:
        """Get tracks in a playlist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, pt.position
            FROM music_tracks m
            JOIN playlist_tracks pt ON m.id = pt.track_id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position
        ''', (playlist_id,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def increment_play_count(self, track_id: int):
        """Increment play count for a track."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE music_tracks
            SET play_count = play_count + 1, last_played = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), track_id))
        
        conn.commit()
        conn.close()
    
    def update_now_playing(self, track_id: Optional[int], state: str = 'playing',
                          position_seconds: float = 0):
        """Update now playing status."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE now_playing
            SET track_id = ?, state = ?, position_seconds = ?, updated_at = ?
            WHERE id = 1
        ''', (track_id, state, position_seconds, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_now_playing(self) -> Dict:
        """Get current now playing info."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT np.*, m.*
            FROM now_playing np
            LEFT JOIN music_tracks m ON np.track_id = m.id
            WHERE np.id = 1
        ''')
        
        row = cursor.fetchone()
        result = dict(row) if row else {}
        conn.close()
        return result
    
    def get_recently_added(self, limit: int = 50) -> List[Dict]:
        """Get recently added tracks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM music_tracks
            ORDER BY date_added DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_most_played(self, limit: int = 50) -> List[Dict]:
        """Get most played tracks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM music_tracks
            WHERE play_count > 0
            ORDER BY play_count DESC, last_played DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_favorites(self) -> List[Dict]:
        """Get favorite tracks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM music_tracks
            WHERE favorite = 1
            ORDER BY date_added DESC
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_by_genre(self, genre: str, limit: int = 100) -> List[Dict]:
        """Get tracks by genre."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM music_tracks
            WHERE genre = ?
            ORDER BY artist, album, track_number
            LIMIT ?
        ''', (genre, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def record_duplicate(self, track_id_1: int, track_id_2: int, 
                        similarity_score: float, match_type: str):
        """Record a duplicate detection."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO duplicates 
            (track_id_1, track_id_2, similarity_score, match_type)
            VALUES (?, ?, ?, ?)
        ''', (track_id_1, track_id_2, similarity_score, match_type))
        
        conn.commit()
        conn.close()
    
    def get_duplicates(self, resolved: bool = False) -> List[Dict]:
        """Get duplicate tracks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, 
                   m1.file_path as path1, m1.title as title1, m1.artist as artist1,
                   m2.file_path as path2, m2.title as title2, m2.artist as artist2
            FROM duplicates d
            JOIN music_tracks m1 ON d.track_id_1 = m1.id
            JOIN music_tracks m2 ON d.track_id_2 = m2.id
            WHERE d.resolved = ?
            ORDER BY d.similarity_score DESC
        ''', (1 if resolved else 0,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def update_storage_stats(self, stats: Dict[str, float]):
        """Update storage statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO storage_stats 
            (total_size_gb, music_size_gb, video_size_gb, other_size_gb, free_size_gb)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            stats.get('total_size_gb', 0),
            stats.get('music_size_gb', 0),
            stats.get('video_size_gb', 0),
            stats.get('other_size_gb', 0),
            stats.get('free_size_gb', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_storage_stats(self) -> Optional[Dict]:
        """Get latest storage statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM storage_stats
            ORDER BY scan_timestamp DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        result = dict(row) if row else None
        conn.close()
        return result
    
    def get_stats(self) -> Dict:
        """Get library statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM music_tracks')
        music_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as count FROM video_files')
        video_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as count FROM playlists')
        playlist_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT artist) as count FROM music_tracks')
        artist_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT album) as count FROM music_tracks')
        album_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(duration_seconds) as total FROM music_tracks')
        total_music_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_music_tracks': music_count,
            'total_video_files': video_count,
            'total_playlists': playlist_count,
            'total_artists': artist_count,
            'total_albums': album_count,
            'total_music_duration_hours': round(total_music_duration / 3600, 2)
        }
