// Real-Time Audio Visualizer - WebGL Rendering Engine
// Optimized for 2000×1200 QLED @ 60 FPS

const canvas = document.getElementById('canvas');
const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

if (!gl) {
    alert('WebGL not supported! Please use a modern browser.');
}

// Configuration
let config = {
    visualizationMode: 'spectrum_bars',
    numBands: 31,
    theme: 'dark',
    effectIntensity: 0.8,
    showParticles: true,
    showVU: true,
    rgbSync: true
};

// State
let currentAnalysis = null;
let currentTheme = null;
let particles = [];
let lastFrameTime = performance.now();
let fps = 60;
let animationFrameId = null;

// WebGL Setup
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    gl.viewport(0, 0, canvas.width, canvas.height);
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Theme Colors
const themes = {
    dark: {
        background: [0.04, 0.04, 0.04],
        spectrumColors: [
            [0, 1, 1],      // Cyan
            [0, 1, 0.53],   // Spring green
            [0.53, 1, 0],   // Chartreuse
            [1, 1, 0],      // Yellow
            [1, 0.53, 0],   // Orange
            [1, 0, 0]       // Red
        ]
    },
    neon: {
        background: [0, 0, 0],
        spectrumColors: [
            [1, 0, 1],      // Magenta
            [1, 0, 0.67],   
            [1, 0, 0.33],   
            [1, 0, 0],      // Red
            [1, 0.67, 0],   
            [1, 1, 0]       // Yellow
        ]
    },
    retro: {
        background: [0.1, 0.06, 0.04],
        spectrumColors: [
            [1, 0, 0.67],   
            [1, 0, 0.4],    
            [1, 0.4, 0],    
            [1, 0.67, 0],   
            [1, 0.87, 0],   
            [1, 1, 0.53]    
        ]
    },
    minimal: {
        background: [0.96, 0.96, 0.96],
        spectrumColors: [
            [0.2, 0.2, 0.2],
            [0.33, 0.33, 0.33],
            [0.47, 0.47, 0.47],
            [0.6, 0.6, 0.6],
            [0.73, 0.73, 0.73],
            [0.87, 0.87, 0.87]
        ]
    },
    ocean: {
        background: [0, 0.1, 0.18],
        spectrumColors: [
            [0, 0, 0.33],
            [0, 0.33, 0.67],
            [0, 0.67, 1],
            [0, 1, 1],
            [0.67, 1, 1],
            [1, 1, 1]
        ]
    },
    fire: {
        background: [0.1, 0, 0],
        spectrumColors: [
            [0.27, 0, 0],
            [0.53, 0, 0],
            [0.8, 0.13, 0],
            [1, 0.27, 0],
            [1, 0.53, 0],
            [1, 0.87, 0]
        ]
    }
};

// Get color for band position
function getSpectrumColor(position, theme) {
    const colors = themes[theme].spectrumColors;
    const index = position * (colors.length - 1);
    const lowerIndex = Math.floor(index);
    const upperIndex = Math.ceil(index);
    const t = index - lowerIndex;
    
    const lower = colors[lowerIndex] || colors[0];
    const upper = colors[upperIndex] || colors[colors.length - 1];
    
    return [
        lower[0] + (upper[0] - lower[0]) * t,
        lower[1] + (upper[1] - lower[1]) * t,
        lower[2] + (upper[2] - lower[2]) * t
    ];
}

// Rendering Functions
function drawSpectrumBars(bandLevels) {
    const numBands = bandLevels.length;
    const barWidth = (canvas.width * 0.9) / numBands;
    const gap = barWidth * 0.1;
    const startX = canvas.width * 0.05;
    const baseY = canvas.height * 0.85;
    const maxHeight = canvas.height * 0.7;
    
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    
    for (let i = 0; i < numBands; i++) {
        const level = bandLevels[i];
        const x = startX + i * barWidth;
        const height = level * maxHeight;
        const y = baseY - height;
        
        const color = getSpectrumColor(i / numBands, config.theme);
        const alpha = 0.7 + level * 0.3;
        
        drawRect(x, y, barWidth - gap, height, [...color, alpha]);
        
        if (config.effectIntensity > 0.5) {
            const glowHeight = height * 0.3;
            const glowAlpha = level * config.effectIntensity * 0.3;
            drawRect(x, y - glowHeight, barWidth - gap, glowHeight, [...color, glowAlpha]);
        }
    }
}

function drawSpectrumLines(bandLevels) {
    const numBands = bandLevels.length;
    const width = canvas.width * 0.9;
    const startX = canvas.width * 0.05;
    const baseY = canvas.height * 0.85;
    const maxHeight = canvas.height * 0.7;
    
    gl.lineWidth(3);
    
    const points = [];
    for (let i = 0; i < numBands; i++) {
        const x = startX + (i / (numBands - 1)) * width;
        const y = baseY - bandLevels[i] * maxHeight;
        points.push([x, y]);
    }
    
    for (let i = 0; i < points.length - 1; i++) {
        const color = getSpectrumColor(i / numBands, config.theme);
        drawLine(points[i], points[i + 1], color);
    }
}

function drawCircularSpectrum(bandLevels) {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const baseRadius = Math.min(canvas.width, canvas.height) * 0.2;
    const maxRadius = Math.min(canvas.width, canvas.height) * 0.4;
    const numBands = bandLevels.length;
    
    for (let i = 0; i < numBands; i++) {
        const angle = (i / numBands) * Math.PI * 2 - Math.PI / 2;
        const level = bandLevels[i];
        const radius = baseRadius + level * maxRadius;
        
        const x1 = centerX + Math.cos(angle) * baseRadius;
        const y1 = centerY + Math.sin(angle) * baseRadius;
        const x2 = centerX + Math.cos(angle) * radius;
        const y2 = centerY + Math.sin(angle) * radius;
        
        const color = getSpectrumColor(i / numBands, config.theme);
        const width = 3 + level * 5;
        
        drawThickLine([x1, y1], [x2, y2], color, width);
    }
    
    drawCircle(centerX, centerY, baseRadius, getSpectrumColor(0.5, config.theme), 2);
}

function drawWaveform(audioData) {
    if (!audioData || audioData.length === 0) return;
    
    const centerY = canvas.height / 2;
    const amplitude = canvas.height * 0.3;
    const width = canvas.width * 0.9;
    const startX = canvas.width * 0.05;
    
    const points = [];
    const step = Math.max(1, Math.floor(audioData.length / width));
    
    for (let i = 0; i < audioData.length; i += step) {
        const x = startX + (i / audioData.length) * width;
        const y = centerY + audioData[i] * amplitude;
        points.push([x, y]);
    }
    
    const color = getSpectrumColor(0.5, config.theme);
    
    for (let i = 0; i < points.length - 1; i++) {
        drawLine(points[i], points[i + 1], color);
    }
}

function drawVUMeters(bassLevel, midLevel, trebleLevel) {
    if (!config.showVU) return;
    
    const meterWidth = canvas.width * 0.15;
    const meterHeight = 30;
    const spacing = 50;
    const startY = canvas.height - 120;
    const startX = canvas.width * 0.05;
    
    drawVUMeter(startX, startY, meterWidth, meterHeight, bassLevel, 'BASS');
    drawVUMeter(startX, startY + spacing, meterWidth, meterHeight, midLevel, 'MID');
    drawVUMeter(startX, startY + spacing * 2, meterWidth, meterHeight, trebleLevel, 'TREBLE');
}

function drawVUMeter(x, y, width, height, level, label) {
    drawRect(x, y, width, height, [0.2, 0.2, 0.2, 0.8]);
    
    const fillWidth = width * level;
    let color;
    if (level < 0.7) {
        color = [0, 1, 0.53, 0.9];
    } else if (level < 0.9) {
        color = [1, 1, 0, 0.9];
    } else {
        color = [1, 0, 0, 0.9];
    }
    
    drawRect(x, y, fillWidth, height, color);
}

function drawParticles() {
    if (!config.showParticles || !currentAnalysis?.effects?.particles) return;
    
    const particleData = currentAnalysis.effects.particles;
    
    for (const particle of particleData) {
        const x = particle.x * canvas.width;
        const y = particle.y * canvas.height;
        const size = particle.size;
        const color = particle.color;
        const alpha = particle.life;
        
        const r = color[0] / 255;
        const g = color[1] / 255;
        const b = color[2] / 255;
        
        drawCircle(x, y, size, [r, g, b, alpha]);
    }
}

// Primitive Drawing Functions (WebGL)
function drawRect(x, y, width, height, color) {
    const x1 = (x / canvas.width) * 2 - 1;
    const y1 = 1 - (y / canvas.height) * 2;
    const x2 = ((x + width) / canvas.width) * 2 - 1;
    const y2 = 1 - ((y + height) / canvas.height) * 2;
    
    const vertices = new Float32Array([
        x1, y1,
        x2, y1,
        x1, y2,
        x2, y2
    ]);
    
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    
    if (!window.shaderProgram) {
        initShaders();
    }
    
    gl.useProgram(window.shaderProgram);
    
    const position = gl.getAttribLocation(window.shaderProgram, 'a_position');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    
    const colorLocation = gl.getUniformLocation(window.shaderProgram, 'u_color');
    gl.uniform4f(colorLocation, color[0], color[1], color[2], color[3] || 1.0);
    
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    
    gl.deleteBuffer(buffer);
}

function drawLine(p1, p2, color) {
    const x1 = (p1[0] / canvas.width) * 2 - 1;
    const y1 = 1 - (p1[1] / canvas.height) * 2;
    const x2 = (p2[0] / canvas.width) * 2 - 1;
    const y2 = 1 - (p2[1] / canvas.height) * 2;
    
    const vertices = new Float32Array([x1, y1, x2, y2]);
    
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    
    if (!window.shaderProgram) {
        initShaders();
    }
    
    gl.useProgram(window.shaderProgram);
    
    const position = gl.getAttribLocation(window.shaderProgram, 'a_position');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    
    const colorLocation = gl.getUniformLocation(window.shaderProgram, 'u_color');
    gl.uniform4f(colorLocation, color[0], color[1], color[2], 1.0);
    
    gl.drawArrays(gl.LINES, 0, 2);
    
    gl.deleteBuffer(buffer);
}

function drawThickLine(p1, p2, color, thickness) {
    for (let i = 0; i < thickness; i++) {
        drawLine([p1[0] + i, p1[1]], [p2[0] + i, p2[1]], color);
    }
}

function drawCircle(x, y, radius, color, thickness = 0) {
    const segments = 32;
    const vertices = [];
    
    for (let i = 0; i <= segments; i++) {
        const angle = (i / segments) * Math.PI * 2;
        const px = x + Math.cos(angle) * radius;
        const py = y + Math.sin(angle) * radius;
        vertices.push((px / canvas.width) * 2 - 1);
        vertices.push(1 - (py / canvas.height) * 2);
    }
    
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
    
    if (!window.shaderProgram) {
        initShaders();
    }
    
    gl.useProgram(window.shaderProgram);
    
    const position = gl.getAttribLocation(window.shaderProgram, 'a_position');
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
    
    const colorLocation = gl.getUniformLocation(window.shaderProgram, 'u_color');
    gl.uniform4f(colorLocation, color[0], color[1], color[2], color[3] || 1.0);
    
    gl.drawArrays(thickness > 0 ? gl.LINE_LOOP : gl.TRIANGLE_FAN, 0, segments + 1);
    
    gl.deleteBuffer(buffer);
}

// Shader Initialization
function initShaders() {
    const vertexShaderSource = `
        attribute vec2 a_position;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
        }
    `;
    
    const fragmentShaderSource = `
        precision mediump float;
        uniform vec4 u_color;
        void main() {
            gl_FragColor = u_color;
        }
    `;
    
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertexShader, vertexShaderSource);
    gl.compileShader(vertexShader);
    
    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragmentShader, fragmentShaderSource);
    gl.compileShader(fragmentShader);
    
    window.shaderProgram = gl.createProgram();
    gl.attachShader(window.shaderProgram, vertexShader);
    gl.attachShader(window.shaderProgram, fragmentShader);
    gl.linkProgram(window.shaderProgram);
}

// Main Render Loop
function render() {
    const now = performance.now();
    const deltaTime = now - lastFrameTime;
    fps = Math.round(1000 / deltaTime);
    lastFrameTime = now;
    
    const bg = themes[config.theme].background;
    gl.clearColor(bg[0], bg[1], bg[2], 1.0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    
    if (currentAnalysis) {
        const bandLevels = currentAnalysis.fft.band_levels;
        
        switch (config.visualizationMode) {
            case 'spectrum_bars':
                drawSpectrumBars(bandLevels);
                break;
            case 'spectrum_lines':
                drawSpectrumLines(bandLevels);
                break;
            case 'circular':
                drawCircularSpectrum(bandLevels);
                break;
            case 'waveform':
            case 'dual_waveform':
                drawWaveform(bandLevels);
                break;
        }
        
        drawParticles();
        
        drawVUMeters(
            currentAnalysis.fft.bass_level,
            currentAnalysis.fft.mid_level,
            currentAnalysis.fft.treble_level
        );
        
        updateUI();
    }
    
    animationFrameId = requestAnimationFrame(render);
}

// UI Updates
function updateUI() {
    if (!currentAnalysis) return;
    
    document.getElementById('fps').textContent = fps;
    document.getElementById('bpm-value').textContent = Math.round(currentAnalysis.beat.bpm);
    document.getElementById('particles-count').textContent = currentAnalysis.effects.particles.length;
    
    if (currentAnalysis.beat.beat_detected) {
        const indicator = document.getElementById('beat-indicator');
        indicator.classList.remove('pulse');
        void indicator.offsetWidth;
        indicator.classList.add('pulse');
        
        if (config.rgbSync) {
            sendRGBData(currentAnalysis.rgb_lighting);
        }
    }
}

// API Functions
async function fetchAnalysis() {
    try {
        const testSignal = await generateTestAudioData();
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                audio_data: testSignal,
                num_bands: config.numBands
            })
        });
        
        const data = await response.json();
        if (data.ok) {
            currentAnalysis = data.analysis;
        }
    } catch (error) {
        console.error('Analysis error:', error);
    }
}

async function generateTestAudioData() {
    const duration = 0.05;
    const sampleRate = 48000;
    const numSamples = Math.floor(duration * sampleRate);
    const signal = [];
    
    for (let i = 0; i < numSamples; i++) {
        const t = i / sampleRate;
        let sample = 0;
        sample += Math.sin(2 * Math.PI * 100 * t) * 0.3;
        sample += Math.sin(2 * Math.PI * 440 * t) * 0.3;
        sample += Math.sin(2 * Math.PI * 1000 * t) * 0.2;
        sample += (Math.random() - 0.5) * 0.2;
        signal.push(sample);
    }
    
    return signal;
}

async function generateTestSignal(type) {
    try {
        const response = await fetch(`/api/test/generate/${type}`);
        const data = await response.json();
        if (data.ok) {
            console.log('Generated test signal:', type);
        }
    } catch (error) {
        console.error('Test signal error:', error);
    }
}

async function sendRGBData(rgbData) {
    try {
        await fetch('/api/rgb/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(rgbData)
        });
    } catch (error) {
        // Silently fail if RGB controller not available
    }
}

async function saveSettings() {
    try {
        await fetch('/api/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config)
        });
    } catch (error) {
        console.error('Save settings error:', error);
    }
}

// Event Handlers
document.getElementById('viz-mode').addEventListener('change', (e) => {
    config.visualizationMode = e.target.value;
    document.getElementById('mode-display').textContent = e.target.options[e.target.selectedIndex].text;
    saveSettings();
});

document.getElementById('num-bands').addEventListener('change', (e) => {
    config.numBands = parseInt(e.target.value);
    document.getElementById('bands-display').textContent = e.target.value;
    saveSettings();
});

document.getElementById('effect-intensity').addEventListener('input', (e) => {
    config.effectIntensity = parseInt(e.target.value) / 100;
    document.getElementById('intensity-value').textContent = e.target.value + '%';
    saveSettings();
});

document.getElementById('show-particles').addEventListener('change', (e) => {
    config.showParticles = e.target.checked;
    saveSettings();
});

document.getElementById('show-vu').addEventListener('change', (e) => {
    config.showVU = e.target.checked;
    saveSettings();
});

document.getElementById('rgb-sync').addEventListener('change', (e) => {
    config.rgbSync = e.target.checked;
    saveSettings();
});

document.querySelectorAll('.theme-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.theme-button').forEach(b => b.classList.remove('active'));
        button.classList.add('active');
        config.theme = button.dataset.theme;
        saveSettings();
    });
});

document.getElementById('toggle-controls').addEventListener('click', () => {
    document.getElementById('controls').classList.toggle('hidden');
});

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'f' || e.key === 'F') {
        toggleFullscreen();
    }
});

// Initialize
initShaders();
setInterval(fetchAnalysis, 1000 / 60);
render();

console.log('🎵 Real-Time Audio Visualizer initialized');
console.log('🖥️  Optimized for 2000×1200 QLED @ 60 FPS');
