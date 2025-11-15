let currentCategory = 'all';
let refreshInterval = 5000;
let autoRefreshTimer = null;
let allServices = [];
let serviceHealth = {};

async function fetchJSON(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return null;
    }
}

async function postJSON(url, data = {}) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Post error:', error);
        return null;
    }
}

async function loadServices() {
    const data = await fetchJSON('/api/services/all');
    
    if (data && data.ok) {
        allServices = data.services;
        renderServices();
        await checkAllHealth();
    }
}

async function checkAllHealth() {
    const data = await fetchJSON('/api/health/all');
    
    if (data && data.ok) {
        const status = data.status;
        serviceHealth = status.services;
        
        document.getElementById('online-count').textContent = status.online;
        document.getElementById('offline-count').textContent = status.offline;
        
        const healthDot = document.getElementById('health-indicator');
        const healthText = document.getElementById('health-text');
        
        if (status.health_percentage >= 80) {
            healthDot.className = 'health-dot online';
            healthText.textContent = `System Healthy (${status.health_percentage}%)`;
        } else if (status.health_percentage >= 50) {
            healthDot.className = 'health-dot degraded';
            healthText.textContent = `Degraded (${status.health_percentage}%)`;
        } else {
            healthDot.className = 'health-dot offline';
            healthText.textContent = `Critical (${status.health_percentage}%)`;
        }
        
        renderServices();
    }
}

function renderServices() {
    const grid = document.getElementById('services-grid');
    
    let servicesToRender = allServices;
    if (currentCategory !== 'all') {
        servicesToRender = allServices.filter(s => s.category === currentCategory);
    }
    
    if (servicesToRender.length === 0) {
        grid.innerHTML = '<div class="empty-state">No services found</div>';
        return;
    }
    
    grid.innerHTML = servicesToRender.map(service => {
        const health = serviceHealth[service.id] || { online: false };
        const statusClass = health.online ? 'online' : 'offline';
        const statusIcon = health.online ? '🟢' : '🔴';
        
        return `
            <div class="service-card ${statusClass}" data-service="${service.id}">
                <div class="service-status">${statusIcon}</div>
                <div class="service-icon">${service.icon}</div>
                <h3 class="service-name">${service.name}</h3>
                <p class="service-description">${service.description}</p>
                <div class="service-footer">
                    <span class="service-port">:${service.port}</span>
                    ${health.online ? `<button class="open-btn" onclick="openService('${service.id}', ${service.port})">Open</button>` : '<span class="offline-label">Offline</span>'}
                </div>
            </div>
        `;
    }).join('');
}

function openService(serviceId, port) {
    window.open(`http://localhost:${port}`, '_blank');
}

async function updateWidgets() {
    const data = await fetchJSON('/api/widgets/data');
    
    if (data && data.ok) {
        const widgets = data.data;
        
        if (widgets.canbus) {
            document.getElementById('speed-value').textContent = `${widgets.canbus.speed_mph || 0} MPH`;
            document.getElementById('rpm-value').textContent = `${widgets.canbus.rpm || 0} RPM`;
            document.getElementById('fuel-value').textContent = `${widgets.canbus.fuel_level || 0}%`;
        }
        
        if (widgets.media) {
            const title = widgets.media.is_playing ? widgets.media.title : 'Not Playing';
            const artist = widgets.media.is_playing ? widgets.media.artist : '';
            document.getElementById('track-title').textContent = title;
            document.getElementById('track-artist').textContent = artist;
        }
        
        if (widgets.climate) {
            document.getElementById('inside-temp').textContent = `${widgets.climate.temperature_f || 72} °F`;
            document.getElementById('outside-temp').textContent = `${widgets.climate.outside_temp_f || 68} °F`;
        }
        
        if (widgets.tpms) {
            document.getElementById('fl-pressure').textContent = `${widgets.tpms.front_left || 0}`;
            document.getElementById('fr-pressure').textContent = `${widgets.tpms.front_right || 0}`;
            document.getElementById('rl-pressure').textContent = `${widgets.tpms.rear_left || 0}`;
            document.getElementById('rr-pressure').textContent = `${widgets.tpms.rear_right || 0}`;
        }
        
        if (widgets.wireless_charger) {
            const percent = widgets.wireless_charger.battery_percentage || 0;
            document.getElementById('battery-bar').style.width = `${percent}%`;
            document.getElementById('battery-percent').textContent = `${percent}%`;
        }
    }
}

async function updateAlerts() {
    const data = await fetchJSON('/api/alerts');
    
    if (data && data.ok) {
        const count = data.count;
        const badge = document.getElementById('alert-count');
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    }
}

async function loadAlerts() {
    const data = await fetchJSON('/api/alerts');
    const container = document.getElementById('alerts-list');
    
    if (data && data.ok) {
        if (data.alerts.length === 0) {
            container.innerHTML = '<div class="empty-state">No active alerts</div>';
        } else {
            container.innerHTML = data.alerts.map(alert => {
                const levelClass = alert.level === 'critical' ? 'alert-critical' : 
                                  alert.level === 'warning' ? 'alert-warning' : 'alert-info';
                
                return `
                    <div class="alert-item ${levelClass}">
                        <div class="alert-header">
                            <strong>${alert.service_id}</strong>
                            <span class="alert-time">${new Date(alert.created_at).toLocaleTimeString()}</span>
                        </div>
                        <div class="alert-message">${alert.message}</div>
                        <button class="btn sm" onclick="acknowledgeAlert(${alert.id})">Acknowledge</button>
                    </div>
                `;
            }).join('');
        }
    }
}

async function acknowledgeAlert(alertId) {
    await postJSON(`/api/alerts/${alertId}/acknowledge`);
    loadAlerts();
    updateAlerts();
}

function setupEventListeners() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentCategory = tab.dataset.category;
            renderServices();
        });
    });
    
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const body = document.body;
        body.classList.toggle('dark-theme');
        body.classList.toggle('light-theme');
        
        const isDark = body.classList.contains('dark-theme');
        document.getElementById('theme-toggle').querySelector('.icon').textContent = isDark ? '🌙' : '☀️';
    });
    
    document.getElementById('settings-btn').addEventListener('click', () => {
        document.getElementById('settings-modal').classList.remove('hidden');
        loadSettings();
    });
    
    document.getElementById('close-settings').addEventListener('click', () => {
        document.getElementById('settings-modal').classList.add('hidden');
    });
    
    document.getElementById('alerts-btn').addEventListener('click', () => {
        document.getElementById('alerts-modal').classList.remove('hidden');
        loadAlerts();
    });
    
    document.getElementById('close-alerts').addEventListener('click', () => {
        document.getElementById('alerts-modal').classList.add('hidden');
    });
    
    document.getElementById('view-alerts-btn').addEventListener('click', () => {
        document.getElementById('alerts-modal').classList.remove('hidden');
        loadAlerts();
    });
    
    document.getElementById('refresh-all-btn').addEventListener('click', async () => {
        const btn = document.getElementById('refresh-all-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="icon spinner">⟳</span> Refreshing...';
        
        await checkAllHealth();
        await updateWidgets();
        
        btn.disabled = false;
        btn.innerHTML = '<span class="icon">🔄</span> Refresh All';
    });
    
    document.getElementById('save-settings').addEventListener('click', saveSettings);
    
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-box')) {
            document.getElementById('search-results').classList.add('hidden');
        }
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

async function handleSearch() {
    const query = document.getElementById('search-input').value.trim();
    const resultsDiv = document.getElementById('search-results');
    
    if (query.length < 2) {
        resultsDiv.classList.add('hidden');
        return;
    }
    
    const data = await fetchJSON(`/api/search?q=${encodeURIComponent(query)}`);
    
    if (data && data.ok) {
        if (data.results.length === 0) {
            resultsDiv.innerHTML = '<div class="search-result-item">No results found</div>';
        } else {
            resultsDiv.innerHTML = data.results.map(service => `
                <div class="search-result-item" onclick="openService('${service.id}', ${service.port})">
                    <span class="icon">${service.icon}</span>
                    <div>
                        <div class="result-name">${service.name}</div>
                        <div class="result-desc">${service.description}</div>
                    </div>
                </div>
            `).join('');
        }
        resultsDiv.classList.remove('hidden');
    }
}

async function loadSettings() {
    const data = await fetchJSON('/api/preferences');
    
    if (data && data.ok) {
        const prefs = data.preferences;
        
        if (prefs.theme) {
            document.getElementById('theme-select').value = prefs.theme;
        }
        if (prefs.auto_refresh_interval) {
            document.getElementById('refresh-interval').value = prefs.auto_refresh_interval;
        }
        if (prefs.show_offline_services) {
            document.getElementById('show-offline').checked = prefs.show_offline_services === 'true';
        }
        if (prefs.enable_animations) {
            document.getElementById('enable-animations').checked = prefs.enable_animations === 'true';
        }
        if (prefs.temperature_unit) {
            document.getElementById('temp-unit').value = prefs.temperature_unit;
        }
    }
}

async function saveSettings() {
    const settings = {
        theme: document.getElementById('theme-select').value,
        auto_refresh_interval: document.getElementById('refresh-interval').value,
        show_offline_services: document.getElementById('show-offline').checked ? 'true' : 'false',
        enable_animations: document.getElementById('enable-animations').checked ? 'true' : 'false',
        temperature_unit: document.getElementById('temp-unit').value
    };
    
    const result = await postJSON('/api/preferences', settings);
    
    if (result && result.ok) {
        refreshInterval = parseInt(settings.auto_refresh_interval);
        startAutoRefresh();
        
        document.getElementById('settings-modal').classList.add('hidden');
    }
}

function updateUptime() {
    fetchJSON('/health').then(data => {
        if (data && data.ok) {
            const seconds = data.uptime_seconds;
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            
            let uptimeStr = '';
            if (hours > 0) {
                uptimeStr = `${hours}h ${minutes}m`;
            } else {
                uptimeStr = `${minutes}m`;
            }
            
            document.getElementById('uptime-display').textContent = uptimeStr;
        }
    });
}

function startAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
    }
    
    autoRefreshTimer = setInterval(() => {
        checkAllHealth();
        updateWidgets();
        updateAlerts();
        updateUptime();
    }, refreshInterval);
}

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    
    await loadServices();
    await updateWidgets();
    await updateAlerts();
    updateUptime();
    
    startAutoRefresh();
    
    setInterval(updateUptime, 60000);
});
