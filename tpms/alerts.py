#!/usr/bin/env python3
"""
TPMS Alert System
Manages tire pressure monitoring alerts and notifications
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from services.tpms.database import TPMSDatabase
from services.tpms.monitor import TPMSMonitor


class TPMSAlertSystem:
    """TPMS alert management system."""
    
    def __init__(self, db: TPMSDatabase, monitor: TPMSMonitor):
        """Initialize alert system."""
        self.db = db
        self.monitor = monitor
        
        # Alert thresholds (can be overridden by seasonal settings)
        self.min_psi = 28.0
        self.max_psi = 36.0
        self.recommended_psi = 33.0
        
        # Spare tire has different thresholds
        self.spare_min_psi = 50.0
        self.spare_max_psi = 65.0
        
        # Temperature thresholds
        self.temp_warning_f = 150.0
        self.temp_critical_f = 180.0
        
        # Tracking active alerts to avoid duplicates
        self.active_alert_types = {}
    
    def update_thresholds_from_seasonal(self, seasonal_settings: Dict = None):
        """Update thresholds from seasonal settings."""
        if not seasonal_settings:
            seasonal_settings = self.db.get_active_seasonal_setting()
        
        if seasonal_settings:
            self.min_psi = seasonal_settings['min_psi']
            self.max_psi = seasonal_settings['max_psi']
            self.recommended_psi = seasonal_settings['recommended_psi']
    
    def check_all_pressures(self) -> List[Dict]:
        """Check all tire pressures and generate alerts."""
        readings = self.monitor.get_current_readings()
        alerts = []
        
        for position, reading in readings.items():
            pressure = reading['pressure_psi']
            temp = reading['temperature_f']
            
            # Use different thresholds for spare
            if position == 'spare':
                min_psi = self.spare_min_psi
                max_psi = self.spare_max_psi
            else:
                min_psi = self.min_psi
                max_psi = self.max_psi
            
            # Check low pressure
            if pressure < min_psi:
                alert = self._create_alert(
                    position, 
                    'low_pressure',
                    'warning' if pressure > min_psi - 5 else 'critical',
                    f"{position.replace('_', ' ').title()} tire pressure is low ({pressure} PSI). Recommended: {self.recommended_psi} PSI",
                    pressure,
                    temp
                )
                if alert:
                    alerts.append(alert)
            
            # Check high pressure
            elif pressure > max_psi:
                alert = self._create_alert(
                    position,
                    'high_pressure',
                    'warning',
                    f"{position.replace('_', ' ').title()} tire pressure is high ({pressure} PSI). Recommended: {self.recommended_psi} PSI",
                    pressure,
                    temp
                )
                if alert:
                    alerts.append(alert)
            
            # Check temperature
            if temp >= self.temp_critical_f:
                alert = self._create_alert(
                    position,
                    'high_temperature',
                    'critical',
                    f"{position.replace('_', ' ').title()} tire temperature is critically high ({temp}°F)! Pull over safely.",
                    pressure,
                    temp
                )
                if alert:
                    alerts.append(alert)
            
            elif temp >= self.temp_warning_f:
                alert = self._create_alert(
                    position,
                    'warm_temperature',
                    'warning',
                    f"{position.replace('_', ' ').title()} tire temperature is elevated ({temp}°F).",
                    pressure,
                    temp
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def check_slow_leaks(self) -> List[Dict]:
        """Check for slow leaks in all tires."""
        alerts = []
        positions = ['front_left', 'front_right', 'rear_left', 'rear_right', 'spare']
        
        for position in positions:
            leak_data = self.db.detect_slow_leak(position, hours=72)
            
            if leak_data:
                alert = self._create_alert(
                    position,
                    'slow_leak',
                    leak_data['severity'],
                    f"{position.replace('_', ' ').title()} tire may have a slow leak. "
                    f"Losing {leak_data['drop_rate_psi_per_day']:.2f} PSI per day.",
                    None,
                    None
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def check_sensor_battery(self) -> List[Dict]:
        """Check TPMS sensor battery levels."""
        alerts = []
        sensors = self.db.get_sensors()
        
        for sensor in sensors:
            battery = sensor.get('battery_voltage', 3.0)
            
            if battery < 2.5:
                alert = self._create_alert(
                    sensor['tire_position'],
                    'sensor_battery_low',
                    'warning',
                    f"TPMS sensor battery low for {sensor['tire_position'].replace('_', ' ')} tire ({battery}V). Consider replacement.",
                    None,
                    None
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def check_spare_tire(self) -> Optional[Dict]:
        """Check if spare tire has been checked recently."""
        spare_reading = self.monitor.get_reading('spare')
        
        if not spare_reading or not spare_reading.get('last_update'):
            return None
        
        # Parse last update
        try:
            last_update = datetime.fromisoformat(spare_reading['last_update'])
            days_since_check = (datetime.now() - last_update).days
            
            # Remind to check spare every 30 days
            if days_since_check > 30:
                return self._create_alert(
                    'spare',
                    'spare_check_reminder',
                    'info',
                    f"Spare tire hasn't been checked in {days_since_check} days. Please verify pressure.",
                    spare_reading['pressure_psi'],
                    spare_reading['temperature_f']
                )
        except:
            pass
        
        return None
    
    def check_rotation_needed(self, current_mileage: int) -> Optional[Dict]:
        """Check if tire rotation is needed."""
        last_rotation_mileage = self.db.get_last_rotation_mileage()
        
        if not last_rotation_mileage:
            # No rotation recorded, suggest first rotation
            if current_mileage > 5000:
                return {
                    'type': 'rotation_needed',
                    'severity': 'info',
                    'message': f"Tire rotation recommended. Current mileage: {current_mileage} miles.",
                    'miles_since_rotation': current_mileage
                }
        else:
            miles_since_rotation = current_mileage - last_rotation_mileage
            
            # Recommend rotation every 6000-8000 miles for Sonic
            if miles_since_rotation >= 6000:
                severity = 'warning' if miles_since_rotation >= 8000 else 'info'
                return {
                    'type': 'rotation_needed',
                    'severity': severity,
                    'message': f"Tire rotation recommended. {miles_since_rotation} miles since last rotation.",
                    'miles_since_rotation': miles_since_rotation,
                    'last_rotation_mileage': last_rotation_mileage
                }
        
        return None
    
    def _create_alert(self, tire_position: str, alert_type: str, severity: str,
                     message: str, pressure_psi: float = None, 
                     temperature_f: float = None) -> Optional[Dict]:
        """Create and store an alert if not already active."""
        # Check if this type of alert is already active for this tire
        alert_key = f"{tire_position}:{alert_type}"
        
        if alert_key in self.active_alert_types:
            return None
        
        # Generate unique alert ID
        alert_id = f"alert_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        # Store in database
        try:
            self.db.add_alert(
                alert_id=alert_id,
                tire_position=tire_position,
                alert_type=alert_type,
                severity=severity,
                message=message,
                pressure_psi=pressure_psi,
                temperature_f=temperature_f
            )
            
            # Track active alert
            self.active_alert_types[alert_key] = alert_id
            
            return {
                'alert_id': alert_id,
                'tire_position': tire_position,
                'alert_type': alert_type,
                'severity': severity,
                'message': message,
                'pressure_psi': pressure_psi,
                'temperature_f': temperature_f,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error creating alert: {e}")
            return None
    
    def dismiss_alert(self, alert_id: str):
        """Dismiss an alert."""
        self.db.dismiss_alert(alert_id)
        
        # Remove from active tracking
        for key, active_id in list(self.active_alert_types.items()):
            if active_id == alert_id:
                del self.active_alert_types[key]
    
    def dismiss_all_alerts(self, tire_position: str = None):
        """Dismiss all alerts or all for a specific tire."""
        self.db.dismiss_all_alerts(tire_position)
        
        # Clear active tracking
        if tire_position:
            keys_to_remove = [k for k in self.active_alert_types.keys() if k.startswith(f"{tire_position}:")]
            for key in keys_to_remove:
                del self.active_alert_types[key]
        else:
            self.active_alert_types.clear()
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts from database."""
        return self.db.get_active_alerts()
    
    def refresh_active_alerts(self):
        """Refresh active alerts tracking from database."""
        active_alerts = self.db.get_active_alerts()
        self.active_alert_types.clear()
        
        for alert in active_alerts:
            alert_key = f"{alert['tire_position']}:{alert['alert_type']}"
            self.active_alert_types[alert_key] = alert['alert_id']
    
    def get_alert_summary(self) -> Dict:
        """Get summary of alerts by severity."""
        alerts = self.get_active_alerts()
        
        summary = {
            'total': len(alerts),
            'critical': 0,
            'warning': 0,
            'info': 0,
            'by_tire': {}
        }
        
        for alert in alerts:
            severity = alert['severity']
            position = alert['tire_position']
            
            summary[severity] = summary.get(severity, 0) + 1
            
            if position not in summary['by_tire']:
                summary['by_tire'][position] = []
            
            summary['by_tire'][position].append({
                'type': alert['alert_type'],
                'severity': severity,
                'message': alert['message']
            })
        
        return summary
