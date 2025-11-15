const API_BASE = '';

let currentPosition = 'driver';
let speakerPositions = {};
let listeningPositions = {};

async function init() {
    await checkHealth();
    await loadSpeakerPositions();
    await loadAcousticData();
    setupEventListeners();
    updateVisualization();
}

function setupEventListeners() {
    document.getElementById('listeningPosition').addEventListener('change', function() {
        currentPosition = this.value;
        updateVisualization();
        calculateOptimal();
    });
    
    document.getElementById('balanceSlider').addEventListener('input', function() {
        const value = parseFloat(this.value);
        document.getElementById('balanceValue').textContent = value.toFixed(1) + ' dB';
        updateBalanceMeter(value);
    });
    
    document.getElementById('faderSlider').addEventListener('input', function() {
        const value = parseFloat(this.value);
        document.getElementById('faderValue').textContent = value.toFixed(1) + ' dB';
        updateFaderMeter(value);
    });
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.ok) {
            document.getElementById('serviceStatus').textContent = 'Service Online';
            document.getElementById('aiStatus').textContent = data.ai_available 
                ? 'AI: Ready (Claude)' 
                : 'AI: Rule-based (No API key)';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('serviceStatus').innerHTML = 
            '<span class="status-indicator offline"></span>Service Offline';
    }
}

async function loadSpeakerPositions() {
    try {
        const response = await fetch(`${API_BASE}/api/positioning/speakers`);
        const data = await response.json();
        
        if (data.ok) {
            speakerPositions = data.speaker_positions;
            listeningPositions = data.listening_positions;
        }
    } catch (error) {
        console.error('Failed to load speaker positions:', error);
    }
}

function updateVisualization() {
    const visualizer = document.getElementById('visualizer');
    const markersContainer = document.getElementById('speakerMarkers');
    markersContainer.innerHTML = '';
    
    const width = visualizer.clientWidth;
    const height = visualizer.clientHeight;
    
    const scaleX = width / 68;
    const scaleY = height / 55;
    
    for (const [name, pos] of Object.entries(speakerPositions)) {
        const marker = document.createElement('div');
        marker.className = 'speaker-marker';
        marker.style.left = (pos.x * scaleX) + 'px';
        marker.style.top = (pos.y * scaleY) + 'px';
        
        const label = document.createElement('div');
        label.className = 'speaker-label';
        label.textContent = name.replace(/_/g, ' ');
        marker.appendChild(label);
        
        markersContainer.appendChild(marker);
    }
    
    if (listeningPositions[currentPosition]) {
        const listenerPos = listeningPositions[currentPosition];
        const listenerMarker = document.createElement('div');
        listenerMarker.className = 'listener-marker';
        listenerMarker.style.left = (listenerPos.x * scaleX) + 'px';
        listenerMarker.style.top = (listenerPos.y * scaleY) + 'px';
        listenerMarker.title = 'Listening Position: ' + currentPosition;
        
        markersContainer.appendChild(listenerMarker);
    }
}

async function calculateOptimal() {
    try {
        const [timeAlign, balance, fader, centerImage] = await Promise.all([
            fetch(`${API_BASE}/api/positioning/time-alignment/${currentPosition}`).then(r => r.json()),
            fetch(`${API_BASE}/api/positioning/balance/${currentPosition}`).then(r => r.json()),
            fetch(`${API_BASE}/api/positioning/fader/${currentPosition}`).then(r => r.json()),
            fetch(`${API_BASE}/api/positioning/center-image/${currentPosition}`).then(r => r.json())
        ]);
        
        if (balance.ok && balance.balance_corrections_db) {
            const avgBalance = Object.values(balance.balance_corrections_db).reduce((a, b) => a + b, 0) 
                / Object.keys(balance.balance_corrections_db).length;
            document.getElementById('balanceSlider').value = avgBalance.toFixed(1);
            document.getElementById('balanceValue').textContent = avgBalance.toFixed(1) + ' dB';
            updateBalanceMeter(avgBalance);
        }
        
        if (fader.ok && fader.fader_settings) {
            const faderDb = fader.fader_settings.fader_db;
            document.getElementById('faderSlider').value = faderDb.toFixed(1);
            document.getElementById('faderValue').textContent = faderDb.toFixed(1) + ' dB';
            updateFaderMeter(faderDb);
        }
        
        if (centerImage.ok && centerImage.center_image) {
            const score = centerImage.center_image.quality_score;
            document.getElementById('centerImageScore').textContent = score.toFixed(0) + '/100';
            
            const quality = score > 80 ? 'Excellent' : score > 60 ? 'Good' : score > 40 ? 'Fair' : 'Poor';
            document.getElementById('soundstageQuality').textContent = quality;
        }
        
    } catch (error) {
        console.error('Failed to calculate optimal settings:', error);
    }
}

function updateBalanceMeter(value) {
    const meter = document.getElementById('balanceMeter');
    const percentage = ((parseFloat(value) + 10) / 20) * 100;
    meter.style.width = percentage + '%';
    
    if (Math.abs(value) < 1) {
        meter.textContent = 'Centered';
    } else if (value < 0) {
        meter.textContent = 'Left ' + Math.abs(value).toFixed(1) + 'dB';
    } else {
        meter.textContent = 'Right ' + value.toFixed(1) + 'dB';
    }
}

function updateFaderMeter(value) {
    const meter = document.getElementById('faderMeter');
    const percentage = ((parseFloat(value) + 10) / 20) * 100;
    meter.style.width = percentage + '%';
    
    if (Math.abs(value) < 1) {
        meter.textContent = 'Centered';
    } else if (value < 0) {
        meter.textContent = 'Rear ' + Math.abs(value).toFixed(1) + 'dB';
    } else {
        meter.textContent = 'Front ' + value.toFixed(1) + 'dB';
    }
}

async function loadAcousticData() {
    try {
        const [cabinInfo, rt60] = await Promise.all([
            fetch(`${API_BASE}/api/acoustics/cabin-info`).then(r => r.json()),
            fetch(`${API_BASE}/api/acoustics/rt60`).then(r => r.json())
        ]);
        
        if (rt60.ok) {
            document.getElementById('rt60Value').textContent = 
                (rt60.rt60_seconds * 1000).toFixed(0) + ' ms';
        }
        
        if (cabinInfo.ok && cabinInfo.cabin_acoustics) {
            const modes = cabinInfo.cabin_acoustics.room_modes;
            displayRoomModes(modes);
            
            const corrections = cabinInfo.cabin_acoustics.recommended_corrections;
            displayEQCorrections(corrections);
        }
    } catch (error) {
        console.error('Failed to load acoustic data:', error);
    }
}

function displayRoomModes(modes) {
    const container = document.getElementById('roomModesList');
    container.innerHTML = '';
    
    if (!modes || !modes.axial) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: #888;">No room modes data</div>';
        return;
    }
    
    modes.axial.slice(0, 8).forEach(mode => {
        const item = document.createElement('div');
        item.className = 'recommendation-item low';
        item.innerHTML = `
            <div><strong>${mode.mode}</strong></div>
            <div>${mode.frequency_hz.toFixed(1)} Hz</div>
            <div style="font-size: 0.9em; color: #888; margin-top: 5px;">
                ${mode.dimension} resonance
            </div>
        `;
        container.appendChild(item);
    });
}

function displayEQCorrections(corrections) {
    const container = document.getElementById('eqCorrectionsList');
    container.innerHTML = '';
    
    if (!corrections || corrections.length === 0) {
        container.innerHTML = '<div style="padding: 20px; text-align: center; color: #888;">No corrections needed</div>';
        return;
    }
    
    corrections.forEach(corr => {
        const item = document.createElement('div');
        item.className = 'recommendation-item ' + (corr.type.includes('cut') ? 'high' : 'medium');
        item.innerHTML = `
            <div><strong>${corr.frequency_hz.toFixed(0)} Hz</strong></div>
            <div>Gain: ${corr.gain_db > 0 ? '+' : ''}${corr.gain_db.toFixed(1)} dB, Q: ${corr.q_factor.toFixed(1)}</div>
            <div style="font-size: 0.9em; color: #888; margin-top: 5px;">
                ${corr.reason}
            </div>
        `;
        container.appendChild(item);
    });
}

async function getAIRecommendations() {
    const container = document.getElementById('aiRecommendations');
    container.innerHTML = '<div class="loading" style="text-align: center; padding: 40px;">Analyzing setup...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/ai/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                listening_position: currentPosition
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            displayRecommendations(data);
        } else {
            container.innerHTML = '<div style="padding: 20px; color: #ff6b6b;">Failed to get recommendations</div>';
        }
    } catch (error) {
        console.error('Failed to get AI recommendations:', error);
        container.innerHTML = '<div style="padding: 20px; color: #ff6b6b;">Error: ' + error.message + '</div>';
    }
}

function displayRecommendations(data) {
    const container = document.getElementById('aiRecommendations');
    container.innerHTML = '';
    
    const analysisDiv = document.createElement('div');
    analysisDiv.style.whiteSpace = 'pre-wrap';
    analysisDiv.style.fontSize = '0.9em';
    analysisDiv.style.lineHeight = '1.6';
    analysisDiv.textContent = data.analysis;
    container.appendChild(analysisDiv);
    
    if (data.recommendations && Array.isArray(data.recommendations)) {
        data.recommendations.forEach(rec => {
            const item = document.createElement('div');
            item.className = 'recommendation-item ' + (rec.priority || 'medium');
            item.innerHTML = `
                <div>
                    <span class="badge ${rec.priority || 'medium'}">${rec.priority?.toUpperCase() || 'MEDIUM'}</span>
                    <strong>${rec.category || 'General'}</strong>
                </div>
                <div style="margin-top: 5px;">${rec.action}</div>
                <div style="font-size: 0.9em; color: #888; margin-top: 5px;">
                    ${rec.reason || rec.impact || ''}
                </div>
            `;
            container.appendChild(item);
        });
    }
    
    if (data.source === 'rule_based') {
        const note = document.createElement('div');
        note.style.marginTop = '15px';
        note.style.padding = '10px';
        note.style.background = 'rgba(255, 165, 0, 0.1)';
        note.style.borderRadius = '5px';
        note.style.fontSize = '0.9em';
        note.textContent = '💡 ' + (data.note || 'Using rule-based analysis');
        container.appendChild(note);
    }
}

async function autoTune() {
    const container = document.getElementById('aiRecommendations');
    container.innerHTML = '<div class="loading" style="text-align: center; padding: 40px;">Calculating auto-tune settings...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/ai/auto-tune`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                listening_position: currentPosition
            })
        });
        
        const data = await response.json();
        
        if (data.ok && data.auto_tune_settings) {
            applyAutoTuneSettings(data.auto_tune_settings);
            
            container.innerHTML = `
                <div style="padding: 20px; text-align: center;">
                    <div style="font-size: 1.5em; color: #4ade80; margin-bottom: 10px;">✓ Auto-Tune Applied</div>
                    <div style="color: #888;">${data.description}</div>
                    <div style="margin-top: 15px; padding: 15px; background: rgba(74, 222, 128, 0.1); border-radius: 5px;">
                        <strong>Estimated Improvement:</strong><br>
                        ${data.estimated_improvement}
                    </div>
                </div>
            `;
            
            calculateOptimal();
        }
    } catch (error) {
        console.error('Auto-tune failed:', error);
        container.innerHTML = '<div style="padding: 20px; color: #ff6b6b;">Auto-tune failed: ' + error.message + '</div>';
    }
}

function applyAutoTuneSettings(settings) {
    if (settings.balance_db !== undefined) {
        document.getElementById('balanceSlider').value = settings.balance_db;
        document.getElementById('balanceValue').textContent = settings.balance_db.toFixed(1) + ' dB';
        updateBalanceMeter(settings.balance_db);
    }
    
    if (settings.fader_db !== undefined) {
        document.getElementById('faderSlider').value = settings.fader_db;
        document.getElementById('faderValue').textContent = settings.fader_db.toFixed(1) + ' dB';
        updateFaderMeter(settings.fader_db);
    }
}

async function generateSweepTone() {
    try {
        const response = await fetch(`${API_BASE}/api/measurement/sweep-tone`);
        const data = await response.json();
        
        if (data.ok) {
            alert(`Sweep Tone Generated\n\n` +
                  `${data.sweep_tone.start_frequency_hz}Hz - ${data.sweep_tone.end_frequency_hz}Hz\n` +
                  `Duration: ${data.sweep_tone.duration_seconds}s\n` +
                  `Sample Rate: ${data.sweep_tone.sample_rate_hz}Hz\n\n` +
                  `Follow the instructions in the measurement guide.`);
        }
    } catch (error) {
        console.error('Failed to generate sweep tone:', error);
    }
}

async function showMeasurementGuide() {
    try {
        const response = await fetch(`${API_BASE}/api/measurement/guide`);
        const data = await response.json();
        
        if (data.ok) {
            let guideText = 'MEASUREMENT GUIDE\n\n';
            guideText += 'Equipment Needed:\n';
            data.measurement_guide.equipment_needed.forEach(item => {
                guideText += '• ' + item + '\n';
            });
            guideText += '\nMeasurement Sequence:\n';
            data.measurement_guide.measurement_sequence.forEach((step, i) => {
                guideText += (i + 1) + '. ' + step + '\n';
            });
            
            alert(guideText);
        }
    } catch (error) {
        console.error('Failed to load measurement guide:', error);
    }
}

async function loadPreset() {
    const presetName = document.getElementById('presetSelect').value;
    if (!presetName) {
        alert('Please select a preset');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/presets/${presetName}`);
        const data = await response.json();
        
        if (data.ok && data.preset) {
            const preset = data.preset;
            
            if (preset.listening_position) {
                document.getElementById('listeningPosition').value = preset.listening_position;
                currentPosition = preset.listening_position;
            }
            
            if (preset.balance_settings && preset.balance_settings.balance_db !== undefined) {
                const balanceDb = preset.balance_settings.balance_db;
                document.getElementById('balanceSlider').value = balanceDb;
                document.getElementById('balanceValue').textContent = balanceDb.toFixed(1) + ' dB';
                updateBalanceMeter(balanceDb);
            }
            
            if (preset.fader_settings && preset.fader_settings.fader_db !== undefined) {
                const faderDb = preset.fader_settings.fader_db;
                document.getElementById('faderSlider').value = faderDb;
                document.getElementById('faderValue').textContent = faderDb.toFixed(1) + ' dB';
                updateFaderMeter(faderDb);
            }
            
            updateVisualization();
            
            alert(`Preset "${preset.preset_name || presetName}" loaded successfully`);
        }
    } catch (error) {
        console.error('Failed to load preset:', error);
        alert('Failed to load preset: ' + error.message);
    }
}

async function savePreset() {
    const presetName = prompt('Enter preset name:');
    if (!presetName) return;
    
    const description = prompt('Enter description (optional):') || '';
    
    try {
        const response = await fetch(`${API_BASE}/api/presets/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                preset_name: presetName,
                description: description,
                listening_position: currentPosition,
                balance_settings: {
                    balance_db: parseFloat(document.getElementById('balanceSlider').value)
                },
                fader_settings: {
                    fader_db: parseFloat(document.getElementById('faderSlider').value)
                }
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            alert(`Preset "${presetName}" saved successfully`);
        }
    } catch (error) {
        console.error('Failed to save preset:', error);
        alert('Failed to save preset: ' + error.message);
    }
}

async function applyToDSP() {
    if (!confirm('Apply current soundstage settings to DSP system?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/dsp/apply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                listening_position: currentPosition
            })
        });
        
        const data = await response.json();
        
        if (data.ok && data.applied_to_dsp) {
            alert('Settings applied to DSP system successfully!');
        } else {
            alert('Failed to apply to DSP: ' + (data.error || 'DSP service may not be available'));
        }
    } catch (error) {
        console.error('Failed to apply to DSP:', error);
        alert('Failed to apply to DSP: ' + error.message);
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    
    const contentMap = {
        'cabin': 'cabinTab',
        'modes': 'modesTab',
        'eq': 'eqTab'
    };
    
    const contentId = contentMap[tabName];
    if (contentId) {
        document.getElementById(contentId).classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', init);
