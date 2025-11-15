#!/usr/bin/env python3
"""
Maintenance Alert System
Generates and manages maintenance reminders and notifications
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


class MaintenanceAlertSystem:
    """Handles maintenance alerts and reminders."""
    
    def __init__(self, database, scheduler):
        """Initialize alert system."""
        self.db = database
        self.scheduler = scheduler
    
    def generate_alerts(self) -> List[Dict]:
        """Generate alerts for upcoming and overdue maintenance."""
        upcoming = self.scheduler.get_upcoming_maintenance(miles_ahead=1000, days_ahead=60)
        
        alerts_created = []
        
        for item in upcoming:
            schedule_id = item['schedule_id']
            schedule_name = item['schedule_name']
            
            if item['is_overdue']:
                alert = self._create_overdue_alert(item)
            elif item['is_due_soon']:
                alert = self._create_due_soon_alert(item)
            else:
                continue
            
            if alert:
                alert_id = self.db.create_alert(
                    schedule_id=schedule_id,
                    alert_type=alert['type'],
                    severity=alert['severity'],
                    title=alert['title'],
                    message=alert['message'],
                    miles_until_due=item.get('miles_remaining'),
                    days_until_due=item.get('days_remaining'),
                    is_overdue=item['is_overdue']
                )
                
                if alert_id:
                    alerts_created.append({
                        'alert_id': alert_id,
                        **alert
                    })
        
        return alerts_created
    
    def _create_overdue_alert(self, item: Dict) -> Dict:
        """Create alert for overdue maintenance."""
        schedule_name = item['schedule_name']
        miles_remaining = item.get('miles_remaining')
        days_remaining = item.get('days_remaining')
        
        overdue_msg_parts = []
        
        if miles_remaining is not None and miles_remaining < 0:
            overdue_msg_parts.append(f"{abs(miles_remaining)} miles overdue")
        
        if days_remaining is not None and days_remaining < 0:
            overdue_msg_parts.append(f"{abs(days_remaining)} days overdue")
        
        overdue_msg = " and ".join(overdue_msg_parts) if overdue_msg_parts else "overdue"
        
        return {
            'type': 'overdue',
            'severity': 'critical',
            'title': f'{schedule_name} Overdue!',
            'message': f'Your {schedule_name.lower()} is {overdue_msg}. Schedule service immediately to avoid potential damage.'
        }
    
    def _create_due_soon_alert(self, item: Dict) -> Dict:
        """Create alert for maintenance due soon."""
        schedule_name = item['schedule_name']
        miles_remaining = item.get('miles_remaining')
        days_remaining = item.get('days_remaining')
        
        due_msg_parts = []
        
        if miles_remaining is not None and 0 <= miles_remaining <= 500:
            due_msg_parts.append(f"in {miles_remaining} miles")
        
        if days_remaining is not None and 0 <= days_remaining <= 30:
            due_msg_parts.append(f"in {days_remaining} days")
        
        due_msg = " or ".join(due_msg_parts) if due_msg_parts else "soon"
        
        severity = 'warning' if (miles_remaining or 501) <= 250 or (days_remaining or 31) <= 14 else 'info'
        
        return {
            'type': 'due_soon',
            'severity': severity,
            'title': f'{schedule_name} Due Soon',
            'message': f'Your {schedule_name.lower()} is due {due_msg}. Plan to schedule service soon.'
        }
    
    def get_alert_summary(self) -> Dict:
        """Get summary of active alerts."""
        alerts = self.db.get_active_alerts()
        
        critical_count = len([a for a in alerts if a['severity'] == 'critical'])
        warning_count = len([a for a in alerts if a['severity'] == 'warning'])
        info_count = len([a for a in alerts if a['severity'] == 'info'])
        
        return {
            'total_alerts': len(alerts),
            'critical': critical_count,
            'warning': warning_count,
            'info': info_count,
            'alerts': alerts
        }
    
    def send_reminder(self, alert: Dict, method: str = 'email') -> Dict:
        """
        Simulate sending reminder via email/SMS.
        In production, this would integrate with email/SMS services.
        """
        timestamp = datetime.now().isoformat()
        
        if method == 'email':
            return {
                'ok': True,
                'method': 'email',
                'simulated': True,
                'to': 'owner@example.com',
                'subject': alert['title'],
                'body': alert['message'],
                'sent_at': timestamp
            }
        elif method == 'sms':
            return {
                'ok': True,
                'method': 'sms',
                'simulated': True,
                'to': '+1234567890',
                'message': f"{alert['title']}: {alert['message']}",
                'sent_at': timestamp
            }
        else:
            return {
                'ok': False,
                'error': 'Invalid method'
            }
    
    def create_custom_reminder(self, title: str, message: str, 
                              miles_until: int = None, days_until: int = None) -> Optional[str]:
        """Create a custom reminder."""
        alert_id = self.db.create_alert(
            schedule_id=None,
            alert_type='custom',
            severity='info',
            title=title,
            message=message,
            miles_until_due=miles_until,
            days_until_due=days_until,
            is_overdue=False
        )
        
        return alert_id
    
    def get_maintenance_forecast(self, months: int = 6) -> List[Dict]:
        """Forecast maintenance for upcoming months."""
        schedules = self.scheduler.get_all_schedules_status()
        current_miles = self.db.get_current_mileage() or 0
        
        avg_miles_per_month = 1000
        
        forecast = []
        
        for month in range(1, months + 1):
            projected_miles = current_miles + (avg_miles_per_month * month)
            month_date = datetime.now().replace(day=1) + timedelta(days=30 * month)
            
            due_this_month = []
            
            for schedule in schedules:
                if schedule.get('next_miles') and schedule['next_miles'] <= projected_miles:
                    if schedule['next_miles'] > current_miles + (avg_miles_per_month * (month - 1)):
                        due_this_month.append({
                            'service': schedule['schedule_name'],
                            'estimated_cost': schedule['estimated_cost'],
                            'reason': 'mileage'
                        })
            
            forecast.append({
                'month': month_date.strftime('%B %Y'),
                'projected_miles': projected_miles,
                'services_due': due_this_month,
                'estimated_cost': sum(s['estimated_cost'] or 0 for s in due_this_month)
            })
        
        return forecast


from datetime import timedelta
from typing import Optional
