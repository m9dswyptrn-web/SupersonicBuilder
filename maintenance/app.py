#!/usr/bin/env python3
"""
Maintenance Reminder Service
Comprehensive vehicle maintenance tracking system
Port: 9800
"""

import os
import sys
import json
import requests
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from threading import Thread, Lock
import time

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.maintenance.database import MaintenanceDatabase
from services.maintenance.scheduler import MaintenanceScheduler
from services.maintenance.alerts import MaintenanceAlertSystem
from services.maintenance.costs import MaintenanceCostTracker

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

TEMPLATE_DIR = Path(__file__).parent / 'templates'
STATIC_DIR = Path(__file__).parent / 'static'
UPLOAD_DIR = ROOT / 'services' / 'maintenance' / 'uploads'

TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.template_folder = str(TEMPLATE_DIR)
app.static_folder = str(STATIC_DIR)

db = MaintenanceDatabase()
scheduler = MaintenanceScheduler(db)
alert_system = MaintenanceAlertSystem(db, scheduler)
cost_tracker = MaintenanceCostTracker(db)

CAN_BUS_URL = os.environ.get('CAN_BUS_URL', 'http://localhost:7000')
BOM_GENERATOR_URL = os.environ.get('BOM_GENERATOR_URL', 'http://localhost:8080')

can_polling_active = False
can_poll_lock = Lock()


def poll_can_bus_mileage():
    """Poll CAN bus for mileage updates."""
    global can_polling_active
    
    while can_polling_active:
        try:
            response = requests.get(f'{CAN_BUS_URL}/api/obd/data', timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ok'):
                    obd_data = data.get('data', {})
                    speed = obd_data.get('speed_mph', 0)
                    
                    current_mileage = db.get_current_mileage()
                    if current_mileage and speed > 0:
                        estimated_miles = speed / 3600
                        new_mileage = int(current_mileage + estimated_miles)
                        db.update_mileage(new_mileage, 'can_bus_auto')
        
        except Exception as e:
            print(f"CAN bus polling error: {e}")
        
        time.sleep(10)


@app.route('/')
def index():
    """Serve main dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('MAINTENANCE_PORT', 9800))
    
    current_mileage = db.get_current_mileage()
    active_alerts = len(db.get_active_alerts())
    
    return jsonify({
        'ok': True,
        'service': 'maintenance_reminder',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': {
            'maintenance_tracking': True,
            'mileage_tracking': True,
            'cost_analysis': True,
            'predictive_alerts': True,
            'can_bus_integration': True,
            'bom_integration': True
        },
        'current_mileage': current_mileage,
        'active_alerts': active_alerts,
        'can_polling': can_polling_active
    })


@app.route('/api/mileage/current')
def api_get_mileage():
    """Get current mileage."""
    try:
        mileage = db.get_current_mileage()
        
        return jsonify({
            'ok': True,
            'odometer_reading': mileage or 0
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/mileage/update', methods=['POST'])
def api_update_mileage():
    """Update current mileage."""
    try:
        data = request.json or {}
        odometer = int(data.get('odometer_reading', 0))
        
        if odometer <= 0:
            return jsonify({
                'ok': False,
                'error': 'Invalid odometer reading'
            }), 400
        
        success = db.update_mileage(odometer, 'manual')
        
        if not success:
            return jsonify({
                'ok': False,
                'error': 'Failed to update mileage'
            }), 500
        
        return jsonify({
            'ok': True,
            'odometer_reading': odometer
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/mileage/can-polling', methods=['POST'])
def api_toggle_can_polling():
    """Toggle CAN bus polling for automatic mileage updates."""
    try:
        global can_polling_active
        
        data = request.json or {}
        enable = data.get('enable', True)
        
        with can_poll_lock:
            if enable and not can_polling_active:
                can_polling_active = True
                Thread(target=poll_can_bus_mileage, daemon=True).start()
            elif not enable and can_polling_active:
                can_polling_active = False
        
        return jsonify({
            'ok': True,
            'can_polling_active': can_polling_active
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/schedules')
def api_get_schedules():
    """Get all maintenance schedules."""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        schedules = db.get_schedules(active_only=active_only)
        
        return jsonify({
            'ok': True,
            'schedules': schedules,
            'count': len(schedules)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/schedules/status')
def api_get_schedules_status():
    """Get status of all maintenance schedules."""
    try:
        status_list = scheduler.get_all_schedules_status()
        
        return jsonify({
            'ok': True,
            'schedules': status_list,
            'count': len(status_list)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/schedules/upcoming')
def api_get_upcoming_maintenance():
    """Get upcoming maintenance."""
    try:
        miles_ahead = int(request.args.get('miles_ahead', 5000))
        days_ahead = int(request.args.get('days_ahead', 90))
        
        upcoming = scheduler.get_upcoming_maintenance(miles_ahead, days_ahead)
        
        return jsonify({
            'ok': True,
            'upcoming': upcoming,
            'count': len(upcoming)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/schedules/add', methods=['POST'])
def api_add_schedule():
    """Add custom maintenance schedule."""
    try:
        data = request.json or {}
        
        name = data.get('name')
        schedule_type = data.get('type', 'custom')
        mile_interval = data.get('mile_interval')
        month_interval = data.get('month_interval')
        description = data.get('description')
        parts_needed = data.get('parts_needed')
        estimated_cost = float(data.get('estimated_cost', 0))
        
        if not name:
            return jsonify({
                'ok': False,
                'error': 'Schedule name is required'
            }), 400
        
        schedule_id = db.add_schedule(
            name=name,
            schedule_type=schedule_type,
            mile_interval=mile_interval,
            month_interval=month_interval,
            description=description,
            parts_needed=parts_needed,
            estimated_cost=estimated_cost
        )
        
        if not schedule_id:
            return jsonify({
                'ok': False,
                'error': 'Failed to add schedule'
            }), 500
        
        return jsonify({
            'ok': True,
            'schedule_id': schedule_id
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/records')
def api_get_records():
    """Get maintenance records."""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        records = db.get_maintenance_records(limit=limit, offset=offset)
        
        return jsonify({
            'ok': True,
            'records': records,
            'count': len(records)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/records/<record_id>')
def api_get_record(record_id: str):
    """Get single maintenance record."""
    try:
        record = db.get_record(record_id)
        
        if not record:
            return jsonify({
                'ok': False,
                'error': 'Record not found'
            }), 404
        
        return jsonify({
            'ok': True,
            'record': record
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/records/add', methods=['POST'])
def api_add_record():
    """Add maintenance record."""
    try:
        data = request.json or {}
        
        service_type = data.get('service_type')
        service_date = data.get('service_date')
        odometer = int(data.get('odometer_reading', 0))
        schedule_id = data.get('schedule_id')
        service_provider = data.get('service_provider')
        service_category = data.get('service_category', 'shop')
        labor_hours = float(data.get('labor_hours', 0))
        parts_used = data.get('parts_used')
        parts_cost = float(data.get('parts_cost', 0))
        labor_cost = float(data.get('labor_cost', 0))
        notes = data.get('notes')
        
        if not service_type or not service_date or odometer <= 0:
            return jsonify({
                'ok': False,
                'error': 'Service type, date, and odometer reading are required'
            }), 400
        
        record_id = db.add_maintenance_record(
            service_type=service_type,
            service_date=service_date,
            odometer=odometer,
            schedule_id=schedule_id,
            service_provider=service_provider,
            service_category=service_category,
            labor_hours=labor_hours,
            parts_used=parts_used,
            parts_cost=parts_cost,
            labor_cost=labor_cost,
            notes=notes
        )
        
        if not record_id:
            return jsonify({
                'ok': False,
                'error': 'Failed to add record'
            }), 500
        
        return jsonify({
            'ok': True,
            'record_id': record_id
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts')
def api_get_alerts():
    """Get active alerts."""
    try:
        alerts = db.get_active_alerts()
        
        return jsonify({
            'ok': True,
            'alerts': alerts,
            'count': len(alerts)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/generate', methods=['POST'])
def api_generate_alerts():
    """Generate alerts for upcoming maintenance."""
    try:
        alerts = alert_system.generate_alerts()
        
        return jsonify({
            'ok': True,
            'alerts_generated': len(alerts),
            'alerts': alerts
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/<alert_id>/dismiss', methods=['POST'])
def api_dismiss_alert(alert_id: str):
    """Dismiss an alert."""
    try:
        success = db.dismiss_alert(alert_id)
        
        if not success:
            return jsonify({
                'ok': False,
                'error': 'Failed to dismiss alert'
            }), 500
        
        return jsonify({
            'ok': True
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/summary')
def api_alerts_summary():
    """Get alert summary."""
    try:
        summary = alert_system.get_alert_summary()
        
        return jsonify({
            'ok': True,
            **summary
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/<alert_id>/send', methods=['POST'])
def api_send_reminder(alert_id: str):
    """Send reminder (simulated)."""
    try:
        alerts = db.get_active_alerts()
        alert = next((a for a in alerts if a['alert_id'] == alert_id), None)
        
        if not alert:
            return jsonify({
                'ok': False,
                'error': 'Alert not found'
            }), 404
        
        data = request.json or {}
        method = data.get('method', 'email')
        
        result = alert_system.send_reminder(alert, method)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/costs/summary')
def api_cost_summary():
    """Get cost summary."""
    try:
        period = request.args.get('period', 'all')
        summary = cost_tracker.get_cost_summary(period)
        
        return jsonify({
            'ok': True,
            'summary': summary,
            'period': period
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/costs/trends')
def api_cost_trends():
    """Get cost trends."""
    try:
        months = int(request.args.get('months', 12))
        trends = cost_tracker.get_cost_trends(months)
        
        return jsonify({
            'ok': True,
            **trends
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/costs/diy-savings')
def api_diy_savings():
    """Get DIY savings calculation."""
    try:
        savings = cost_tracker.calculate_diy_savings()
        
        return jsonify({
            'ok': True,
            'savings': savings
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/costs/comparison')
def api_cost_comparison():
    """Get estimated vs actual cost comparison."""
    try:
        comparison = cost_tracker.compare_estimated_vs_actual()
        
        return jsonify({
            'ok': True,
            **comparison
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/costs/by-type')
def api_costs_by_type():
    """Get costs by maintenance type."""
    try:
        costs = cost_tracker.get_cost_by_type()
        
        return jsonify({
            'ok': True,
            'costs_by_type': costs
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/costs/per-mile')
def api_cost_per_mile():
    """Get cost per mile."""
    try:
        data = cost_tracker.calculate_cost_per_mile()
        
        return jsonify({
            'ok': True,
            **data
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/costs/projection')
def api_cost_projection():
    """Get annual cost projection."""
    try:
        annual_miles = int(request.args.get('annual_miles', 12000))
        projection = cost_tracker.project_annual_costs(annual_miles)
        
        return jsonify({
            'ok': True,
            **projection
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/analysis/estimate-annual')
def api_estimate_annual():
    """Estimate annual maintenance costs."""
    try:
        annual_miles = int(request.args.get('annual_miles', 12000))
        estimate = scheduler.estimate_annual_costs(annual_miles)
        
        return jsonify({
            'ok': True,
            **estimate
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/analysis/forecast')
def api_maintenance_forecast():
    """Get maintenance forecast."""
    try:
        months = int(request.args.get('months', 6))
        forecast = alert_system.get_maintenance_forecast(months)
        
        return jsonify({
            'ok': True,
            'forecast': forecast
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/parts/recommendations')
def api_get_parts_recommendations():
    """Get parts recommendations."""
    try:
        schedule_id = request.args.get('schedule_id')
        
        if schedule_id:
            schedule_id = int(schedule_id)
        
        recommendations = db.get_parts_recommendations(schedule_id)
        
        return jsonify({
            'ok': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/parts/recommendations/add', methods=['POST'])
def api_add_parts_recommendation():
    """Add parts recommendation."""
    try:
        data = request.json or {}
        
        schedule_id = int(data.get('schedule_id', 0))
        part_name = data.get('part_name')
        part_number = data.get('part_number')
        part_type = data.get('part_type', 'OEM')
        estimated_price = data.get('estimated_price')
        supplier = data.get('supplier')
        supplier_url = data.get('supplier_url')
        notes = data.get('notes')
        
        if not schedule_id or not part_name:
            return jsonify({
                'ok': False,
                'error': 'Schedule ID and part name are required'
            }), 400
        
        rec_id = db.add_parts_recommendation(
            schedule_id=schedule_id,
            part_name=part_name,
            part_number=part_number,
            part_type=part_type,
            estimated_price=estimated_price,
            supplier=supplier,
            supplier_url=supplier_url,
            notes=notes
        )
        
        if not rec_id:
            return jsonify({
                'ok': False,
                'error': 'Failed to add recommendation'
            }), 500
        
        return jsonify({
            'ok': True,
            'recommendation_id': rec_id
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/integration/bom/generate', methods=['POST'])
def api_generate_bom():
    """Generate BOM for maintenance parts (integration with BOM service)."""
    try:
        data = request.json or {}
        schedule_id = data.get('schedule_id')
        
        if not schedule_id:
            return jsonify({
                'ok': False,
                'error': 'Schedule ID is required'
            }), 400
        
        parts = db.get_parts_recommendations(int(schedule_id))
        
        bom_data = {
            'parts': [
                {
                    'name': p['part_name'],
                    'part_number': p['part_number'],
                    'quantity': 1,
                    'estimated_price': p['estimated_price']
                }
                for p in parts
            ]
        }
        
        try:
            response = requests.post(f'{BOM_GENERATOR_URL}/api/bom/generate', json=bom_data, timeout=5)
            
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({
                    'ok': False,
                    'error': 'BOM service unavailable'
                }), 503
        except:
            return jsonify({
                'ok': False,
                'error': 'BOM service unavailable'
            }), 503
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('MAINTENANCE_PORT', 9800))
    print(f"🔧 Maintenance Reminder Service starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
