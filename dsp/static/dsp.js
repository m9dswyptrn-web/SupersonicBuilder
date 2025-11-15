// Advanced DSP Control Center - Frontend JavaScript
// Professional audio tuning interface

const API_BASE = window.location.origin;

let eqBands = [];
let currentEQCurve = [];
let analyzerInterval = null;
let currentSettings = {};

// Initialize DSP interface
async function initializeDSP() {
    console.log('🎚️ Initializing DSP Control Center...');
    
    try {
        await loadEQBandInfo();
        await loadPresets();
        await loadCurrentSettings();
        
        setupEQBands();
        setupCrossoverFrequencies();
        setupSpeakerDistances();
        updateBassDisplay();
        
        console.log('✅ DSP Control Center initialized successfully');
    } catch (error) {
        console.error('Error initializing DSP:', error);
        showAlert('error', 'Failed to initialize DSP Control Center');
    }
}

// Load EQ band information
async function loadEQBandInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/eq/info`);
        const data = await response.json();
        
        if (data.ok) {
            eqBands = data.bands;
        }
    } catch (error) {
        console.error('Error loading EQ info:', error);
    }
}

// Setup EQ band sliders
function setupEQBands() {
    const container = document.getElementById('eq-bands-container');
    container.innerHTML = '';
    
    eqBands.forEach((band, index) => {
        const bandDiv = document.createElement('div');
        bandDiv.className = 'eq-band';
        bandDiv.innerHTML = `
            <div class="eq-slider-container">
                <input type="range" 
                       class="eq-slider" 
                       id="eq-band-${index}" 
                       min="-12" 
                       max="12" 
                       step="0.5" 
                       value="0" 
                       orient="vertical"
                       oninput="updateEQValue(${index})">
            </div>
            <div class="eq-value" id="eq-value-${index}">0.0 dB</div>
            <div class="eq-frequency">${band.frequency}Hz</div>
        `;
        container.appendChild(bandDiv);
    });
}

// Update EQ value display
function updateEQValue(index) {
    const slider = document.getElementById(`eq-band-${index}`);
    const valueDisplay = document.getElementById(`eq-value-${index}`);
    const value = parseFloat(slider.value);
    valueDisplay.textContent = `${value >= 0 ? '+' : ''}${value.toFixed(1)} dB`;
}

// Update EQ channel
function updateEQChannel() {
    const channel = document.getElementById('eq-channel').value;
    console.log(`Switched to channel: ${channel}`);
}

// Apply EQ settings
async function applyEQ() {
    try {
        const gains = {};
        eqBands.forEach((band, index) => {
            const slider = document.getElementById(`eq-band-${index}`);
            gains[band.frequency] = parseFloat(slider.value);
        });
        
        const qFactor = parseFloat(document.getElementById('eq-q-factor').value);
        const channel = document.getElementById('eq-channel').value;
        
        const response = await fetch(`${API_BASE}/api/eq/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gains, q_factor: qFactor, channel })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            currentEQCurve = data.eq_curve;
            showAlert('eq', 'success', 'EQ applied successfully!');
            
            if (data.headroom_recommendation.clipping_risk !== 'low') {
                const warning = `⚠️ Clipping risk: ${data.headroom_recommendation.clipping_risk}. ` +
                              `Reduce master volume by ${data.headroom_recommendation.reduce_master_volume_db.toFixed(1)} dB.`;
                showAlert('eq', 'warning', warning);
            }
            
            await updateFrequencyResponse();
        } else {
            showAlert('eq', 'error', data.error);
        }
    } catch (error) {
        console.error('Error applying EQ:', error);
        showAlert('eq', 'error', 'Failed to apply EQ settings');
    }
}

// Reset EQ to flat
function resetEQ() {
    eqBands.forEach((band, index) => {
        const slider = document.getElementById(`eq-band-${index}`);
        slider.value = 0;
        updateEQValue(index);
    });
    showAlert('eq', 'success', 'EQ reset to flat');
}

// Apply Sonic cabin correction
async function applyCabinCorrection() {
    try {
        const gains = {};
        eqBands.forEach((band, index) => {
            const slider = document.getElementById(`eq-band-${index}`);
            gains[band.frequency] = parseFloat(slider.value);
        });
        
        const qFactor = parseFloat(document.getElementById('eq-q-factor').value);
        
        const eqResponse = await fetch(`${API_BASE}/api/eq/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gains, q_factor: qFactor, channel: 'all' })
        });
        
        const eqData = await eqResponse.json();
        
        if (eqData.ok) {
            const correctionResponse = await fetch(`${API_BASE}/api/eq/cabin-correction`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ eq_curve: eqData.eq_curve })
            });
            
            const correctionData = await correctionResponse.json();
            
            if (correctionData.ok) {
                correctionData.corrected_eq.forEach((band, index) => {
                    const slider = document.getElementById(`eq-band-${index}`);
                    slider.value = band.gain_db;
                    updateEQValue(index);
                });
                
                showAlert('eq', 'success', 'Chevy Sonic cabin correction applied!');
            }
        }
    } catch (error) {
        console.error('Error applying cabin correction:', error);
        showAlert('eq', 'error', 'Failed to apply cabin correction');
    }
}

// Update frequency response chart
async function updateFrequencyResponse() {
    try {
        const response = await fetch(`${API_BASE}/api/eq/frequency-response`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ eq_curve: currentEQCurve })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            displayFrequencyResponse(data.frequency_response);
        }
    } catch (error) {
        console.error('Error updating frequency response:', error);
    }
}

// Display frequency response (simple text visualization)
function displayFrequencyResponse(response) {
    const chart = document.getElementById('frequency-response-chart');
    chart.innerHTML = '<p style="color: #a0a0a0; padding: 20px;">Frequency response graph (simplified visualization)</p>';
    chart.innerHTML += `<p style="color: #00d4ff; padding: 10px;">Points: ${response.length} | Range: 20Hz - 20kHz</p>`;
}

// Setup crossover frequency inputs
function setupCrossoverFrequencies() {
    updateCrossoverConfig();
}

// Update crossover configuration
function updateCrossoverConfig() {
    const config = document.getElementById('crossover-config').value;
    const container = document.getElementById('crossover-frequencies-container');
    
    container.innerHTML = '<div class="controls-row">';
    
    if (config === '2-way') {
        container.innerHTML += `
            <div class="control-group">
                <label>Crossover Frequency (Hz)</label>
                <input type="number" id="crossover-freq-1" value="2500" min="20" max="20000">
            </div>
        `;
    } else if (config === '3-way') {
        container.innerHTML += `
            <div class="control-group">
                <label>Low-Mid Crossover (Hz)</label>
                <input type="number" id="crossover-freq-1" value="250" min="20" max="20000">
            </div>
            <div class="control-group">
                <label>Mid-High Crossover (Hz)</label>
                <input type="number" id="crossover-freq-2" value="2500" min="20" max="20000">
            </div>
        `;
    } else if (config === '4-way') {
        container.innerHTML += `
            <div class="control-group">
                <label>Sub-Low Crossover (Hz)</label>
                <input type="number" id="crossover-freq-1" value="80" min="20" max="20000">
            </div>
            <div class="control-group">
                <label>Low-Mid Crossover (Hz)</label>
                <input type="number" id="crossover-freq-2" value="250" min="20" max="20000">
            </div>
            <div class="control-group">
                <label>Mid-High Crossover (Hz)</label>
                <input type="number" id="crossover-freq-3" value="2500" min="20" max="20000">
            </div>
        `;
    }
    
    container.innerHTML += '</div>';
}

// Apply crossover settings
async function applyCrossover() {
    try {
        const config = document.getElementById('crossover-config').value;
        const filterType = document.getElementById('crossover-filter-type').value;
        const slopeDb = parseInt(document.getElementById('crossover-slope').value);
        
        let requestBody = { filter_type: filterType, slope_db: slopeDb };
        
        if (config === '2-way') {
            requestBody.frequency = parseInt(document.getElementById('crossover-freq-1').value);
        } else if (config === '3-way') {
            requestBody.low_mid_freq = parseInt(document.getElementById('crossover-freq-1').value);
            requestBody.mid_high_freq = parseInt(document.getElementById('crossover-freq-2').value);
        } else if (config === '4-way') {
            requestBody.sub_low_freq = parseInt(document.getElementById('crossover-freq-1').value);
            requestBody.low_mid_freq = parseInt(document.getElementById('crossover-freq-2').value);
            requestBody.mid_high_freq = parseInt(document.getElementById('crossover-freq-3').value);
        }
        
        const response = await fetch(`${API_BASE}/api/crossover/create/${config}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showAlert('crossover', 'success', `${config} crossover applied successfully!`);
        } else {
            showAlert('crossover', 'error', data.error);
        }
    } catch (error) {
        console.error('Error applying crossover:', error);
        showAlert('crossover', 'error', 'Failed to apply crossover settings');
    }
}

// Get recommended crossover frequencies
async function getRecommendedCrossover() {
    try {
        const config = document.getElementById('crossover-config').value;
        
        const response = await fetch(`${API_BASE}/api/crossover/recommend/${config}`);
        const data = await response.json();
        
        if (data.ok) {
            const rec = data.recommendations;
            let message = `${rec.description}\n\nRecommended frequencies:\n`;
            rec.frequencies.forEach((freq, index) => {
                message += `Crossover ${index + 1}: ${freq} Hz\n`;
            });
            message += `\n${rec.notes}`;
            
            alert(message);
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
    }
}

// Setup speaker distance inputs
function setupSpeakerDistances() {
    const container = document.getElementById('speaker-distances-container');
    const speakers = ['front_left', 'front_right', 'rear_left', 'rear_right', 'subwoofer'];
    const labels = ['Front Left', 'Front Right', 'Rear Left', 'Rear Right', 'Subwoofer'];
    
    container.innerHTML = '';
    
    speakers.forEach((speaker, index) => {
        const div = document.createElement('div');
        div.className = 'control-group';
        div.innerHTML = `
            <label>${labels[index]} Distance</label>
            <input type="number" id="dist-${speaker}" value="0" step="1" min="0">
        `;
        container.appendChild(div);
    });
}

// Calculate time alignment
async function calculateTimeAlignment() {
    try {
        const speakers = ['front_left', 'front_right', 'rear_left', 'rear_right', 'subwoofer'];
        const distances = {};
        
        speakers.forEach(speaker => {
            const input = document.getElementById(`dist-${speaker}`);
            distances[speaker] = parseFloat(input.value);
        });
        
        const listeningPosition = document.getElementById('ta-listening-position').value;
        const distanceUnit = document.getElementById('ta-distance-unit').value;
        
        const response = await fetch(`${API_BASE}/api/time-alignment/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                speaker_distances: distances,
                listening_position: listeningPosition,
                distance_unit: distanceUnit
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showAlert('ta', 'success', 'Time alignment calculated successfully!');
            displaySoundstageVisualization(data.time_alignment);
        } else {
            showAlert('ta', 'error', data.error);
        }
    } catch (error) {
        console.error('Error calculating time alignment:', error);
        showAlert('ta', 'error', 'Failed to calculate time alignment');
    }
}

// Load Sonic default speaker positions
async function loadSonicDefaults() {
    try {
        const listeningPosition = document.getElementById('ta-listening-position').value;
        
        const response = await fetch(`${API_BASE}/api/time-alignment/sonic-defaults/${listeningPosition}`);
        const data = await response.json();
        
        if (data.ok) {
            const speakers = data.time_alignment.speakers;
            
            for (const [speaker, speakerData] of Object.entries(speakers)) {
                const input = document.getElementById(`dist-${speaker}`);
                if (input) {
                    input.value = speakerData.distance_inches.toFixed(1);
                }
            }
            
            showAlert('ta', 'success', 'Loaded default Chevy Sonic speaker positions');
            displaySoundstageVisualization(data.time_alignment);
        }
    } catch (error) {
        console.error('Error loading Sonic defaults:', error);
        showAlert('ta', 'error', 'Failed to load default positions');
    }
}

// Display soundstage visualization
async function displaySoundstageVisualization(timeAlignment) {
    try {
        const response = await fetch(`${API_BASE}/api/time-alignment/visualize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ speaker_delays: timeAlignment })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            const container = document.getElementById('soundstage-diagram');
            container.innerHTML = '';
            
            data.visualization.speakers.forEach(speaker => {
                const speakerDiv = document.createElement('div');
                speakerDiv.className = 'speaker-icon';
                speakerDiv.style.left = `${50 + speaker.x}%`;
                speakerDiv.style.top = `${50 + speaker.y}%`;
                speakerDiv.innerHTML = `
                    <div class="speaker-label">${speaker.name}</div>
                    ${speaker.delay_ms.toFixed(2)}ms
                `;
                container.appendChild(speakerDiv);
            });
        }
    } catch (error) {
        console.error('Error displaying soundstage:', error);
    }
}

// Update bass management display
function updateBassDisplay() {
    const level = parseFloat(document.getElementById('bass-level').value);
    const subsonic = parseInt(document.getElementById('bass-subsonic').value);
    const boost = parseFloat(document.getElementById('bass-boost').value);
    const phase = parseInt(document.getElementById('bass-phase').value);
    
    document.getElementById('bass-level-display').textContent = `${level >= 0 ? '+' : ''}${level.toFixed(1)} dB`;
    document.getElementById('bass-subsonic-display').textContent = `${subsonic} Hz`;
    document.getElementById('bass-boost-display').textContent = `${boost.toFixed(1)} dB`;
    document.getElementById('bass-phase-display').textContent = `${phase}°`;
}

// Apply bass settings
async function applyBassSettings() {
    try {
        const settings = {
            level_db: parseFloat(document.getElementById('bass-level').value),
            subsonic_filter_hz: parseInt(document.getElementById('bass-subsonic').value),
            boost_db: parseFloat(document.getElementById('bass-boost').value),
            phase_degrees: parseInt(document.getElementById('bass-phase').value)
        };
        
        const response = await fetch(`${API_BASE}/api/bass/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showAlert('bass', 'success', 'Bass settings applied successfully!');
        } else {
            showAlert('bass', 'error', data.error);
        }
    } catch (error) {
        console.error('Error applying bass settings:', error);
        showAlert('bass', 'error', 'Failed to apply bass settings');
    }
}

// Apply loudness settings
async function applyLoudnessSettings() {
    try {
        const settings = {
            enabled: document.getElementById('loudness-enabled').value === 'true',
            compensation_curve: document.getElementById('loudness-curve').value
        };
        
        const response = await fetch(`${API_BASE}/api/loudness/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showAlert('bass', 'success', 'Loudness settings applied successfully!');
        } else {
            showAlert('bass', 'error', data.error);
        }
    } catch (error) {
        console.error('Error applying loudness settings:', error);
        showAlert('bass', 'error', 'Failed to apply loudness settings');
    }
}

// Start spectrum analyzer
function startAnalyzer() {
    if (analyzerInterval) {
        clearInterval(analyzerInterval);
    }
    
    const signalType = document.getElementById('analyzer-signal-type').value;
    const includePeaks = document.getElementById('analyzer-peak-hold').value === 'true';
    
    setupSpectrumBars();
    
    analyzerInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/analyzer/spectrum?signal_type=${signalType}&include_peaks=${includePeaks}`);
            const data = await response.json();
            
            if (data.ok) {
                updateSpectrumDisplay(data.spectrum);
            }
        } catch (error) {
            console.error('Error fetching spectrum:', error);
        }
    }, 100);
}

// Stop spectrum analyzer
function stopAnalyzer() {
    if (analyzerInterval) {
        clearInterval(analyzerInterval);
        analyzerInterval = null;
    }
}

// Reset peak hold values
async function resetPeaks() {
    try {
        const response = await fetch(`${API_BASE}/api/analyzer/reset-peaks`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            console.log('Peak hold values reset');
        }
    } catch (error) {
        console.error('Error resetting peaks:', error);
    }
}

// Setup spectrum bars
function setupSpectrumBars() {
    const container = document.getElementById('spectrum-bars');
    container.innerHTML = '';
    
    for (let i = 0; i < 31; i++) {
        const bar = document.createElement('div');
        bar.className = 'spectrum-bar';
        bar.id = `spectrum-bar-${i}`;
        container.appendChild(bar);
    }
}

// Update spectrum display
function updateSpectrumDisplay(spectrum) {
    spectrum.bands.forEach((band, index) => {
        const bar = document.getElementById(`spectrum-bar-${index}`);
        if (bar) {
            const levelPercent = Math.max(0, Math.min(100, ((band.level_db + 96) / 96) * 100));
            bar.style.height = `${levelPercent}%`;
        }
    });
}

// Load presets
async function loadPresets() {
    try {
        const response = await fetch(`${API_BASE}/api/presets`);
        const data = await response.json();
        
        if (data.ok) {
            displayPresets(data.presets);
        }
    } catch (error) {
        console.error('Error loading presets:', error);
    }
}

// Display presets
function displayPresets(presets) {
    const builtinContainer = document.getElementById('builtin-presets');
    const userContainer = document.getElementById('user-presets');
    
    builtinContainer.innerHTML = '';
    userContainer.innerHTML = '';
    
    presets.forEach(preset => {
        const button = document.createElement('button');
        button.className = 'btn-secondary btn';
        button.textContent = preset.name;
        button.onclick = () => loadPreset(preset.id);
        
        if (preset.type === 'builtin') {
            builtinContainer.appendChild(button);
        } else {
            userContainer.appendChild(button);
        }
    });
}

// Load preset
async function loadPreset(presetName) {
    try {
        const response = await fetch(`${API_BASE}/api/presets/${presetName}/load`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showAlert('preset', 'success', `Preset "${presetName}" loaded successfully!`);
            location.reload();
        } else {
            showAlert('preset', 'error', data.error);
        }
    } catch (error) {
        console.error('Error loading preset:', error);
        showAlert('preset', 'error', 'Failed to load preset');
    }
}

// Save preset
async function savePreset() {
    try {
        const name = document.getElementById('preset-name').value.trim();
        const description = document.getElementById('preset-description').value.trim();
        
        if (!name) {
            showAlert('preset', 'error', 'Please enter a preset name');
            return;
        }
        
        const presetId = name.toLowerCase().replace(/[^a-z0-9]+/g, '_');
        
        const response = await fetch(`${API_BASE}/api/presets/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                preset_id: presetId,
                name: name,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showAlert('preset', 'success', `Preset "${name}" saved successfully!`);
            await loadPresets();
        } else {
            showAlert('preset', 'error', data.error);
        }
    } catch (error) {
        console.error('Error saving preset:', error);
        showAlert('preset', 'error', 'Failed to save preset');
    }
}

// Export Android configuration
async function exportAndroidConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/export/android-full`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            const jsonStr = JSON.stringify(data.android_config, null, 2);
            downloadJSON(jsonStr, 'eoenkk_dsp_config.json');
            showAlert('preset', 'success', 'Android configuration exported!');
        } else {
            showAlert('preset', 'error', data.error);
        }
    } catch (error) {
        console.error('Error exporting Android config:', error);
        showAlert('preset', 'error', 'Failed to export configuration');
    }
}

// Export preset as JSON
async function exportPresetJSON() {
    try {
        const response = await fetch(`${API_BASE}/api/current-settings`);
        const data = await response.json();
        
        if (data.ok) {
            const jsonStr = JSON.stringify(data.settings, null, 2);
            downloadJSON(jsonStr, 'dsp_preset.json');
            showAlert('preset', 'success', 'Preset exported as JSON!');
        }
    } catch (error) {
        console.error('Error exporting preset:', error);
        showAlert('preset', 'error', 'Failed to export preset');
    }
}

// Download JSON file
function downloadJSON(jsonStr, filename) {
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Load current settings
async function loadCurrentSettings() {
    try {
        const response = await fetch(`${API_BASE}/api/current-settings`);
        const data = await response.json();
        
        if (data.ok) {
            currentSettings = data.settings;
        }
    } catch (error) {
        console.error('Error loading current settings:', error);
    }
}

// Show alert message
function showAlert(context, type, message) {
    const containerId = context + '-alert-container';
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.warn(`Alert container ${containerId} not found`);
        return;
    }
    
    let alertClass = 'alert-success';
    if (type === 'error') alertClass = 'alert-danger';
    if (type === 'warning') alertClass = 'alert-warning';
    
    container.innerHTML = `
        <div class="alert ${alertClass}">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

console.log('🎚️ DSP Control Center JavaScript loaded');
