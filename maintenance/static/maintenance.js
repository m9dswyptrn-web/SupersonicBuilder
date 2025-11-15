const API_BASE = '';

let currentTab = 'dashboard';

async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { ok: false, error: error.message };
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
    
    currentTab = tabName;
    
    if (tabName === 'schedules') {
        loadAllSchedules();
    } else if (tabName === 'history') {
        loadServiceHistory();
    } else if (tabName === 'alerts') {
        loadAlerts();
    } else if (tabName === 'costs') {
        loadCostAnalysis();
    } else if (tabName === 'dashboard') {
        loadUpcomingMaintenance();
    }
}

async function loadDashboard() {
    const mileageData = await fetchAPI('/api/mileage/current');
    if (mileageData.ok) {
        document.getElementById('currentMileage').textContent = mileageData.odometer_reading.toLocaleString();
    }
    
    const alertsData = await fetchAPI('/api/alerts');
    if (alertsData.ok) {
        document.getElementById('alertCount').textContent = alertsData.count;
    }
    
    const costData = await fetchAPI('/api/analysis/estimate-annual');
    if (costData.ok) {
        document.getElementById('annualCost').textContent = `$${costData.total_estimated_annual.toFixed(0)}`;
    }
    
    const summaryData = await fetchAPI('/api/costs/summary?period=year');
    if (summaryData.ok) {
        document.getElementById('servicesCount').textContent = summaryData.summary.total_services || 0;
    }
    
    loadUpcomingMaintenance();
}

async function loadUpcomingMaintenance() {
    const data = await fetchAPI('/api/schedules/upcoming');
    const container = document.getElementById('upcomingMaintenance');
    
    if (!data.ok || data.count === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <p>No upcoming maintenance scheduled. You're all caught up!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.upcoming.map(item => {
        const statusClass = item.is_overdue ? 'status-overdue' : 
                          item.is_due_soon ? 'status-due-soon' : 'status-ok';
        const statusText = item.is_overdue ? 'OVERDUE' : 
                         item.is_due_soon ? 'DUE SOON' : 'OK';
        
        let dueInfo = '';
        if (item.miles_remaining !== null) {
            dueInfo += `${Math.abs(item.miles_remaining)} miles ${item.miles_remaining < 0 ? 'overdue' : 'remaining'}`;
        }
        if (item.days_remaining !== null) {
            if (dueInfo) dueInfo += ' or ';
            dueInfo += `${Math.abs(item.days_remaining)} days ${item.days_remaining < 0 ? 'overdue' : 'remaining'}`;
        }
        
        return `
            <div class="schedule-item">
                <h3>${item.schedule_name}</h3>
                <p>${item.description || ''}</p>
                <p><strong>Estimated Cost:</strong> $${(item.estimated_cost || 0).toFixed(2)}</p>
                <div class="schedule-status">
                    <span>${dueInfo}</span>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
            </div>
        `;
    }).join('');
}

async function loadAllSchedules() {
    const data = await fetchAPI('/api/schedules/status');
    const container = document.getElementById('allSchedules');
    
    if (!data.ok || data.count === 0) {
        container.innerHTML = '<div class="loading">No schedules found</div>';
        return;
    }
    
    container.innerHTML = data.schedules.map(item => {
        const statusClass = item.is_overdue ? 'status-overdue' : 
                          item.is_due_soon ? 'status-due-soon' : 'status-ok';
        const statusText = item.is_overdue ? 'OVERDUE' : 
                         item.is_due_soon ? 'DUE SOON' : 'UP TO DATE';
        
        let intervalText = '';
        if (item.mile_interval) {
            intervalText += `Every ${item.mile_interval.toLocaleString()} miles`;
        }
        if (item.month_interval) {
            if (intervalText) intervalText += ' or ';
            intervalText += `Every ${item.month_interval} months`;
        }
        
        return `
            <div class="schedule-item">
                <h3>${item.schedule_name}</h3>
                <p>${item.description || ''}</p>
                <p><strong>Interval:</strong> ${intervalText}</p>
                <p><strong>Estimated Cost:</strong> $${(item.estimated_cost || 0).toFixed(2)}</p>
                ${item.last_service_miles ? `<p><strong>Last Service:</strong> ${item.last_service_miles.toLocaleString()} miles</p>` : ''}
                <div class="schedule-status">
                    <span></span>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
            </div>
        `;
    }).join('');
}

async function loadServiceHistory() {
    const data = await fetchAPI('/api/records?limit=100');
    const container = document.getElementById('serviceHistory');
    
    if (!data.ok || data.count === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <p>No service records yet. Add your first maintenance record to get started!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="record-row record-header">
            <div>Date</div>
            <div>Service</div>
            <div>Mileage</div>
            <div>Cost</div>
            <div>Type</div>
        </div>
        ${data.records.map(record => `
            <div class="record-row">
                <div>${record.service_date}</div>
                <div>${record.service_type}</div>
                <div>${record.odometer_reading.toLocaleString()} mi</div>
                <div>$${record.total_cost.toFixed(2)}</div>
                <div>${record.service_category === 'diy' ? 'DIY' : 'Shop'}</div>
            </div>
        `).join('')}
    `;
}

async function loadAlerts() {
    const data = await fetchAPI('/api/alerts');
    const container = document.getElementById('alertsList');
    
    if (!data.ok || data.count === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">✅</div>
                <p>No active alerts. All maintenance is up to date!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.alerts.map(alert => {
        const alertClass = alert.severity === 'critical' ? 'critical' : 
                          alert.severity === 'warning' ? 'warning' : 'info';
        
        return `
            <div class="alert ${alertClass}">
                <div>
                    <strong>${alert.title}</strong><br>
                    <span>${alert.message}</span>
                </div>
                <button class="btn btn-small btn-secondary" onclick="dismissAlert('${alert.alert_id}')">Dismiss</button>
            </div>
        `;
    }).join('');
}

async function loadCostAnalysis() {
    const container = document.getElementById('costAnalysis');
    
    const summaryData = await fetchAPI('/api/costs/summary?period=all');
    const diySavings = await fetchAPI('/api/costs/diy-savings');
    const perMile = await fetchAPI('/api/costs/per-mile');
    const byType = await fetchAPI('/api/costs/by-type');
    
    let html = '<h3>Cost Summary</h3>';
    
    if (summaryData.ok) {
        const summary = summaryData.summary;
        html += `
            <div class="dashboard" style="margin: 20px 0;">
                <div class="card">
                    <h2>Total Spent</h2>
                    <div class="stat-value">$${(summary.total_spent || 0).toFixed(2)}</div>
                </div>
                <div class="card">
                    <h2>Parts Cost</h2>
                    <div class="stat-value">$${(summary.total_parts || 0).toFixed(2)}</div>
                </div>
                <div class="card">
                    <h2>Labor Cost</h2>
                    <div class="stat-value">$${(summary.total_labor || 0).toFixed(2)}</div>
                </div>
                <div class="card">
                    <h2>Avg per Service</h2>
                    <div class="stat-value">$${(summary.avg_cost || 0).toFixed(2)}</div>
                </div>
            </div>
        `;
    }
    
    if (diySavings.ok && diySavings.savings.diy_services > 0) {
        html += `
            <h3>DIY Savings</h3>
            <div class="chart">
                <p><strong>DIY Services:</strong> ${diySavings.savings.diy_services}</p>
                <p><strong>Actual DIY Cost:</strong> $${diySavings.savings.actual_diy_cost.toFixed(2)}</p>
                <p><strong>Estimated Shop Cost:</strong> $${diySavings.savings.estimated_shop_cost.toFixed(2)}</p>
                <p style="color: #27ae60; font-size: 1.2em; font-weight: bold;">
                    💰 Total Savings: $${diySavings.savings.total_savings.toFixed(2)}
                </p>
            </div>
        `;
    }
    
    if (perMile.ok && perMile.total_miles > 0) {
        html += `
            <h3>Cost Per Mile</h3>
            <div class="chart">
                <p><strong>Cost per Mile:</strong> $${perMile.cost_per_mile.toFixed(4)}/mile</p>
                <p><strong>Total Miles Tracked:</strong> ${perMile.total_miles.toLocaleString()} miles</p>
            </div>
        `;
    }
    
    if (byType.ok && byType.costs_by_type.length > 0) {
        html += `
            <h3>Cost by Type</h3>
            <div class="chart">
                ${byType.costs_by_type.map(type => `
                    <div style="margin: 10px 0;">
                        <strong>${type.type}:</strong> $${type.total_cost.toFixed(2)} 
                        (${type.service_count} services, avg $${type.avg_cost.toFixed(2)})
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    container.innerHTML = html;
}

async function generateAlerts() {
    const result = await fetchAPI('/api/alerts/generate', { method: 'POST' });
    
    if (result.ok) {
        alert(`Generated ${result.alerts_generated} alerts`);
        loadAlerts();
        loadDashboard();
    } else {
        alert('Failed to generate alerts: ' + result.error);
    }
}

async function dismissAlert(alertId) {
    const result = await fetchAPI(`/api/alerts/${alertId}/dismiss`, { method: 'POST' });
    
    if (result.ok) {
        loadAlerts();
        loadDashboard();
    } else {
        alert('Failed to dismiss alert');
    }
}

function showAddRecordModal() {
    document.getElementById('serviceDate').valueAsDate = new Date();
    document.getElementById('addRecordModal').classList.add('active');
}

function showUpdateMileage() {
    document.getElementById('updateMileageModal').classList.add('active');
}

function showAddScheduleModal() {
    document.getElementById('addScheduleModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

async function updateMileage(event) {
    event.preventDefault();
    
    const odometer = parseInt(document.getElementById('newMileage').value);
    
    const result = await fetchAPI('/api/mileage/update', {
        method: 'POST',
        body: JSON.stringify({ odometer_reading: odometer })
    });
    
    if (result.ok) {
        closeModal('updateMileageModal');
        loadDashboard();
        document.getElementById('newMileage').value = '';
    } else {
        alert('Failed to update mileage: ' + result.error);
    }
}

async function addMaintenanceRecord(event) {
    event.preventDefault();
    
    const record = {
        service_type: document.getElementById('serviceType').value,
        service_date: document.getElementById('serviceDate').value,
        odometer_reading: parseInt(document.getElementById('odometerReading').value),
        service_provider: document.getElementById('serviceProvider').value,
        service_category: document.getElementById('serviceCategory').value,
        parts_cost: parseFloat(document.getElementById('partsCost').value) || 0,
        labor_cost: parseFloat(document.getElementById('laborCost').value) || 0,
        labor_hours: parseFloat(document.getElementById('laborHours').value) || 0,
        notes: document.getElementById('notes').value
    };
    
    const result = await fetchAPI('/api/records/add', {
        method: 'POST',
        body: JSON.stringify(record)
    });
    
    if (result.ok) {
        closeModal('addRecordModal');
        event.target.reset();
        loadDashboard();
        if (currentTab === 'history') {
            loadServiceHistory();
        }
        alert('Maintenance record added successfully!');
    } else {
        alert('Failed to add record: ' + result.error);
    }
}

async function addSchedule(event) {
    event.preventDefault();
    
    const schedule = {
        name: document.getElementById('scheduleName').value,
        type: document.getElementById('scheduleType').value || 'custom',
        mile_interval: parseInt(document.getElementById('mileInterval').value) || null,
        month_interval: parseInt(document.getElementById('monthInterval').value) || null,
        description: document.getElementById('scheduleDescription').value,
        estimated_cost: parseFloat(document.getElementById('estimatedCost').value) || 0
    };
    
    const result = await fetchAPI('/api/schedules/add', {
        method: 'POST',
        body: JSON.stringify(schedule)
    });
    
    if (result.ok) {
        closeModal('addScheduleModal');
        event.target.reset();
        if (currentTab === 'schedules') {
            loadAllSchedules();
        }
        alert('Custom schedule added successfully!');
    } else {
        alert('Failed to add schedule: ' + result.error);
    }
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}

loadDashboard();
