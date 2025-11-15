let isSessionActive = false;
let updateInterval = null;

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

startBtn.addEventListener('click', startSession);
stopBtn.addEventListener('click', stopSession);

async function startSession() {
    try {
        const response = await fetch('/api/session/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fuel_cost_per_gallon: 3.50
            })
        });

        const data = await response.json();

        if (data.ok) {
            isSessionActive = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusIndicator.className = 'status-indicator status-active';
            statusText.textContent = 'Active';
            statusText.style.color = '#10b981';

            startUpdates();

            console.log('Session started:', data.session_id);
        } else {
            alert('Failed to start session: ' + data.error);
        }
    } catch (error) {
        console.error('Error starting session:', error);
        alert('Error starting session');
    }
}

async function stopSession() {
    try {
        const response = await fetch('/api/session/stop', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.ok) {
            isSessionActive = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            statusIndicator.className = 'status-indicator status-inactive';
            statusText.textContent = 'Not Active';
            statusText.style.color = 'white';

            stopUpdates();

            displaySessionSummary(data);

            console.log('Session stopped:', data.session_id);
        } else {
            alert('Failed to stop session: ' + data.error);
        }
    } catch (error) {
        console.error('Error stopping session:', error);
        alert('Error stopping session');
    }
}

function startUpdates() {
    updateInterval = setInterval(updateDashboard, 1000);
}

function stopUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

async function updateDashboard() {
    try {
        const response = await fetch('/api/session/current');
        const data = await response.json();

        if (data.ok && data.session) {
            const session = data.session;

            document.getElementById('instantMpg').textContent = session.instant_mpg.toFixed(1);
            document.getElementById('tripMpg').textContent = session.trip_mpg.toFixed(1);
            document.getElementById('tankMpg').textContent = session.tank_avg_mpg.toFixed(1);
            document.getElementById('lifetimeMpg').textContent = session.lifetime_avg_mpg.toFixed(1);

            if (session.epa_comparison) {
                const diff = session.epa_comparison.percent_difference;
                const sign = diff > 0 ? '+' : '';
                document.getElementById('epaCompare').textContent = `${sign}${diff.toFixed(1)}%`;
                
                const epaEl = document.getElementById('epaCompare');
                if (diff > 5) {
                    epaEl.style.color = '#10b981';
                } else if (diff > 0) {
                    epaEl.style.color = '#3b82f6';
                } else if (diff > -5) {
                    epaEl.style.color = '#f59e0b';
                } else {
                    epaEl.style.color = '#ef4444';
                }
            }

            if (session.efficiency_score) {
                const eff = session.efficiency_score;
                document.getElementById('efficiencyScore').textContent = Math.round(eff.total_score);
                document.getElementById('efficiencyGrade').textContent = eff.grade || '--';

                document.getElementById('accelScore').textContent = Math.round(eff.acceleration_score) + '%';
                document.getElementById('accelBar').style.width = eff.acceleration_score + '%';

                document.getElementById('brakeScore').textContent = Math.round(eff.braking_score) + '%';
                document.getElementById('brakeBar').style.width = eff.braking_score + '%';

                document.getElementById('rpmScore').textContent = Math.round(eff.rpm_score) + '%';
                document.getElementById('rpmBar').style.width = eff.rpm_score + '%';
            }

            document.getElementById('tripDistance').textContent = session.distance_miles.toFixed(1);
            document.getElementById('fuelConsumed').textContent = session.fuel_consumed_gallons.toFixed(2);
            document.getElementById('tripCost').textContent = '$' + session.trip_fuel_cost.toFixed(2);
            document.getElementById('costPerMile').textContent = '$' + session.cost_per_mile.toFixed(3);

            document.getElementById('currentSpeed').textContent = Math.round(session.current_speed_mph);
            document.getElementById('currentRpm').textContent = session.current_rpm;
            document.getElementById('currentThrottle').textContent = Math.round(session.current_throttle);
            document.getElementById('fuelRate').textContent = session.fuel_rate_gph.toFixed(2);

            updateTips(session.active_tips);
        }
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

function updateTips(tips) {
    const container = document.getElementById('tipsContainer');

    if (!tips || tips.length === 0) {
        container.innerHTML = '<div class="no-tips">No tips at the moment - keep driving efficiently!</div>';
        return;
    }

    container.innerHTML = '';

    tips.forEach(tip => {
        const tipEl = document.createElement('div');
        tipEl.className = `tip ${tip.severity}`;

        const header = document.createElement('div');
        header.className = 'tip-header';

        const icon = document.createElement('span');
        icon.className = 'tip-icon';
        icon.textContent = tip.icon || '💡';

        const title = document.createElement('span');
        title.className = 'tip-title';
        title.textContent = tip.title;

        header.appendChild(icon);
        header.appendChild(title);

        const message = document.createElement('div');
        message.className = 'tip-message';
        message.textContent = tip.message;

        tipEl.appendChild(header);
        tipEl.appendChild(message);

        if (tip.action) {
            const action = document.createElement('div');
            action.className = 'tip-action';
            action.textContent = '→ ' + tip.action;
            tipEl.appendChild(action);
        }

        container.appendChild(tipEl);
    });
}

function displaySessionSummary(data) {
    const summary = data.summary;
    const efficiency = data.efficiency;
    const epaComparison = data.epa_comparison;

    let message = `Session Complete!\n\n`;
    message += `Distance: ${summary.distance_miles.toFixed(1)} miles\n`;
    message += `Fuel Used: ${summary.fuel_consumed_gallons.toFixed(2)} gallons\n`;
    message += `Average MPG: ${summary.avg_mpg.toFixed(1)}\n`;
    message += `Fuel Cost: $${summary.total_fuel_cost.toFixed(2)}\n\n`;
    message += `Efficiency Score: ${Math.round(efficiency.total_score)}/100 (${efficiency.grade})\n\n`;
    
    if (epaComparison) {
        message += `EPA Comparison: ${epaComparison.message}`;
    }

    alert(message);
}

async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();

        if (data.ok) {
            console.log('Service healthy:', data);
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

checkHealth();
