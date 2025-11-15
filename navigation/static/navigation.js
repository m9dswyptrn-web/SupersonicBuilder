// Navigation Overlay+ Frontend JavaScript

let updateInterval = null;
let currentSession = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    checkHealth();
    loadSavedLocations();
    setInterval(checkHealth, 30000);
});

// Check service health
async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        const systemStatus = document.getElementById('systemStatus');
        const navStatus = document.getElementById('navStatus');
        
        if (data.ok) {
            systemStatus.textContent = 'System Healthy';
            systemStatus.className = 'status-badge badge-active';
            
            if (data.active_navigation) {
                navStatus.textContent = 'Navigating';
                navStatus.className = 'status-badge badge-active';
                if (!updateInterval) {
                    startUpdates();
                }
            } else {
                navStatus.textContent = 'Not Navigating';
                navStatus.className = 'status-badge badge-inactive';
            }
        } else {
            systemStatus.textContent = 'System Error';
            systemStatus.className = 'status-badge badge-danger';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('systemStatus').textContent = 'Offline';
        document.getElementById('systemStatus').className = 'status-badge badge-danger';
    }
}

// Start navigation
async function startNavigation() {
    const destLat = parseFloat(document.getElementById('destLat').value);
    const destLng = parseFloat(document.getElementById('destLng').value);
    const strategy = document.getElementById('routeStrategy').value;
    
    if (!destLat || !destLng) {
        alert('Please enter destination coordinates');
        return;
    }
    
    try {
        const response = await fetch('/api/navigation/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                destination: {
                    lat: destLat,
                    lng: destLng,
                    address: 'Destination'
                },
                strategy: strategy
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            currentSession = data.session_id;
            alert('Navigation started!');
            displayRoute(data.route);
            displayTraffic(data.traffic);
            displayPOIs(data.nearby_pois);
            startUpdates();
        } else {
            alert('Failed to start navigation: ' + data.error);
        }
    } catch (error) {
        console.error('Start navigation error:', error);
        alert('Failed to start navigation');
    }
}

// Stop navigation
async function stopNavigation() {
    if (!currentSession) {
        alert('No active navigation');
        return;
    }
    
    try {
        const response = await fetch('/api/navigation/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            currentSession = null;
            alert('Navigation stopped');
            stopUpdates();
            resetDisplay();
        } else {
            alert('Failed to stop navigation: ' + data.error);
        }
    } catch (error) {
        console.error('Stop navigation error:', error);
        alert('Failed to stop navigation');
    }
}

// Start periodic updates
function startUpdates() {
    if (updateInterval) return;
    
    updateInterval = setInterval(async () => {
        await updateHUD();
        await updateSpeed();
        await checkVoiceAlerts();
    }, 2000);
}

// Stop periodic updates
function stopUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// Update HUD display
async function updateHUD() {
    try {
        const response = await fetch('/api/hud');
        const data = await response.json();
        
        if (data.ok) {
            const hud = data.hud;
            
            // Update next turn
            if (hud.next_turn.distance_feet < 500) {
                document.getElementById('turnDistance').textContent = 
                    hud.next_turn.distance_feet + ' ft';
            } else {
                document.getElementById('turnDistance').textContent = 
                    hud.next_turn.distance_miles.toFixed(1) + ' mi';
            }
            document.getElementById('turnInstruction').textContent = hud.next_turn.instruction;
            
            // Update ETA
            document.getElementById('eta').textContent = hud.eta.estimated_arrival;
            document.getElementById('remainingDistance').textContent = 
                hud.eta.remaining_distance_miles.toFixed(1) + ' mi';
            document.getElementById('trafficDelay').textContent = 
                hud.traffic.delay_minutes + ' min';
        }
    } catch (error) {
        console.error('HUD update error:', error);
    }
}

// Update speed display
async function updateSpeed() {
    try {
        const response = await fetch('/api/speed/current');
        const data = await response.json();
        
        if (data.ok) {
            const status = data.speed_status;
            
            document.getElementById('currentSpeed').textContent = 
                Math.round(status.current_speed_mph);
            document.getElementById('speedLimit').textContent = status.speed_limit_mph;
            
            // Update status badge
            const statusDiv = document.getElementById('speedStatus');
            statusDiv.textContent = status.message;
            statusDiv.className = 'speed-status status-' + status.status;
        }
    } catch (error) {
        console.error('Speed update error:', error);
    }
}

// Check for voice alerts
async function checkVoiceAlerts() {
    try {
        const response = await fetch('/api/voice/alerts');
        const data = await response.json();
        
        if (data.ok && data.alerts.length > 0) {
            data.alerts.forEach(alert => {
                // In a real implementation, this would use Web Speech API
                console.log('Voice Alert:', alert.message);
                // For now, show as notification
                showNotification(alert.type, alert.message);
            });
        }
    } catch (error) {
        console.error('Voice alerts error:', error);
    }
}

// Show notification
function showNotification(type, message) {
    // Create a simple notification div
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.background = 'rgba(244, 67, 54, 0.9)';
    notification.style.color = 'white';
    notification.style.padding = '15px 20px';
    notification.style.borderRadius = '8px';
    notification.style.zIndex = '9999';
    notification.textContent = '🔊 ' + message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Display route information
function displayRoute(route) {
    // Update lane guidance if available
    if (route.lane_guidance && route.lane_guidance.length > 0) {
        const laneGuidance = document.getElementById('laneGuidance');
        laneGuidance.style.display = 'block';
        
        const lanes = document.getElementById('lanes');
        lanes.innerHTML = '';
        
        const firstGuidance = route.lane_guidance[0];
        const recommendedLanes = firstGuidance.recommended_lanes || [];
        
        // Create 4 lanes
        for (let i = 1; i <= 4; i++) {
            const lane = document.createElement('div');
            lane.className = 'lane';
            
            let laneName = '';
            if (i === 1) laneName = 'Left';
            else if (i === 2) laneName = 'Center-Left';
            else if (i === 3) laneName = 'Center-Right';
            else laneName = 'Right';
            
            lane.textContent = laneName;
            
            if (recommendedLanes.some(l => l.includes(laneName.toLowerCase().replace('-', '_')))) {
                lane.className += ' lane-recommended';
            }
            
            lanes.appendChild(lane);
        }
    }
}

// Display traffic information
function displayTraffic(traffic) {
    const segmentsDiv = document.getElementById('trafficSegments');
    const incidentsDiv = document.getElementById('trafficIncidents');
    
    // Display traffic segments
    if (traffic.segments && traffic.segments.length > 0) {
        segmentsDiv.innerHTML = '<h3>Traffic Segments</h3>';
        
        traffic.segments.forEach(segment => {
            const segDiv = document.createElement('div');
            segDiv.className = 'traffic-segment traffic-' + segment.color;
            segDiv.innerHTML = `
                <div>
                    <strong>Mile ${segment.start_mile} - ${segment.end_mile}</strong><br>
                    ${segment.description}
                </div>
                <div>
                    ${segment.typical_speed_mph} mph<br>
                    <small>+${segment.estimated_delay_minutes} min delay</small>
                </div>
            `;
            segmentsDiv.appendChild(segDiv);
        });
    }
    
    // Display incidents
    if (traffic.incidents && traffic.incidents.length > 0) {
        incidentsDiv.innerHTML = '<h3>Traffic Incidents</h3>';
        
        traffic.incidents.forEach(incident => {
            const incDiv = document.createElement('div');
            incDiv.className = 'incident';
            incDiv.innerHTML = `
                <div>
                    <span class="incident-icon">⚠️</span>
                    <strong>${incident.type.replace('_', ' ').toUpperCase()}</strong>
                </div>
                <div style="margin-top: 5px;">${incident.description}</div>
                <div style="margin-top: 5px; font-size: 0.9em;">
                    ${incident.distance_miles} mi ahead • +${incident.delay_minutes} min delay
                </div>
            `;
            incidentsDiv.appendChild(incDiv);
        });
    }
}

// Display POIs
function displayPOIs(pois) {
    const poiList = document.getElementById('poiList');
    poiList.innerHTML = '';
    
    Object.keys(pois).forEach(category => {
        const categoryPOIs = pois[category];
        
        categoryPOIs.forEach(poi => {
            const poiDiv = document.createElement('div');
            poiDiv.className = 'poi-item';
            
            const amenities = (poi.amenities || []).join(', ');
            
            poiDiv.innerHTML = `
                <h4>${poi.name}</h4>
                <div>
                    <span class="poi-category">${category.replace('_', ' ')}</span>
                    <span class="rating">⭐ ${poi.rating}</span>
                </div>
                <div class="distance">${poi.distance_miles} mi away</div>
                <div style="font-size: 0.9em; margin-top: 5px; opacity: 0.8;">
                    ${poi.address}<br>
                    ${amenities}
                </div>
            `;
            
            poiList.appendChild(poiDiv);
        });
    });
}

// Search POI
async function searchPOI() {
    const category = prompt('Enter POI category (gas_station, restaurant, ev_charging, rest_area, parking):');
    
    if (!category) return;
    
    try {
        const response = await fetch(`/api/poi/search?category=${category}&limit=10`);
        const data = await response.json();
        
        if (data.ok) {
            displayPOIs(data.pois);
        } else {
            alert('Failed to search POI: ' + data.error);
        }
    } catch (error) {
        console.error('POI search error:', error);
        alert('Failed to search POI');
    }
}

// Filter POI by category
async function filterPOI(category) {
    try {
        const response = await fetch(`/api/poi/search?category=${category}&limit=10`);
        const data = await response.json();
        
        if (data.ok) {
            displayPOIs(data.pois);
        } else {
            alert('Failed to search POI: ' + data.error);
        }
    } catch (error) {
        console.error('POI filter error:', error);
        alert('Failed to filter POI');
    }
}

// Plan route
async function planRoute() {
    const destLat = parseFloat(document.getElementById('destLat').value);
    const destLng = parseFloat(document.getElementById('destLng').value);
    const strategy = document.getElementById('routeStrategy').value;
    
    if (!destLat || !destLng) {
        alert('Please enter destination coordinates');
        return;
    }
    
    try {
        const response = await fetch('/api/route/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                destination: {
                    lat: destLat,
                    lng: destLng
                },
                strategy: strategy
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            const route = data.route;
            alert(`Route planned!\n` +
                  `Distance: ${route.distance_miles} mi\n` +
                  `Duration: ${route.duration_minutes} min\n` +
                  `Fuel: ${route.estimated_fuel_gallons} gal ($${route.estimated_fuel_cost})`);
        } else {
            alert('Failed to plan route: ' + data.error);
        }
    } catch (error) {
        console.error('Route planning error:', error);
        alert('Failed to plan route');
    }
}

// Plan and start route
async function planAndStartRoute() {
    await planRoute();
    await startNavigation();
}

// Load saved locations
async function loadSavedLocations() {
    try {
        const response = await fetch('/api/locations/saved');
        const data = await response.json();
        
        if (data.ok) {
            const savedLocDiv = document.getElementById('savedLocations');
            
            if (data.locations.length === 0) {
                savedLocDiv.innerHTML = '<p style="opacity: 0.7;">No saved locations</p>';
                return;
            }
            
            savedLocDiv.innerHTML = '';
            
            data.locations.forEach(location => {
                const locDiv = document.createElement('div');
                locDiv.className = 'saved-location';
                
                let icon = '📍';
                if (location.label === 'home') icon = '🏠';
                else if (location.label === 'work') icon = '💼';
                else if (location.label === 'favorite') icon = '⭐';
                
                locDiv.innerHTML = `
                    <div>
                        <span class="location-icon">${icon}</span>
                        <strong>${location.name}</strong><br>
                        <small style="opacity: 0.8;">${location.address || 'No address'}</small>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="navigateToLocation('${location.location_id}')" 
                                style="padding: 8px 12px; font-size: 0.9em;">Go</button>
                        <button class="btn btn-danger" onclick="deleteLocation('${location.location_id}')" 
                                style="padding: 8px 12px; font-size: 0.9em; margin-left: 5px;">Delete</button>
                    </div>
                `;
                
                savedLocDiv.appendChild(locDiv);
            });
        }
    } catch (error) {
        console.error('Load saved locations error:', error);
    }
}

// Save current location
async function saveCurrentLocation() {
    const name = document.getElementById('locationName').value;
    const label = document.getElementById('locationLabel').value;
    
    if (!name) {
        alert('Please enter a name for this location');
        return;
    }
    
    // Use default coordinates (in real app, would use current GPS position)
    const latitude = 42.3314;
    const longitude = -83.0458;
    
    try {
        const response = await fetch('/api/locations/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                label: label,
                latitude: latitude,
                longitude: longitude,
                address: 'Current location'
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            alert('Location saved!');
            document.getElementById('locationName').value = '';
            loadSavedLocations();
        } else {
            alert('Failed to save location: ' + data.error);
        }
    } catch (error) {
        console.error('Save location error:', error);
        alert('Failed to save location');
    }
}

// Navigate to saved location
async function navigateToLocation(locationId) {
    try {
        const response = await fetch(`/api/locations/navigate/${locationId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            currentSession = data.session_id;
            alert('Navigation started to saved location!');
            startUpdates();
        } else {
            alert('Failed to navigate: ' + data.error);
        }
    } catch (error) {
        console.error('Navigate to location error:', error);
        alert('Failed to navigate');
    }
}

// Delete saved location
async function deleteLocation(locationId) {
    if (!confirm('Are you sure you want to delete this location?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/locations/${locationId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            alert('Location deleted');
            loadSavedLocations();
        } else {
            alert('Failed to delete location: ' + data.error);
        }
    } catch (error) {
        console.error('Delete location error:', error);
        alert('Failed to delete location');
    }
}

// Reset display
function resetDisplay() {
    document.getElementById('currentSpeed').textContent = '0';
    document.getElementById('speedLimit').textContent = '35';
    document.getElementById('speedStatus').textContent = 'Speed OK';
    document.getElementById('speedStatus').className = 'speed-status status-safe';
    document.getElementById('turnDistance').textContent = '--';
    document.getElementById('turnInstruction').textContent = 'Continue straight';
    document.getElementById('eta').textContent = '--';
    document.getElementById('remainingDistance').textContent = '--';
    document.getElementById('trafficDelay').textContent = '0 min';
    document.getElementById('trafficSegments').innerHTML = 
        '<p style="opacity: 0.7;">Start navigation to see traffic conditions</p>';
    document.getElementById('trafficIncidents').innerHTML = '';
    document.getElementById('laneGuidance').style.display = 'none';
}
