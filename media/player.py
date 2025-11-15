#!/usr/bin/env python3
"""
Media Center Pro - Player Integration
Integration with Android music player and queue management
"""

import json
from typing import List, Dict, Optional
from datetime import datetime


class PlayerIntegration:
    """Integrates with Android music player."""
    
    def __init__(self, database):
        self.db = database
        self.queue = []
        self.current_index = -1
        self.shuffle_enabled = False
        self.repeat_mode = 'off'
    
    def play_track(self, track_id: int) -> Dict:
        """Play a specific track."""
        self.db.update_now_playing(track_id, state='playing', position_seconds=0)
        self.db.increment_play_count(track_id)
        
        return {
            'success': True,
            'message': f'Now playing track {track_id}',
            'track_id': track_id,
            'state': 'playing'
        }
    
    def pause(self) -> Dict:
        """Pause playback."""
        now_playing = self.db.get_now_playing()
        track_id = now_playing.get('track_id')
        position = now_playing.get('position_seconds', 0)
        
        self.db.update_now_playing(track_id, state='paused', position_seconds=position)
        
        return {
            'success': True,
            'message': 'Playback paused',
            'state': 'paused'
        }
    
    def resume(self) -> Dict:
        """Resume playback."""
        now_playing = self.db.get_now_playing()
        track_id = now_playing.get('track_id')
        position = now_playing.get('position_seconds', 0)
        
        self.db.update_now_playing(track_id, state='playing', position_seconds=position)
        
        return {
            'success': True,
            'message': 'Playback resumed',
            'state': 'playing'
        }
    
    def stop(self) -> Dict:
        """Stop playback."""
        self.db.update_now_playing(None, state='stopped', position_seconds=0)
        
        return {
            'success': True,
            'message': 'Playback stopped',
            'state': 'stopped'
        }
    
    def next_track(self) -> Dict:
        """Skip to next track in queue."""
        if not self.queue:
            return {'success': False, 'error': 'Queue is empty'}
        
        if self.current_index < len(self.queue) - 1:
            self.current_index += 1
            track_id = self.queue[self.current_index]
            return self.play_track(track_id)
        elif self.repeat_mode == 'all':
            self.current_index = 0
            track_id = self.queue[self.current_index]
            return self.play_track(track_id)
        else:
            return {'success': False, 'error': 'End of queue'}
    
    def previous_track(self) -> Dict:
        """Go to previous track in queue."""
        if not self.queue:
            return {'success': False, 'error': 'Queue is empty'}
        
        if self.current_index > 0:
            self.current_index -= 1
            track_id = self.queue[self.current_index]
            return self.play_track(track_id)
        else:
            return {'success': False, 'error': 'Beginning of queue'}
    
    def add_to_queue(self, track_ids: List[int]) -> Dict:
        """Add tracks to play queue."""
        self.queue.extend(track_ids)
        
        return {
            'success': True,
            'message': f'Added {len(track_ids)} track(s) to queue',
            'queue_length': len(self.queue)
        }
    
    def clear_queue(self) -> Dict:
        """Clear the play queue."""
        self.queue = []
        self.current_index = -1
        
        return {
            'success': True,
            'message': 'Queue cleared',
            'queue_length': 0
        }
    
    def get_queue(self) -> List[Dict]:
        """Get current play queue."""
        tracks = []
        for i, track_id in enumerate(self.queue):
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM music_tracks WHERE id = ?', (track_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                track = dict(row)
                track['queue_position'] = i
                track['is_current'] = (i == self.current_index)
                tracks.append(track)
        
        return tracks
    
    def set_shuffle(self, enabled: bool) -> Dict:
        """Enable or disable shuffle."""
        self.shuffle_enabled = enabled
        
        if enabled and self.queue:
            import random
            current_track = self.queue[self.current_index] if self.current_index >= 0 else None
            random.shuffle(self.queue)
            if current_track:
                self.current_index = self.queue.index(current_track)
        
        return {
            'success': True,
            'shuffle_enabled': enabled,
            'message': f'Shuffle {"enabled" if enabled else "disabled"}'
        }
    
    def set_repeat(self, mode: str) -> Dict:
        """Set repeat mode: off, all, one."""
        if mode not in ['off', 'all', 'one']:
            return {'success': False, 'error': 'Invalid repeat mode'}
        
        self.repeat_mode = mode
        
        return {
            'success': True,
            'repeat_mode': mode,
            'message': f'Repeat mode set to {mode}'
        }
    
    def seek(self, position_seconds: float) -> Dict:
        """Seek to position in current track."""
        now_playing = self.db.get_now_playing()
        track_id = now_playing.get('track_id')
        state = now_playing.get('state', 'stopped')
        
        if not track_id:
            return {'success': False, 'error': 'No track playing'}
        
        self.db.update_now_playing(track_id, state=state, position_seconds=position_seconds)
        
        return {
            'success': True,
            'position_seconds': position_seconds,
            'message': f'Seeked to {position_seconds}s'
        }
    
    def get_now_playing(self) -> Dict:
        """Get currently playing track info."""
        now_playing = self.db.get_now_playing()
        
        if not now_playing.get('track_id'):
            return {
                'playing': False,
                'state': 'stopped'
            }
        
        return {
            'playing': True,
            'state': now_playing.get('state', 'stopped'),
            'track': {
                'id': now_playing.get('track_id'),
                'title': now_playing.get('title'),
                'artist': now_playing.get('artist'),
                'album': now_playing.get('album'),
                'duration_seconds': now_playing.get('duration_seconds'),
                'album_art_path': now_playing.get('album_art_path')
            },
            'position_seconds': now_playing.get('position_seconds', 0),
            'volume': now_playing.get('volume', 75),
            'shuffle': self.shuffle_enabled,
            'repeat': self.repeat_mode,
            'queue_length': len(self.queue),
            'queue_position': self.current_index + 1 if self.current_index >= 0 else 0
        }
    
    def play_playlist(self, playlist_id: int) -> Dict:
        """Play all tracks from a playlist."""
        tracks = self.db.get_playlist_tracks(playlist_id)
        
        if not tracks:
            return {'success': False, 'error': 'Playlist is empty'}
        
        track_ids = [t['id'] for t in tracks]
        self.queue = track_ids
        self.current_index = 0
        
        return self.play_track(track_ids[0])
    
    def play_album(self, artist: str, album: str) -> Dict:
        """Play all tracks from an album."""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM music_tracks
            WHERE artist = ? AND album = ?
            ORDER BY disc_number, track_number
        ''', (artist, album))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {'success': False, 'error': 'Album not found'}
        
        track_ids = [row[0] for row in rows]
        self.queue = track_ids
        self.current_index = 0
        
        return self.play_track(track_ids[0])
    
    def play_artist(self, artist: str, shuffle: bool = False) -> Dict:
        """Play all tracks from an artist."""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM music_tracks
            WHERE artist = ?
            ORDER BY album, disc_number, track_number
        ''', (artist,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {'success': False, 'error': 'Artist not found'}
        
        track_ids = [row[0] for row in rows]
        
        if shuffle:
            import random
            random.shuffle(track_ids)
        
        self.queue = track_ids
        self.current_index = 0
        
        return self.play_track(track_ids[0])
    
    def create_android_intent(self, track_id: int) -> Dict:
        """Create Android intent for external player."""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM music_tracks WHERE id = ?', (track_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {'success': False, 'error': 'Track not found'}
        
        track = dict(row)
        
        return {
            'success': True,
            'intent': {
                'action': 'android.intent.action.VIEW',
                'data': track['file_path'],
                'type': 'audio/*',
                'extras': {
                    'title': track.get('title'),
                    'artist': track.get('artist'),
                    'album': track.get('album')
                }
            }
        }
