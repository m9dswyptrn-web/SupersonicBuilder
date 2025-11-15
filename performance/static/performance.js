const socket = io();

let cpuChart, gpuChart, memChart, storageChart, tempChart, batteryChart;
let tempHistory = [];
const MAX_TEMP_HISTORY = 30;

socket.on('connect', () => {
    console.log('Connected to Performance Dashboard');
    document.getElementById('connectionStatus').style.background = '#10b981';
});

socket.on('disconnect', () => {
    console.log('Disconnected');
    document.getElementById('connectionStatus').style.background = '#ef4444';
});

socket.on('metrics_update', (data) => {
    updateMetrics(data);
});

socket.on('health_update', (data) => {
    updateHealth(data);
});

socket.on('alerts', (alerts) => {
    alerts.forEach(alert => showAlert(alert));
});

function createGauge(canvasId) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#667eea', 'rgba(255, 255, 255, 0.1)'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            rotation: -90,
            circumference: 180,
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

function updateGauge(chart, value) {
    chart.data.datasets[0].data = [value, 100 - value];
    
    const color = value > 90 ? '#dc2626' : value > 80 ? '#fb923c' : value > 60 ? '#fbbf24' : '#10b981';
    chart.data.datasets[0].backgroundColor[0] = color;
    
    chart.update('none');
}

cpuChart = createGauge('cpuGauge');
gpuChart = createGauge('gpuGauge');
memChart = createGauge('memGauge');
batteryChart = createGauge('batteryGauge');

const ctx = document.getElementById('storageChart').getContext('2d');
storageChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Apps', 'Music', 'Videos', 'Photos', 'System', 'Other'],
        datasets: [{
            data: [0, 0, 0, 0, 0, 0],
            backgroundColor: [
                '#667eea', '#764ba2', '#f093fb', '#4facfe', 
                '#43e97b', '#fa709a'
            ]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { color: '#fff' }
            }
        }
    }
});

const tempCtx = document.getElementById('tempChart').getContext('2d');
tempChart = new Chart(tempCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'SoC Temp',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4
            },
            {
                label: 'Battery Temp',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: '#fff' }
            }
        },
        scales: {
            x: {
                display: false
            },
            y: {
                ticks: { color: '#8b95a5' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            }
        }
    }
});

function updateMetrics(metrics) {
    updateGauge(cpuChart, metrics.cpu.total_usage);
    document.getElementById('cpuValue').textContent = metrics.cpu.total_usage + '%';
    document.getElementById('cpuFreq').textContent = metrics.cpu.frequency_ghz.toFixed(2) + ' GHz';
    updateStatusBadge('cpuStatus', metrics.cpu.status);
    
    const coreGrid = document.getElementById('coreGrid');
    coreGrid.innerHTML = '';
    metrics.cpu.core_usage.forEach((usage, index) => {
        coreGrid.innerHTML += `
            <div class="core-item">
                <div class="core-label">Core ${index}</div>
                <div class="core-value">${usage}%</div>
            </div>
        `;
    });
    
    updateGauge(gpuChart, metrics.gpu.usage_percent);
    document.getElementById('gpuValue').textContent = metrics.gpu.usage_percent + '%';
    document.getElementById('gpuFreq').textContent = Math.round(metrics.gpu.frequency_mhz) + ' MHz';
    document.getElementById('gpuTemp').textContent = metrics.gpu.temperature_c + '°C';
    document.getElementById('gpuFps').textContent = metrics.gpu.opengl_fps.toFixed(1);
    
    updateGauge(memChart, metrics.memory.usage_percent);
    document.getElementById('memValue').textContent = metrics.memory.usage_percent + '%';
    document.getElementById('memUsed').textContent = `${metrics.memory.used_gb} / ${metrics.memory.total_gb} GB`;
    document.getElementById('memFree').textContent = metrics.memory.free_gb + ' GB';
    document.getElementById('swapUsed').textContent = metrics.memory.swap_used_mb.toFixed(1) + ' MB';
    
    storageChart.data.datasets[0].data = [
        metrics.storage.by_category.apps,
        metrics.storage.by_category.music,
        metrics.storage.by_category.videos,
        metrics.storage.by_category.photos,
        metrics.storage.by_category.system,
        metrics.storage.by_category.other
    ];
    storageChart.update();
    document.getElementById('storageUsed').textContent = `${metrics.storage.used_gb} / ${metrics.storage.total_gb} GB`;
    document.getElementById('storageFree').textContent = metrics.storage.free_gb + ' GB';
    
    tempHistory.push({
        soc: metrics.temperature.soc_temp_c,
        battery: metrics.temperature.battery_temp_c
    });
    if (tempHistory.length > MAX_TEMP_HISTORY) {
        tempHistory.shift();
    }
    tempChart.data.labels = tempHistory.map((_, i) => i);
    tempChart.data.datasets[0].data = tempHistory.map(t => t.soc);
    tempChart.data.datasets[1].data = tempHistory.map(t => t.battery);
    tempChart.update('none');
    
    document.getElementById('socTemp').textContent = metrics.temperature.soc_temp_c + '°C';
    document.getElementById('batteryTemp').textContent = metrics.temperature.battery_temp_c + '°C';
    
    const throttleStatus = document.getElementById('throttleStatus');
    if (metrics.temperature.thermal_throttling) {
        throttleStatus.textContent = 'Active';
        throttleStatus.className = 'status-badge status-critical';
    } else {
        throttleStatus.textContent = 'Inactive';
        throttleStatus.className = 'status-badge status-normal';
    }
    
    updateGauge(batteryChart, metrics.battery.battery_percent);
    document.getElementById('batteryValue').textContent = metrics.battery.battery_percent + '%';
    document.getElementById('batteryVoltage').textContent = metrics.battery.voltage_v.toFixed(2) + ' V';
    document.getElementById('batteryCurrent').textContent = Math.round(metrics.battery.current_ma) + ' mA';
    
    if (metrics.battery.estimated_runtime_min) {
        const hours = Math.floor(metrics.battery.estimated_runtime_min / 60);
        const mins = Math.round(metrics.battery.estimated_runtime_min % 60);
        document.getElementById('batteryRuntime').textContent = `${hours}h ${mins}m`;
    } else {
        document.getElementById('batteryRuntime').textContent = 'Charging';
    }
    
    document.getElementById('networkType').textContent = metrics.network.connection_type + 
        (metrics.network.wifi_connected ? ' (WiFi)' : '');
    document.getElementById('signalStrength').textContent = metrics.network.signal_strength + '%';
    document.getElementById('speedDown').textContent = metrics.network.speed_down_mbps.toFixed(1) + ' Mbps';
    document.getElementById('speedUp').textContent = metrics.network.speed_up_mbps.toFixed(1) + ' Mbps';
    document.getElementById('dataUsed').textContent = metrics.network.data_used_mb.toFixed(1) + ' MB';
    
    const processList = document.getElementById('processList');
    processList.innerHTML = '';
    metrics.processes.top_processes.forEach(proc => {
        processList.innerHTML += `
            <div class="process-item">
                <span class="process-name">${proc.name}</span>
                <span class="process-cpu">${proc.cpu_percent}% CPU</span>
                <span class="process-mem">${proc.memory_mb.toFixed(0)} MB</span>
                <button class="kill-btn" onclick="killProcess('${proc.name}', ${proc.pid})">Kill</button>
            </div>
        `;
    });
    
    fetchSuggestions();
}

function updateHealth(health) {
    updateStatusBadge('overallStatus', health.status);
    
    const issuesContainer = document.getElementById('healthIssues');
    if (health.issues && health.issues.length > 0) {
        issuesContainer.innerHTML = '<h3 style="color:#ef4444; margin-top:15px;">⚠️ Critical Issues</h3>';
        health.issues.forEach(issue => {
            issuesContainer.innerHTML += `<div class="metric-row"><span class="metric-label" style="color:#ef4444;">${issue}</span></div>`;
        });
    } else {
        issuesContainer.innerHTML = '';
    }
    
    const warningsContainer = document.getElementById('healthWarnings');
    if (health.warnings && health.warnings.length > 0) {
        warningsContainer.innerHTML = '<h3 style="color:#fb923c; margin-top:15px;">⚠️ Warnings</h3>';
        health.warnings.forEach(warning => {
            warningsContainer.innerHTML += `<div class="metric-row"><span class="metric-label" style="color:#fb923c;">${warning}</span></div>`;
        });
    } else {
        warningsContainer.innerHTML = '';
    }
}

function updateStatusBadge(elementId, status) {
    const element = document.getElementById(elementId);
    element.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    element.className = 'status-badge status-' + status;
}

function showAlert(alert) {
    const container = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert ' + (alert.severity === 'warning' ? 'warning' : '');
    alertDiv.innerHTML = `
        <strong>${alert.severity.toUpperCase()}</strong><br>
        ${alert.message}
    `;
    container.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const mode = btn.dataset.mode;
        
        const response = await fetch('/api/performance/mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
        
        const result = await response.json();
        if (result.ok) {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            showAlert({ severity: 'info', message: result.message });
        }
    });
});

async function optimizeMemory() {
    const response = await fetch('/api/optimize/memory', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function optimizeStorage() {
    const response = await fetch('/api/optimize/storage', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function optimizeCPU() {
    const response = await fetch('/api/optimize/cpu', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function optimizeGPU() {
    const response = await fetch('/api/optimize/gpu', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function optimizeBattery() {
    const response = await fetch('/api/optimize/battery', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function coolDownSystem() {
    const response = await fetch('/api/optimize/cooldown', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function clearCache() {
    const response = await fetch('/api/optimize/cache', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function closeBackgroundApps() {
    const response = await fetch('/api/optimize/background-apps', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function fullOptimization() {
    const response = await fetch('/api/optimize/full', { method: 'POST' });
    const result = await response.json();
    if (result.ok) {
        showAlert({ severity: 'info', message: result.result.message });
    }
}

async function killProcess(name, pid) {
    const response = await fetch('/api/optimize/process/kill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ process_name: name, pid })
    });
    const result = await response.json();
    if (result.ok) {
        showAlert({ 
            severity: result.result.success ? 'info' : 'warning', 
            message: result.result.message || result.result.error 
        });
    }
}

async function fetchSuggestions() {
    const response = await fetch('/api/suggestions');
    const result = await response.json();
    if (result.ok && result.suggestions.length > 0) {
        const container = document.getElementById('suggestions');
        container.innerHTML = '<h3 style="margin-top:15px;">💡 Optimization Suggestions</h3>';
        result.suggestions.forEach(sug => {
            container.innerHTML += `
                <div class="suggestion-item">
                    <div class="suggestion-title">${sug.title}</div>
                    <div class="suggestion-desc">${sug.description}</div>
                </div>
            `;
        });
    }
}

fetchSuggestions();
