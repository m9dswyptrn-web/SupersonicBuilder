#!/usr/bin/env python3
"""
Media Center Pro - Metadata Extraction
Extracts and manages metadata for music and video files
"""

import os
import json
from typing import Dict, Optional, Any
from pathlib import Path


class MetadataExtractor:
    """Extracts metadata from media files."""
    
    def __init__(self):
        self.mock_mode = True
        self.album_art_cache = Path('data/album_art')
        self.album_art_cache.mkdir(parents=True, exist_ok=True)
        self.thumbnail_cache = Path('data/thumbnails')
        self.thumbnail_cache.mkdir(parents=True, exist_ok=True)
    
    def extract_music_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from music file."""
        if self.mock_mode:
            return self._mock_music_metadata(file_path)
        
        try:
            import mutagen
            from mutagen.mp3 import MP3
            from mutagen.flac import FLAC
            from mutagen.mp4 import MP4
            
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.mp3':
                audio = MP3(file_path)
                metadata = self._extract_id3_tags(audio)
            elif ext == '.flac':
                audio = FLAC(file_path)
                metadata = self._extract_vorbis_tags(audio)
            elif ext in ['.m4a', '.mp4']:
                audio = MP4(file_path)
                metadata = self._extract_mp4_tags(audio)
            else:
                audio = mutagen.File(file_path)
                metadata = {}
            
            if hasattr(audio, 'info'):
                metadata['duration_seconds'] = audio.info.length
                metadata['bitrate'] = getattr(audio.info, 'bitrate', 0)
                metadata['sample_rate'] = getattr(audio.info, 'sample_rate', 0)
                metadata['channels'] = getattr(audio.info, 'channels', 2)
            
            return metadata
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return {}
    
    def extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from video file."""
        if self.mock_mode:
            return self._mock_video_metadata(file_path)
        
        try:
            import subprocess
            
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return self._parse_ffprobe_output(data)
            
        except Exception as e:
            print(f"Error extracting video metadata from {file_path}: {e}")
        
        return {}
    
    def extract_album_art(self, file_path: str, track_id: int) -> Optional[str]:
        """Extract album art from music file."""
        if self.mock_mode:
            return f'/static/mock_album_art_{track_id % 10}.jpg'
        
        try:
            import mutagen
            from mutagen.id3 import ID3, APIC
            from mutagen.flac import FLAC, Picture
            from mutagen.mp4 import MP4
            
            ext = os.path.splitext(file_path)[1].lower()
            image_data = None
            
            if ext == '.mp3':
                audio = ID3(file_path)
                for key in audio.keys():
                    if key.startswith('APIC'):
                        image_data = audio[key].data
                        break
            
            elif ext == '.flac':
                audio = FLAC(file_path)
                if audio.pictures:
                    image_data = audio.pictures[0].data
            
            elif ext in ['.m4a', '.mp4']:
                audio = MP4(file_path)
                if 'covr' in audio:
                    image_data = bytes(audio['covr'][0])
            
            if image_data:
                art_path = self.album_art_cache / f'art_{track_id}.jpg'
                with open(art_path, 'wb') as f:
                    f.write(image_data)
                return str(art_path)
        
        except Exception as e:
            print(f"Error extracting album art from {file_path}: {e}")
        
        return None
    
    def generate_video_thumbnail(self, file_path: str, video_id: int) -> Optional[str]:
        """Generate thumbnail for video file."""
        if self.mock_mode:
            return f'/static/mock_thumbnail_{video_id % 5}.jpg'
        
        try:
            import subprocess
            
            thumb_path = self.thumbnail_cache / f'thumb_{video_id}.jpg'
            
            subprocess.run([
                'ffmpeg', '-i', file_path, '-ss', '00:00:10',
                '-vframes', '1', '-vf', 'scale=320:-1',
                str(thumb_path)
            ], capture_output=True)
            
            if thumb_path.exists():
                return str(thumb_path)
        
        except Exception as e:
            print(f"Error generating thumbnail for {file_path}: {e}")
        
        return None
    
    def update_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata in file."""
        if self.mock_mode:
            return True
        
        try:
            import mutagen
            
            audio = mutagen.File(file_path)
            
            if 'title' in metadata:
                audio['TIT2'] = metadata['title']
            if 'artist' in metadata:
                audio['TPE1'] = metadata['artist']
            if 'album' in metadata:
                audio['TALB'] = metadata['album']
            if 'year' in metadata:
                audio['TDRC'] = str(metadata['year'])
            if 'genre' in metadata:
                audio['TCON'] = metadata['genre']
            
            audio.save()
            return True
        
        except Exception as e:
            print(f"Error updating metadata for {file_path}: {e}")
            return False
    
    def download_album_art(self, artist: str, album: str) -> Optional[str]:
        """Download album art from online sources."""
        return None
    
    def fix_missing_metadata(self, file_path: str) -> Dict[str, Any]:
        """Attempt to fix missing metadata."""
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        parts = name_without_ext.split(' - ')
        
        if len(parts) >= 2:
            return {
                'artist': parts[0].strip(),
                'title': parts[1].strip()
            }
        
        return {'title': name_without_ext}
    
    def _extract_id3_tags(self, audio) -> Dict:
        """Extract ID3 tags from MP3."""
        metadata = {}
        
        tag_map = {
            'TIT2': 'title',
            'TPE1': 'artist',
            'TALB': 'album',
            'TPE2': 'album_artist',
            'TDRC': 'year',
            'TCON': 'genre',
            'TRCK': 'track_number',
            'TPOS': 'disc_number'
        }
        
        for tag_id, field_name in tag_map.items():
            if tag_id in audio:
                value = str(audio[tag_id].text[0])
                if field_name in ['year', 'track_number', 'disc_number']:
                    try:
                        metadata[field_name] = int(value.split('/')[0])
                    except:
                        pass
                else:
                    metadata[field_name] = value
        
        return metadata
    
    def _extract_vorbis_tags(self, audio) -> Dict:
        """Extract Vorbis tags from FLAC."""
        metadata = {}
        
        tag_map = {
            'title': 'title',
            'artist': 'artist',
            'album': 'album',
            'albumartist': 'album_artist',
            'date': 'year',
            'genre': 'genre',
            'tracknumber': 'track_number',
            'discnumber': 'disc_number'
        }
        
        for tag_id, field_name in tag_map.items():
            if tag_id in audio:
                value = audio[tag_id][0]
                if field_name in ['year', 'track_number', 'disc_number']:
                    try:
                        metadata[field_name] = int(value.split('/')[0])
                    except:
                        pass
                else:
                    metadata[field_name] = value
        
        return metadata
    
    def _extract_mp4_tags(self, audio) -> Dict:
        """Extract tags from MP4/M4A."""
        metadata = {}
        
        tag_map = {
            '\xa9nam': 'title',
            '\xa9ART': 'artist',
            '\xa9alb': 'album',
            'aART': 'album_artist',
            '\xa9day': 'year',
            '\xa9gen': 'genre',
            'trkn': 'track_number',
            'disk': 'disc_number'
        }
        
        for tag_id, field_name in tag_map.items():
            if tag_id in audio:
                value = audio[tag_id][0]
                if field_name in ['year']:
                    try:
                        metadata[field_name] = int(str(value)[:4])
                    except:
                        pass
                elif field_name in ['track_number', 'disc_number']:
                    metadata[field_name] = value[0] if isinstance(value, tuple) else value
                else:
                    metadata[field_name] = str(value)
        
        return metadata
    
    def _parse_ffprobe_output(self, data: Dict) -> Dict:
        """Parse FFprobe JSON output."""
        metadata = {}
        
        if 'format' in data:
            fmt = data['format']
            metadata['duration_seconds'] = float(fmt.get('duration', 0))
            metadata['bitrate'] = int(fmt.get('bit_rate', 0))
        
        if 'streams' in data:
            for stream in data['streams']:
                if stream.get('codec_type') == 'video':
                    metadata['width'] = stream.get('width', 0)
                    metadata['height'] = stream.get('height', 0)
                    metadata['codec'] = stream.get('codec_name', '')
                    
                    fps_str = stream.get('r_frame_rate', '24/1')
                    try:
                        num, den = map(int, fps_str.split('/'))
                        metadata['fps'] = round(num / den, 2)
                    except:
                        metadata['fps'] = 24.0
        
        return metadata
    
    def _mock_music_metadata(self, file_path: str) -> Dict:
        """Generate mock metadata for testing."""
        return {}
    
    def _mock_video_metadata(self, file_path: str) -> Dict:
        """Generate mock video metadata for testing."""
        return {}
