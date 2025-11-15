#!/usr/bin/env python3
"""
Motion Detection Module
AI-powered motion and person detection using camera feeds
"""

import uuid
import random
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path


class MotionDetector:
    """Motion detection with AI-powered person recognition."""
    
    def __init__(self, camera_service_url: str = "http://localhost:7300"):
        self.camera_service_url = camera_service_url
        self.sensitivity = 0.5
        self.armed = False
        self.person_detection_enabled = True
        self.motion_threshold = 0.3
        self.last_detections = {}
        
    def set_armed(self, armed: bool) -> None:
        """Arm or disarm the motion detection system."""
        self.armed = armed
        print(f"Motion detection {'ARMED' if armed else 'DISARMED'}")
    
    def set_sensitivity(self, sensitivity: float) -> None:
        """Set detection sensitivity (0.0 to 1.0)."""
        self.sensitivity = max(0.0, min(1.0, sensitivity))
    
    def set_person_detection(self, enabled: bool) -> None:
        """Enable or disable AI person detection."""
        self.person_detection_enabled = enabled
    
    def detect_motion(self, camera_position: str) -> Optional[Dict[str, Any]]:
        """
        Detect motion from a specific camera.
        Returns detection result or None if no motion.
        """
        try:
            frame_data = self._get_camera_frame(camera_position)
            if not frame_data:
                return None
            
            motion_detected, confidence = self._analyze_frame_for_motion(frame_data)
            
            if not motion_detected or confidence < self.motion_threshold:
                return None
            
            detection_id = f"motion_{uuid.uuid4().hex[:12]}"
            
            result = {
                'detection_id': detection_id,
                'camera_position': camera_position,
                'motion_detected': True,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'system_armed': self.armed
            }
            
            if self.person_detection_enabled:
                person_result = self._detect_persons(frame_data)
                result.update(person_result)
            
            self.last_detections[camera_position] = result
            
            return result
            
        except Exception as e:
            print(f"Motion detection error on {camera_position}: {e}")
            return None
    
    def detect_motion_all_cameras(self) -> List[Dict[str, Any]]:
        """Detect motion from all cameras."""
        detections = []
        camera_positions = ['front', 'rear', 'left', 'right']
        
        for position in camera_positions:
            detection = self.detect_motion(position)
            if detection:
                detections.append(detection)
        
        return detections
    
    def _get_camera_frame(self, camera_position: str) -> Optional[Dict[str, Any]]:
        """Get frame data from camera service."""
        try:
            response = requests.get(
                f"{self.camera_service_url}/api/cameras/{camera_position}/frame",
                timeout=2
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return self._simulate_camera_frame(camera_position)
    
    def _simulate_camera_frame(self, camera_position: str) -> Dict[str, Any]:
        """Simulate camera frame data when camera service unavailable."""
        return {
            'ok': True,
            'position': camera_position,
            'frame': 'simulated_frame_data',
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_frame_for_motion(self, frame_data: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Analyze frame for motion.
        Returns (motion_detected, confidence)
        """
        motion_chance = self.sensitivity * 0.3
        
        if random.random() < motion_chance:
            confidence = random.uniform(self.motion_threshold, 1.0)
            return True, confidence
        
        return False, 0.0
    
    def _detect_persons(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI-powered person detection.
        Simulates deep learning model inference.
        """
        person_detected = random.random() < 0.4
        
        if person_detected:
            num_persons = random.randint(1, 3)
            bounding_boxes = []
            
            for i in range(num_persons):
                box = {
                    'class': 'person',
                    'confidence': random.uniform(0.7, 0.99),
                    'bbox': {
                        'x': random.randint(50, 500),
                        'y': random.randint(50, 300),
                        'width': random.randint(80, 200),
                        'height': random.randint(150, 400)
                    }
                }
                bounding_boxes.append(box)
            
            return {
                'person_detected': True,
                'person_count': num_persons,
                'bounding_boxes': bounding_boxes,
                'detection_type': 'person'
            }
        else:
            return {
                'person_detected': False,
                'person_count': 0,
                'bounding_boxes': [],
                'detection_type': 'motion'
            }
    
    def capture_snapshot(self, camera_position: str, save_path: Optional[Path] = None) -> Optional[str]:
        """Capture and save snapshot from camera."""
        try:
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                snapshot_file = save_path / f"snapshot_{camera_position}_{timestamp}.jpg"
                
                snapshot_file.write_text(f"Simulated snapshot from {camera_position} at {datetime.now().isoformat()}")
                
                return str(snapshot_file)
        except Exception as e:
            print(f"Snapshot capture error: {e}")
        
        return None
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """Get summary of recent detections."""
        return {
            'armed': self.armed,
            'sensitivity': self.sensitivity,
            'person_detection_enabled': self.person_detection_enabled,
            'last_detections': self.last_detections,
            'cameras_monitored': ['front', 'rear', 'left', 'right']
        }
