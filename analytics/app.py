#!/usr/bin/env python3
"""
Driving Analytics & Logs Service
Comprehensive trip tracking, driving score analysis, and route visualization
Port: 9200
"""

import os
import sys
import json
import uuid
import csv
import io
import requests
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from threading import Thread, Lock
import time

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.analytics.database import DrivingAnalyticsDatabase
from services.analytics.trip import TripComputer
from services.analytics.scoring import DrivingScoreCalculator
from services.analytics.routes import RouteTracker

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

TEMPLATE_DIR = Path(__file__).parent / 'templates'
STATIC_DIR = Path(__file__).parent / 'static'
EXPORT_DIR = ROOT / 'exports' / 'analytics'

TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

app.template_folder = str(TEMPLATE_DIR)
app.static_folder = str(STATIC_DIR)

# Initialize components
db = DrivingAnalyticsDatabase()
trip_computer = TripComputer(db)
score_calculator = DrivingScoreCalculator()
route_tracker = RouteTracker(db)

# CAN bus integration
CAN_BUS_URL = os.environ.get('CAN_BUS_URL', 'http://localhost:7000')
can_polling_active = False
can_poll_lock = Lock()


def poll_can_bus():
    """Poll CAN bus for vehicle data and update trip computer."""
    global can_polling_active
    
    while can_polling_active:
        try:
            if not trip_computer.current_trip_id:
                time.sleep(1)
                continue
            
            # Fetch data from CAN bus service
            response = requests.get(f'{CAN_BUS_URL}/api/obd/data', timeout=2)
            
            if response.status_code == 200:
                can_data = response.json()
                
                if can_data.get('ok'):
                    data = can_data.get('data', {})
                    
                    # Extract vehicle data
                    vehicle_data = {
                        'speed_mph': data.get('speed_mph', 0),
                        'rpm': data.get('rpm', 0),
                        'throttle_percent': data.get('throttle_position', 0),
                        'fuel_rate': data.get('fuel_rate', 0),
                        'latitude': None,  # Will be populated from GPS if available
                        'longitude': None,
                        'altitude_feet': None
                    }
                    
                    # Try to get GPS data
                    try:
                        gps_response = requests.get(f'{CAN_BUS_URL}/api/gps/location', timeout=1)
                        if gps_response.status_code == 200:
                            gps_data = gps_response.json()
                            if gps_data.get('ok'):
                                vehicle_data['latitude'] = gps_data.get('latitude')
                                vehicle_data['longitude'] = gps_data.get('longitude')
                                vehicle_data['altitude_feet'] = gps_data.get('altitude')
                    except:
                        pass
                    
                    # Update trip computer
                    trip_computer.update(vehicle_data)
                    
                    # Update route tracker if GPS available
                    if vehicle_data['latitude'] and vehicle_data['longitude']:
                        route_tracker.add_point(
                            latitude=vehicle_data['latitude'],
                            longitude=vehicle_data['longitude'],
                            altitude=vehicle_data['altitude_feet'],
                            speed=vehicle_data['speed_mph']
                        )
        
        except Exception as e:
            print(f"CAN bus polling error: {e}")
        
        time.sleep(1)  # Poll every second


@app.route('/')
def index():
    """Serve main dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('ANALYTICS_PORT', 9200))
    
    return jsonify({
        'ok': True,
        'service': 'driving_analytics',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': {
            'trip_tracking': True,
            'driving_scores': True,
            'route_tracking': True,
            'can_bus_integration': True,
            'export_gpx': True,
            'export_csv': True
        },
        'active_trip': trip_computer.current_trip_id is not None,
        'can_polling': can_polling_active
    })


# ============================================================================
# TRIP MANAGEMENT
# ============================================================================

@app.route('/api/trip/start', methods=['POST'])
def api_start_trip():
    """Start a new trip."""
    try:
        global can_polling_active
        
        data = request.json or {}
        notes = data.get('notes', '')
        enable_can = data.get('enable_can_polling', True)
        
        trip_id = trip_computer.start_trip(notes)
        
        if not trip_id:
            return jsonify({
                'ok': False,
                'error': 'Trip already active or failed to start'
            }), 400
        
        # Clear route tracker for new trip
        route_tracker.clear_current_route()
        
        # Start CAN bus polling if requested
        if enable_can and not can_polling_active:
            with can_poll_lock:
                can_polling_active = True
                Thread(target=poll_can_bus, daemon=True).start()
        
        return jsonify({
            'ok': True,
            'trip_id': trip_id,
            'can_polling': can_polling_active
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/trip/end', methods=['POST'])
def api_end_trip():
    """End current trip."""
    try:
        global can_polling_active
        
        data = request.json or {}
        fuel_cost_per_gallon = float(data.get('fuel_cost_per_gallon', 3.50))
        
        if not trip_computer.current_trip_id:
            return jsonify({
                'ok': False,
                'error': 'No active trip'
            }), 400
        
        trip_id = trip_computer.current_trip_id
        
        # Get trip data for scoring
        trip_data = db.get_trip_data_points(trip_id)
        
        # End the trip
        trip_summary = trip_computer.end_trip(fuel_cost_per_gallon)
        
        if not trip_summary:
            return jsonify({
                'ok': False,
                'error': 'Failed to end trip'
            }), 500
        
        # Calculate driving score
        driving_score = score_calculator.calculate_full_score(
            trip_data=trip_data,
            avg_mpg=trip_summary['avg_mpg'],
            avg_speed=trip_summary['avg_speed_mph'],
            max_speed=trip_summary['max_speed_mph']
        )
        
        # Save driving score
        db.save_driving_score(trip_id, driving_score)
        
        # Save route
        route_id = None
        if route_tracker.current_route_points:
            route_id = route_tracker.save_route(trip_id)
            route_tracker.clear_current_route()
        
        # Stop CAN bus polling
        with can_poll_lock:
            can_polling_active = False
        
        return jsonify({
            'ok': True,
            'trip_id': trip_id,
            'summary': trip_summary,
            'driving_score': driving_score,
            'route_id': route_id
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/trip/current')
def api_current_trip():
    """Get current trip statistics."""
    try:
        stats = trip_computer.get_current_stats()
        
        return jsonify({
            'ok': True,
            'trip': stats,
            'can_polling': can_polling_active
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/trip/reset', methods=['POST'])
def api_reset_trip():
    """Reset current trip."""
    try:
        success = trip_computer.reset_trip()
        
        if not success:
            return jsonify({
                'ok': False,
                'error': 'No active trip to reset'
            }), 400
        
        # Clear route
        route_tracker.clear_current_route()
        
        return jsonify({
            'ok': True,
            'message': 'Trip reset successfully',
            'new_trip_id': trip_computer.current_trip_id
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# TRIP HISTORY
# ============================================================================

@app.route('/api/trips')
def api_list_trips():
    """List all trips."""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        trips = db.list_trips(limit=limit, offset=offset)
        
        return jsonify({
            'ok': True,
            'trips': trips,
            'count': len(trips)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/trips/<trip_id>')
def api_get_trip(trip_id: str):
    """Get trip details."""
    try:
        trip = db.get_trip(trip_id)
        
        if not trip:
            return jsonify({
                'ok': False,
                'error': 'Trip not found'
            }), 404
        
        # Get driving score
        score = db.get_driving_score(trip_id)
        
        # Get route
        route = db.get_route(trip_id)
        
        return jsonify({
            'ok': True,
            'trip': trip,
            'driving_score': score,
            'route': route
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# FUEL ECONOMY
# ============================================================================

@app.route('/api/fuel/current')
def api_current_fuel():
    """Get current fuel economy data."""
    try:
        stats = trip_computer.get_current_stats()
        
        fuel_data = {
            'instant_mpg': stats['instant_mpg'],
            'trip_mpg': stats['avg_mpg'],
            'fuel_consumed': stats['fuel_consumed_gallons'],
            'fuel_cost': round(stats['fuel_consumed_gallons'] * 3.50, 2),
            'efficiency_rating': trip_computer.get_efficiency_rating(stats['avg_mpg'])
        }
        
        return jsonify({
            'ok': True,
            'fuel': fuel_data
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/fuel/calculate', methods=['POST'])
def api_calculate_fuel_cost():
    """Calculate fuel cost."""
    try:
        data = request.json or {}
        
        gallons = float(data.get('gallons', 0))
        cost_per_gallon = float(data.get('cost_per_gallon', 3.50))
        
        total_cost = trip_computer.calculate_fuel_cost(gallons, cost_per_gallon)
        
        return jsonify({
            'ok': True,
            'gallons': gallons,
            'cost_per_gallon': cost_per_gallon,
            'total_cost': round(total_cost, 2)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# DRIVING SCORES
# ============================================================================

@app.route('/api/scores/<trip_id>')
def api_get_score(trip_id: str):
    """Get driving score for a trip."""
    try:
        score = db.get_driving_score(trip_id)
        
        if not score:
            return jsonify({
                'ok': False,
                'error': 'Driving score not found'
            }), 404
        
        # Add ratings
        score['acceleration_rating'] = score_calculator.get_score_rating(score['acceleration_score'])
        score['braking_rating'] = score_calculator.get_score_rating(score['braking_score'])
        score['cornering_rating'] = score_calculator.get_score_rating(score['cornering_score'])
        score['overall_rating'] = score_calculator.get_score_rating(score['overall_score'])
        
        return jsonify({
            'ok': True,
            'score': score
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/api/routes/<trip_id>')
def api_get_route(trip_id: str):
    """Get route for a trip."""
    try:
        route = db.get_route(trip_id)
        
        if not route:
            return jsonify({
                'ok': False,
                'error': 'Route not found'
            }), 404
        
        # Get data points for route replay
        data_points = db.get_trip_data_points(trip_id, limit=5000)
        
        route_points = [
            {
                'latitude': dp['latitude'],
                'longitude': dp['longitude'],
                'timestamp': dp['timestamp'],
                'speed': dp['speed_mph']
            }
            for dp in data_points
            if dp.get('latitude') and dp.get('longitude')
        ]
        
        return jsonify({
            'ok': True,
            'route': route,
            'points': route_points
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/routes/<trip_id>/gpx')
def api_export_gpx(trip_id: str):
    """Export route as GPX file."""
    try:
        route = db.get_route(trip_id)
        
        if not route:
            return jsonify({
                'ok': False,
                'error': 'Route not found'
            }), 404
        
        gpx_data = route.get('gpx_data', '')
        
        if not gpx_data:
            return jsonify({
                'ok': False,
                'error': 'GPX data not available'
            }), 404
        
        # Create in-memory file
        gpx_file = io.BytesIO(gpx_data.encode('utf-8'))
        gpx_file.seek(0)
        
        return send_file(
            gpx_file,
            mimetype='application/gpx+xml',
            as_attachment=True,
            download_name=f'{trip_id}.gpx'
        )
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# STATISTICS
# ============================================================================

@app.route('/api/statistics')
def api_statistics():
    """Get overall driving statistics."""
    try:
        stats = db.get_statistics()
        
        # Add additional computed stats
        trips = db.list_trips(limit=1000)
        
        # Calculate lifetime MPG
        total_distance = sum(t.get('distance_miles', 0) for t in trips if t.get('status') == 'completed')
        total_fuel = sum(t.get('fuel_consumed_gallons', 0) for t in trips if t.get('status') == 'completed')
        lifetime_mpg = total_distance / total_fuel if total_fuel > 0 else 0
        
        stats['lifetime_mpg'] = round(lifetime_mpg, 2)
        stats['completed_trips'] = sum(1 for t in trips if t.get('status') == 'completed')
        
        return jsonify({
            'ok': True,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# EXPORT
# ============================================================================

@app.route('/api/export/trip/<trip_id>/csv')
def api_export_trip_csv(trip_id: str):
    """Export trip data as CSV."""
    try:
        trip = db.get_trip(trip_id)
        
        if not trip:
            return jsonify({
                'ok': False,
                'error': 'Trip not found'
            }), 404
        
        data_points = db.get_trip_data_points(trip_id, limit=10000)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'timestamp', 'speed_mph', 'rpm', 'throttle_percent',
            'fuel_rate', 'latitude', 'longitude', 'altitude_feet'
        ])
        
        writer.writeheader()
        writer.writerows(data_points)
        
        # Convert to bytes
        csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{trip_id}_data.csv'
        )
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/export/trip/<trip_id>/json')
def api_export_trip_json(trip_id: str):
    """Export complete trip data as JSON."""
    try:
        trip = db.get_trip(trip_id)
        
        if not trip:
            return jsonify({
                'ok': False,
                'error': 'Trip not found'
            }), 404
        
        data_points = db.get_trip_data_points(trip_id, limit=10000)
        score = db.get_driving_score(trip_id)
        route = db.get_route(trip_id)
        
        export_data = {
            'trip': trip,
            'data_points': data_points,
            'driving_score': score,
            'route': route,
            'exported_at': datetime.now().isoformat()
        }
        
        json_str = json.dumps(export_data, indent=2)
        json_bytes = io.BytesIO(json_str.encode('utf-8'))
        json_bytes.seek(0)
        
        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{trip_id}_complete.json'
        )
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# ECO DRIVING TIPS
# ============================================================================

@app.route('/api/tips/current')
def api_current_tips():
    """Get real-time eco-driving tips for current trip."""
    try:
        if not trip_computer.current_trip_id:
            return jsonify({
                'ok': True,
                'tips': ['Start a trip to receive eco-driving tips']
            })
        
        stats = trip_computer.get_current_stats()
        
        # Get last 100 data points
        trip_data = trip_computer.data_points[-100:] if trip_computer.data_points else []
        
        tips = score_calculator.generate_eco_tips(
            data_points=trip_data,
            avg_speed=stats['avg_speed_mph'],
            max_speed=stats['max_speed_mph']
        )
        
        return jsonify({
            'ok': True,
            'tips': tips[:5]  # Return top 5 tips
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


# ============================================================================
# MANUAL DATA INPUT (for testing without CAN bus)
# ============================================================================

@app.route('/api/data/inject', methods=['POST'])
def api_inject_data():
    """Manually inject vehicle data (for testing)."""
    try:
        if not trip_computer.current_trip_id:
            return jsonify({
                'ok': False,
                'error': 'No active trip'
            }), 400
        
        data = request.json or {}
        
        vehicle_data = {
            'speed_mph': float(data.get('speed_mph', 0)),
            'rpm': int(data.get('rpm', 0)),
            'throttle_percent': float(data.get('throttle_percent', 0)),
            'fuel_rate': float(data.get('fuel_rate', 0)),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'altitude_feet': data.get('altitude_feet')
        }
        
        success = trip_computer.update(vehicle_data)
        
        if vehicle_data['latitude'] and vehicle_data['longitude']:
            route_tracker.add_point(
                latitude=vehicle_data['latitude'],
                longitude=vehicle_data['longitude'],
                altitude=vehicle_data['altitude_feet'],
                speed=vehicle_data['speed_mph']
            )
        
        return jsonify({
            'ok': True,
            'message': 'Data injected successfully'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('ANALYTICS_PORT', 9200))
    print(f"🚗 Driving Analytics & Logs Service starting on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"🔌 CAN Bus URL: {CAN_BUS_URL}")
    app.run(host='0.0.0.0', port=port, debug=False)
