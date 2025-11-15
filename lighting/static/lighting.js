let socket;
let currentZones = {};

const API_BASE = '';

document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    loadZones();
    loadScenes();
    loadStats();
    setupEventListeners();
    setInterval(loadStats, 10000);
});

function initWebSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
    });
    
    socket.on('zones_status', (data) => {
        updateZonesDisplay(data);
    });
    
    socket.on('zone_update', (data) => {
        updateZonePreview(data.zone, data.color);
    });
    
    socket.on('brightness_update', (data) => {
        document.getElementById('globalBrightness').value = data.brightness;
        document.getElementById('brightnessValue').textContent = data.brightness + '%';
    });
    
    socket.on('scene_applied', (data) => {
        showNotification(`Scene applied: ${data.scene_name}`);
    });
    
    socket.on('music_mode_update', (data) => {
        updateMusicModeDisplay(data.mode);
    });
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    if (connected) {
        statusEl.textContent = '🟢 Connected';
        statusEl.style.color = '#4caf50';
    } else {
        statusEl.textContent = '🔴 Disconnected';
        statusEl.style.color = '#f44336';
    }
}

function setupEventListeners() {
    const brightnessSlider = document.getElementById('globalBrightness');
    brightnessSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        document.getElementById('brightnessValue').textContent = value + '%';
    });
    
    brightnessSlider.addEventListener('change', (e) => {
        setBrightness(parseInt(e.target.value));
    });
    
    const sensitivitySlider = document.getElementById('sensitivity');
    sensitivitySlider.addEventListener('input', (e) => {
        const value = e.target.value;
        document.getElementById('sensitivityValue').textContent = value + '%';
    });
    
    sensitivitySlider.addEventListener('change', (e) => {
        setSensitivity(parseInt(e.target.value));
    });
    
    document.querySelectorAll('input[name="musicMode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            setMusicMode(e.target.value);
        });
    });
}

async function loadZones() {
    try {
        const response = await fetch(`${API_BASE}/api/zones`);
        const data = await response.json();
        
        if (data.ok) {
            currentZones = data.status.zones;
            updateZonesDisplay(data.status);
            renderZoneControls(data.status.zones);
        }
    } catch (error) {
        console.error('Error loading zones:', error);
    }
}

function updateZonesDisplay(status) {
    if (status.zones) {
        Object.keys(status.zones).forEach(zoneName => {
            const zone = status.zones[zoneName];
            const color = zone.actual_color;
            updateZonePreview(zoneName, color);
        });
    }
}

function updateZonePreview(zoneName, color) {
    const previewEl = document.getElementById(`preview-${zoneName}`);
    if (previewEl && color) {
        previewEl.style.backgroundColor = `rgb(${color.r}, ${color.g}, ${color.b})`;
    }
}

function renderZoneControls(zones) {
    const container = document.getElementById('zoneControlsList');
    container.innerHTML = '';
    
    Object.keys(zones).forEach(zoneName => {
        const zone = zones[zoneName];
        const zoneControl = document.createElement('div');
        zoneControl.className = 'zone-control';
        zoneControl.innerHTML = `
            <div class="zone-control-header">
                <h4>${zone.name}</h4>
                <div class="zone-control-preview" id="control-preview-${zoneName}"></div>
            </div>
            <div class="zone-control-inputs">
                <input type="color" id="color-${zoneName}" class="color-picker" 
                       value="${rgbToHex(zone.color.r, zone.color.g, zone.color.b)}">
                <button onclick="applyZoneColor('${zoneName}')" class="btn-apply">Apply</button>
            </div>
        `;
        container.appendChild(zoneControl);
        
        const color = zone.actual_color;
        const previewEl = document.getElementById(`control-preview-${zoneName}`);
        if (previewEl) {
            previewEl.style.backgroundColor = `rgb(${color.r}, ${color.g}, ${color.b})`;
        }
    });
}

async function applyZoneColor(zoneName) {
    const colorInput = document.getElementById(`color-${zoneName}`);
    const hex = colorInput.value;
    const rgb = hexToRgb(hex);
    
    try {
        const response = await fetch(`${API_BASE}/api/zones/${zoneName}/color`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(rgb)
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Updated ${zoneName}`);
        }
    } catch (error) {
        console.error('Error setting zone color:', error);
    }
}

async function setBrightness(brightness) {
    try {
        const response = await fetch(`${API_BASE}/api/brightness`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({brightness})
        });
        
        const data = await response.json();
        if (data.ok) {
            document.getElementById('globalBrightness').value = brightness;
            document.getElementById('brightnessValue').textContent = brightness + '%';
        }
    } catch (error) {
        console.error('Error setting brightness:', error);
    }
}

async function setMusicMode(mode) {
    try {
        const response = await fetch(`${API_BASE}/api/music/mode`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mode})
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Music mode: ${mode}`);
            updateMusicStatus();
        }
    } catch (error) {
        console.error('Error setting music mode:', error);
    }
}

async function setSensitivity(sensitivity) {
    try {
        const response = await fetch(`${API_BASE}/api/music/sensitivity`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({sensitivity})
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Sensitivity: ${sensitivity}%`);
        }
    } catch (error) {
        console.error('Error setting sensitivity:', error);
    }
}

async function updateMusicStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/music/test-connection`);
        const data = await response.json();
        
        const statusEl = document.getElementById('musicStatus');
        if (data.ok && data.connected) {
            statusEl.textContent = '✅ Connected to Audio Visualizer';
            statusEl.style.color = '#4caf50';
        } else {
            statusEl.textContent = '⚠️ Audio Visualizer not available (using mock data)';
            statusEl.style.color = '#ff9800';
        }
    } catch (error) {
        console.error('Error checking music connection:', error);
    }
}

function updateMusicModeDisplay(mode) {
    document.querySelector(`input[name="musicMode"][value="${mode}"]`).checked = true;
}

async function loadScenes() {
    try {
        const response = await fetch(`${API_BASE}/api/scenes`);
        const data = await response.json();
        
        if (data.ok) {
            renderScenes(data.scenes);
        }
    } catch (error) {
        console.error('Error loading scenes:', error);
    }
}

function renderScenes(scenes) {
    const container = document.getElementById('scenesList');
    container.innerHTML = '';
    
    scenes.forEach(scene => {
        const sceneCard = document.createElement('div');
        sceneCard.className = 'scene-card';
        if (scene.is_builtin) {
            sceneCard.classList.add('builtin');
        }
        
        sceneCard.innerHTML = `
            <h4>${scene.scene_name} ${scene.is_favorite ? '⭐' : ''}</h4>
            <p class="scene-description">${scene.description || ''}</p>
            <div class="scene-preview">
                ${Object.entries(scene.zone_colors).slice(0, 4).map(([zone, color]) => 
                    `<div class="scene-color-dot" style="background: rgb(${color.r}, ${color.g}, ${color.b})"></div>`
                ).join('')}
            </div>
            <button onclick="applyScene('${scene.scene_name}')" class="btn-apply">Apply</button>
            ${!scene.is_builtin ? `<button onclick="deleteScene('${scene.scene_name}')" class="btn-delete">Delete</button>` : ''}
        `;
        container.appendChild(sceneCard);
    });
}

async function applyScene(sceneName) {
    try {
        const response = await fetch(`${API_BASE}/api/scenes/${sceneName}/apply`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Applied scene: ${sceneName}`);
            loadZones();
        }
    } catch (error) {
        console.error('Error applying scene:', error);
    }
}

async function deleteScene(sceneName) {
    if (!confirm(`Delete scene "${sceneName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/scenes/${sceneName}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Deleted scene: ${sceneName}`);
            loadScenes();
        }
    } catch (error) {
        console.error('Error deleting scene:', error);
    }
}

function showSaveSceneDialog() {
    document.getElementById('saveSceneDialog').style.display = 'flex';
}

function hideSaveSceneDialog() {
    document.getElementById('saveSceneDialog').style.display = 'none';
    document.getElementById('sceneName').value = '';
    document.getElementById('sceneDescription').value = '';
}

async function saveScene() {
    const name = document.getElementById('sceneName').value.trim();
    const description = document.getElementById('sceneDescription').value.trim();
    
    if (!name) {
        alert('Please enter a scene name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/scenes`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                scene_name: name,
                description: description
            })
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Saved scene: ${name}`);
            hideSaveSceneDialog();
            loadScenes();
        }
    } catch (error) {
        console.error('Error saving scene:', error);
    }
}

async function quickColor(color) {
    try {
        const response = await fetch(`${API_BASE}/api/quick/solid/${color}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Applied ${color}`);
            loadZones();
        }
    } catch (error) {
        console.error('Error applying quick color:', error);
    }
}

async function quickRainbow() {
    try {
        const response = await fetch(`${API_BASE}/api/quick/rainbow`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification('Applied rainbow gradient');
            loadZones();
        }
    } catch (error) {
        console.error('Error applying rainbow:', error);
    }
}

async function fadeIn() {
    try {
        const response = await fetch(`${API_BASE}/api/control/fade-in`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification('Fading in...');
        }
    } catch (error) {
        console.error('Error fading in:', error);
    }
}

async function fadeOut() {
    try {
        const response = await fetch(`${API_BASE}/api/control/fade-out`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification('Fading out...');
        }
    } catch (error) {
        console.error('Error fading out:', error);
    }
}

async function turnOffAll() {
    if (!confirm('Turn off all zones?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/control/off`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification('All zones turned off');
            loadZones();
        }
    } catch (error) {
        console.error('Error turning off:', error);
    }
}

async function autoDim() {
    try {
        const response = await fetch(`${API_BASE}/api/control/auto-dim`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.ok) {
            showNotification(`Auto-dim: ${data.brightness}%`);
        }
    } catch (error) {
        console.error('Error applying auto-dim:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        
        if (data.ok) {
            renderStats(data);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function renderStats(stats) {
    const container = document.getElementById('statsDisplay');
    container.innerHTML = `
        <div class="stat-item">
            <span class="stat-label">Total Zones:</span>
            <span class="stat-value">${stats.led_controller.total_zones}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Active Zones:</span>
            <span class="stat-value">${stats.led_controller.enabled_zones}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Total LEDs:</span>
            <span class="stat-value">${stats.led_controller.total_leds}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Power Draw:</span>
            <span class="stat-value">${stats.led_controller.power_draw_watts}W</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Total Scenes:</span>
            <span class="stat-value">${stats.scene_manager.total_scenes}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Music Mode:</span>
            <span class="stat-value">${stats.music_reactive.mode}</span>
        </div>
    `;
}

function refreshScenes() {
    loadScenes();
    showNotification('Scenes refreshed');
}

function showNotification(message) {
    console.log('Notification:', message);
}

function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(x => {
        const hex = x.toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    }).join('');
}

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : {r: 0, g: 0, b: 0};
}
