let allApps = [];
let currentCategory = 'all';
let searchQuery = '';

async function loadStorageOverview() {
    try {
        const response = await fetch('/api/storage/overview');
        const data = await response.json();
        
        if (data.ok) {
            const storage = data.storage;
            document.getElementById('usedStorage').textContent = storage.used_storage_gb.toFixed(1);
            document.getElementById('freeStorage').textContent = storage.free_storage_gb.toFixed(1);
            document.getElementById('storageProgress').style.width = storage.usage_percent + '%';
            
            drawStorageChart(storage);
        }
    } catch (error) {
        console.error('Error loading storage overview:', error);
    }
}

async function loadApps() {
    try {
        const response = await fetch('/api/apps');
        const data = await response.json();
        
        if (data.ok) {
            allApps = data.apps;
            document.getElementById('totalApps').textContent = data.count;
            renderApps();
        }
    } catch (error) {
        console.error('Error loading apps:', error);
    }
}

async function loadRecommendations() {
    try {
        const response = await fetch('/api/storage/recommendations');
        const data = await response.json();
        
        if (data.ok) {
            const container = document.getElementById('recommendations');
            if (data.recommendations.length === 0) {
                container.innerHTML = '<div class="empty-state">No recommendations at this time</div>';
                return;
            }
            
            container.innerHTML = data.recommendations.map(rec => `
                <div class="recommendation ${rec.priority}">
                    <div class="recommendation-title">
                        ${rec.priority === 'critical' ? '🔴' : rec.priority === 'high' ? '🟠' : '🟡'} ${rec.title}
                    </div>
                    <div class="recommendation-desc">${rec.description}</div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

async function loadTopApps() {
    try {
        const response = await fetch('/api/storage/top-apps?limit=5');
        const data = await response.json();
        
        if (data.ok) {
            const container = document.getElementById('topApps');
            container.innerHTML = data.top_apps.map((app, index) => `
                <div class="top-app-item">
                    <div class="rank">${index + 1}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">${app.app_name}</div>
                        <div style="font-size: 12px; color: #888;">${formatSize(app.total_size_mb)}</div>
                    </div>
                    <div style="color: #667eea; font-weight: 600;">${app.percent_of_total}%</div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading top apps:', error);
    }
}

function renderApps() {
    const filteredApps = allApps.filter(app => {
        const matchesCategory = currentCategory === 'all' || app.category === currentCategory;
        const matchesSearch = app.app_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             app.package_name.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesCategory && matchesSearch;
    });
    
    const container = document.getElementById('appList');
    
    if (filteredApps.length === 0) {
        container.innerHTML = '<div class="empty-state">No apps found</div>';
        return;
    }
    
    container.innerHTML = filteredApps.map(app => `
        <div class="app-item" onclick="showAppDetails('${app.package_name}')">
            <div class="app-icon">${app.app_name.charAt(0).toUpperCase()}</div>
            <div class="app-info">
                <div class="app-name">${app.app_name}</div>
                <div class="app-package">${app.package_name}</div>
            </div>
            <div class="app-category">${app.category}</div>
            <div class="app-size">${formatSize(app.total_size_mb)}</div>
            <div class="actions" onclick="event.stopPropagation()">
                <button class="action-btn btn-primary" onclick="launchApp('${app.package_name}', '${app.app_name}')" title="Launch">▶️</button>
                <button class="action-btn btn-warning" onclick="clearCache('${app.package_name}', '${app.app_name}')" title="Clear Cache">🧹</button>
                <button class="action-btn btn-danger" onclick="forceStop('${app.package_name}', '${app.app_name}')" title="Force Stop">⏹️</button>
            </div>
        </div>
    `).join('');
}

async function showAppDetails(packageName) {
    try {
        const response = await fetch(`/api/apps/${packageName}`);
        const data = await response.json();
        
        if (data.ok) {
            const app = data.app;
            const permissions = data.permissions;
            const privacyConcerns = data.privacy_concerns;
            
            document.getElementById('modalAppName').textContent = app.app_name;
            
            const dangerousPerms = permissions.filter(p => p.is_dangerous);
            
            document.getElementById('modalContent').innerHTML = `
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #667eea; margin-bottom: 10px;">App Information</h3>
                    <div style="background: #f8f9ff; padding: 15px; border-radius: 8px;">
                        <div style="margin-bottom: 8px;"><strong>Package:</strong> ${app.package_name}</div>
                        <div style="margin-bottom: 8px;"><strong>Version:</strong> ${app.version_name} (${app.version_code})</div>
                        <div style="margin-bottom: 8px;"><strong>Category:</strong> ${app.category}</div>
                        <div style="margin-bottom: 8px;"><strong>Installed:</strong> ${new Date(app.installation_date).toLocaleDateString()}</div>
                        <div style="margin-bottom: 8px;"><strong>Last Used:</strong> ${new Date(app.last_used).toLocaleDateString()}</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #667eea; margin-bottom: 10px;">Storage Breakdown</h3>
                    <div style="background: #f8f9ff; padding: 15px; border-radius: 8px;">
                        <div style="margin-bottom: 8px;"><strong>App Size:</strong> ${formatSize(app.app_size_mb)}</div>
                        <div style="margin-bottom: 8px;"><strong>Data:</strong> ${formatSize(app.data_size_mb)}</div>
                        <div style="margin-bottom: 8px;"><strong>Cache:</strong> ${formatSize(app.cache_size_mb)}</div>
                        <div style="margin-bottom: 8px;"><strong>Total:</strong> <strong>${formatSize(app.total_size_mb)}</strong></div>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #667eea; margin-bottom: 10px;">
                        Permissions (${permissions.length})
                        ${dangerousPerms.length > 0 ? `<span class="badge badge-danger">${dangerousPerms.length} Dangerous</span>` : ''}
                    </h3>
                    <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; max-height: 200px; overflow-y: auto;">
                        ${permissions.map(p => `
                            <div style="margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                                <div style="font-size: 13px;">${p.permission_name}</div>
                                ${p.is_dangerous ? '<span class="badge badge-danger">Dangerous</span>' : ''}
                                ${p.privacy_concern_level === 'high' ? '<span class="badge badge-warning">Privacy</span>' : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${privacyConcerns.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #e74c3c; margin-bottom: 10px;">⚠️ Privacy Concerns</h3>
                        <div style="background: #ffebee; padding: 15px; border-radius: 8px;">
                            ${privacyConcerns.map(p => `
                                <div style="margin-bottom: 5px; font-size: 13px;">• ${p.permission_name}</div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <button class="action-btn btn-primary btn-large" onclick="launchApp('${app.package_name}', '${app.app_name}'); closeModal();">Launch App</button>
                    <button class="action-btn btn-warning btn-large" onclick="clearCache('${app.package_name}', '${app.app_name}'); closeModal();">Clear Cache</button>
                    <button class="action-btn btn-warning btn-large" onclick="clearData('${app.package_name}', '${app.app_name}'); closeModal();">Clear Data</button>
                    <button class="action-btn btn-danger btn-large" onclick="forceStop('${app.package_name}', '${app.app_name}'); closeModal();">Force Stop</button>
                    ${!app.is_system_app ? `
                        <button class="action-btn btn-danger btn-large" style="grid-column: 1 / -1;" onclick="uninstallApp('${app.package_name}', '${app.app_name}'); closeModal();">Uninstall App</button>
                    ` : ''}
                </div>
            `;
            
            document.getElementById('appModal').classList.add('active');
        }
    } catch (error) {
        console.error('Error loading app details:', error);
        alert('Failed to load app details');
    }
}

function closeModal() {
    document.getElementById('appModal').classList.remove('active');
}

async function launchApp(packageName, appName) {
    try {
        const response = await fetch(`/api/apps/${packageName}/launch`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok && data.result.success) {
            alert(`✅ ${appName} launched successfully!`);
        } else {
            alert(`❌ Failed to launch ${appName}`);
        }
    } catch (error) {
        console.error('Error launching app:', error);
        alert('Error launching app');
    }
}

async function clearCache(packageName, appName) {
    if (!confirm(`Clear cache for ${appName}?`)) return;
    
    try {
        const response = await fetch(`/api/apps/${packageName}/clear-cache`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok && data.result.success) {
            alert(`✅ Cleared ${data.result.space_freed_mb.toFixed(1)} MB from ${appName}`);
            loadApps();
            loadStorageOverview();
            loadTopApps();
        } else {
            alert(`❌ Failed to clear cache for ${appName}`);
        }
    } catch (error) {
        console.error('Error clearing cache:', error);
        alert('Error clearing cache');
    }
}

async function clearData(packageName, appName) {
    if (!confirm(`⚠️ Clear ALL data for ${appName}? This will reset the app to its initial state.`)) return;
    
    try {
        const response = await fetch(`/api/apps/${packageName}/clear-data`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok && data.result.success) {
            alert(`✅ Cleared ${data.result.space_freed_mb.toFixed(1)} MB from ${appName}\n${data.result.warning || ''}`);
            loadApps();
            loadStorageOverview();
            loadTopApps();
        } else {
            alert(`❌ ${data.result.message}`);
        }
    } catch (error) {
        console.error('Error clearing data:', error);
        alert('Error clearing data');
    }
}

async function forceStop(packageName, appName) {
    try {
        const response = await fetch(`/api/apps/${packageName}/force-stop`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok && data.result.success) {
            alert(`✅ Force stopped ${appName}`);
        } else {
            alert(`❌ Failed to force stop ${appName}`);
        }
    } catch (error) {
        console.error('Error force stopping app:', error);
        alert('Error force stopping app');
    }
}

async function uninstallApp(packageName, appName) {
    if (!confirm(`⚠️ Uninstall ${appName}? This cannot be undone.`)) return;
    
    try {
        const response = await fetch(`/api/apps/${packageName}/uninstall`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok && data.result.success) {
            alert(`✅ Uninstalled ${appName}, freed ${data.result.space_freed_mb.toFixed(1)} MB`);
            loadApps();
            loadStorageOverview();
            loadTopApps();
            loadRecommendations();
        } else {
            alert(`❌ ${data.result.message}`);
        }
    } catch (error) {
        console.error('Error uninstalling app:', error);
        alert('Error uninstalling app');
    }
}

async function clearAllCaches() {
    if (!confirm('Clear cache for all apps? This is safe and can free up significant space.')) return;
    
    try {
        const response = await fetch('/api/apps/batch/clear-cache', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok && data.result.success) {
            alert(`✅ ${data.result.message}\nFreed ${data.result.space_freed_mb.toFixed(1)} MB`);
            loadApps();
            loadStorageOverview();
            loadTopApps();
            loadRecommendations();
        } else {
            alert('❌ Failed to clear caches');
        }
    } catch (error) {
        console.error('Error clearing all caches:', error);
        alert('Error clearing caches');
    }
}

function formatSize(mb) {
    if (mb < 1) {
        return (mb * 1024).toFixed(0) + ' KB';
    } else if (mb < 1024) {
        return mb.toFixed(1) + ' MB';
    } else {
        return (mb / 1024).toFixed(2) + ' GB';
    }
}

function drawStorageChart(storage) {
    const canvas = document.getElementById('storageChart');
    const ctx = canvas.getContext('2d');
    
    canvas.width = canvas.offsetWidth * 2;
    canvas.height = 300 * 2;
    ctx.scale(2, 2);
    
    const centerX = canvas.width / 4;
    const centerY = 150;
    const radius = 100;
    
    const data = [
        { label: 'Apps', value: storage.apps_storage_gb, color: '#667eea' },
        { label: 'Photos', value: storage.photos_gb, color: '#f39c12' },
        { label: 'Videos', value: storage.videos_gb, color: '#e74c3c' },
        { label: 'Audio', value: storage.audio_gb, color: '#27ae60' },
        { label: 'System', value: storage.system_gb, color: '#95a5a6' },
        { label: 'Other', value: storage.other_gb, color: '#bdc3c7' }
    ];
    
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = -Math.PI / 2;
    
    data.forEach(item => {
        const sliceAngle = (item.value / total) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = item.color;
        ctx.fill();
        
        currentAngle += sliceAngle;
    });
    
    let legendY = 20;
    data.forEach(item => {
        ctx.fillStyle = item.color;
        ctx.fillRect(centerX + radius + 20, legendY, 15, 15);
        
        ctx.fillStyle = '#333';
        ctx.font = '12px "Segoe UI"';
        ctx.fillText(`${item.label}: ${item.value.toFixed(1)} GB`, centerX + radius + 40, legendY + 12);
        
        legendY += 25;
    });
}

document.getElementById('searchBox').addEventListener('input', (e) => {
    searchQuery = e.target.value;
    renderApps();
});

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentCategory = e.target.dataset.category;
        renderApps();
    });
});

document.getElementById('appModal').addEventListener('click', (e) => {
    if (e.target.id === 'appModal') {
        closeModal();
    }
});

loadStorageOverview();
loadApps();
loadRecommendations();
loadTopApps();

setInterval(() => {
    loadStorageOverview();
    loadTopApps();
}, 30000);
