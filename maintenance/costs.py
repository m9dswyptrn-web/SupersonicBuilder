#!/usr/bin/env python3
"""
Maintenance Cost Tracking & Analysis
Analyzes maintenance costs, trends, and budget planning
"""

from datetime import datetime, timedelta
from typing import Dict, List


class MaintenanceCostTracker:
    """Handles cost tracking and analysis."""
    
    def __init__(self, database):
        """Initialize cost tracker."""
        self.db = database
    
    def get_cost_summary(self, period: str = 'all') -> Dict:
        """
        Get cost summary for a period.
        period: 'all', 'year', 'month', 'ytd'
        """
        start_date = None
        end_date = None
        
        if period == 'month':
            start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        elif period == 'year':
            start_date = datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
        elif period == 'ytd':
            start_date = datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        summary = self.db.get_cost_summary(start_date, end_date)
        
        summary['total_spent'] = summary.get('total_spent') or 0
        summary['total_parts'] = summary.get('total_parts') or 0
        summary['total_labor'] = summary.get('total_labor') or 0
        summary['avg_cost'] = summary.get('avg_cost') or 0
        summary['diy_count'] = summary.get('diy_count') or 0
        summary['shop_count'] = summary.get('shop_count') or 0
        summary['total_services'] = summary.get('total_services') or 0
        
        return summary
    
    def calculate_diy_savings(self, start_date: str = None, end_date: str = None) -> Dict:
        """Calculate money saved by doing DIY maintenance."""
        records = self.db.get_maintenance_records(limit=1000)
        
        if start_date:
            records = [r for r in records if r['service_date'] >= start_date]
        if end_date:
            records = [r for r in records if r['service_date'] <= end_date]
        
        diy_records = [r for r in records if r['service_category'] == 'diy']
        
        total_diy_cost = sum(r['total_cost'] for r in diy_records)
        total_diy_labor_hours = sum(r['labor_hours'] or 0 for r in diy_records)
        
        avg_shop_labor_rate = 100.0
        estimated_shop_cost = total_diy_cost + (total_diy_labor_hours * avg_shop_labor_rate)
        
        savings = estimated_shop_cost - total_diy_cost
        
        return {
            'diy_services': len(diy_records),
            'actual_diy_cost': round(total_diy_cost, 2),
            'estimated_shop_cost': round(estimated_shop_cost, 2),
            'total_savings': round(savings, 2),
            'labor_hours_invested': round(total_diy_labor_hours, 2),
            'avg_shop_labor_rate': avg_shop_labor_rate
        }
    
    def get_cost_trends(self, months: int = 12) -> Dict:
        """Get monthly cost trends."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        records = self.db.get_maintenance_records(limit=1000)
        records = [r for r in records if r['service_date'] >= start_date.strftime('%Y-%m-%d')]
        
        monthly_costs = {}
        
        for record in records:
            try:
                service_date = datetime.strptime(record['service_date'], '%Y-%m-%d')
                month_key = service_date.strftime('%Y-%m')
                
                if month_key not in monthly_costs:
                    monthly_costs[month_key] = {
                        'month': service_date.strftime('%B %Y'),
                        'total_cost': 0,
                        'service_count': 0,
                        'diy_cost': 0,
                        'shop_cost': 0
                    }
                
                monthly_costs[month_key]['total_cost'] += record['total_cost']
                monthly_costs[month_key]['service_count'] += 1
                
                if record['service_category'] == 'diy':
                    monthly_costs[month_key]['diy_cost'] += record['total_cost']
                else:
                    monthly_costs[month_key]['shop_cost'] += record['total_cost']
            except:
                continue
        
        trend_data = sorted(monthly_costs.values(), key=lambda x: x['month'])
        
        total_spent = sum(m['total_cost'] for m in trend_data)
        avg_monthly = total_spent / len(trend_data) if trend_data else 0
        
        return {
            'monthly_data': trend_data,
            'total_spent': round(total_spent, 2),
            'avg_monthly': round(avg_monthly, 2),
            'months_tracked': len(trend_data)
        }
    
    def compare_estimated_vs_actual(self) -> Dict:
        """Compare estimated costs vs actual costs."""
        schedules = self.db.get_schedules(active_only=True)
        records = self.db.get_maintenance_records(limit=1000)
        
        comparisons = []
        
        for schedule in schedules:
            matching_records = [r for r in records if r.get('schedule_id') == schedule['id']]
            
            if not matching_records:
                continue
            
            actual_costs = [r['total_cost'] for r in matching_records]
            avg_actual = sum(actual_costs) / len(actual_costs)
            estimated = schedule['estimated_cost'] or 0
            
            variance = avg_actual - estimated
            variance_percent = (variance / estimated * 100) if estimated > 0 else 0
            
            comparisons.append({
                'service_name': schedule['schedule_name'],
                'estimated_cost': estimated,
                'avg_actual_cost': round(avg_actual, 2),
                'variance': round(variance, 2),
                'variance_percent': round(variance_percent, 1),
                'service_count': len(matching_records)
            })
        
        return {
            'comparisons': comparisons,
            'total_comparisons': len(comparisons)
        }
    
    def get_cost_by_type(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get costs grouped by maintenance type."""
        records = self.db.get_maintenance_records(limit=1000)
        
        if start_date:
            records = [r for r in records if r['service_date'] >= start_date]
        if end_date:
            records = [r for r in records if r['service_date'] <= end_date]
        
        type_costs = {}
        
        for record in records:
            service_type = record.get('schedule_type') or 'other'
            
            if service_type not in type_costs:
                type_costs[service_type] = {
                    'type': service_type,
                    'total_cost': 0,
                    'service_count': 0,
                    'avg_cost': 0
                }
            
            type_costs[service_type]['total_cost'] += record['total_cost']
            type_costs[service_type]['service_count'] += 1
        
        result = []
        for type_data in type_costs.values():
            type_data['avg_cost'] = type_data['total_cost'] / type_data['service_count']
            type_data['total_cost'] = round(type_data['total_cost'], 2)
            type_data['avg_cost'] = round(type_data['avg_cost'], 2)
            result.append(type_data)
        
        result.sort(key=lambda x: x['total_cost'], reverse=True)
        
        return result
    
    def get_most_expensive_services(self, limit: int = 10) -> List[Dict]:
        """Get the most expensive service records."""
        records = self.db.get_maintenance_records(limit=1000)
        
        sorted_records = sorted(records, key=lambda x: x['total_cost'], reverse=True)
        
        return sorted_records[:limit]
    
    def calculate_cost_per_mile(self) -> Dict:
        """Calculate maintenance cost per mile driven."""
        records = self.db.get_maintenance_records(limit=1000)
        
        if not records:
            return {
                'total_cost': 0,
                'total_miles': 0,
                'cost_per_mile': 0
            }
        
        total_cost = sum(r['total_cost'] for r in records)
        
        odometers = [r['odometer_reading'] for r in records]
        min_odometer = min(odometers)
        max_odometer = max(odometers)
        total_miles = max_odometer - min_odometer
        
        cost_per_mile = total_cost / total_miles if total_miles > 0 else 0
        
        return {
            'total_cost': round(total_cost, 2),
            'total_miles': total_miles,
            'cost_per_mile': round(cost_per_mile, 4),
            'min_odometer': min_odometer,
            'max_odometer': max_odometer
        }
    
    def project_annual_costs(self, annual_miles: int = 12000) -> Dict:
        """Project annual maintenance costs based on historical data."""
        cost_per_mile_data = self.calculate_cost_per_mile()
        cost_per_mile = cost_per_mile_data['cost_per_mile']
        
        projected_annual = cost_per_mile * annual_miles
        projected_monthly = projected_annual / 12
        
        return {
            'cost_per_mile': cost_per_mile,
            'annual_miles': annual_miles,
            'projected_annual_cost': round(projected_annual, 2),
            'projected_monthly_cost': round(projected_monthly, 2),
            'based_on_historical_data': cost_per_mile_data['total_miles'] > 0
        }
