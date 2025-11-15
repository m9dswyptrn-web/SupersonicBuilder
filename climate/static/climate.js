// Advanced Climate Control UI JavaScript
// Real-time updates and interactive controls

class ClimateControl {
    constructor() {
        this.state = {
            driver_temp_f: 72,
            passenger_temp_f: 72,
            fan_speed: 0,
            mode: 'auto',
            ac_enabled: false,
            max_ac: false,
            recirculation: false,
            defrost_front: false,
            defrost_rear: false,
            heated_mirrors: false,
            auto_mode: false,
            heated_seat_driver: 0,
            heated_seat_passenger: 0
        };
        
        this.maestroConnected = false;
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadStatus();
        this.startAutoUpdate();
    }
    
    setupEventListeners() {
        // Temperature sliders
        document.getElementById('driver-slider').addEventListener('input', (e) => {
            this.updateTemperature(e.target.value, 'driver');
        });
        
        document.getElementById('passenger-slider').addEventListener('input', (e) => {
            this.updateTemperature(e.target.value, 'passenger');
        });
        
        // Fan speed buttons
        document.querySelectorAll('.fan-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const speed = parseInt(e.target.dataset.speed);
                this.setFanSpeed(speed);
            });
        });
        
        // Mode buttons
        document.querySelectorAll('.mode-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.setMode(mode);
            });
        });
        
        // Toggle buttons
        document.getElementById('ac-toggle').addEventListener('click', () => this.toggleAC());
        document.getElementById('max-ac-toggle').addEventListener('click', () => this.toggleMaxAC());
        document.getElementById('recirc-toggle').addEventListener('click', () => this.toggleRecirculation());
        document.getElementById('auto-toggle').addEventListener('click', () => this.toggleAuto());
        document.getElementById('defrost-front-toggle').addEventListener('click', () => this.toggleDefrost('front'));
        document.getElementById('defrost-rear-toggle').addEventListener('click', () => this.toggleDefrost('rear'));
        document.getElementById('heated-mirrors-toggle').addEventListener('click', () => this.toggleHeatedMirrors());
        document.getElementById('sync-toggle').addEventListener('click', () => this.syncFromVehicle());
        
        // Preset buttons
        document.querySelectorAll('.preset-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const preset = e.currentTarget.dataset.preset;
                this.applyPreset(preset);
            });
        });
        
        // Heated seat controls
        document.querySelectorAll('.seat-level').forEach(button => {
            button.addEventListener('click', (e) => {
                const seat = e.currentTarget.dataset.seat;
                const level = parseInt(e.currentTarget.dataset.level);
                this.setHeatedSeat(seat, level);
            });
        });
    }
    
    async loadStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.ok) {
                this.updateStateFromAPI(data.state);
                this.maestroConnected = data.maestro_connected;
                this.updateMaestroStatus();
            }
        } catch (error) {
            console.error('Error loading status:', error);
        }
    }
    
    async updateTemperature(tempF, zone) {
        const displayId = zone === 'driver' ? 'driver-temp' : 'passenger-temp';
        document.getElementById(displayId).textContent = `${tempF}°F`;
        
        if (zone === 'driver') {
            this.state.driver_temp_f = tempF;
        } else {
            this.state.passenger_temp_f = tempF;
        }
        
        try {
            const response = await fetch('/api/temperature', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    temperature: parseFloat(tempF),
                    zone: zone,
                    unit: 'F'
                })
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error setting temperature:', error);
        }
    }
    
    async setFanSpeed(speed) {
        this.state.fan_speed = speed;
        
        // Update UI
        document.querySelectorAll('.fan-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-speed="${speed}"]`).classList.add('active');
        
        // Update fan animation
        const fanIcon = document.getElementById('fan-icon');
        fanIcon.className = `fan-animation speed-${speed}`;
        
        // Update footer
        document.getElementById('current-fan').textContent = speed === 0 ? 'OFF' : 
                                                             speed === 7 ? 'Auto' : 
                                                             `Level ${speed}`;
        
        try {
            const response = await fetch('/api/fan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({speed: speed, zone: 'driver'})
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error setting fan speed:', error);
        }
    }
    
    async setMode(mode) {
        this.state.mode = mode;
        
        // Update UI
        document.querySelectorAll('.mode-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        // Update footer
        const modeLabels = {
            'face': 'Face',
            'feet': 'Feet',
            'defrost': 'Defrost',
            'face_feet': 'Face+Feet',
            'auto': 'Auto'
        };
        document.getElementById('current-mode').textContent = modeLabels[mode] || mode;
        
        try {
            const response = await fetch('/api/mode', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mode: mode})
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error setting mode:', error);
        }
    }
    
    async toggleAC() {
        try {
            const response = await fetch('/api/ac', {method: 'POST'});
            const data = await response.json();
            
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error toggling AC:', error);
        }
    }
    
    async toggleMaxAC() {
        try {
            const enabled = !this.state.max_ac;
            const response = await fetch('/api/max-ac', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: enabled})
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error toggling max AC:', error);
        }
    }
    
    async toggleRecirculation() {
        try {
            const response = await fetch('/api/recirculation', {method: 'POST'});
            const data = await response.json();
            
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error toggling recirculation:', error);
        }
    }
    
    async toggleDefrost(location) {
        try {
            const response = await fetch('/api/defrost', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({location: location})
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error toggling defrost:', error);
        }
    }
    
    async toggleHeatedMirrors() {
        try {
            const response = await fetch('/api/heated-mirrors', {method: 'POST'});
            const data = await response.json();
            
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error toggling heated mirrors:', error);
        }
    }
    
    async toggleAuto() {
        try {
            const enabled = !this.state.auto_mode;
            const response = await fetch('/api/auto', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: enabled})
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error toggling auto:', error);
        }
    }
    
    async setHeatedSeat(seat, level) {
        try {
            const response = await fetch('/api/heated-seat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({seat: seat, level: level})
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error setting heated seat:', error);
        }
    }
    
    async applyPreset(presetName) {
        try {
            const response = await fetch(`/api/preset/apply/${presetName}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            if (data.ok) {
                this.updateStateFromAPI(data.state);
            }
        } catch (error) {
            console.error('Error applying preset:', error);
        }
    }
    
    async syncFromVehicle() {
        try {
            const response = await fetch('/api/sync', {method: 'POST'});
            const data = await response.json();
            
            if (data.ok) {
                this.updateStateFromAPI(data.state);
                // Visual feedback
                const syncBtn = document.getElementById('sync-toggle');
                syncBtn.style.backgroundColor = 'rgba(0, 255, 0, 0.3)';
                setTimeout(() => {
                    syncBtn.style.backgroundColor = '';
                }, 1000);
            }
        } catch (error) {
            console.error('Error syncing from vehicle:', error);
        }
    }
    
    updateStateFromAPI(state) {
        if (!state) return;
        
        // Update temperatures
        if (state.driver_zone) {
            const tempF = this.celsiusToFahrenheit(state.driver_zone.temperature);
            this.state.driver_temp_f = Math.round(tempF);
            document.getElementById('driver-temp').textContent = `${this.state.driver_temp_f}°F`;
            document.getElementById('driver-slider').value = this.state.driver_temp_f;
            
            // Heated seat
            this.state.heated_seat_driver = state.driver_zone.heated_seat_level || 0;
            this.updateHeatedSeatUI('driver', this.state.heated_seat_driver);
        }
        
        if (state.passenger_zone) {
            const tempF = this.celsiusToFahrenheit(state.passenger_zone.temperature);
            this.state.passenger_temp_f = Math.round(tempF);
            document.getElementById('passenger-temp').textContent = `${this.state.passenger_temp_f}°F`;
            document.getElementById('passenger-slider').value = this.state.passenger_temp_f;
            
            // Heated seat
            this.state.heated_seat_passenger = state.passenger_zone.heated_seat_level || 0;
            this.updateHeatedSeatUI('passenger', this.state.heated_seat_passenger);
        }
        
        // Update fan speed
        if (state.driver_zone && state.driver_zone.fan_speed !== undefined) {
            this.state.fan_speed = state.driver_zone.fan_speed;
            document.querySelectorAll('.fan-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-speed="${this.state.fan_speed}"]`)?.classList.add('active');
            
            const fanIcon = document.getElementById('fan-icon');
            fanIcon.className = `fan-animation speed-${this.state.fan_speed}`;
            
            document.getElementById('current-fan').textContent = 
                this.state.fan_speed === 0 ? 'OFF' : 
                state.auto_mode ? 'Auto' : 
                `Level ${this.state.fan_speed}`;
        }
        
        // Update mode
        if (state.mode) {
            this.state.mode = state.mode;
            document.querySelectorAll('.mode-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-mode="${state.mode}"]`)?.classList.add('active');
            
            const modeLabels = {
                'face': 'Face',
                'feet': 'Feet',
                'defrost': 'Defrost',
                'face_feet': 'Face+Feet',
                'auto': 'Auto'
            };
            document.getElementById('current-mode').textContent = modeLabels[state.mode] || state.mode;
        }
        
        // Update toggles
        this.state.ac_enabled = state.ac_enabled || false;
        this.state.max_ac = state.max_ac || false;
        this.state.recirculation = state.recirculation || false;
        this.state.defrost_front = state.defrost_front || false;
        this.state.defrost_rear = state.defrost_rear || false;
        this.state.heated_mirrors = state.heated_mirrors || false;
        this.state.auto_mode = state.auto_mode || false;
        
        this.updateToggleButton('ac-toggle', this.state.ac_enabled);
        this.updateToggleButton('max-ac-toggle', this.state.max_ac);
        this.updateToggleButton('recirc-toggle', this.state.recirculation);
        this.updateToggleButton('defrost-front-toggle', this.state.defrost_front);
        this.updateToggleButton('defrost-rear-toggle', this.state.defrost_rear);
        this.updateToggleButton('heated-mirrors-toggle', this.state.heated_mirrors);
        this.updateToggleButton('auto-toggle', this.state.auto_mode);
        
        // Update outside temperature
        if (state.outside_temp !== null && state.outside_temp !== undefined) {
            const outsideTempF = Math.round(this.celsiusToFahrenheit(state.outside_temp));
            document.getElementById('outside-temp').textContent = `${outsideTempF}°F`;
        }
    }
    
    updateToggleButton(id, active) {
        const button = document.getElementById(id);
        if (button) {
            if (active) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        }
    }
    
    updateHeatedSeatUI(seat, level) {
        document.querySelectorAll(`[data-seat="${seat}"]`).forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.querySelector(`[data-seat="${seat}"][data-level="${level}"]`)?.classList.add('active');
    }
    
    async checkMaestroStatus() {
        try {
            const response = await fetch('/api/maestro/status');
            const data = await response.json();
            
            if (data.ok) {
                this.maestroConnected = data.connected;
                this.updateMaestroStatus();
            }
        } catch (error) {
            this.maestroConnected = false;
            this.updateMaestroStatus();
        }
    }
    
    updateMaestroStatus() {
        const statusDot = document.getElementById('maestro-status');
        if (this.maestroConnected) {
            statusDot.classList.remove('offline');
        } else {
            statusDot.classList.add('offline');
        }
    }
    
    startAutoUpdate() {
        // Update status every 5 seconds
        this.updateInterval = setInterval(() => {
            this.loadStatus();
            this.checkMaestroStatus();
        }, 5000);
    }
    
    celsiusToFahrenheit(celsius) {
        return (celsius * 9/5) + 32;
    }
    
    fahrenheitToCelsius(fahrenheit) {
        return (fahrenheit - 32) * 5/9;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.climateControl = new ClimateControl();
});
