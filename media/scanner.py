#!/usr/bin/env python3
"""
Media Center Pro - File Scanner
Scans directories for music and video files
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Callable, Optional


class MediaScanner:
    """Scans for media files in specified directories."""
    
    MUSIC_EXTENSIONS = {
        '.mp3', '.flac', '.aac', '.m4a', '.wav', '.ogg', 
        '.wma', '.opus', '.ape', '.alac'
    }
    
    VIDEO_EXTENSIONS = {
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv',
        '.webm', '.m4v', '.mpg', '.mpeg', '.3gp'
    }
    
    def __init__(self):
        self.scan_paths = ['/media', '/storage', '/sdcard/Music', '/sdcard/Movies']
        self.mock_mode = True
    
    def scan_music(self, path: Optional[str] = None, 
                   progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scan for music files."""
        if self.mock_mode:
            return self._generate_mock_music()
        
        music_files = []
        scan_dir = path if path else self.scan_paths
        
        if isinstance(scan_dir, str):
            scan_dirs = [scan_dir]
        else:
            scan_dirs = scan_dir
        
        for directory in scan_dirs:
            if not os.path.exists(directory):
                continue
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.MUSIC_EXTENSIONS:
                        file_path = os.path.join(root, file)
                        try:
                            file_info = self._get_file_info(file_path)
                            music_files.append(file_info)
                            
                            if progress_callback:
                                progress_callback(len(music_files), file)
                        except Exception as e:
                            print(f"Error scanning {file_path}: {e}")
        
        return music_files
    
    def scan_videos(self, path: Optional[str] = None,
                   progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scan for video files."""
        if self.mock_mode:
            return self._generate_mock_videos()
        
        video_files = []
        scan_dir = path if path else self.scan_paths
        
        if isinstance(scan_dir, str):
            scan_dirs = [scan_dir]
        else:
            scan_dirs = scan_dir
        
        for directory in scan_dirs:
            if not os.path.exists(directory):
                continue
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.VIDEO_EXTENSIONS:
                        file_path = os.path.join(root, file)
                        try:
                            file_info = self._get_file_info(file_path)
                            file_info['folder_path'] = root
                            video_files.append(file_info)
                            
                            if progress_callback:
                                progress_callback(len(video_files), file)
                        except Exception as e:
                            print(f"Error scanning {file_path}: {e}")
        
        return video_files
    
    def _get_file_info(self, file_path: str) -> Dict:
        """Get basic file information."""
        stat = os.stat(file_path)
        
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': stat.st_size,
            'file_hash': self._calculate_hash(file_path),
            'format': os.path.splitext(file_path)[1].lower()[1:]
        }
    
    def _calculate_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of file (first 1MB for speed)."""
        try:
            md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                data = f.read(1024 * 1024)
                md5.update(data)
            return md5.hexdigest()
        except:
            return ''
    
    def find_duplicates(self, tracks: List[Dict]) -> List[Dict]:
        """Find potential duplicate files."""
        duplicates = []
        hash_map = {}
        
        for track in tracks:
            file_hash = track.get('file_hash')
            if file_hash and file_hash in hash_map:
                duplicates.append({
                    'track1': hash_map[file_hash],
                    'track2': track,
                    'match_type': 'exact_hash',
                    'similarity_score': 1.0
                })
            elif file_hash:
                hash_map[file_hash] = track
        
        title_map = {}
        for track in tracks:
            title = track.get('title', '').lower().strip()
            artist = track.get('artist', '').lower().strip()
            key = f"{artist}_{title}"
            
            if key and title and artist and key in title_map:
                existing = title_map[key]
                if existing.get('file_hash') != track.get('file_hash'):
                    duplicates.append({
                        'track1': existing,
                        'track2': track,
                        'match_type': 'title_artist',
                        'similarity_score': 0.9
                    })
            elif key and title and artist:
                title_map[key] = track
        
        return duplicates
    
    def get_storage_usage(self) -> Dict:
        """Get storage usage statistics."""
        if self.mock_mode:
            return {
                'total_size_gb': 256.0,
                'music_size_gb': 45.3,
                'video_size_gb': 128.7,
                'other_size_gb': 50.2,
                'free_size_gb': 31.8,
                'music_percent': 17.7,
                'video_percent': 50.3,
                'free_percent': 12.4
            }
        
        import shutil
        
        total, used, free = shutil.disk_usage('/')
        
        return {
            'total_size_gb': round(total / (1024**3), 2),
            'free_size_gb': round(free / (1024**3), 2),
            'used_size_gb': round(used / (1024**3), 2),
            'free_percent': round((free / total) * 100, 1)
        }
    
    def _generate_mock_music(self) -> List[Dict]:
        """Generate mock music data for testing."""
        artists = ['The Beatles', 'Pink Floyd', 'Led Zeppelin', 'Queen', 'AC/DC']
        albums = ['Greatest Hits', 'Studio Album', 'Live Concert', 'Best Of']
        genres = ['Rock', 'Pop', 'Jazz', 'Classical', 'Electronic']
        
        tracks = []
        for i in range(50):
            artist = artists[i % len(artists)]
            album = albums[i % len(albums)]
            genre = genres[i % len(genres)]
            
            tracks.append({
                'file_path': f'/mock/music/{artist}/{album}/track_{i+1}.mp3',
                'file_name': f'Track {i+1}.mp3',
                'file_size': 3500000 + (i * 50000),
                'file_hash': hashlib.md5(f'track_{i}'.encode()).hexdigest(),
                'title': f'Song Title {i+1}',
                'artist': artist,
                'album': album,
                'year': 2020 - (i % 10),
                'genre': genre,
                'track_number': (i % 12) + 1,
                'duration_seconds': 180 + (i * 5),
                'bitrate': 320000,
                'sample_rate': 44100,
                'channels': 2,
                'format': 'mp3'
            })
        
        return tracks
    
    def _generate_mock_videos(self) -> List[Dict]:
        """Generate mock video data for testing."""
        folders = ['/Movies', '/TV Shows', '/Documentaries', '/Music Videos']
        
        videos = []
        for i in range(20):
            folder = folders[i % len(folders)]
            
            videos.append({
                'file_path': f'/mock/videos{folder}/video_{i+1}.mp4',
                'file_name': f'Video {i+1}.mp4',
                'file_size': 500000000 + (i * 10000000),
                'file_hash': hashlib.md5(f'video_{i}'.encode()).hexdigest(),
                'title': f'Video Title {i+1}',
                'duration_seconds': 3600 + (i * 300),
                'width': 1920,
                'height': 1080,
                'fps': 24.0,
                'codec': 'h264',
                'bitrate': 5000000,
                'format': 'mp4',
                'folder_path': f'/mock/videos{folder}'
            })
        
        return videos
