#!/usr/bin/env python3
"""
Continuous Loop Recording Module
Handles continuous dashcam recording with quality settings and overlays
"""

import os
import io
import time
import uuid
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from PIL import Image, ImageDraw, ImageFont


class LoopRecorder:
    """Continuous loop recording manager for dashcam."""
    
    def __init__(self, output_dir: str = None, max_storage_gb: float = 128):
        """
        Initialize loop recorder.
        
        Args:
            output_dir: Directory to save recordings
            max_storage_gb: Maximum storage to use (in GB)
        """
        if output_dir is None:
            output_dir = Path(__file__).parent / "recordings"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_storage_bytes = max_storage_gb * 1024 * 1024 * 1024
        
        self.active_recordings = {}
        self.recording_lock = threading.Lock()
        
        self.quality_settings = {
            '720p': {'width': 1280, 'height': 720, 'bitrate': '2M', 'fps': 30},
            '1080p': {'width': 1920, 'height': 1080, 'bitrate': '4M', 'fps': 30},
            '4K': {'width': 3840, 'height': 2160, 'bitrate': '20M', 'fps': 30}
        }
        
        self.continuous_recording_active = False
        self.continuous_thread = None
        
        self.timestamp_overlay = True
        self.gps_overlay = True
        
        self.parking_mode_active = False
        self.parking_mode_time_lapse = False
    
    def start_continuous_recording(self, camera_system, camera_layout: str = 'dual',
                                   quality: str = '1080p',
                                   gps_tracker=None) -> Dict:
        """
        Start continuous loop recording.
        
        Args:
            camera_system: CameraSystem instance from camera service
            camera_layout: Layout to record (front, rear, dual, quad)
            quality: Recording quality (720p, 1080p, 4K)
            gps_tracker: Optional GPS tracker for location overlay
        
        Returns:
            Recording info dict
        """
        with self.recording_lock:
            if self.continuous_recording_active:
                return {'ok': False, 'error': 'Continuous recording already active'}
        
        recording_id = f"continuous_{uuid.uuid4().hex[:8]}"
        
        recording_info = {
            'recording_id': recording_id,
            'camera_layout': camera_layout,
            'quality': quality,
            'recording_type': 'continuous',
            'start_time': time.time(),
            'camera_system': camera_system,
            'gps_tracker': gps_tracker,
            'status': 'recording',
            'segment_count': 0
        }
        
        with self.recording_lock:
            self.continuous_recording_active = True
            self.active_recordings[recording_id] = recording_info
        
        self.continuous_thread = threading.Thread(
            target=self._continuous_recording_loop,
            args=(recording_id,),
            daemon=True
        )
        self.continuous_thread.start()
        
        return {
            'ok': True,
            'recording_id': recording_id,
            'camera_layout': camera_layout,
            'quality': quality,
            'status': 'started'
        }
    
    def stop_continuous_recording(self) -> Dict:
        """Stop continuous recording."""
        with self.recording_lock:
            if not self.continuous_recording_active:
                return {'ok': False, 'error': 'No continuous recording active'}
            
            self.continuous_recording_active = False
        
        time.sleep(2)
        
        return {'ok': True, 'status': 'stopped'}
    
    def _continuous_recording_loop(self, recording_id: str):
        """Background loop for continuous recording."""
        segment_duration = 60
        
        while True:
            with self.recording_lock:
                if not self.continuous_recording_active:
                    break
                
                if recording_id not in self.active_recordings:
                    break
                
                recording_info = self.active_recordings[recording_id]
            
            self._check_and_cleanup_storage()
            
            segment_result = self._record_segment(recording_info, segment_duration)
            
            if segment_result:
                with self.recording_lock:
                    if recording_id in self.active_recordings:
                        self.active_recordings[recording_id]['segment_count'] += 1
            
            time.sleep(1)
    
    def _record_segment(self, recording_info: Dict, duration_seconds: int) -> Optional[Dict]:
        """Record a segment of video."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            camera_layout = recording_info['camera_layout']
            quality = recording_info['quality']
            segment_num = recording_info['segment_count']
            
            filename = f"{camera_layout}_{quality}_{timestamp}_seg{segment_num}.mp4"
            video_path = self.output_dir / filename
            
            camera_system = recording_info['camera_system']
            gps_tracker = recording_info.get('gps_tracker')
            
            fps = 10
            frame_delay = 1.0 / fps
            total_frames = int(duration_seconds * fps)
            
            frames = []
            
            for frame_num in range(total_frames):
                if not self.continuous_recording_active:
                    break
                
                try:
                    frame = self._capture_frame(camera_system, camera_layout)
                    
                    if self.timestamp_overlay or self.gps_overlay:
                        frame = self._add_overlays(frame, gps_tracker)
                    
                    frames.append(frame)
                    
                except Exception as e:
                    print(f"Frame capture error: {e}")
                
                time.sleep(frame_delay)
            
            if frames:
                self._save_frames_as_gif(frames, video_path)
                
                file_size_mb = video_path.stat().st_size / (1024 * 1024)
                
                return {
                    'video_path': str(video_path),
                    'duration_seconds': duration_seconds,
                    'file_size_mb': file_size_mb,
                    'frame_count': len(frames)
                }
        
        except Exception as e:
            print(f"Segment recording error: {e}")
        
        return None
    
    def _capture_frame(self, camera_system, camera_layout: str) -> Image.Image:
        """Capture frame from camera system."""
        if camera_layout == 'front':
            camera = camera_system.get_camera('front')
            return camera.generate_frame() if camera else self._create_placeholder()
        
        elif camera_layout == 'rear':
            camera = camera_system.get_camera('rear')
            return camera.generate_frame() if camera else self._create_placeholder()
        
        elif camera_layout == 'dual':
            front_cam = camera_system.get_camera('front')
            rear_cam = camera_system.get_camera('rear')
            
            front_frame = front_cam.generate_frame() if front_cam else self._create_placeholder()
            rear_frame = rear_cam.generate_frame() if rear_cam else self._create_placeholder()
            
            return self._combine_dual_view(front_frame, rear_frame)
        
        elif camera_layout == 'quad':
            from services.cameras.stitcher import create_quad_view
            all_frames = {}
            for pos in ['front', 'rear', 'left', 'right']:
                cam = camera_system.get_camera(pos)
                if cam:
                    all_frames[pos] = cam.generate_frame()
            
            if len(all_frames) == 4:
                return create_quad_view(all_frames)
        
        return self._create_placeholder()
    
    def _combine_dual_view(self, front_frame: Image.Image, 
                          rear_frame: Image.Image) -> Image.Image:
        """Combine front and rear frames into dual view."""
        width = front_frame.width
        height = front_frame.height * 2
        
        combined = Image.new('RGB', (width, height))
        combined.paste(front_frame, (0, 0))
        combined.paste(rear_frame, (0, front_frame.height))
        
        draw = ImageDraw.Draw(combined)
        draw.text((10, 10), "FRONT", fill=(255, 255, 255))
        draw.text((10, front_frame.height + 10), "REAR", fill=(255, 255, 255))
        
        return combined
    
    def _add_overlays(self, frame: Image.Image, gps_tracker=None) -> Image.Image:
        """Add timestamp and GPS overlays to frame."""
        draw = ImageDraw.Draw(frame)
        
        if self.timestamp_overlay:
            timestamp_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            draw.text((10, frame.height - 30), timestamp_text, fill=(255, 255, 255))
        
        if self.gps_overlay and gps_tracker:
            try:
                location = gps_tracker.get_current_location()
                lat = location.get('latitude', 0)
                lng = location.get('longitude', 0)
                speed = location.get('speed_kmh', 0)
                
                gps_text = f"GPS: {lat:.5f}, {lng:.5f} | {speed:.1f} km/h"
                draw.text((10, frame.height - 60), gps_text, fill=(255, 255, 255))
            except:
                pass
        
        return frame
    
    def _create_placeholder(self) -> Image.Image:
        """Create placeholder frame."""
        return Image.new('RGB', (640, 480), color=(30, 30, 30))
    
    def _save_frames_as_gif(self, frames: List[Image.Image], output_path: Path):
        """Save frames as animated GIF (mock video)."""
        if not frames:
            return
        
        gif_path = str(output_path).replace('.mp4', '.gif')
        
        if len(frames) > 100:
            step = len(frames) // 100
            frames = frames[::step]
        
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,
            loop=0,
            optimize=False
        )
    
    def record_incident_clip(self, camera_system, incident_id: str,
                            duration_seconds: int = 30,
                            quality: str = '1080p',
                            gps_tracker=None) -> Dict:
        """
        Record incident clip (protected recording).
        
        Args:
            camera_system: CameraSystem instance
            incident_id: Incident ID to associate with
            duration_seconds: Clip duration
            quality: Recording quality
            gps_tracker: Optional GPS tracker
        
        Returns:
            Clip info dict
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"incident_{incident_id}_{timestamp}.mp4"
        video_path = self.output_dir / filename
        
        fps = 10
        frame_delay = 1.0 / fps
        total_frames = int(duration_seconds * fps)
        
        frames = []
        
        for _ in range(total_frames):
            try:
                frame = self._capture_frame(camera_system, 'dual')
                
                if self.timestamp_overlay or self.gps_overlay:
                    frame = self._add_overlays(frame, gps_tracker)
                
                frames.append(frame)
                
            except Exception as e:
                print(f"Incident clip frame error: {e}")
            
            time.sleep(frame_delay)
        
        if frames:
            self._save_frames_as_gif(frames, video_path)
            
            file_size_mb = video_path.stat().st_size / (1024 * 1024)
            
            return {
                'ok': True,
                'incident_id': incident_id,
                'video_path': str(video_path),
                'duration_seconds': duration_seconds,
                'file_size_mb': file_size_mb,
                'protected': True
            }
        
        return {'ok': False, 'error': 'Failed to record incident clip'}
    
    def capture_snapshot(self, camera_system, reason: str = 'manual') -> Dict:
        """Capture single snapshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{reason}_{timestamp}.jpg"
        snapshot_path = self.output_dir / filename
        
        try:
            frame = self._capture_frame(camera_system, 'front')
            frame.save(str(snapshot_path), 'JPEG', quality=95)
            
            file_size_mb = snapshot_path.stat().st_size / (1024 * 1024)
            
            return {
                'ok': True,
                'snapshot_path': str(snapshot_path),
                'file_size_mb': file_size_mb,
                'reason': reason
            }
        
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def _check_and_cleanup_storage(self):
        """Check storage usage and cleanup if needed."""
        try:
            total_size = sum(f.stat().st_size for f in self.output_dir.glob('*') if f.is_file())
            
            if total_size > self.max_storage_bytes * 0.9:
                self._cleanup_old_recordings()
        
        except Exception as e:
            print(f"Storage check error: {e}")
    
    def _cleanup_old_recordings(self):
        """Delete oldest unprotected recordings."""
        try:
            files = sorted(
                self.output_dir.glob('*.gif'),
                key=lambda f: f.stat().st_mtime
            )
            
            protected_keywords = ['incident', 'protected']
            
            for file in files[:10]:
                if not any(keyword in file.name.lower() for keyword in protected_keywords):
                    file.unlink()
                    print(f"Deleted old recording: {file.name}")
        
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        try:
            files = list(self.output_dir.glob('*'))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            total_size_gb = total_size / (1024**3)
            available_gb = (self.max_storage_bytes - total_size) / (1024**3)
            
            return {
                'total_recordings': len([f for f in files if f.suffix in ['.gif', '.mp4']]),
                'total_size_gb': round(total_size_gb, 2),
                'max_storage_gb': round(self.max_storage_bytes / (1024**3), 2),
                'available_gb': round(available_gb, 2),
                'usage_percent': round((total_size / self.max_storage_bytes) * 100, 1)
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def is_recording(self) -> bool:
        """Check if continuous recording is active."""
        return self.continuous_recording_active
    
    def get_status(self) -> Dict:
        """Get recorder status."""
        return {
            'continuous_recording_active': self.continuous_recording_active,
            'parking_mode_active': self.parking_mode_active,
            'timestamp_overlay': self.timestamp_overlay,
            'gps_overlay': self.gps_overlay,
            'active_recordings': len(self.active_recordings),
            'storage': self.get_storage_stats()
        }
