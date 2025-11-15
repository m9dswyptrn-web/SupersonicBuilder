let updateInterval = null;

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.ok) {
            updateUI(data);
        }
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

async function fetchIncidents() {
    try {
        const response = await fetch('/api/incidents?limit=20');
        const data = await response.json();
        
        if (data.ok && data.incidents.length > 0) {
            renderIncidents(data.incidents);
        }
    } catch (error) {
        console.error('Error fetching incidents:', error);
    }
}

async function fetchRecordings() {
    try {
        const response = await fetch('/api/recordings?limit=50');
        const data = await response.json();
        
        if (data.ok && data.recordings.length > 0) {
            renderRecordings(data.recordings);
        }
    } catch (error) {
        console.error('Error fetching recordings:', error);
    }
}

async function fetchCloudStatus() {
    try {
        const response = await fetch('/api/cloud/status');
        const data = await response.json();
        
        if (data.ok) {
            updateCloudUI(data);
        }
    } catch (error) {
        console.error('Error fetching cloud status:', error);
    }
}

function updateUI(data) {
    const isRecording = data.recorder.continuous_recording_active;
    const recordingStatus = document.getElementById('recordingStatus');
    
    if (isRecording) {
        recordingStatus.className = 'status-value status-recording';
        recordingStatus.textContent = '● Recording';
    } else {
        recordingStatus.className = 'status-value status-inactive';
        recordingStatus.textContent = '○ Stopped';
    }
    
    document.getElementById('startRecordingBtn').disabled = isRecording;
    document.getElementById('stopRecordingBtn').disabled = !isRecording;
    
    const storage = data.recorder.storage;
    if (storage && !storage.error) {
        document.getElementById('storageUsed').textContent = `${storage.usage_percent}%`;
        document.getElementById('storageUsedGB').textContent = `${storage.total_size_gb} GB`;
        document.getElementById('storageAvailableGB').textContent = `${storage.available_gb} GB`;
        
        const storageFill = document.getElementById('storageFill');
        storageFill.style.width = `${storage.usage_percent}%`;
        storageFill.textContent = `${storage.usage_percent}%`;
    }
    
    if (data.stats) {
        document.getElementById('totalIncidents').textContent = data.stats.total_incidents || 0;
        document.getElementById('cloudUploads').textContent = data.stats.cloud_uploads_completed || 0;
    }
    
    if (data.battery) {
        const batteryVoltage = document.getElementById('batteryVoltage');
        batteryVoltage.textContent = `${data.battery.voltage.toFixed(1)}V`;
        
        if (data.battery.voltage < 12.0) {
            batteryVoltage.style.color = '#ef4444';
        } else {
            batteryVoltage.style.color = '#10b981';
        }
        
        const batteryInfo = document.getElementById('batteryInfo');
        let batteryStatus = 'Normal';
        if (data.battery.voltage < 11.8) {
            batteryStatus = 'Critical';
        } else if (data.battery.voltage < 12.0) {
            batteryStatus = 'Low';
        }
        batteryInfo.textContent = `${data.battery.voltage.toFixed(1)}V (${batteryStatus})`;
    }
    
    if (data.parking_mode && data.parking_mode.active) {
        document.getElementById('parkingModeIndicator').classList.add('active');
        document.getElementById('parkingModeToggle').classList.add('active');
    } else {
        document.getElementById('parkingModeIndicator').classList.remove('active');
        document.getElementById('parkingModeToggle').classList.remove('active');
    }
}

function updateCloudUI(data) {
    const indicator = document.getElementById('cloudIndicator');
    const statusText = document.getElementById('cloudStatusText');
    
    if (data.status.wifi_connected) {
        indicator.classList.add('connected');
        statusText.textContent = 'WiFi Connected - Cloud Active';
    } else {
        indicator.classList.remove('connected');
        statusText.textContent = 'WiFi Disconnected';
    }
    
    document.getElementById('uploadQueue').textContent = data.status.queue_size || 0;
    
    if (data.status.cloud_storage) {
        document.getElementById('uploadsCompleted').textContent = 
            data.status.cloud_storage.total_uploads || 0;
    }
}

function renderIncidents(incidents) {
    const incidentList = document.getElementById('incidentList');
    
    if (incidents.length === 0) {
        incidentList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p>No incidents detected</p>
            </div>
        `;
        return;
    }
    
    incidentList.innerHTML = incidents.map(incident => `
        <div class="incident-item">
            <div class="incident-header">
                <div class="incident-type">${formatIncidentType(incident.incident_type)}</div>
                <span class="severity-badge severity-${incident.severity}">
                    ${incident.severity.toUpperCase()}
                </span>
            </div>
            <div class="incident-details">
                <div class="detail-item">
                    <div class="detail-label">G-Force</div>
                    <div class="detail-value">${incident.g_force_value?.toFixed(3) || 'N/A'}g</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Speed</div>
                    <div class="detail-value">${incident.speed_kmh ? incident.speed_kmh.toFixed(0) + ' km/h' : 'N/A'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Time</div>
                    <div class="detail-value">${formatTimestamp(incident.created_at)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Location</div>
                    <div class="detail-value">
                        ${incident.location_lat ? `${incident.location_lat.toFixed(5)}, ${incident.location_lng.toFixed(5)}` : 'N/A'}
                    </div>
                </div>
            </div>
            <div class="btn-group">
                ${incident.cloud_uploaded ? 
                    '<span style="color: #10b981; font-size: 0.85rem;">☁️ Uploaded to Cloud</span>' :
                    `<button class="btn btn-small" onclick="uploadToCloud('${incident.incident_id}')">☁️ Upload</button>`
                }
            </div>
        </div>
    `).join('');
}

function renderRecordings(recordings) {
    const recordingList = document.getElementById('recordingList');
    
    if (recordings.length === 0) {
        recordingList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📁</div>
                <p>No recordings yet</p>
            </div>
        `;
        return;
    }
    
    recordingList.innerHTML = recordings.map(rec => `
        <div class="recording-item">
            <div class="incident-header">
                <div>
                    <div class="incident-type">${rec.camera_layout.toUpperCase()} - ${rec.quality}</div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">
                        ${formatTimestamp(rec.created_at)}
                    </div>
                </div>
                ${rec.protected ? '<span class="protected-badge">🔒 PROTECTED</span>' : ''}
            </div>
            <div class="incident-details">
                <div class="detail-item">
                    <div class="detail-label">Type</div>
                    <div class="detail-value">${rec.recording_type}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Duration</div>
                    <div class="detail-value">${rec.duration_seconds ? rec.duration_seconds.toFixed(0) + 's' : 'N/A'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Size</div>
                    <div class="detail-value">${rec.file_size_mb ? rec.file_size_mb.toFixed(2) + ' MB' : 'N/A'}</div>
                </div>
            </div>
            <div class="btn-group">
                ${!rec.protected ? 
                    `<button class="btn btn-small btn-success" onclick="protectRecording('${rec.recording_id}')">🔒 Protect</button>` :
                    `<button class="btn btn-small" onclick="unprotectRecording('${rec.recording_id}')">🔓 Unprotect</button>`
                }
                ${!rec.protected ? 
                    `<button class="btn btn-small btn-danger" onclick="deleteRecording('${rec.recording_id}')">🗑️ Delete</button>` :
                    ''
                }
            </div>
        </div>
    `).join('');
}

function formatIncidentType(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit'
    });
}

async function startRecording() {
    const cameraLayout = document.getElementById('cameraLayout').value;
    const quality = document.getElementById('recordingQuality').value;
    
    try {
        const response = await fetch('/api/recording/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ camera_layout: cameraLayout, quality: quality })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('✅ Recording started', 'success');
            fetchStatus();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to start recording', 'error');
        console.error(error);
    }
}

async function stopRecording() {
    try {
        const response = await fetch('/api/recording/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('⏹️ Recording stopped', 'info');
            fetchStatus();
            fetchRecordings();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to stop recording', 'error');
        console.error(error);
    }
}

async function captureSnapshot() {
    try {
        const response = await fetch('/api/recording/snapshot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason: 'manual' })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('📸 Snapshot captured', 'success');
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to capture snapshot', 'error');
        console.error(error);
    }
}

async function simulateIncident() {
    try {
        const response = await fetch('/api/incidents/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                incident_type: 'hard_braking',
                g_force: 0.9
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('⚠️ Incident simulated and saved', 'warning');
            fetchIncidents();
            fetchRecordings();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to simulate incident', 'error');
        console.error(error);
    }
}

async function uploadToCloud(incidentId) {
    try {
        const response = await fetch('/api/cloud/queue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ incident_id: incidentId, priority: true })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('☁️ Queued for cloud upload', 'info');
            fetchCloudStatus();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to queue upload', 'error');
        console.error(error);
    }
}

async function cleanupStorage() {
    if (!confirm('Delete old unprotected recordings? Protected recordings will be kept.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/storage/cleanup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keep_count: 50 })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`🗑️ Deleted ${data.deleted_count} old recordings`, 'success');
            fetchStatus();
            fetchRecordings();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to cleanup storage', 'error');
        console.error(error);
    }
}

async function protectRecording(recordingId) {
    try {
        const response = await fetch(`/api/recordings/${recordingId}/protect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ protected: true })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('🔒 Recording protected', 'success');
            fetchRecordings();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to protect recording', 'error');
        console.error(error);
    }
}

async function unprotectRecording(recordingId) {
    try {
        const response = await fetch(`/api/recordings/${recordingId}/protect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ protected: false })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('🔓 Recording unprotected', 'info');
            fetchRecordings();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to unprotect recording', 'error');
        console.error(error);
    }
}

async function deleteRecording(recordingId) {
    if (!confirm('Delete this recording permanently?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/recordings/${recordingId}/delete`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('🗑️ Recording deleted', 'info');
            fetchRecordings();
            fetchStatus();
        } else {
            showNotification(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showNotification('❌ Failed to delete recording', 'error');
        console.error(error);
    }
}

async function connectWiFi() {
    try {
        const response = await fetch('/api/cloud/wifi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ connected: true })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('📡 WiFi connected - Auto-upload enabled', 'success');
            fetchCloudStatus();
        }
    } catch (error) {
        showNotification('❌ Failed to connect WiFi', 'error');
        console.error(error);
    }
}

async function disconnectWiFi() {
    try {
        const response = await fetch('/api/cloud/wifi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ connected: false })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('📡 WiFi disconnected', 'info');
            fetchCloudStatus();
        }
    } catch (error) {
        showNotification('❌ Failed to disconnect WiFi', 'error');
        console.error(error);
    }
}

async function toggleParkingMode(element) {
    const active = !element.classList.contains('active');
    
    try {
        const response = await fetch('/api/parking_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                active: active,
                sensitivity: 0.7,
                time_lapse: document.getElementById('timeLapseToggle').classList.contains('active')
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            element.classList.toggle('active');
            showNotification(active ? '🅿️ Parking mode enabled' : '🅿️ Parking mode disabled', 'info');
            fetchStatus();
        }
    } catch (error) {
        showNotification('❌ Failed to toggle parking mode', 'error');
        console.error(error);
    }
}

function toggleTimeLapse(element) {
    element.classList.toggle('active');
    const active = element.classList.contains('active');
    showNotification(active ? '⏱️ Time-lapse enabled' : '⏱️ Time-lapse disabled', 'info');
}

function toggleGSensor(element) {
    element.classList.toggle('active');
    const active = element.classList.contains('active');
    showNotification(active ? '⚡ G-Sensor enabled' : '⚡ G-Sensor disabled', 'info');
}

function toggleHonkSnapshot(element) {
    element.classList.toggle('active');
    const active = element.classList.contains('active');
    showNotification(active ? '📸 Auto-snapshot on honk enabled' : '📸 Auto-snapshot on honk disabled', 'info');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease;
        font-weight: 600;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    fetchIncidents();
    fetchRecordings();
    fetchCloudStatus();
    
    updateInterval = setInterval(() => {
        fetchStatus();
        fetchCloudStatus();
    }, 5000);
    
    setTimeout(() => {
        fetchIncidents();
        fetchRecordings();
    }, 2000);
    
    setInterval(() => {
        fetchIncidents();
        fetchRecordings();
    }, 15000);
});

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
