const API_BASE = '';

function loadStatus() {
    fetch(`${API_BASE}/api/status`)
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                const systemStatus = document.getElementById('systemStatus');
                const statusValue = systemStatus.querySelector('.value');
                
                if (data.system_armed) {
                    statusValue.textContent = 'ARMED';
                    statusValue.className = 'value armed';
                } else {
                    statusValue.textContent = 'DISARMED';
                    statusValue.className = 'value disarmed';
                }
                
                if (data.battery) {
                    document.getElementById('batteryVoltage').textContent = 
                        data.battery.voltage.toFixed(1) + 'V';
                }
                
                if (data.panic_mode) {
                    document.getElementById('systemStatus').style.background = 
                        'linear-gradient(135deg, #ff0000, #cc0000)';
                }
            }
        })
        .catch(err => console.error('Status load error:', err));
}

function loadAlerts() {
    fetch(`${API_BASE}/api/alerts?acknowledged=false`)
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                const container = document.getElementById('alertsContainer');
                const countElement = document.getElementById('activeAlertsCount');
                
                countElement.textContent = data.active.length;
                
                if (data.active.length === 0) {
                    container.innerHTML = '<p style="color: #888;">No active alerts</p>';
                } else {
                    container.innerHTML = data.active.map(alert => `
                        <div class="alert-item ${alert.severity}">
                            <h4>${alert.title}</h4>
                            <p>${alert.message}</p>
                            <p class="time">${formatTime(alert.timestamp)}</p>
                            <button class="btn btn-secondary" style="margin-top: 10px; padding: 5px 10px;" 
                                    onclick="acknowledgeAlert('${alert.alert_id}')">
                                Acknowledge
                            </button>
                        </div>
                    `).join('');
                }
            }
        })
        .catch(err => console.error('Alerts load error:', err));
}

function loadEvents() {
    fetch(`${API_BASE}/api/events?limit=20`)
        .then(res => res.json())
        .then(data => {
            if (data.ok && data.events.length > 0) {
                const container = document.getElementById('eventLog');
                container.innerHTML = data.events.map(event => `
                    <div class="event-item">
                        <span class="event-type">${event.event_type}</span>: ${event.description}
                        <div class="event-time">${formatTime(event.created_at)}</div>
                    </div>
                `).join('');
            }
        })
        .catch(err => console.error('Events load error:', err));
}

function loadGPSLocation() {
    fetch(`${API_BASE}/api/gps/location`)
        .then(res => res.json())
        .then(data => {
            if (data.ok && data.location) {
                const loc = data.location;
                document.getElementById('currentLocation').textContent = 
                    `${loc.latitude.toFixed(6)}, ${loc.longitude.toFixed(6)}`;
                document.getElementById('currentSpeed').textContent = 
                    loc.speed_kmh.toFixed(1);
                document.getElementById('currentHeading').textContent = 
                    loc.heading.toFixed(0);
            }
        })
        .catch(err => console.error('GPS load error:', err));
}

function loadGeofences() {
    fetch(`${API_BASE}/api/gps/geofences`)
        .then(res => res.json())
        .then(data => {
            if (data.ok && data.geofences.length > 0) {
                const container = document.getElementById('geofenceList');
                container.innerHTML = data.geofences.map(fence => `
                    <div class="geofence-item">
                        <div>
                            <span class="name">${fence.fence_name}</span>
                            <span class="badge ${fence.enabled ? 'active' : 'inactive'}">
                                ${fence.enabled ? 'ACTIVE' : 'INACTIVE'}
                            </span>
                        </div>
                        <div class="radius">${fence.radius_meters}m radius</div>
                    </div>
                `).join('');
            }
        })
        .catch(err => console.error('Geofences load error:', err));
}

function armSystem(armed) {
    fetch(`${API_BASE}/api/arm`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({armed: armed})
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showNotification(data.message, 'success');
            loadStatus();
        }
    })
    .catch(err => console.error('Arm error:', err));
}

function updateSensitivity(value) {
    document.getElementById('sensitivityValue').textContent = value;
    
    fetch(`${API_BASE}/api/motion/sensitivity`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({sensitivity: value / 100})
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showNotification(`Sensitivity updated to ${value}%`, 'success');
        }
    })
    .catch(err => console.error('Sensitivity error:', err));
}

function activatePanic() {
    if (confirm('⚠️ ACTIVATE PANIC MODE?\n\nThis will:\n- Sound horn\n- Flash lights\n- Record all cameras\n- Notify emergency services (simulated)\n\nContinue?')) {
        fetch(`${API_BASE}/api/panic`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({activate: true})
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                showNotification('🚨 PANIC MODE ACTIVATED!', 'error');
                loadStatus();
                loadAlerts();
            }
        })
        .catch(err => console.error('Panic error:', err));
    }
}

function toggleStolenMode(enabled) {
    const action = enabled ? 'ENABLE' : 'DISABLE';
    if (confirm(`${action} STOLEN VEHICLE MODE?\n\n${enabled ? 'This will activate high-frequency GPS tracking and notify law enforcement.' : 'This will return to normal tracking mode.'}`)) {
        fetch(`${API_BASE}/api/stolen_mode`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({enabled: enabled})
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                showNotification(data.message, enabled ? 'error' : 'success');
                loadStatus();
            }
        })
        .catch(err => console.error('Stolen mode error:', err));
    }
}

function testMotionDetection() {
    showNotification('Running motion detection...', 'info');
    
    fetch(`${API_BASE}/api/motion/detect`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({camera_position: 'all'})
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            const resultsDiv = document.getElementById('motionResults');
            if (data.count === 0) {
                resultsDiv.innerHTML = '<p style="color: #888;">No motion detected</p>';
            } else {
                resultsDiv.innerHTML = data.detections.map(d => `
                    <div style="color: ${d.person_detected ? '#ff4444' : '#00ff88'}; margin: 5px 0;">
                        ${d.camera_position}: ${d.person_detected ? '👤 PERSON' : '💨 Motion'} 
                        (${(d.confidence * 100).toFixed(0)}%)
                    </div>
                `).join('');
            }
            loadAlerts();
            loadEvents();
        }
    })
    .catch(err => console.error('Motion detection error:', err));
}

function testDoor(authorized) {
    fetch(`${API_BASE}/api/door`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            door_location: 'driver',
            open: true,
            authorized: authorized
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showNotification(`Door opened ${authorized ? '(authorized)' : '(UNAUTHORIZED!)'}`, 
                           authorized ? 'info' : 'error');
            loadAlerts();
            loadEvents();
        }
    })
    .catch(err => console.error('Door test error:', err));
}

function testIgnition(keyPresent) {
    fetch(`${API_BASE}/api/ignition`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            ignition_on: true,
            key_present: keyPresent
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showNotification(`Ignition activated ${keyPresent ? '(with key)' : '(NO KEY!)'}`, 
                           keyPresent ? 'info' : 'error');
            loadAlerts();
            loadEvents();
        }
    })
    .catch(err => console.error('Ignition test error:', err));
}

function testTowAway() {
    fetch(`${API_BASE}/api/tow`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            acceleration: 0.8,
            tilt_angle: 25.0
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showNotification('🚚 TOW-AWAY DETECTED!', 'error');
            loadAlerts();
            loadEvents();
        }
    })
    .catch(err => console.error('Tow test error:', err));
}

function testBatteryDisconnect() {
    fetch(`${API_BASE}/api/battery`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            voltage: 0,
            connected: false
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showNotification('🔋 BATTERY DISCONNECTED!', 'error');
            loadAlerts();
            loadEvents();
            
            setTimeout(() => {
                fetch(`${API_BASE}/api/battery`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        voltage: 12.6,
                        connected: true
                    })
                });
            }, 3000);
        }
    })
    .catch(err => console.error('Battery test error:', err));
}

function createGeofence() {
    const name = prompt('Geofence Name:', 'Home');
    if (!name) return;
    
    const radius = prompt('Radius (meters):', '1000');
    if (!radius) return;
    
    fetch(`${API_BASE}/api/gps/location`)
        .then(res => res.json())
        .then(data => {
            if (data.ok && data.location) {
                return fetch(`${API_BASE}/api/gps/geofences`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        fence_name: name,
                        center_lat: data.location.latitude,
                        center_lng: data.location.longitude,
                        radius_meters: parseFloat(radius),
                        alert_on_exit: true,
                        alert_on_entry: false
                    })
                });
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                showNotification(`Geofence "${name}" created`, 'success');
                loadGeofences();
            }
        })
        .catch(err => console.error('Geofence creation error:', err));
}

function acknowledgeAlert(alertId) {
    fetch(`${API_BASE}/api/alerts/${alertId}/acknowledge`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showNotification('Alert acknowledged', 'success');
            loadAlerts();
        }
    })
    .catch(err => console.error('Acknowledge error:', err));
}

function showNotification(message, type) {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    const colors = {
        success: '#44ff44',
        error: '#ff4444',
        warning: '#ffaa00',
        info: '#0088ff'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        z-index: 10000;
        font-weight: bold;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}
