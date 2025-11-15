// Bass Management System - Frontend JavaScript
// EOENKK Android 15 Integration

const API_BASE = '/api';

// Update slider value displays
document.getElementById('subLevel').addEventListener('input', function() {
    document.getElementById('subLevelValue').textContent = this.value + '%';
});

document.getElementById('subPhase').addEventListener('input', function() {
    document.getElementById('subPhaseValue').textContent = this.value + '°';
    updatePhaseVisualization(parseFloat(this.value));
});

document.getElementById('subDelay').addEventListener('input', function() {
    document.getElementById('subDelayValue').textContent = this.value + ' ms';
});

document.getElementById('boostAmount').addEventListener('input', function() {
    document.getElementById('boostAmountValue').textContent = this.value + ' dB';
    
    if (parseFloat(this.value) > 6) {
        document.getElementById('boostWarning').style.display = 'block';
    } else {
        document.getElementById('boostWarning').style.display = 'none';
    }
});

document.getElementById('qFactor').addEventListener('input', function() {
    document.getElementById('qFactorValue').textContent = this.value;
});

document.getElementById('boostType').addEventListener('change', function() {
    const qFactorGroup = document.getElementById('qFactorGroup');
    if (this.value === 'peak') {
        qFactorGroup.style.display = 'block';
    } else {
        qFactorGroup.style.display = 'none';
    }
});

// Apply subwoofer settings
async function applySubwooferSettings() {
    const level = parseFloat(document.getElementById('subLevel').value);
    const phase = parseFloat(document.getElementById('subPhase').value);
    const delay = parseFloat(document.getElementById('subDelay').value);
    
    try {
        const response = await fetch(`${API_BASE}/subwoofer/configure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sub_id: 1,
                level_percent: level,
                phase_degrees: phase,
                delay_ms: delay
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showStatus('subStatus', 'success', 
                `Subwoofer configured: ${level}% level, ${phase}° phase, ${delay} ms delay`);
        } else {
            showStatus('subStatus', 'error', `Error: ${data.error}`);
        }
    } catch (error) {
        showStatus('subStatus', 'error', `Failed to apply settings: ${error.message}`);
    }
}

// Apply filters
async function applyFilters() {
    const subsonicFreq = parseFloat(document.getElementById('subsonicFreq').value);
    const subsonicSlope = parseInt(document.getElementById('subsonicSlope').value);
    const crossoverFreq = parseFloat(document.getElementById('crossoverFreq').value);
    const crossoverSlope = parseInt(document.getElementById('crossoverSlope').value);
    
    try {
        const subsonicResponse = await fetch(`${API_BASE}/filters/subsonic`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frequency_hz: subsonicFreq,
                slope_db: subsonicSlope
            })
        });
        
        const crossoverResponse = await fetch(`${API_BASE}/filters/crossover`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frequency_hz: crossoverFreq,
                slope_db: crossoverSlope,
                alignment: 'linkwitz_riley'
            })
        });
        
        const subsonicData = await subsonicResponse.json();
        const crossoverData = await crossoverResponse.json();
        
        if (subsonicData.ok && crossoverData.ok) {
            showStatus('filterStatus', 'success', 
                `Filters configured: Subsonic ${subsonicFreq} Hz, Crossover ${crossoverFreq} Hz`);
        } else {
            showStatus('filterStatus', 'error', 'Failed to apply filters');
        }
    } catch (error) {
        showStatus('filterStatus', 'error', `Error: ${error.message}`);
    }
}

// Apply bass boost
async function applyBassBoost() {
    const boostType = document.getElementById('boostType').value;
    const boostFreq = parseFloat(document.getElementById('boostFreq').value);
    const boostAmount = parseFloat(document.getElementById('boostAmount').value);
    const qFactor = parseFloat(document.getElementById('qFactor').value);
    
    try {
        const response = await fetch(`${API_BASE}/filters/bass-boost`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                boost_type: boostType,
                frequency_hz: boostFreq,
                boost_db: boostAmount,
                q_factor: qFactor
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showStatus('boostStatus', 'success', 
                `Bass boost: ${boostType} ${boostAmount} dB @ ${boostFreq} Hz`);
        } else {
            showStatus('boostStatus', 'error', `Error: ${data.error}`);
        }
    } catch (error) {
        showStatus('boostStatus', 'error', `Error: ${error.message}`);
    }
}

// Optimize phase alignment
async function optimizePhase() {
    const subDistance = parseFloat(document.getElementById('subDistance').value);
    const mainDistance = parseFloat(document.getElementById('mainDistance').value);
    
    try {
        const response = await fetch(`${API_BASE}/phase/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subwoofer_distance: subDistance,
                main_speaker_distance: mainDistance,
                unit: 'inches',
                crossover_frequency: parseFloat(document.getElementById('crossoverFreq').value)
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            const opt = data.phase_optimization;
            showStatus('phaseStatus', 'success', 
                `Recommendation: ${opt.action_required}<br>` +
                `Delay difference: ${opt.delay_difference_ms.toFixed(2)} ms<br>` +
                `Recommended phase: ${opt.recommended_phase_degrees}°`);
            
            document.getElementById('subPhase').value = opt.recommended_phase_degrees;
            document.getElementById('subPhaseValue').textContent = opt.recommended_phase_degrees + '°';
            updatePhaseVisualization(opt.recommended_phase_degrees);
        } else {
            showStatus('phaseStatus', 'error', `Error: ${data.error}`);
        }
    } catch (error) {
        showStatus('phaseStatus', 'error', `Error: ${error.message}`);
    }
}

// Play test tone
async function playTone(frequency) {
    try {
        const response = await fetch(`${API_BASE}/testtones/sine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frequency_hz: frequency,
                duration_seconds: 5.0,
                amplitude_db: -20.0
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showStatus('toneStatus', 'info', 
                `Playing ${frequency} Hz sine wave for 5 seconds<br>` +
                `${data.sine_wave.use_case}`);
        }
    } catch (error) {
        showStatus('toneStatus', 'error', `Error: ${error.message}`);
    }
}

// Play sweep tone
async function playSweep() {
    try {
        const response = await fetch(`${API_BASE}/testtones/sweep`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_hz: 20,
                end_hz: 200,
                duration_seconds: 30.0,
                sweep_type: 'logarithmic',
                amplitude_db: -20.0
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showStatus('toneStatus', 'info', 
                'Playing 20-200 Hz sweep (30 seconds)<br>' +
                'Listen for resonances and smooth response');
        }
    } catch (error) {
        showStatus('toneStatus', 'error', `Error: ${error.message}`);
    }
}

// Play pink noise
async function playPinkNoise() {
    try {
        const response = await fetch(`${API_BASE}/testtones/pink-noise`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                duration_seconds: 30.0,
                amplitude_db: -20.0,
                bass_weighted: true,
                lowpass_hz: 200
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showStatus('toneStatus', 'info', 
                'Playing bass-weighted pink noise (30 seconds)<br>' +
                'Use with SPL meter for calibration');
        }
    } catch (error) {
        showStatus('toneStatus', 'error', `Error: ${error.message}`);
    }
}

// Start calibration sequence
async function startCalibrationSequence() {
    try {
        const response = await fetch(`${API_BASE}/testtones/calibration-sequence`);
        const data = await response.json();
        
        if (data.ok) {
            const seq = data.calibration_sequence;
            showStatus('toneStatus', 'info', 
                `Calibration sequence ready<br>` +
                `${seq.total_steps} steps, ~${seq.estimated_time_minutes} minutes<br>` +
                `Follow on-screen instructions for each step`);
        }
    } catch (error) {
        showStatus('toneStatus', 'error', `Error: ${error.message}`);
    }
}

// Load preset
async function loadPreset(presetName) {
    try {
        const response = await fetch(`${API_BASE}/filters/preset/${presetName}`);
        const data = await response.json();
        
        if (data.ok) {
            const preset = data.preset;
            
            document.getElementById('subsonicFreq').value = preset.subsonic_filter.frequency_hz;
            document.getElementById('subsonicSlope').value = preset.subsonic_filter.slope_db_per_octave;
            document.getElementById('crossoverFreq').value = preset.lowpass_crossover.frequency_hz;
            document.getElementById('crossoverSlope').value = preset.lowpass_crossover.slope_db_per_octave;
            
            if (preset.bass_boost) {
                document.getElementById('boostType').value = preset.bass_boost.type.includes('shelf') ? 'shelf' : 'peak';
                document.getElementById('boostFreq').value = preset.bass_boost.frequency_hz;
                document.getElementById('boostAmount').value = preset.bass_boost.boost_db;
            } else {
                document.getElementById('boostAmount').value = 0;
            }
            
            showStatus('presetStatus', 'success', 
                `Loaded preset: ${preset.name}<br>${preset.description}`);
        }
    } catch (error) {
        showStatus('presetStatus', 'error', `Error: ${error.message}`);
    }
}

// Save configuration
async function saveConfiguration() {
    const configName = document.getElementById('configName').value.trim();
    
    if (!configName) {
        showStatus('presetStatus', 'error', 'Please enter a configuration name');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/config/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                config_name: configName,
                notes: 'Saved from web UI'
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showStatus('presetStatus', 'success', 
                `Configuration saved: ${data.config_name} (ID: ${data.config_id})`);
            document.getElementById('configName').value = '';
        } else {
            showStatus('presetStatus', 'error', `Error: ${data.error}`);
        }
    } catch (error) {
        showStatus('presetStatus', 'error', `Error: ${error.message}`);
    }
}

// Load configurations
async function loadConfigurations() {
    try {
        const response = await fetch(`${API_BASE}/config/list`);
        const data = await response.json();
        
        if (data.ok) {
            showStatus('presetStatus', 'info', 
                `Found ${data.total} saved configurations<br>` +
                'Check browser console for details');
            console.log('Saved configurations:', data.configurations);
        }
    } catch (error) {
        showStatus('presetStatus', 'error', `Error: ${error.message}`);
    }
}

// Measure SPL
async function measureSPL() {
    const frequency = parseFloat(document.getElementById('splFreq').value);
    const subLevel = parseFloat(document.getElementById('subLevel').value);
    
    try {
        const response = await fetch(`${API_BASE}/spl/measure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frequency_hz: frequency,
                subwoofer_level: (subLevel / 100) * 75,
                room_acoustics: 'average'
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            const measurement = data.spl_measurement;
            const statusClass = measurement.measured_spl_db >= 73 && measurement.measured_spl_db <= 77 ? 'success' : 'info';
            
            document.getElementById('splResults').innerHTML = `
                <div class="status ${statusClass}">
                    <div class="metric">
                        <span class="metric-label">Frequency:</span>
                        <span class="metric-value">${measurement.frequency_hz} Hz</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Measured SPL:</span>
                        <span class="metric-value">${measurement.measured_spl_db} dB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Room Gain:</span>
                        <span class="metric-value">${measurement.room_gain_db} dB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Status:</span>
                        <span class="metric-value">${measurement.status}</span>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        showStatus('splResults', 'error', `Error: ${error.message}`);
    }
}

// Sync with DSP
async function syncWithDSP() {
    try {
        const response = await fetch(`${API_BASE}/dsp/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showStatus('integrationStatus', 'success', 
                `Synced with DSP (port ${data.dsp_sync.dsp_port})<br>` +
                'Bass settings ready for integration');
            console.log('DSP sync data:', data.dsp_sync);
        }
    } catch (error) {
        showStatus('integrationStatus', 'error', `Error: ${error.message}`);
    }
}

// Export to Android
async function exportToAndroid() {
    try {
        const response = await fetch(`${API_BASE}/export/android`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.ok) {
            console.log('Android export configuration:', data.android_config);
            
            navigator.clipboard.writeText(JSON.stringify(data.android_config, null, 2));
            
            showStatus('integrationStatus', 'success', 
                'Configuration copied to clipboard!<br>' +
                'Paste into EOENKK Android 15 DSP settings');
        }
    } catch (error) {
        showStatus('integrationStatus', 'error', `Error: ${error.message}`);
    }
}

// Update phase visualization
function updatePhaseVisualization(phaseDegrees) {
    const path = document.getElementById('phaseWavePath');
    
    const phaseShift = (phaseDegrees / 180) * 200;
    
    if (phaseDegrees === 0) {
        path.setAttribute('d', 'M 0 60 Q 100 10 200 60 T 400 60');
        path.style.stroke = '#00d4ff';
    } else if (phaseDegrees === 180) {
        path.setAttribute('d', 'M 0 60 Q 100 110 200 60 T 400 60');
        path.style.stroke = '#ff4757';
    } else {
        const controlY = 60 - (50 * Math.sin((phaseDegrees / 180) * Math.PI));
        path.setAttribute('d', `M 0 60 Q 100 ${controlY} 200 60 T 400 60`);
        path.style.stroke = '#ffa500';
    }
}

// Show status message
function showStatus(elementId, type, message) {
    const element = document.getElementById(elementId);
    element.className = `status ${type}`;
    element.innerHTML = message;
    element.style.display = 'block';
    
    if (type !== 'info') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 8000);
    }
}

// Initialize on load
window.addEventListener('load', function() {
    console.log('Bass Management System loaded');
    updatePhaseVisualization(0);
});
