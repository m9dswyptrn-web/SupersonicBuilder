// Media Center Pro - Frontend JavaScript

const API_BASE = '';

// Tab management
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        
        tab.classList.add('active');
        document.getElementById(tabName).classList.add('active');
        
        // Load content for active tab
        if (tabName === 'music') loadMusic('all');
        if (tabName === 'videos') loadVideos();
        if (tabName === 'playlists') loadPlaylists();
        if (tabName === 'player') loadNowPlaying();
        if (tabName === 'storage') loadStorage();
    });
});

// Load library statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/library/stats`);
        const data = await response.json();
        
        if (data.ok && data.stats) {
            document.getElementById('statMusic').textContent = data.stats.total_music_tracks || 0;
            document.getElementById('statVideos').textContent = data.stats.total_video_files || 0;
            document.getElementById('statArtists').textContent = data.stats.total_artists || 0;
            document.getElementById('statAlbums').textContent = data.stats.total_albums || 0;
            document.getElementById('statPlaylists').textContent = data.stats.total_playlists || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load music tracks
async function loadMusic(type = 'all') {
    const content = document.getElementById('musicContent');
    content.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        let url = `${API_BASE}/api/music/all`;
        
        if (type === 'recent') {
            url = `${API_BASE}/api/playlists/smart/recently-added`;
        } else if (type === 'most-played') {
            url = `${API_BASE}/api/playlists/smart/most-played`;
        } else if (type === 'favorites') {
            url = `${API_BASE}/api/playlists/smart/favorites`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        const tracks = data.tracks || data.results || [];
        
        if (tracks.length === 0) {
            content.innerHTML = '<p>No tracks found. Click "Scan Library" to import music.</p>';
            return;
        }
        
        content.innerHTML = tracks.map(track => `
            <div class="track-item" onclick="playTrack(${track.id})">
                <div class="track-info">
                    <div class="track-title">${track.title || track.file_name}</div>
                    <div class="track-meta">
                        ${track.artist || 'Unknown Artist'} • ${track.album || 'Unknown Album'}
                        ${track.year ? `• ${track.year}` : ''}
                    </div>
                </div>
                <div class="track-meta">
                    ${formatDuration(track.duration_seconds)}
                    ${track.play_count ? `• ${track.play_count} plays` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        content.innerHTML = '<div class="error">Error loading music</div>';
        console.error('Error loading music:', error);
    }
}

// Load videos
async function loadVideos() {
    const content = document.getElementById('videosContent');
    content.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/videos/all`);
        const data = await response.json();
        
        const videos = data.videos || [];
        
        if (videos.length === 0) {
            content.innerHTML = '<p>No videos found. Click "Scan Library" to import videos.</p>';
            return;
        }
        
        content.innerHTML = videos.map(video => `
            <div class="video-card">
                <div class="video-thumb">🎬</div>
                <div class="track-title">${video.title || video.file_name}</div>
                <div class="track-meta">${formatDuration(video.duration_seconds)}</div>
                <div class="track-meta">${video.width}x${video.height}</div>
            </div>
        `).join('');
    } catch (error) {
        content.innerHTML = '<div class="error">Error loading videos</div>';
        console.error('Error loading videos:', error);
    }
}

// Load playlists
async function loadPlaylists() {
    const content = document.getElementById('playlistsContent');
    content.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/playlists`);
        const data = await response.json();
        
        const playlists = data.playlists || [];
        
        if (playlists.length === 0) {
            content.innerHTML = '<p>No playlists yet. Create your first playlist!</p>';
            return;
        }
        
        content.innerHTML = playlists.map(playlist => `
            <div class="track-item" onclick="playPlaylist(${playlist.id})">
                <div class="track-info">
                    <div class="track-title">📋 ${playlist.name}</div>
                    <div class="track-meta">
                        ${playlist.track_count} tracks
                        ${playlist.type !== 'manual' ? `• ${playlist.type}` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        content.innerHTML = '<div class="error">Error loading playlists</div>';
        console.error('Error loading playlists:', error);
    }
}

// Player control
async function playerControl(action) {
    try {
        const response = await fetch(`${API_BASE}/api/player/${action}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok) {
            loadNowPlaying();
        }
    } catch (error) {
        console.error(`Error ${action}:`, error);
    }
}

// Play track
async function playTrack(trackId) {
    try {
        const response = await fetch(`${API_BASE}/api/player/play`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ track_id: trackId })
        });
        const data = await response.json();
        
        if (data.ok) {
            loadNowPlaying();
            showMessage('Now playing', 'success');
        }
    } catch (error) {
        console.error('Error playing track:', error);
    }
}

// Play playlist
async function playPlaylist(playlistId) {
    try {
        const response = await fetch(`${API_BASE}/api/player/playlist/${playlistId}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok) {
            loadNowPlaying();
            showMessage('Playlist started', 'success');
        }
    } catch (error) {
        console.error('Error playing playlist:', error);
    }
}

// Load now playing
async function loadNowPlaying() {
    try {
        const response = await fetch(`${API_BASE}/api/player/now-playing`);
        const data = await response.json();
        
        if (data.ok && data.now_playing) {
            const np = data.now_playing;
            
            if (np.playing && np.track) {
                document.getElementById('nowPlayingTitle').textContent = np.track.title || 'Unknown';
                document.getElementById('nowPlayingArtist').textContent = 
                    `${np.track.artist || 'Unknown Artist'} • ${np.track.album || 'Unknown Album'}`;
                
                const progress = (np.position_seconds / np.track.duration_seconds) * 100;
                document.getElementById('progressFill').style.width = `${progress}%`;
                
                document.getElementById('nowPlayingTime').textContent = 
                    `${formatDuration(np.position_seconds)} / ${formatDuration(np.track.duration_seconds)}`;
            } else {
                document.getElementById('nowPlayingTitle').textContent = 'No track playing';
                document.getElementById('nowPlayingArtist').textContent = '';
                document.getElementById('progressFill').style.width = '0%';
                document.getElementById('nowPlayingTime').textContent = '0:00 / 0:00';
            }
        }
        
        // Load queue
        const queueResponse = await fetch(`${API_BASE}/api/player/queue`);
        const queueData = await queueResponse.json();
        
        if (queueData.ok) {
            const queue = queueData.queue || [];
            const queueContent = document.getElementById('queueContent');
            
            if (queue.length === 0) {
                queueContent.innerHTML = '<p>Queue is empty</p>';
            } else {
                queueContent.innerHTML = queue.map(track => `
                    <div class="track-item ${track.is_current ? 'active' : ''}">
                        <div class="track-info">
                            <div class="track-title">
                                ${track.is_current ? '▶️ ' : ''}
                                ${track.title || track.file_name}
                            </div>
                            <div class="track-meta">${track.artist || 'Unknown'}</div>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading now playing:', error);
    }
}

// Load storage info
async function loadStorage() {
    try {
        const response = await fetch(`${API_BASE}/api/storage`);
        const data = await response.json();
        
        if (data.ok && data.current) {
            const storage = data.current;
            const storageBar = document.getElementById('storageBar');
            
            const musicPercent = storage.music_percent || 0;
            const videoPercent = storage.video_percent || 0;
            const freePercent = storage.free_percent || 0;
            const otherPercent = 100 - musicPercent - videoPercent - freePercent;
            
            storageBar.innerHTML = `
                <div class="storage-segment" style="width: ${musicPercent}%; background: #667eea;">
                    Music ${musicPercent.toFixed(1)}%
                </div>
                <div class="storage-segment" style="width: ${videoPercent}%; background: #764ba2;">
                    Video ${videoPercent.toFixed(1)}%
                </div>
                <div class="storage-segment" style="width: ${otherPercent}%; background: #f093fb;">
                    Other ${otherPercent.toFixed(1)}%
                </div>
                <div class="storage-segment" style="width: ${freePercent}%; background: rgba(255,255,255,0.3);">
                    Free ${freePercent.toFixed(1)}%
                </div>
            `;
            
            const details = document.getElementById('storageDetails');
            details.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${storage.total_size_gb}GB</div>
                        <div class="stat-label">Total Storage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${storage.music_size_gb}GB</div>
                        <div class="stat-label">Music</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${storage.video_size_gb}GB</div>
                        <div class="stat-label">Videos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${storage.free_size_gb}GB</div>
                        <div class="stat-label">Free Space</div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading storage:', error);
    }
}

// Scan library
async function scanLibrary(type) {
    const scanProgress = document.getElementById('scanProgress');
    scanProgress.innerHTML = '<div class="loading">Starting scan...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/library/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type })
        });
        const data = await response.json();
        
        if (data.ok) {
            scanProgress.innerHTML = '<div class="success">Scan started!</div>';
            monitorScanProgress();
        }
    } catch (error) {
        scanProgress.innerHTML = '<div class="error">Error starting scan</div>';
        console.error('Error scanning library:', error);
    }
}

// Monitor scan progress
async function monitorScanProgress() {
    const scanProgress = document.getElementById('scanProgress');
    
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/library/scan/progress`);
            const data = await response.json();
            
            if (data.ok) {
                if (data.scanning) {
                    const progress = data.progress;
                    scanProgress.innerHTML = `
                        <div class="success">
                            Scanning: ${progress.file}<br>
                            Progress: ${progress.current} / ${progress.total}
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${(progress.current / progress.total * 100) || 0}%"></div>
                            </div>
                        </div>
                    `;
                } else {
                    clearInterval(interval);
                    scanProgress.innerHTML = '<div class="success">Scan completed!</div>';
                    loadStats();
                }
            }
        } catch (error) {
            clearInterval(interval);
            console.error('Error monitoring scan:', error);
        }
    }, 1000);
}

// Scan for duplicates
async function scanDuplicates() {
    const scanResults = document.getElementById('scanResults');
    scanResults.innerHTML = '<div class="loading">Scanning for duplicates...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/duplicates/scan`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.ok) {
            scanResults.innerHTML = `
                <div class="success">
                    Found ${data.duplicates_found} potential duplicates
                </div>
            `;
        }
    } catch (error) {
        scanResults.innerHTML = '<div class="error">Error scanning for duplicates</div>';
        console.error('Error scanning duplicates:', error);
    }
}

// Create playlist
function createPlaylist() {
    const name = prompt('Enter playlist name:');
    if (!name) return;
    
    fetch(`${API_BASE}/api/playlists/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    })
    .then(response => response.json())
    .then(data => {
        if (data.ok) {
            showMessage('Playlist created!', 'success');
            loadPlaylists();
        }
    })
    .catch(error => console.error('Error creating playlist:', error));
}

// Music search
document.getElementById('musicSearch')?.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    if (query.length > 2) {
        searchMusic(query);
    } else if (query.length === 0) {
        loadMusic('all');
    }
});

async function searchMusic(query) {
    const content = document.getElementById('musicContent');
    
    try {
        const response = await fetch(`${API_BASE}/api/music/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        const tracks = data.results || [];
        
        if (tracks.length === 0) {
            content.innerHTML = '<p>No results found</p>';
            return;
        }
        
        content.innerHTML = tracks.map(track => `
            <div class="track-item" onclick="playTrack(${track.id})">
                <div class="track-info">
                    <div class="track-title">${track.title || track.file_name}</div>
                    <div class="track-meta">
                        ${track.artist || 'Unknown'} • ${track.album || 'Unknown'}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error searching:', error);
    }
}

// Utility functions
function formatDuration(seconds) {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function showMessage(message, type) {
    const div = document.createElement('div');
    div.className = type === 'success' ? 'success' : 'error';
    div.textContent = message;
    div.style.position = 'fixed';
    div.style.top = '20px';
    div.style.right = '20px';
    div.style.zIndex = '1000';
    document.body.appendChild(div);
    
    setTimeout(() => div.remove(), 3000);
}

// Initialize
loadStats();
loadMusic('all');

// Auto-refresh now playing
setInterval(() => {
    const playerSection = document.getElementById('player');
    if (playerSection.classList.contains('active')) {
        loadNowPlaying();
    }
}, 5000);
