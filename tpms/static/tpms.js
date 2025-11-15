// TPMS Monitor Frontend JavaScript

let pressureChart = null;
let updateInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    startMonitoring();
    loadCurrentReadings();
    loadAlerts();
    loadSeasonalSettings();
    
    // Start auto-update
    updateInterval = setInterval(() => {
        loadCurrentReadings();
        loadAlerts();
    }, 3000);
});

// Start monitoring
async function startMonitoring() {
    try {
        const response = await fetch('/api/monitoring/start', {
            method: 'POST'
        });
        
        if (response.ok) {
            document.getElementById('monitor-status').textContent = 'Monitoring Active';
            document.getElementById('monitor-indicator').style.background = '#4CAF50';
        }
    } catch (error) {
        console.error('Error starting monitoring:', error);
    }
}

// Load current tire readings
async function loadCurrentReadings() {
    try {
        const response = await fetch('/api/readings/current');
        const data = await response.json();
        
        if (data.ok) {
            updateTireDisplay(data.readings, data.thresholds);
            updateOverview(data.readings, data.thresholds);
        }
    } catch (error) {
        console.error('Error loading readings:', error);
    }
}

// Update tire display
function updateTireDisplay(readings, thresholds) {
    const positions = ['front_left', 'front_right', 'rear_left', 'rear_right'];
    
    positions.forEach(position => {
        const reading = readings[position];
        if (!reading) return;
        
        const element = document.getElementById(position.replace('_', '-'));
        if (!element) return;
        
        // Update pressure and temperature
        const pressureEl = element.querySelector('.tire-pressure');
        const tempEl = element.querySelector('.tire-temp');
        const statusEl = element.querySelector('.tire-status');
        
        pressureEl.textContent = `${reading.pressure_psi} PSI`;
        tempEl.textContent = `${reading.temperature_f}°F`;
        
        // Update status and color
        const pressureStatus = reading.pressure_status;
        const tempStatus = reading.temperature_status;
        
        let status = 'normal';
        let statusText = 'Normal';
        
        if (pressureStatus === 'low') {
            status = 'warning';
            statusText = 'Low Pressure';
        } else if (pressureStatus === 'high') {
            status = 'warning';
            statusText = 'High Pressure';
        }
        
        if (tempStatus === 'critical') {
            status = 'critical';
            statusText = 'Overheating!';
        } else if (tempStatus === 'warning' && status !== 'critical') {
            status = 'warning';
            statusText = 'High Temp';
        }
        
        // Update visual state
        element.className = `tire ${status}`;
        statusEl.textContent = statusText;
    });
    
    // Update spare tire
    const spare = readings.spare;
    if (spare) {
        const spareInfo = document.getElementById('spare-info');
        const spareStatus = document.getElementById('spare-status');
        
        spareInfo.textContent = `${spare.pressure_psi} PSI / ${spare.temperature_f}°F`;
        
        let spareStatusText = 'Normal';
        let spareClass = '';
        
        if (spare.pressure_status === 'low') {
            spareStatusText = 'Low Pressure';
            spareClass = 'warning';
        } else if (spare.pressure_status === 'high') {
            spareStatusText = 'High Pressure';
            spareClass = 'warning';
        }
        
        spareStatus.textContent = spareStatusText;
        spareStatus.className = `tire-status ${spareClass}`;
    }
}

// Update overview statistics
function updateOverview(readings, thresholds) {
    // Calculate averages
    const positions = ['front_left', 'front_right', 'rear_left', 'rear_right'];
    let totalPressure = 0;
    let totalTemp = 0;
    let count = 0;
    
    positions.forEach(position => {
        const reading = readings[position];
        if (reading) {
            totalPressure += reading.pressure_psi;
            totalTemp += reading.temperature_f;
            count++;
        }
    });
    
    if (count > 0) {
        const avgPressure = (totalPressure / count).toFixed(1);
        const avgTemp = (totalTemp / count).toFixed(1);
        
        document.getElementById('avg-pressure').textContent = `${avgPressure} PSI`;
        document.getElementById('avg-temp').textContent = `${avgTemp}°F`;
    }
    
    // Update recommended values
    document.getElementById('recommended-psi').textContent = `${thresholds.recommended_psi} PSI`;
    document.getElementById('pressure-range').textContent = `${thresholds.min_psi}-${thresholds.max_psi} PSI`;
}

// Load alerts
async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        
        if (data.ok) {
            displayAlerts(data.alerts);
            document.getElementById('alert-count').textContent = data.summary.total;
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// Display alerts
function displayAlerts(alerts) {
    const panel = document.getElementById('alerts-panel');
    
    if (alerts.length === 0) {
        panel.innerHTML = '<div class="empty-state">No active alerts</div>';
        return;
    }
    
    panel.innerHTML = alerts.map(alert => `
        <div class="alert ${alert.severity}">
            <div class="alert-content">
                <div class="alert-header">
                    <span class="alert-severity">${alert.severity}</span>
                    <span style="font-size: 0.85em; opacity: 0.8;">${formatTime(alert.created_at)}</span>
                </div>
                <div class="alert-message">${alert.message}</div>
                ${alert.pressure_psi ? `<div style="font-size: 0.85em; margin-top: 5px; opacity: 0.8;">Pressure: ${alert.pressure_psi} PSI</div>` : ''}
            </div>
            <button class="btn btn-small" onclick="dismissAlert('${alert.alert_id}')">Dismiss</button>
        </div>
    `).join('');
}

// Dismiss alert
async function dismissAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/dismiss`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadAlerts();
        }
    } catch (error) {
        console.error('Error dismissing alert:', error);
    }
}

// Dismiss all alerts
async function dismissAllAlerts() {
    if (!confirm('Dismiss all active alerts?')) return;
    
    try {
        const response = await fetch('/api/alerts/dismiss-all', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            loadAlerts();
        }
    } catch (error) {
        console.error('Error dismissing alerts:', error);
    }
}

// Check alerts
async function checkAlerts() {
    try {
        const response = await fetch('/api/alerts/check', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            loadAlerts();
            if (data.new_alerts.length > 0) {
                alert(`${data.new_alerts.length} new alert(s) detected`);
            } else {
                alert('All systems normal');
            }
        }
    } catch (error) {
        console.error('Error checking alerts:', error);
    }
}

// Load seasonal settings
async function loadSeasonalSettings() {
    try {
        const response = await fetch('/api/seasonal/settings');
        const data = await response.json();
        
        if (data.ok) {
            displaySeasonalSettings(data.settings, data.active);
            
            if (data.active) {
                document.getElementById('current-season').textContent = data.active.season.charAt(0).toUpperCase() + data.active.season.slice(1);
            }
        }
    } catch (error) {
        console.error('Error loading seasonal settings:', error);
    }
}

// Display seasonal settings
function displaySeasonalSettings(settings, active) {
    const container = document.getElementById('seasonal-settings');
    
    container.innerHTML = settings.map(setting => `
        <div class="season-card ${active && active.season === setting.season ? 'active' : ''}" 
             onclick="activateSeason('${setting.season}')">
            <div style="font-size: 1.5em; margin-bottom: 10px;">${getSeasonIcon(setting.season)}</div>
            <div style="font-weight: bold; margin-bottom: 5px;">${setting.season.charAt(0).toUpperCase() + setting.season.slice(1)}</div>
            <div style="font-size: 0.9em;">${setting.recommended_psi} PSI</div>
            <div style="font-size: 0.8em; opacity: 0.8; margin-top: 5px;">${setting.min_psi}-${setting.max_psi} PSI</div>
        </div>
    `).join('');
}

// Get season icon
function getSeasonIcon(season) {
    const icons = {
        'winter': '❄️',
        'spring': '🌸',
        'summer': '☀️',
        'fall': '🍂'
    };
    return icons[season] || '🌡️';
}

// Activate season
async function activateSeason(season) {
    try {
        const response = await fetch('/api/seasonal/activate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({season})
        });
        
        if (response.ok) {
            loadSeasonalSettings();
            loadCurrentReadings();
            alert(`${season.charAt(0).toUpperCase() + season.slice(1)} settings activated`);
        }
    } catch (error) {
        console.error('Error activating season:', error);
    }
}

// Calculate adjusted pressure
async function calculateAdjustedPressure() {
    const ambientTemp = parseFloat(document.getElementById('ambient-temp').value);
    
    try {
        const response = await fetch('/api/seasonal/adjust-pressure', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ambient_temp_f: ambientTemp})
        });
        
        const data = await response.json();
        
        if (data.ok) {
            document.getElementById('adjusted-pressure').textContent = `${data.recommended_pressure_psi} PSI`;
            
            const adjustment = data.adjustment_psi;
            const sign = adjustment >= 0 ? '+' : '';
            alert(`Recommended pressure: ${data.recommended_pressure_psi} PSI\n(${sign}${adjustment} PSI adjustment for ${ambientTemp}°F)`);
        }
    } catch (error) {
        console.error('Error calculating adjustment:', error);
    }
}

// Show tab
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Show selected tab
    document.querySelector(`[onclick="showTab('${tabName}')"]`)?.classList.add('active');
    document.getElementById(`${tabName}-content`)?.classList.add('active');
    
    // Load tab-specific data
    if (tabName === 'history') {
        loadPressureHistory();
    } else if (tabName === 'rotation') {
        loadRotationInfo();
    } else if (tabName === 'sensors') {
        loadSensors();
    }
}

// Load pressure history
async function loadPressureHistory() {
    try {
        const response = await fetch('/api/history/all?hours=24');
        const data = await response.json();
        
        if (data.ok) {
            displayPressureChart(data.history);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Display pressure chart
function displayPressureChart(history) {
    const ctx = document.getElementById('pressureChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (pressureChart) {
        pressureChart.destroy();
    }
    
    // Prepare datasets
    const datasets = [];
    const colors = {
        'front_left': '#FF6384',
        'front_right': '#36A2EB',
        'rear_left': '#FFCE56',
        'rear_right': '#4BC0C0'
    };
    
    for (const [position, readings] of Object.entries(history)) {
        if (position === 'spare' || readings.length === 0) continue;
        
        datasets.push({
            label: position.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
            data: readings.map(r => ({
                x: new Date(r.timestamp),
                y: r.pressure_psi
            })),
            borderColor: colors[position],
            backgroundColor: colors[position] + '33',
            tension: 0.4,
            fill: false
        });
    }
    
    pressureChart = new Chart(ctx, {
        type: 'line',
        data: {datasets},
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour',
                        displayFormats: {
                            hour: 'HH:mm'
                        }
                    },
                    ticks: {color: 'rgba(255,255,255,0.8)'},
                    grid: {color: 'rgba(255,255,255,0.1)'}
                },
                y: {
                    title: {
                        display: true,
                        text: 'Pressure (PSI)',
                        color: 'rgba(255,255,255,0.8)'
                    },
                    ticks: {color: 'rgba(255,255,255,0.8)'},
                    grid: {color: 'rgba(255,255,255,0.1)'}
                }
            },
            plugins: {
                legend: {
                    labels: {color: 'rgba(255,255,255,0.8)'}
                }
            }
        }
    });
}

// Load rotation info
async function loadRotationInfo() {
    try {
        const response = await fetch('/api/rotations/check-needed');
        const data = await response.json();
        
        if (data.ok && data.rotation_info) {
            document.getElementById('last-rotation').textContent = 
                data.rotation_info.last_rotation_mileage ? `${data.rotation_info.last_rotation_mileage} mi` : 'Never';
            document.getElementById('miles-since-rotation').textContent = 
                data.rotation_info.miles_since_rotation ? `${data.rotation_info.miles_since_rotation} mi` : '--';
        }
        
        loadRotationHistory();
    } catch (error) {
        console.error('Error loading rotation info:', error);
    }
}

// Load rotation history
async function loadRotationHistory() {
    try {
        const response = await fetch('/api/rotations?limit=5');
        const data = await response.json();
        
        if (data.ok) {
            const container = document.getElementById('rotation-history');
            
            if (data.rotations.length === 0) {
                container.innerHTML = '<div class="empty-state">No rotation history</div>';
                return;
            }
            
            container.innerHTML = `
                <h4 style="margin-bottom: 15px;">Recent Rotations</h4>
                ${data.rotations.map(rotation => `
                    <div class="info-item" style="margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <strong>${rotation.rotation_date}</strong>
                            <span>${rotation.odometer_reading} mi</span>
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.8;">Pattern: ${rotation.rotation_pattern}</div>
                        ${rotation.notes ? `<div style="font-size: 0.85em; opacity: 0.7; margin-top: 3px;">${rotation.notes}</div>` : ''}
                    </div>
                `).join('')}
            `;
        }
    } catch (error) {
        console.error('Error loading rotation history:', error);
    }
}

// Log rotation
async function logRotation() {
    const odometer = prompt('Enter current odometer reading (miles):');
    if (!odometer) return;
    
    const pattern = prompt('Rotation pattern (front_to_back, cross, etc.):', 'front_to_back');
    if (!pattern) return;
    
    try {
        const response = await fetch('/api/rotations/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                odometer_reading: parseInt(odometer),
                rotation_pattern: pattern,
                rotation_date: new Date().toISOString().split('T')[0]
            })
        });
        
        if (response.ok) {
            alert('Tire rotation logged successfully');
            loadRotationInfo();
        }
    } catch (error) {
        console.error('Error logging rotation:', error);
    }
}

// Load sensors
async function loadSensors() {
    try {
        const response = await fetch('/api/sensors');
        const data = await response.json();
        
        if (data.ok) {
            displaySensors(data.sensors);
        }
    } catch (error) {
        console.error('Error loading sensors:', error);
    }
}

// Display sensors
function displaySensors(sensors) {
    const container = document.getElementById('sensors-list');
    
    if (sensors.length === 0) {
        container.innerHTML = '<div class="empty-state">No sensors learned</div>';
        return;
    }
    
    container.innerHTML = sensors.map(sensor => `
        <div class="info-item" style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <strong>${sensor.tire_position.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</strong>
                <span style="font-size: 0.9em; opacity: 0.8;">${sensor.sensor_id}</span>
            </div>
            ${sensor.battery_voltage ? `<div style="font-size: 0.9em;">Battery: ${sensor.battery_voltage}V</div>` : ''}
            ${sensor.live_data ? `
                <div style="font-size: 0.85em; opacity: 0.8; margin-top: 5px;">
                    Signal: ${sensor.live_data.signal}% | Battery: ${sensor.live_data.battery}V
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Learn sensors
async function learnSensors() {
    const position = prompt('Tire position (front_left, front_right, rear_left, rear_right, spare):');
    if (!position) return;
    
    try {
        const response = await fetch('/api/sensors/learn', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({tire_position: position})
        });
        
        const data = await response.json();
        
        if (data.ok) {
            alert(`Sensor learned for ${position}: ${data.sensor.sensor_id}`);
            loadSensors();
        }
    } catch (error) {
        console.error('Error learning sensor:', error);
    }
}

// Reset sensors
async function resetSensors() {
    if (!confirm('Reset all TPMS sensors? This will require re-learning all sensors.')) return;
    
    try {
        const response = await fetch('/api/sensors/reset', {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('All sensors reset');
            loadSensors();
        }
    } catch (error) {
        console.error('Error resetting sensors:', error);
    }
}

// Test puncture simulation
async function testPuncture() {
    const position = prompt('Tire position to simulate puncture (front_left, front_right, rear_left, rear_right):', 'front_left');
    if (!position) return;
    
    try {
        const response = await fetch('/api/test/simulate-puncture', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({tire_position: position})
        });
        
        if (response.ok) {
            alert(`Puncture simulated for ${position}`);
        }
    } catch (error) {
        console.error('Error simulating puncture:', error);
    }
}

// Format time
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
