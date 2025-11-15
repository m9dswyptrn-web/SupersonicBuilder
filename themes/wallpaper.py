#!/usr/bin/env python3
"""
Wallpaper Management
Handles wallpaper upload, resizing, slideshow, and time-based features
"""

import os
import io
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime, time
from PIL import Image


class WallpaperManager:
    """Wallpaper management system."""
    
    TARGET_WIDTH = 2000
    TARGET_HEIGHT = 1200
    MAX_FILE_SIZE_MB = 10
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP', 'BMP']
    
    def __init__(self, upload_dir: Path):
        """Initialize wallpaper manager."""
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.wallpapers_dir = upload_dir / 'wallpapers'
        self.thumbnails_dir = upload_dir / 'thumbnails'
        
        self.wallpapers_dir.mkdir(exist_ok=True)
        self.thumbnails_dir.mkdir(exist_ok=True)
    
    def validate_image(self, file_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate uploaded image."""
        if len(file_data) > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            return False, f"File too large. Maximum size is {self.MAX_FILE_SIZE_MB}MB"
        
        try:
            img = Image.open(io.BytesIO(file_data))
            
            if img.format not in self.SUPPORTED_FORMATS:
                return False, f"Unsupported format. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            
            if img.width < 800 or img.height < 480:
                return False, "Image resolution too low. Minimum 800x480"
            
            return True, None
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    def save_and_resize_wallpaper(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Save and resize wallpaper to target resolution."""
        valid, error = self.validate_image(file_data)
        if not valid:
            raise ValueError(error)
        
        img = Image.open(io.BytesIO(file_data))
        
        original_width = img.width
        original_height = img.height
        original_format = img.format
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = Path(filename).stem
        ext = Path(filename).suffix.lower() or '.jpg'
        
        safe_name = f"{base_name}_{timestamp}{ext}"
        wallpaper_path = self.wallpapers_dir / safe_name
        thumbnail_path = self.thumbnails_dir / f"thumb_{safe_name}"
        
        resized_img = self._resize_image(img, self.TARGET_WIDTH, self.TARGET_HEIGHT)
        
        save_format = 'JPEG' if ext in ['.jpg', '.jpeg'] else 'PNG'
        save_kwargs = {'quality': 90, 'optimize': True} if save_format == 'JPEG' else {}
        
        resized_img.save(wallpaper_path, format=save_format, **save_kwargs)
        
        thumbnail = self._resize_image(img, 400, 240)
        thumbnail.save(thumbnail_path, format=save_format, **save_kwargs)
        
        file_size_kb = wallpaper_path.stat().st_size / 1024
        
        return {
            'file_path': str(wallpaper_path.relative_to(self.upload_dir.parent)),
            'thumbnail_path': str(thumbnail_path.relative_to(self.upload_dir.parent)),
            'original_width': original_width,
            'original_height': original_height,
            'resized_width': self.TARGET_WIDTH,
            'resized_height': self.TARGET_HEIGHT,
            'file_size_kb': int(file_size_kb),
            'format': save_format
        }
    
    def _resize_image(self, img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """Resize image maintaining aspect ratio with center crop."""
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            new_width = target_width
            new_height = int(new_width / img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        img = img.crop((left, top, right, bottom))
        
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (0, 0, 0))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
    
    def create_slideshow_config(self, wallpaper_ids: List[int], interval: int = 300) -> Dict[str, Any]:
        """Create slideshow configuration."""
        if interval < 60:
            raise ValueError("Slideshow interval must be at least 60 seconds")
        
        if len(wallpaper_ids) < 2:
            raise ValueError("Slideshow requires at least 2 wallpapers")
        
        return {
            'wallpaper_ids': wallpaper_ids,
            'interval': interval,
            'shuffle': False,
            'transition': 'fade',
            'enabled': True
        }
    
    def create_time_based_config(self, day_wallpaper_id: int, night_wallpaper_id: int,
                                 day_start: str = "06:00", night_start: str = "18:00") -> Dict[str, Any]:
        """Create time-based wallpaper configuration."""
        try:
            day_time = time.fromisoformat(day_start)
            night_time = time.fromisoformat(night_start)
        except ValueError as e:
            raise ValueError(f"Invalid time format. Use HH:MM format: {str(e)}")
        
        return {
            'day_wallpaper_id': day_wallpaper_id,
            'night_wallpaper_id': night_wallpaper_id,
            'day_start': day_start,
            'night_start': night_start,
            'enabled': True
        }
    
    def get_current_wallpaper(self, time_based_config: Optional[Dict[str, Any]] = None) -> int:
        """Get current wallpaper ID based on time-based configuration."""
        if not time_based_config or not time_based_config.get('enabled'):
            return None
        
        current_time = datetime.now().time()
        day_start = time.fromisoformat(time_based_config['day_start'])
        night_start = time.fromisoformat(time_based_config['night_start'])
        
        if day_start <= current_time < night_start:
            return time_based_config['day_wallpaper_id']
        else:
            return time_based_config['night_wallpaper_id']
    
    def delete_wallpaper(self, file_path: str, thumbnail_path: Optional[str] = None) -> bool:
        """Delete wallpaper and thumbnail files."""
        try:
            full_path = self.upload_dir.parent / file_path
            if full_path.exists():
                full_path.unlink()
            
            if thumbnail_path:
                full_thumb_path = self.upload_dir.parent / thumbnail_path
                if full_thumb_path.exists():
                    full_thumb_path.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting wallpaper: {e}")
            return False
    
    def get_wallpaper_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a wallpaper file."""
        try:
            full_path = self.upload_dir.parent / file_path
            
            if not full_path.exists():
                return None
            
            img = Image.open(full_path)
            stat = full_path.stat()
            
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'file_size_kb': int(stat.st_size / 1024),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception as e:
            print(f"Error getting wallpaper info: {e}")
            return None
    
    def batch_resize(self, wallpaper_paths: List[str]) -> Dict[str, Any]:
        """Batch resize multiple wallpapers."""
        results = {
            'success': [],
            'failed': []
        }
        
        for path in wallpaper_paths:
            try:
                full_path = self.upload_dir.parent / path
                
                if not full_path.exists():
                    results['failed'].append({
                        'path': path,
                        'error': 'File not found'
                    })
                    continue
                
                with open(full_path, 'rb') as f:
                    file_data = f.read()
                
                filename = full_path.name
                result = self.save_and_resize_wallpaper(file_data, filename)
                results['success'].append({
                    'original': path,
                    'resized': result
                })
            except Exception as e:
                results['failed'].append({
                    'path': path,
                    'error': str(e)
                })
        
        return results
