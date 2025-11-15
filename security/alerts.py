#!/usr/bin/env python3
"""
Alert System Module
Handles theft alerts, notifications, and emergency responses
"""

import uuid
import random
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path


class AlertSystem:
    """Security alert system with multiple notification channels."""
    
    def __init__(self):
        self.alerts = []
        self.active_alerts = []
        self.callbacks = []
        
        self.sms_enabled = True
        self.email_enabled = True
        self.push_enabled = True
        
        self.emergency_contacts = []
        self.panic_mode_active = False
        
    def register_callback(self, callback: Callable) -> None:
        """Register callback for alert notifications."""
        self.callbacks.append(callback)
    
    def trigger_alert(self, alert_type: str, title: str, message: str, 
                     severity: str = 'warning', triggered_by: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger a security alert."""
        alert_id = f"alert_{uuid.uuid4().hex[:12]}"
        
        alert = {
            'alert_id': alert_id,
            'alert_type': alert_type,
            'title': title,
            'message': message,
            'severity': severity,
            'triggered_by': triggered_by,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {},
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        self.active_alerts.append(alert)
        
        self._send_notifications(alert)
        
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Callback error: {e}")
        
        return alert
    
    def motion_alert(self, camera_position: str, person_detected: bool = False,
                    person_count: int = 0, confidence: float = 0.0) -> Dict[str, Any]:
        """Trigger motion detection alert."""
        if person_detected:
            title = f"Person Detected - {camera_position.title()} Camera"
            message = f"{person_count} person(s) detected at {camera_position} camera"
            severity = 'critical'
        else:
            title = f"Motion Detected - {camera_position.title()} Camera"
            message = f"Motion detected at {camera_position} camera"
            severity = 'warning'
        
        return self.trigger_alert(
            alert_type='motion_detection',
            title=title,
            message=message,
            severity=severity,
            triggered_by=f"camera_{camera_position}",
            metadata={
                'camera_position': camera_position,
                'person_detected': person_detected,
                'person_count': person_count,
                'confidence': confidence
            }
        )
    
    def door_alert(self, door_location: str, authorized: bool = False) -> Dict[str, Any]:
        """Trigger door open alert."""
        if authorized:
            severity = 'info'
            title = "Door Opened (Authorized)"
            message = f"{door_location} door opened with key"
        else:
            severity = 'critical'
            title = "UNAUTHORIZED Door Access!"
            message = f"{door_location} door opened WITHOUT authorization"
        
        return self.trigger_alert(
            alert_type='door_access',
            title=title,
            message=message,
            severity=severity,
            triggered_by=f"door_sensor_{door_location}",
            metadata={'door_location': door_location, 'authorized': authorized}
        )
    
    def ignition_alert(self, key_present: bool = False) -> Dict[str, Any]:
        """Trigger ignition alert."""
        if key_present:
            severity = 'info'
            title = "Vehicle Started (Authorized)"
            message = "Ignition activated with authorized key"
        else:
            severity = 'critical'
            title = "THEFT ATTEMPT - Ignition Without Key!"
            message = "Ignition activated WITHOUT authorized key"
        
        return self.trigger_alert(
            alert_type='ignition',
            title=title,
            message=message,
            severity=severity,
            triggered_by='ignition_sensor',
            metadata={'key_present': key_present}
        )
    
    def tow_away_alert(self, acceleration: float, tilt_angle: float) -> Dict[str, Any]:
        """Trigger tow-away detection alert."""
        return self.trigger_alert(
            alert_type='tow_away',
            title='TOW-AWAY DETECTED!',
            message=f'Vehicle movement detected - Acceleration: {acceleration:.2f}g, Tilt: {tilt_angle:.1f}°',
            severity='critical',
            triggered_by='accelerometer',
            metadata={'acceleration': acceleration, 'tilt_angle': tilt_angle}
        )
    
    def battery_alert(self, voltage: float, disconnected: bool = False) -> Dict[str, Any]:
        """Trigger battery alert."""
        if disconnected:
            title = 'BATTERY DISCONNECTED!'
            message = 'Vehicle battery has been disconnected'
            severity = 'critical'
        elif voltage < 11.5:
            title = 'Critical Battery Voltage'
            message = f'Battery voltage critically low: {voltage:.2f}V'
            severity = 'critical'
        elif voltage < 12.0:
            title = 'Low Battery Warning'
            message = f'Battery voltage low: {voltage:.2f}V'
            severity = 'warning'
        else:
            return None
        
        return self.trigger_alert(
            alert_type='battery',
            title=title,
            message=message,
            severity=severity,
            triggered_by='battery_monitor',
            metadata={'voltage': voltage, 'disconnected': disconnected}
        )
    
    def geofence_alert(self, fence_name: str, event_type: str, location: tuple) -> Dict[str, Any]:
        """Trigger geofence alert."""
        lat, lng = location
        
        if event_type == 'exit':
            title = f'Geofence Exit - {fence_name}'
            message = f'Vehicle has left geofence area: {fence_name}'
        else:
            title = f'Geofence Entry - {fence_name}'
            message = f'Vehicle has entered geofence area: {fence_name}'
        
        return self.trigger_alert(
            alert_type='geofence',
            title=title,
            message=message,
            severity='warning',
            triggered_by=f'geofence_{fence_name}',
            metadata={
                'fence_name': fence_name,
                'event_type': event_type,
                'latitude': lat,
                'longitude': lng
            }
        )
    
    def activate_panic_mode(self, trigger_source: str = 'manual') -> Dict[str, Any]:
        """Activate panic mode - emergency response."""
        self.panic_mode_active = True
        
        print("🚨 PANIC MODE ACTIVATED! 🚨")
        print("  - Sounding horn")
        print("  - Flashing lights")
        print("  - Recording all cameras")
        print("  - Sending emergency notifications")
        print("  - Notifying 911 (simulated)")
        
        alert = self.trigger_alert(
            alert_type='panic',
            title='🚨 PANIC MODE ACTIVATED!',
            message='Emergency panic button pressed - All emergency services notified',
            severity='critical',
            triggered_by=trigger_source,
            metadata={
                'horn_active': True,
                'lights_flashing': True,
                'emergency_911_notified': True,
                'all_cameras_recording': True
            }
        )
        
        self._emergency_911_notification()
        
        return alert
    
    def deactivate_panic_mode(self) -> Dict[str, Any]:
        """Deactivate panic mode."""
        self.panic_mode_active = False
        
        return {
            'panic_mode_active': False,
            'message': 'Panic mode deactivated',
            'timestamp': datetime.now().isoformat()
        }
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.active_alerts:
            if alert['alert_id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
                self.active_alerts.remove(alert)
                return True
        return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unacknowledged) alerts."""
        return self.active_alerts.copy()
    
    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alert history."""
        return self.alerts[-limit:] if len(self.alerts) > limit else self.alerts.copy()
    
    def _send_notifications(self, alert: Dict[str, Any]) -> None:
        """Send notifications via configured channels."""
        sent_channels = []
        
        if self.sms_enabled:
            self._send_sms(alert)
            sent_channels.append('SMS')
        
        if self.email_enabled:
            self._send_email(alert)
            sent_channels.append('Email')
        
        if self.push_enabled:
            self._send_push_notification(alert)
            sent_channels.append('Push')
        
        if sent_channels:
            print(f"📱 Notifications sent via: {', '.join(sent_channels)}")
    
    def _send_sms(self, alert: Dict[str, Any]) -> None:
        """Send SMS notification (simulated)."""
        print(f"[SMS] {alert['severity'].upper()}: {alert['message']}")
    
    def _send_email(self, alert: Dict[str, Any]) -> None:
        """Send email notification (simulated)."""
        print(f"[EMAIL] Subject: {alert['title']}")
        print(f"        {alert['message']}")
    
    def _send_push_notification(self, alert: Dict[str, Any]) -> None:
        """Send push notification (simulated)."""
        print(f"[PUSH] {alert['title']}: {alert['message']}")
    
    def _emergency_911_notification(self) -> None:
        """Notify emergency services (simulated)."""
        print("\n🚨 EMERGENCY 911 NOTIFICATION (SIMULATED)")
        print("   Emergency Type: Panic Alert")
        print("   Vehicle: GPS coordinates transmitted")
        print("   Status: Emergency services dispatched")
        print("   Live camera feeds: Streaming to emergency services\n")
    
    def configure_notifications(self, sms: bool = True, email: bool = True, 
                              push: bool = True) -> Dict[str, Any]:
        """Configure notification channels."""
        self.sms_enabled = sms
        self.email_enabled = email
        self.push_enabled = push
        
        return {
            'sms_enabled': self.sms_enabled,
            'email_enabled': self.email_enabled,
            'push_enabled': self.push_enabled
        }
    
    def add_emergency_contact(self, name: str, phone: str, email: str) -> None:
        """Add emergency contact."""
        self.emergency_contacts.append({
            'name': name,
            'phone': phone,
            'email': email,
            'added_at': datetime.now().isoformat()
        })
    
    def get_status(self) -> Dict[str, Any]:
        """Get alert system status."""
        return {
            'active_alerts_count': len(self.active_alerts),
            'total_alerts': len(self.alerts),
            'panic_mode_active': self.panic_mode_active,
            'notifications': {
                'sms_enabled': self.sms_enabled,
                'email_enabled': self.email_enabled,
                'push_enabled': self.push_enabled
            },
            'emergency_contacts_count': len(self.emergency_contacts)
        }
