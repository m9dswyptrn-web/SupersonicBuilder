#!/usr/bin/env python3
"""
Incident Detection Module
G-sensor (accelerometer) simulation and collision/hard braking detection
"""

import uuid
import random
import math
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable


class IncidentDetector:
    """G-sensor based incident detection for dashcam."""
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize incident detector.
        
        Args:
            callback: Optional callback function called when incident detected
        """
        self.sensitivity = 0.5
        self.enabled = True
        self.callback = callback
        
        self.g_force_thresholds = {
            'hard_braking': 0.6,
            'collision': 1.2,
            'rapid_acceleration': 0.5,
            'sharp_turn': 0.7
        }
        
        self.incident_types = [
            'collision',
            'hard_braking',
            'rapid_acceleration',
            'sharp_turn',
            'near_miss',
            'pothole',
            'sudden_swerve'
        ]
        
        self.current_g_force = {'x': 0.0, 'y': 0.0, 'z': 1.0}
        self.last_incident_time = None
        self.incident_cooldown = 5
        
        self.auto_snapshot_on_honk = True
        
    def set_sensitivity(self, sensitivity: float):
        """Set G-sensor sensitivity (0.0 to 1.0)."""
        self.sensitivity = max(0.0, min(1.0, sensitivity))
    
    def set_enabled(self, enabled: bool):
        """Enable or disable incident detection."""
        self.enabled = enabled
    
    def simulate_g_force(self, speed_kmh: float = None, 
                        driving_mode: str = 'normal') -> Dict[str, float]:
        """
        Simulate G-force readings based on driving conditions.
        
        Args:
            speed_kmh: Current speed
            driving_mode: Driving mode (normal, aggressive, parking)
        
        Returns:
            G-force dict with x, y, z values
        """
        if driving_mode == 'parking' or (speed_kmh and speed_kmh < 5):
            g_force = {
                'x': random.uniform(-0.1, 0.1),
                'y': random.uniform(-0.1, 0.1),
                'z': random.uniform(0.95, 1.05)
            }
        elif driving_mode == 'aggressive':
            g_force = {
                'x': random.uniform(-0.8, 0.8),
                'y': random.uniform(-0.8, 0.8),
                'z': random.uniform(0.8, 1.2)
            }
        else:
            g_force = {
                'x': random.uniform(-0.3, 0.3),
                'y': random.uniform(-0.3, 0.3),
                'z': random.uniform(0.9, 1.1)
            }
        
        self.current_g_force = g_force
        return g_force
    
    def detect_incident(self, g_force: Dict[str, float] = None,
                       speed_kmh: float = None,
                       location: Dict[str, float] = None) -> Optional[Dict[str, Any]]:
        """
        Detect incidents based on G-force readings.
        
        Args:
            g_force: G-force readings (if None, uses simulated values)
            speed_kmh: Current speed
            location: GPS location dict with lat/lng
        
        Returns:
            Incident dict if detected, None otherwise
        """
        if not self.enabled:
            return None
        
        if self.last_incident_time:
            time_since_last = (datetime.now() - self.last_incident_time).total_seconds()
            if time_since_last < self.incident_cooldown:
                return None
        
        if g_force is None:
            g_force = self.simulate_g_force(speed_kmh)
        
        total_g = math.sqrt(g_force['x']**2 + g_force['y']**2 + (g_force['z'] - 1.0)**2)
        
        adjusted_threshold = 0.8 * (1.0 - self.sensitivity * 0.5)
        
        if total_g < adjusted_threshold:
            return None
        
        incident_type = self._classify_incident(g_force, total_g, speed_kmh)
        severity = self._calculate_severity(total_g)
        
        incident = self._create_incident_event(
            incident_type=incident_type,
            g_force_value=total_g,
            g_force_vector=g_force,
            speed_kmh=speed_kmh,
            location=location,
            severity=severity
        )
        
        self.last_incident_time = datetime.now()
        
        if self.callback:
            self.callback(incident)
        
        return incident
    
    def _classify_incident(self, g_force: Dict[str, float], total_g: float,
                          speed_kmh: Optional[float]) -> str:
        """Classify the type of incident based on G-force patterns."""
        x, y, z = g_force['x'], g_force['y'], g_force['z']
        
        if total_g > self.g_force_thresholds['collision']:
            return 'collision'
        
        if abs(x) > 0.6 and (speed_kmh and speed_kmh > 30):
            if x < 0:
                return 'hard_braking'
            else:
                return 'rapid_acceleration'
        
        if abs(y) > 0.7:
            return 'sharp_turn'
        
        if abs(x) > 0.5 and abs(y) > 0.5:
            return 'sudden_swerve'
        
        if abs(z - 1.0) > 0.4 and (speed_kmh and speed_kmh > 20):
            return 'pothole'
        
        if total_g > 0.6:
            return 'near_miss'
        
        return random.choice(['hard_braking', 'sharp_turn', 'sudden_swerve'])
    
    def _calculate_severity(self, total_g: float) -> str:
        """Calculate incident severity based on G-force magnitude."""
        if total_g > 1.5:
            return 'critical'
        elif total_g > 1.0:
            return 'high'
        elif total_g > 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _create_incident_event(self, incident_type: str, g_force_value: float,
                              g_force_vector: Dict[str, float],
                              speed_kmh: Optional[float],
                              location: Optional[Dict[str, float]],
                              severity: str) -> Dict[str, Any]:
        """Create incident event dictionary."""
        incident_id = f"incident_{uuid.uuid4().hex[:12]}"
        
        incident = {
            'incident_id': incident_id,
            'incident_type': incident_type,
            'severity': severity,
            'g_force_value': round(g_force_value, 3),
            'g_force_vector': {
                'x': round(g_force_vector['x'], 3),
                'y': round(g_force_vector['y'], 3),
                'z': round(g_force_vector['z'], 3)
            },
            'speed_kmh': speed_kmh,
            'timestamp': datetime.now().isoformat(),
            'protected': True,
            'auto_saved': True
        }
        
        if location:
            incident['location'] = {
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude')
            }
        
        return incident
    
    def trigger_manual_snapshot(self, reason: str = 'manual') -> Dict[str, Any]:
        """Trigger manual snapshot (button press or honk)."""
        snapshot_id = f"snapshot_{uuid.uuid4().hex[:12]}"
        
        snapshot = {
            'snapshot_id': snapshot_id,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'type': 'manual_snapshot'
        }
        
        if self.callback:
            self.callback(snapshot)
        
        return snapshot
    
    def detect_honk(self) -> Optional[Dict[str, Any]]:
        """Simulate honk detection for auto-snapshot."""
        if not self.auto_snapshot_on_honk:
            return None
        
        honk_detected = random.random() < 0.1
        
        if honk_detected:
            return self.trigger_manual_snapshot(reason='honk_detected')
        
        return None
    
    def simulate_parking_mode_event(self, motion_detected: bool = False) -> Optional[Dict[str, Any]]:
        """Simulate parking mode motion detection event."""
        if not motion_detected:
            return None
        
        event_id = f"parking_event_{uuid.uuid4().hex[:12]}"
        
        event = {
            'event_id': event_id,
            'event_type': 'parking_mode_motion',
            'motion_detected': True,
            'timestamp': datetime.now().isoformat(),
            'severity': 'medium',
            'protected': True
        }
        
        if self.callback:
            self.callback(event)
        
        return event
    
    def get_recent_g_force(self) -> Dict[str, float]:
        """Get most recent G-force reading."""
        return self.current_g_force.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get incident detector status."""
        return {
            'enabled': self.enabled,
            'sensitivity': self.sensitivity,
            'current_g_force': self.current_g_force,
            'thresholds': self.g_force_thresholds,
            'auto_snapshot_on_honk': self.auto_snapshot_on_honk,
            'last_incident': self.last_incident_time.isoformat() if self.last_incident_time else None
        }
