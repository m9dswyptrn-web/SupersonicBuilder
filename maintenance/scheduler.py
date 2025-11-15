#!/usr/bin/env python3
"""
Maintenance Scheduler
Calculates when maintenance is due based on mileage and time intervals
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class MaintenanceScheduler:
    """Handles maintenance scheduling logic."""
    
    def __init__(self, database):
        """Initialize scheduler with database."""
        self.db = database
    
    def calculate_next_service(self, schedule: Dict, last_service_miles: int = None,
                               last_service_date: str = None) -> Dict:
        """
        Calculate when next service is due.
        
        Returns:
            Dict with next_miles, next_date, miles_remaining, days_remaining
        """
        current_miles = self.db.get_current_mileage() or 0
        current_date = datetime.now()
        
        result = {
            'next_miles': None,
            'next_date': None,
            'miles_remaining': None,
            'days_remaining': None,
            'is_due_soon': False,
            'is_overdue': False
        }
        
        mile_interval = schedule.get('mile_interval')
        month_interval = schedule.get('month_interval')
        
        if mile_interval and last_service_miles is not None:
            result['next_miles'] = last_service_miles + mile_interval
            result['miles_remaining'] = result['next_miles'] - current_miles
        
        if month_interval and last_service_date:
            try:
                last_date = datetime.strptime(last_service_date, '%Y-%m-%d')
                result['next_date'] = (last_date + timedelta(days=month_interval * 30)).strftime('%Y-%m-%d')
                next_date_dt = datetime.strptime(result['next_date'], '%Y-%m-%d')
                result['days_remaining'] = (next_date_dt - current_date).days
            except:
                pass
        
        if result['miles_remaining'] is not None:
            if result['miles_remaining'] < 0:
                result['is_overdue'] = True
            elif result['miles_remaining'] <= 500:
                result['is_due_soon'] = True
        
        if result['days_remaining'] is not None:
            if result['days_remaining'] < 0:
                result['is_overdue'] = True
            elif result['days_remaining'] <= 30:
                result['is_due_soon'] = True
        
        return result
    
    def get_upcoming_maintenance(self, miles_ahead: int = 5000,
                                days_ahead: int = 90) -> List[Dict]:
        """Get all upcoming maintenance items."""
        schedules = self.db.get_schedules(active_only=True)
        current_miles = self.db.get_current_mileage() or 0
        
        upcoming = []
        
        for schedule in schedules:
            last_service = self._get_last_service_for_schedule(schedule['id'])
            
            last_miles = last_service['odometer_reading'] if last_service else 0
            last_date = last_service['service_date'] if last_service else None
            
            next_service = self.calculate_next_service(schedule, last_miles, last_date)
            
            schedule_info = {
                'schedule_id': schedule['id'],
                'schedule_name': schedule['schedule_name'],
                'schedule_type': schedule['schedule_type'],
                'description': schedule['description'],
                'estimated_cost': schedule['estimated_cost'],
                'last_service_miles': last_miles,
                'last_service_date': last_date,
                **next_service
            }
            
            if next_service['is_due_soon'] or next_service['is_overdue']:
                upcoming.append(schedule_info)
            elif next_service['miles_remaining'] is not None and next_service['miles_remaining'] <= miles_ahead:
                upcoming.append(schedule_info)
            elif next_service['days_remaining'] is not None and next_service['days_remaining'] <= days_ahead:
                upcoming.append(schedule_info)
        
        upcoming.sort(key=lambda x: (
            0 if x['is_overdue'] else 1,
            x['miles_remaining'] if x['miles_remaining'] is not None else 999999,
            x['days_remaining'] if x['days_remaining'] is not None else 999999
        ))
        
        return upcoming
    
    def get_all_schedules_status(self) -> List[Dict]:
        """Get status of all maintenance schedules."""
        schedules = self.db.get_schedules(active_only=True)
        
        status_list = []
        
        for schedule in schedules:
            last_service = self._get_last_service_for_schedule(schedule['id'])
            
            last_miles = last_service['odometer_reading'] if last_service else 0
            last_date = last_service['service_date'] if last_service else None
            
            next_service = self.calculate_next_service(schedule, last_miles, last_date)
            
            status_list.append({
                'schedule_id': schedule['id'],
                'schedule_name': schedule['schedule_name'],
                'schedule_type': schedule['schedule_type'],
                'description': schedule['description'],
                'mile_interval': schedule['mile_interval'],
                'month_interval': schedule['month_interval'],
                'estimated_cost': schedule['estimated_cost'],
                'last_service_miles': last_miles,
                'last_service_date': last_date,
                **next_service
            })
        
        return status_list
    
    def _get_last_service_for_schedule(self, schedule_id: int) -> Optional[Dict]:
        """Get the most recent service for a schedule."""
        records = self.db.get_maintenance_records(limit=1000)
        
        matching_records = [r for r in records if r.get('schedule_id') == schedule_id]
        
        if not matching_records:
            return None
        
        matching_records.sort(key=lambda x: (x['service_date'], x['odometer_reading']), reverse=True)
        
        return matching_records[0]
    
    def estimate_annual_costs(self, annual_miles: int = 12000) -> Dict:
        """Estimate annual maintenance costs."""
        schedules = self.db.get_schedules(active_only=True)
        
        total_estimated = 0
        breakdown = []
        
        for schedule in schedules:
            cost_per_year = 0
            services_per_year = 0
            
            if schedule['mile_interval']:
                services_per_year = annual_miles / schedule['mile_interval']
            elif schedule['month_interval']:
                services_per_year = 12 / schedule['month_interval']
            
            if services_per_year > 0:
                cost_per_year = services_per_year * (schedule['estimated_cost'] or 0)
                total_estimated += cost_per_year
                
                breakdown.append({
                    'service_name': schedule['schedule_name'],
                    'services_per_year': round(services_per_year, 2),
                    'cost_per_service': schedule['estimated_cost'],
                    'annual_cost': round(cost_per_year, 2)
                })
        
        return {
            'total_estimated_annual': round(total_estimated, 2),
            'estimated_monthly': round(total_estimated / 12, 2),
            'breakdown': breakdown
        }
    
    def get_mileage_based_schedule(self, target_miles: int) -> List[Dict]:
        """Get maintenance schedule for specific mileage."""
        schedules = self.db.get_schedules(active_only=True)
        current_miles = self.db.get_current_mileage() or 0
        
        due_at_target = []
        
        for schedule in schedules:
            if not schedule['mile_interval']:
                continue
            
            mile_interval = schedule['mile_interval']
            last_service = self._get_last_service_for_schedule(schedule['id'])
            last_miles = last_service['odometer_reading'] if last_service else 0
            
            next_due = last_miles + mile_interval
            
            if current_miles < next_due <= target_miles:
                due_at_target.append({
                    'schedule_name': schedule['schedule_name'],
                    'due_at_miles': next_due,
                    'estimated_cost': schedule['estimated_cost'],
                    'description': schedule['description']
                })
        
        due_at_target.sort(key=lambda x: x['due_at_miles'])
        
        return due_at_target
