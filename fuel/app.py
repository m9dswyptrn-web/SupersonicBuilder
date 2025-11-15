#!/usr/bin/env python3
"""
Fuel Economy Optimizer
Real-time MPG monitoring, driving tips, and fuel cost optimization
Port: 9900
"""

import os
import sys
import json
import uuid
import requests
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from threading import Thread, Lock
import time

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.fuel.database import FuelEconomyDatabase
from services.fuel.optimizer import FuelEconomyOptimizer
from services.fuel.tips import DrivingTipGenerator

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

TEMPLATE_DIR = Path(__file__).parent / 'templates'
STATIC_DIR = Path(__file__).parent / 'static'

TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.template_folder = str(TEMPLATE_DIR)
app.static_folder = str(STATIC_DIR)

db = FuelEconomyDatabase()
optimizer = FuelEconomyOptimizer()
tip_generator = DrivingTipGenerator()

CAN_BUS_URL = os.environ.get('CAN_BUS_URL', 'http://localhost:7000')

current_session = None
session_lock = Lock()
can_polling_active = False
poll_thread = None

session_data = {
    'start_time': None,
    'distance_miles': 0,
    'fuel_consumed_gallons': 0,
    'instant_mpg': 0,
    'trip_mpg': 0,
    'tank_avg_mpg': 0,
    'lifetime_avg_mpg': 0,
    'current_speed_mph': 0,
    'current_rpm': 0,
    'current_throttle': 0,
    'fuel_rate_gph': 0,
    'efficiency_score': 0,
    'active_tips': [],
    'fuel_cost_per_gallon': 3.50,
    'trip_fuel_cost': 0,
    'data_points': []
}


def poll_can_bus():
    """Poll CAN bus for real-time vehicle data."""
    global can_polling_active, session_data
    
    last_update_time = time.time()
    
    while can_polling_active:
        try:
            if not current_session:
                time.sleep(1)
                continue
            
            response = requests.get(f'{CAN_BUS_URL}/api/obd/data', timeout=2)
            
            if response.status_code == 200:
                can_data = response.json()
                
                if can_data.get('ok'):
                    data = can_data.get('data', {})
                    
                    current_time = time.time()
                    time_delta = current_time - last_update_time
                    last_update_time = current_time
                    
                    speed_mph = data.get('speed_mph', 0)
                    rpm = data.get('rpm', 0)
                    throttle = data.get('throttle_position', 0)
                    fuel_rate_gph = data.get('fuel_rate', 0)
                    
                    distance_delta = (speed_mph / 3600) * time_delta
                    session_data['distance_miles'] += distance_delta
                    
                    fuel_delta = (fuel_rate_gph / 3600) * time_delta
                    session_data['fuel_consumed_gallons'] += fuel_delta
                    
                    instant_mpg = optimizer.calculate_instant_mpg(speed_mph, fuel_rate_gph)
                    session_data['instant_mpg'] = instant_mpg
                    
                    trip_mpg = optimizer.calculate_trip_mpg(
                        session_data['distance_miles'],
                        session_data['fuel_consumed_gallons']
                    )
                    session_data['trip_mpg'] = trip_mpg
                    
                    session_data['current_speed_mph'] = speed_mph
                    session_data['current_rpm'] = rpm
                    session_data['current_throttle'] = throttle
                    session_data['fuel_rate_gph'] = fuel_rate_gph
                    
                    tank_avg = db.get_tank_average_mpg()
                    session_data['tank_avg_mpg'] = tank_avg
                    
                    lifetime_stats = db.get_lifetime_stats()
                    session_data['lifetime_avg_mpg'] = lifetime_stats.get('lifetime_avg_mpg', 0)
                    
                    vehicle_data = {
                        'speed_mph': speed_mph,
                        'rpm': rpm,
                        'throttle_percent': throttle,
                        'fuel_rate_gph': fuel_rate_gph,
                        'instant_mpg': instant_mpg,
                        'trip_mpg': trip_mpg,
                        'tank_avg_mpg': tank_avg
                    }
                    
                    session_data['data_points'].append(vehicle_data)
                    
                    if len(session_data['data_points']) > 1000:
                        session_data['data_points'] = session_data['data_points'][-1000:]
                    
                    db.log_data_point(current_session, vehicle_data)
                    
                    tips = tip_generator.analyze_driving(vehicle_data)
                    session_data['active_tips'] = tips
                    
                    for tip in tips:
                        if tip.get('severity') in ['warning', 'info']:
                            db.log_driving_tip(
                                current_session,
                                tip['type'],
                                tip['message'],
                                tip['severity'],
                                vehicle_data
                            )
                    
                    if len(session_data['data_points']) >= 10:
                        efficiency = optimizer.calculate_efficiency_score(session_data['data_points'])
                        session_data['efficiency_score'] = efficiency['total_score']
                    
                    session_data['trip_fuel_cost'] = (
                        session_data['fuel_consumed_gallons'] * 
                        session_data['fuel_cost_per_gallon']
                    )
        
        except Exception as e:
            print(f"CAN bus polling error: {e}")
        
        time.sleep(1)


@app.route('/')
def index():
    """Serve main dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('FUEL_PORT', 9900))
    
    return jsonify({
        'ok': True,
        'service': 'fuel_economy_optimizer',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'vehicle': '2014 Chevrolet Sonic LTZ (1.4L Turbo)',
        'features': {
            'real_time_mpg': True,
            'driving_tips': True,
            'efficiency_scoring': True,
            'fuel_cost_tracking': True,
            'eco_challenges': True,
            'can_bus_integration': True,
            'vehicle_specific_optimization': True
        },
        'active_session': current_session is not None,
        'can_polling': can_polling_active
    })


@app.route('/api/session/start', methods=['POST'])
def api_start_session():
    """Start new fuel economy session."""
    global current_session, can_polling_active, poll_thread, session_data
    
    try:
        with session_lock:
            if current_session:
                return jsonify({
                    'ok': False,
                    'error': 'Session already active',
                    'session_id': current_session
                }), 400
            
            data = request.json or {}
            
            session_id = f"fuel_session_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
            
            vehicle_info = {
                'year': data.get('vehicle_year', 2014),
                'make': data.get('vehicle_make', 'Chevrolet'),
                'model': data.get('vehicle_model', 'Sonic LTZ'),
                'engine': data.get('vehicle_engine', '1.4L Turbo')
            }
            
            db.create_session(session_id, vehicle_info)
            
            current_session = session_id
            
            session_data = {
                'start_time': datetime.now(),
                'distance_miles': 0,
                'fuel_consumed_gallons': 0,
                'instant_mpg': 0,
                'trip_mpg': 0,
                'tank_avg_mpg': db.get_tank_average_mpg(),
                'lifetime_avg_mpg': db.get_lifetime_stats().get('lifetime_avg_mpg', 0),
                'current_speed_mph': 0,
                'current_rpm': 0,
                'current_throttle': 0,
                'fuel_rate_gph': 0,
                'efficiency_score': 0,
                'active_tips': [],
                'fuel_cost_per_gallon': data.get('fuel_cost_per_gallon', 3.50),
                'trip_fuel_cost': 0,
                'data_points': []
            }
            
            if not can_polling_active:
                can_polling_active = True
                poll_thread = Thread(target=poll_can_bus, daemon=True)
                poll_thread.start()
            
            return jsonify({
                'ok': True,
                'session_id': session_id,
                'vehicle': vehicle_info,
                'can_polling': can_polling_active
            })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/session/stop', methods=['POST'])
def api_stop_session():
    """Stop current fuel economy session."""
    global current_session, can_polling_active
    
    try:
        with session_lock:
            if not current_session:
                return jsonify({
                    'ok': False,
                    'error': 'No active session'
                }), 400
            
            can_polling_active = False
            
            efficiency = optimizer.calculate_efficiency_score(session_data['data_points'])
            
            summary = {
                'distance_miles': session_data['distance_miles'],
                'fuel_consumed_gallons': session_data['fuel_consumed_gallons'],
                'avg_mpg': session_data['trip_mpg'],
                'instant_mpg_min': min([d.get('instant_mpg', 0) for d in session_data['data_points']], default=0),
                'instant_mpg_max': max([d.get('instant_mpg', 0) for d in session_data['data_points']], default=0),
                'avg_speed_mph': sum([d.get('speed_mph', 0) for d in session_data['data_points']]) / len(session_data['data_points']) if session_data['data_points'] else 0,
                'max_speed_mph': max([d.get('speed_mph', 0) for d in session_data['data_points']], default=0),
                'efficiency_score': efficiency['total_score'],
                'fuel_cost_per_gallon': session_data['fuel_cost_per_gallon'],
                'total_fuel_cost': session_data['trip_fuel_cost']
            }
            
            db.end_session(current_session, summary)
            
            epa_comparison = optimizer.compare_to_epa(summary['avg_mpg'])
            
            stopped_session = current_session
            current_session = None
            
            return jsonify({
                'ok': True,
                'session_id': stopped_session,
                'summary': summary,
                'efficiency': efficiency,
                'epa_comparison': epa_comparison
            })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/session/current')
def api_current_session():
    """Get current session data."""
    try:
        if not current_session:
            return jsonify({
                'ok': True,
                'session': None
            })
        
        efficiency = {'total_score': session_data['efficiency_score']}
        if len(session_data['data_points']) >= 10:
            efficiency = optimizer.calculate_efficiency_score(session_data['data_points'])
        
        epa_comparison = optimizer.compare_to_epa(session_data['trip_mpg'])
        
        cost_per_mile = optimizer.calculate_cost_per_mile(
            session_data['distance_miles'],
            session_data['fuel_consumed_gallons'],
            session_data['fuel_cost_per_gallon']
        )
        
        return jsonify({
            'ok': True,
            'session': {
                'session_id': current_session,
                'start_time': session_data['start_time'].isoformat() if session_data['start_time'] else None,
                'distance_miles': round(session_data['distance_miles'], 2),
                'fuel_consumed_gallons': round(session_data['fuel_consumed_gallons'], 3),
                'instant_mpg': round(session_data['instant_mpg'], 1),
                'trip_mpg': round(session_data['trip_mpg'], 1),
                'tank_avg_mpg': round(session_data['tank_avg_mpg'], 1),
                'lifetime_avg_mpg': round(session_data['lifetime_avg_mpg'], 1),
                'current_speed_mph': round(session_data['current_speed_mph'], 1),
                'current_rpm': session_data['current_rpm'],
                'current_throttle': round(session_data['current_throttle'], 1),
                'fuel_rate_gph': round(session_data['fuel_rate_gph'], 3),
                'efficiency_score': efficiency,
                'active_tips': session_data['active_tips'],
                'trip_fuel_cost': round(session_data['trip_fuel_cost'], 2),
                'cost_per_mile': cost_per_mile,
                'epa_comparison': epa_comparison
            }
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/fuel/price', methods=['POST'])
def api_update_fuel_price():
    """Update fuel price per gallon."""
    try:
        data = request.json or {}
        price = float(data.get('price_per_gallon', 3.50))
        
        session_data['fuel_cost_per_gallon'] = price
        
        return jsonify({
            'ok': True,
            'price_per_gallon': price
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/fuel/tank/add', methods=['POST'])
def api_add_fuel_tank():
    """Add fuel tank fill-up record."""
    try:
        data = request.json or {}
        
        tank_data = {
            'fill_date': data.get('fill_date', datetime.now().isoformat()),
            'odometer_reading': float(data.get('odometer_reading', 0)),
            'gallons_filled': float(data.get('gallons_filled', 0)),
            'cost_per_gallon': float(data.get('cost_per_gallon', 3.50)),
            'total_cost': float(data.get('total_cost', 0)),
            'miles_driven': float(data.get('miles_driven', 0)),
            'calculated_mpg': float(data.get('calculated_mpg', 0)),
            'is_full_tank': data.get('is_full_tank', True),
            'location': data.get('location', ''),
            'notes': data.get('notes', '')
        }
        
        if tank_data['miles_driven'] > 0 and tank_data['gallons_filled'] > 0:
            tank_data['calculated_mpg'] = tank_data['miles_driven'] / tank_data['gallons_filled']
        
        if tank_data['gallons_filled'] > 0 and tank_data['cost_per_gallon'] > 0:
            tank_data['total_cost'] = tank_data['gallons_filled'] * tank_data['cost_per_gallon']
        
        tank_id = db.add_fuel_tank(tank_data)
        
        return jsonify({
            'ok': True,
            'tank_id': tank_id,
            'calculated_mpg': tank_data['calculated_mpg']
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/stats/lifetime')
def api_lifetime_stats():
    """Get lifetime fuel economy statistics."""
    try:
        stats = db.get_lifetime_stats()
        
        return jsonify({
            'ok': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/cost/project', methods=['POST'])
def api_project_costs():
    """Project monthly/annual fuel costs."""
    try:
        data = request.json or {}
        
        avg_mpg = float(data.get('avg_mpg', session_data.get('trip_mpg', 30)))
        monthly_miles = float(data.get('monthly_miles', 1000))
        price_per_gallon = float(data.get('price_per_gallon', 3.50))
        
        projection = optimizer.project_monthly_cost(avg_mpg, monthly_miles, price_per_gallon)
        
        return jsonify({
            'ok': True,
            'projection': projection
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/eco/challenges')
def api_list_challenges():
    """List active eco challenges."""
    try:
        challenges = db.get_active_challenges()
        
        return jsonify({
            'ok': True,
            'challenges': challenges
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/eco/challenge/create', methods=['POST'])
def api_create_challenge():
    """Create new eco challenge."""
    try:
        data = request.json or {}
        
        challenge_data = {
            'challenge_type': data.get('challenge_type', 'daily'),
            'title': data.get('title', 'Daily MPG Challenge'),
            'description': data.get('description', ''),
            'target_mpg': float(data.get('target_mpg', 35.0)),
            'target_duration_days': int(data.get('target_duration_days', 1)),
            'start_date': data.get('start_date', datetime.now().date().isoformat()),
            'end_date': data.get('end_date', (datetime.now() + timedelta(days=1)).date().isoformat()),
            'reward_points': int(data.get('reward_points', 100))
        }
        
        challenge_id = db.create_eco_challenge(challenge_data)
        
        return jsonify({
            'ok': True,
            'challenge_id': challenge_id
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions')
def api_list_sessions():
    """List past fuel economy sessions."""
    try:
        limit = int(request.args.get('limit', 50))
        sessions = db.list_sessions(limit)
        
        return jsonify({
            'ok': True,
            'sessions': sessions
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions/<session_id>/tips')
def api_session_tips(session_id: str):
    """Get driving tips for a session."""
    try:
        limit = int(request.args.get('limit', 100))
        tips = db.get_session_tips(session_id, limit)
        
        return jsonify({
            'ok': True,
            'tips': tips,
            'count': len(tips)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/tips/sonic')
def api_sonic_tips():
    """Get Sonic LTZ specific tips."""
    try:
        tip = tip_generator.get_random_sonic_tip()
        
        return jsonify({
            'ok': True,
            'tip': tip
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/optimal/highway')
def api_optimal_highway():
    """Get optimal highway speed recommendation."""
    try:
        current_speed = float(request.args.get('speed', session_data.get('current_speed_mph', 60)))
        
        recommendation = optimizer.get_optimal_highway_speed(current_speed)
        
        return jsonify({
            'ok': True,
            'recommendation': recommendation
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/optimal/shift')
def api_optimal_shift():
    """Get gear shift recommendation."""
    try:
        rpm = int(request.args.get('rpm', session_data.get('current_rpm', 2000)))
        throttle = float(request.args.get('throttle', session_data.get('current_throttle', 30)))
        
        should_shift, message = optimizer.get_optimal_shift_point(rpm, throttle)
        
        return jsonify({
            'ok': True,
            'should_shift': should_shift,
            'message': message,
            'current_rpm': rpm,
            'optimal_range': f"{optimizer.SONIC_LTZ_SPECS['optimal_rpm_min']}-{optimizer.SONIC_LTZ_SPECS['optimal_rpm_max']} RPM"
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('FUEL_PORT', 9900))
    print(f"Starting Fuel Economy Optimizer on port {port}")
    print(f"Vehicle: 2014 Chevrolet Sonic LTZ (1.4L Turbo)")
    print(f"CAN Bus URL: {CAN_BUS_URL}")
    app.run(host='0.0.0.0', port=port, debug=False)
