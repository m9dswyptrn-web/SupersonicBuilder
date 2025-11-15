let updateInterval;

function init() {
    console.log('Initializing Wireless Charger Monitor...');
    startUpdates();
    fetchInitialData();
}

function startUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    updateInterval = setInterval(() => {
        updateAllData();
    }, 2000);
}

function fetchInitialData() {
    updateAllData();
    fetchStatistics();
    fetchRecentSessions();
    fetchBatteryTips();
}

async function updateAllData() {
    try {
        const response = await fetch('/api/metrics/current');
        const data = await response.json();
        
        if (data.ok) {
            updateChargingStatus(data.metrics.charging_status);
            updateBatteryGauge(data.metrics.charging_status.battery_percent);
            updateEfficiencyMetrics(data.metrics.efficiency);
            updateCompatibility(data.metrics.compatibility);
            updatePadHealth(data.metrics.pad_health);
            updateAlerts(data.metrics.alerts);
            
            if (data.battery) {
                updateBatteryInfo(data.battery);
            }
        }
    } catch (error) {
        console.error('Error fetching metrics:', error);
        updateConnectionStatus(false);
    }
}

function updateChargingStatus(status) {
    const container = document.getElementById('charging-status');
    const statusClass = status.charging_active ? 'active' : (status.phone_detected ? 'warning' : 'inactive');
    
    let timeToFullHTML = '';
    if (status.time_to_full_minutes !== null) {
        const hours = Math.floor(status.time_to_full_minutes / 60);
        const mins = status.time_to_full_minutes % 60;
        timeToFullHTML = `
            <div class="metric">
                <span class="metric-label">Time to Full</span>
                <span class="metric-value">${hours}h ${mins}m</span>
            </div>
        `;
    }
    
    container.innerHTML = `
        <div style="text-align: center; margin-bottom: 20px;">
            <span class="status-indicator ${statusClass}"></span>
            <strong>${status.status}</strong>
        </div>
        <div class="metric">
            <span class="metric-label">Phone Detected</span>
            <span class="metric-value">${status.phone_detected ? 'Yes' : 'No'}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Charging Active</span>
            <span class="metric-value">${status.charging_active ? 'Yes' : 'No'}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Charging Power</span>
            <span class="metric-value">${status.charging_power_w} W</span>
        </div>
        ${timeToFullHTML}
        ${status.phone_model ? `
            <div class="metric">
                <span class="metric-label">Phone Model</span>
                <span class="metric-value">${status.phone_model}</span>
            </div>
        ` : ''}
    `;
}

function updateBatteryGauge(percent) {
    const gauge = document.getElementById('battery-gauge');
    const valueElement = document.getElementById('battery-percent');
    
    if (percent === null || percent === undefined) {
        valueElement.textContent = '--';
        gauge.style.strokeDashoffset = '502.4';
        return;
    }
    
    valueElement.textContent = percent + '%';
    
    const circumference = 2 * Math.PI * 80;
    const offset = circumference - (percent / 100) * circumference;
    gauge.style.strokeDashoffset = offset;
    
    if (percent >= 80) {
        gauge.style.stroke = '#00ff88';
    } else if (percent >= 20) {
        gauge.style.stroke = '#00d9ff';
    } else {
        gauge.style.stroke = '#ff4444';
    }
}

function updateEfficiencyMetrics(efficiency) {
    const container = document.getElementById('efficiency-metrics');
    
    const statusColors = {
        'excellent': '#00ff88',
        'good': '#00d9ff',
        'poor': '#ffaa00'
    };
    
    const statusColor = statusColors[efficiency.status] || '#888';
    
    container.innerHTML = `
        <div class="metric">
            <span class="metric-label">Input Power</span>
            <span class="metric-value">${efficiency.input_power_w} W</span>
        </div>
        <div class="metric">
            <span class="metric-label">Output Power</span>
            <span class="metric-value">${efficiency.output_power_w} W</span>
        </div>
        <div class="metric">
            <span class="metric-label">Efficiency</span>
            <span class="metric-value" style="color: ${statusColor}">${efficiency.efficiency_percent}%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${efficiency.efficiency_percent}%; background: ${statusColor}"></div>
        </div>
        <div class="metric">
            <span class="metric-label">Heat Generation</span>
            <span class="metric-value">${efficiency.heat_generation_w} W</span>
        </div>
        <div class="metric">
            <span class="metric-label">Pad Temperature</span>
            <span class="metric-value" style="color: ${efficiency.pad_temp_c > 45 ? '#ff4444' : '#00d9ff'}">${efficiency.pad_temp_c}°C</span>
        </div>
        <div class="metric">
            <span class="metric-label">Phone Temperature</span>
            <span class="metric-value">${efficiency.phone_temp_c}°C</span>
        </div>
    `;
}

function updateCompatibility(compat) {
    const container = document.getElementById('compatibility-info');
    
    const alignmentColors = {
        'Excellent': '#00ff88',
        'Good': '#00d9ff',
        'Fair': '#ffaa00',
        'Poor': '#ff4444'
    };
    
    const alignmentColor = alignmentColors[compat.alignment_status] || '#888';
    
    container.innerHTML = `
        <div class="metric">
            <span class="metric-label">Phone Model</span>
            <span class="metric-value">${compat.phone_model}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Qi Compatible</span>
            <span class="metric-value">${compat.qi_compatible ? 'Yes ✓' : 'No ✗'}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Max Power</span>
            <span class="metric-value">${compat.max_supported_power_w} W</span>
        </div>
        <div class="metric">
            <span class="metric-label">Current Power</span>
            <span class="metric-value">${compat.current_power_w} W</span>
        </div>
        <div class="alignment-guide">
            <strong style="color: ${alignmentColor}">Alignment: ${compat.alignment_status}</strong>
            <div class="alignment-circle">
                <div class="phone-icon"></div>
            </div>
            <p style="color: #888; margin-top: 10px;">${compat.positioning_tip}</p>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${compat.alignment_score}%; background: ${alignmentColor}"></div>
        </div>
        <p style="text-align: center; color: #888; margin-top: 5px;">Alignment Score: ${compat.alignment_score}/100</p>
    `;
}

function updatePadHealth(health) {
    const container = document.getElementById('pad-health');
    
    const tempColors = {
        'normal': '#00ff88',
        'elevated': '#00d9ff',
        'warning': '#ffaa00',
        'critical': '#ff4444'
    };
    
    const coilColors = {
        'excellent': '#00ff88',
        'good': '#00d9ff',
        'fair': '#ffaa00',
        'poor': '#ff4444'
    };
    
    const tempColor = tempColors[health.temp_status] || '#888';
    const coilColor = coilColors[health.coil_status] || '#888';
    
    container.innerHTML = `
        <div class="metric">
            <span class="metric-label">Pad Temperature</span>
            <span class="metric-value" style="color: ${tempColor}">${health.pad_temp_c}°C (${health.temp_status})</span>
        </div>
        <div class="metric">
            <span class="metric-label">Coil Health</span>
            <span class="metric-value" style="color: ${coilColor}">${health.coil_health_percent}% (${health.coil_status})</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${health.coil_health_percent}%; background: ${coilColor}"></div>
        </div>
        <div class="metric">
            <span class="metric-label">Charging Cycles</span>
            <span class="metric-value">${health.charging_cycles.toLocaleString()}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Thermal Throttling</span>
            <span class="metric-value" style="color: ${health.thermal_throttling ? '#ff4444' : '#00ff88'}">
                ${health.thermal_throttling ? 'Active' : 'Inactive'}
            </span>
        </div>
        <div class="metric">
            <span class="metric-label">Needs Maintenance</span>
            <span class="metric-value" style="color: ${health.needs_maintenance ? '#ffaa00' : '#00ff88'}">
                ${health.needs_maintenance ? 'Yes' : 'No'}
            </span>
        </div>
        <div class="metric">
            <span class="metric-label">Estimated Lifespan</span>
            <span class="metric-value">${(health.estimated_lifespan_cycles / 1000).toFixed(1)}K cycles</span>
        </div>
    `;
}

function updateAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="color: #888;">No active alerts</p>';
        return;
    }
    
    const severityClass = {
        'critical': 'alert-critical',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert ${severityClass[alert.severity] || 'alert-info'}">
            <span style="font-size: 1.5em;">${alert.severity === 'critical' ? '🚨' : alert.severity === 'warning' ? '⚠️' : 'ℹ️'}</span>
            <div style="flex: 1;">
                <strong>${alert.type.replace(/_/g, ' ').toUpperCase()}</strong>
                <p style="margin-top: 5px; color: #ccc;">${alert.message}</p>
            </div>
        </div>
    `).join('');
}

function updateBatteryInfo(battery) {
    
}

async function fetchBatteryTips() {
    try {
        const response = await fetch('/api/battery/tips');
        const data = await response.json();
        
        if (data.ok && data.daily_tips) {
            const container = document.getElementById('battery-tips');
            container.innerHTML = data.daily_tips.map(tip => `
                <div class="tip">
                    <div class="tip-title">💡 Battery Care Tip</div>
                    <p style="color: #ccc;">${tip}</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error fetching battery tips:', error);
    }
}

async function fetchStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        if (data.ok && data.statistics) {
            const stats = data.statistics;
            const container = document.getElementById('statistics');
            
            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">${stats.total_sessions || 0}</div>
                        <div class="stat-label">Total Sessions</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${stats.avg_duration_min ? Math.round(stats.avg_duration_min) : 0}</div>
                        <div class="stat-label">Avg Duration (min)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${stats.total_power_wh ? stats.total_power_wh.toFixed(1) : 0}</div>
                        <div class="stat-label">Total Energy (Wh)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${stats.avg_efficiency ? stats.avg_efficiency.toFixed(1) : 0}%</div>
                        <div class="stat-label">Avg Efficiency</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${stats.most_used_hour || 'N/A'}</div>
                        <div class="stat-label">Peak Hour</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">${stats.total_misalignments || 0}</div>
                        <div class="stat-label">Misalignments</div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching statistics:', error);
    }
}

async function fetchRecentSessions() {
    try {
        const response = await fetch('/api/sessions?limit=5');
        const data = await response.json();
        
        if (data.ok && data.sessions) {
            const container = document.getElementById('recent-sessions');
            
            if (data.sessions.length === 0) {
                container.innerHTML = '<p style="color: #888;">No charging sessions yet</p>';
                return;
            }
            
            container.innerHTML = data.sessions.map(session => {
                const startDate = new Date(session.start_time);
                const duration = session.duration_minutes || 0;
                
                return `
                    <div class="history-item">
                        <div class="history-header">
                            <strong>${session.phone_model || 'Unknown Phone'}</strong>
                            <span style="color: #888;">${startDate.toLocaleString()}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Duration</span>
                            <span class="metric-value">${duration} min</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Battery</span>
                            <span class="metric-value">${session.start_battery_percent || '--'}% → ${session.end_battery_percent || '--'}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Energy Used</span>
                            <span class="metric-value">${(session.total_power_wh || 0).toFixed(2)} Wh</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Avg Efficiency</span>
                            <span class="metric-value">${(session.avg_efficiency_percent || 0).toFixed(1)}%</span>
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error fetching recent sessions:', error);
    }
}

async function placePhone(alignment) {
    try {
        const response = await fetch('/api/simulate/place-phone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ alignment })
        });
        const data = await response.json();
        
        if (data.ok) {
            console.log('Phone placed:', data.status);
            updateAllData();
        }
    } catch (error) {
        console.error('Error placing phone:', error);
    }
}

async function removePhone() {
    try {
        const response = await fetch('/api/simulate/remove-phone', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok) {
            console.log('Phone removed');
            updateAllData();
        }
    } catch (error) {
        console.error('Error removing phone:', error);
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    const indicator = statusEl.querySelector('.status-indicator');
    const text = statusEl.querySelector('span:last-child');
    
    if (connected) {
        indicator.classList.remove('inactive');
        indicator.classList.add('active');
        text.textContent = 'Connected';
        statusEl.style.background = 'rgba(0, 255, 136, 0.2)';
        statusEl.style.borderColor = 'rgba(0, 255, 136, 0.4)';
    } else {
        indicator.classList.remove('active');
        indicator.classList.add('inactive');
        text.textContent = 'Disconnected';
        statusEl.style.background = 'rgba(255, 68, 68, 0.2)';
        statusEl.style.borderColor = 'rgba(255, 68, 68, 0.4)';
    }
}

document.addEventListener('DOMContentLoaded', init);

window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
