// Driving Analytics Dashboard JavaScript

let currentTripActive = false;
let updateInterval = null;
let map = null;
let routeLayer = null;

// Initialize map
function initMap() {
    map = L.map('map').setView([37.7749, -122.4194], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    routeLayer = L.layerGroup().addTo(map);
}

// Start trip
async function startTrip() {
    try {
        const response = await fetch('/api/trip/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                notes: '',
                enable_can_polling: true
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            currentTripActive = true;
            document.getElementById('startTripBtn').style.display = 'none';
            document.getElementById('endTripBtn').style.display = 'block';
            document.getElementById('resetTripBtn').style.display = 'block';
            
            // Start updating
            startUpdating();
            
            alert('Trip started! CAN bus polling: ' + (data.can_polling ? 'enabled' : 'disabled'));
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error starting trip:', error);
        alert('Failed to start trip');
    }
}

// End trip
async function endTrip() {
    try {
        const response = await fetch('/api/trip/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fuel_cost_per_gallon: 3.50
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            currentTripActive = false;
            document.getElementById('startTripBtn').style.display = 'block';
            document.getElementById('endTripBtn').style.display = 'none';
            document.getElementById('resetTripBtn').style.display = 'none';
            
            stopUpdating();
            
            // Show summary
            const summary = data.summary;
            const score = data.driving_score;
            
            alert(
                `Trip Completed!\n\n` +
                `Distance: ${summary.distance_miles} miles\n` +
                `Duration: ${Math.floor(summary.duration_seconds / 3600)}h ${Math.floor((summary.duration_seconds % 3600) / 60)}m\n` +
                `Avg Speed: ${summary.avg_speed_mph} mph\n` +
                `Avg MPG: ${summary.avg_mpg}\n` +
                `Fuel Cost: $${summary.fuel_cost}\n\n` +
                `Driving Score: ${score.overall_score}/100\n` +
                `Acceleration: ${score.acceleration_score}\n` +
                `Braking: ${score.braking_score}\n` +
                `Cornering: ${score.cornering_score}`
            );
            
            // Refresh displays
            await updateCurrentTrip();
            await loadTripHistory();
            await loadEcoTips();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error ending trip:', error);
        alert('Failed to end trip');
    }
}

// Reset trip
async function resetTrip() {
    if (!confirm('Reset current trip? This will start a new trip.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/trip/reset', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            alert('Trip reset! New trip started.');
            await updateCurrentTrip();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error resetting trip:', error);
        alert('Failed to reset trip');
    }
}

// Update current trip data
async function updateCurrentTrip() {
    try {
        const response = await fetch('/api/trip/current');
        const data = await response.json();
        
        if (data.ok) {
            const trip = data.trip;
            
            // Update speed gauge
            document.getElementById('currentSpeed').textContent = 
                trip.active ? Math.round(trip.avg_speed_mph) : 0;
            
            // Update trip stats
            document.getElementById('tripDistance').textContent = 
                trip.distance_miles + ' mi';
            document.getElementById('tripDuration').textContent = 
                trip.duration_formatted || '00:00:00';
            document.getElementById('maxSpeed').textContent = 
                trip.max_speed_mph + ' mph';
            
            // Update fuel economy
            document.getElementById('instantMpg').textContent = 
                trip.instant_mpg > 0 ? trip.instant_mpg + ' MPG' : '-';
            document.getElementById('avgMpg').textContent = 
                trip.avg_mpg > 0 ? trip.avg_mpg + ' MPG' : '-';
            document.getElementById('fuelUsed').textContent = 
                trip.fuel_consumed_gallons + ' gal';
            document.getElementById('fuelCost').textContent = 
                '$' + (trip.fuel_consumed_gallons * 3.50).toFixed(2);
            
            currentTripActive = trip.active;
        }
    } catch (error) {
        console.error('Error updating trip:', error);
    }
}

// Load eco driving tips
async function loadEcoTips() {
    try {
        const response = await fetch('/api/tips/current');
        const data = await response.json();
        
        if (data.ok && data.tips) {
            const tipsList = document.getElementById('ecoTips');
            tipsList.innerHTML = '';
            
            data.tips.slice(0, 5).forEach(tip => {
                const li = document.createElement('li');
                li.textContent = tip;
                tipsList.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Error loading tips:', error);
    }
}

// Load trip history
async function loadTripHistory() {
    try {
        const response = await fetch('/api/trips?limit=10');
        const data = await response.json();
        
        if (data.ok && data.trips) {
            const historyDiv = document.getElementById('tripHistory');
            historyDiv.innerHTML = '';
            
            if (data.trips.length === 0) {
                historyDiv.innerHTML = '<p style="text-align: center; opacity: 0.7;">No trips yet</p>';
                return;
            }
            
            data.trips.forEach(trip => {
                const item = document.createElement('div');
                item.className = 'trip-item';
                item.onclick = () => loadTripDetails(trip.trip_id);
                
                const status = trip.status === 'active' ? 'status-active' : 'status-completed';
                
                item.innerHTML = `
                    <div>
                        <span class="status-indicator ${status}"></span>
                        <strong>${new Date(trip.start_time).toLocaleDateString()}</strong>
                    </div>
                    <div style="margin-top: 5px; font-size: 0.9rem;">
                        ${trip.distance_miles || 0} mi · 
                        ${trip.avg_mpg || 0} MPG · 
                        ${trip.status}
                    </div>
                `;
                
                historyDiv.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Error loading trip history:', error);
    }
}

// Load trip details
async function loadTripDetails(tripId) {
    try {
        const response = await fetch(`/api/trips/${tripId}`);
        const data = await response.json();
        
        if (data.ok) {
            const trip = data.trip;
            const score = data.driving_score;
            const route = data.route;
            
            let message = `Trip Details\n\n`;
            message += `Distance: ${trip.distance_miles} miles\n`;
            message += `Duration: ${Math.floor(trip.duration_seconds / 3600)}h ${Math.floor((trip.duration_seconds % 3600) / 60)}m\n`;
            message += `Avg Speed: ${trip.avg_speed_mph} mph\n`;
            message += `Max Speed: ${trip.max_speed_mph} mph\n`;
            message += `Avg MPG: ${trip.avg_mpg}\n`;
            message += `Fuel Cost: $${trip.fuel_cost}\n`;
            
            if (score) {
                message += `\nDriving Score: ${score.overall_score}/100\n`;
                message += `Acceleration: ${score.acceleration_score}\n`;
                message += `Braking: ${score.braking_score}\n`;
                message += `Cornering: ${score.cornering_score}\n`;
            }
            
            if (route) {
                message += `\nRoute available`;
            }
            
            alert(message);
            
            // Load route if available
            if (route) {
                await loadRoute(tripId);
            }
        }
    } catch (error) {
        console.error('Error loading trip details:', error);
    }
}

// Load route on map
async function loadRoute(tripId) {
    try {
        const response = await fetch(`/api/routes/${tripId}`);
        const data = await response.json();
        
        if (data.ok && data.points && data.points.length > 0) {
            routeLayer.clearLayers();
            
            const points = data.points
                .filter(p => p.latitude && p.longitude)
                .map(p => [p.latitude, p.longitude]);
            
            if (points.length > 0) {
                const polyline = L.polyline(points, {
                    color: '#4facfe',
                    weight: 4,
                    opacity: 0.8
                }).addTo(routeLayer);
                
                map.fitBounds(polyline.getBounds());
                
                // Add markers for start and end
                L.marker(points[0]).addTo(routeLayer)
                    .bindPopup('Start');
                L.marker(points[points.length - 1]).addTo(routeLayer)
                    .bindPopup('End');
            }
        }
    } catch (error) {
        console.error('Error loading route:', error);
    }
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        if (data.ok && data.statistics) {
            const stats = data.statistics;
            
            document.getElementById('totalMiles').textContent = 
                stats.total_miles + ' mi';
            document.getElementById('totalHours').textContent = 
                stats.total_hours + ' hrs';
            document.getElementById('totalTrips').textContent = 
                stats.completed_trips;
            document.getElementById('lifetimeMpg').textContent = 
                stats.lifetime_mpg + ' MPG';
            document.getElementById('avgScore').textContent = 
                stats.avg_driving_score + '/100';
            
            // Show modal
            document.getElementById('statsModal').classList.add('active');
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Start periodic updates
function startUpdating() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    
    updateInterval = setInterval(() => {
        if (currentTripActive) {
            updateCurrentTrip();
            loadEcoTips();
        }
    }, 2000);  // Update every 2 seconds
}

// Stop periodic updates
function stopUpdating() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    
    // Button handlers
    document.getElementById('startTripBtn').addEventListener('click', startTrip);
    document.getElementById('endTripBtn').addEventListener('click', endTrip);
    document.getElementById('resetTripBtn').addEventListener('click', resetTrip);
    document.getElementById('refreshBtn').addEventListener('click', () => {
        updateCurrentTrip();
        loadTripHistory();
        loadEcoTips();
    });
    document.getElementById('statsBtn').addEventListener('click', loadStatistics);
    
    // Modal close
    document.getElementById('closeModal').addEventListener('click', () => {
        document.getElementById('statsModal').classList.remove('active');
    });
    
    // Initial load
    updateCurrentTrip();
    loadTripHistory();
    loadEcoTips();
    
    // Check if there's an active trip
    fetch('/api/trip/current').then(r => r.json()).then(data => {
        if (data.ok && data.trip.active) {
            currentTripActive = true;
            document.getElementById('startTripBtn').style.display = 'none';
            document.getElementById('endTripBtn').style.display = 'block';
            document.getElementById('resetTripBtn').style.display = 'block';
            startUpdating();
        }
    });
});
