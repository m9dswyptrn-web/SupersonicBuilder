let currentTheme = null;
let themes = [];
let wallpapers = [];

async function init() {
    await loadThemes();
    await loadWallpapers();
    setupEventListeners();
    updatePreview();
}

function setupEventListeners() {
    const colorInputs = [
        'primaryColor', 'secondaryColor', 'accentColor',
        'navBarColor', 'statusBarColor'
    ];
    
    colorInputs.forEach(id => {
        document.getElementById(id).addEventListener('input', updatePreview);
    });
    
    document.getElementById('themeMode').addEventListener('change', updatePreview);
    document.getElementById('buttonStyle').addEventListener('change', updatePreview);
    document.getElementById('fontFamily').addEventListener('change', updatePreview);
}

async function loadThemes() {
    try {
        const response = await fetch('/api/themes');
        const data = await response.json();
        
        if (data.ok) {
            themes = data.themes;
            displayThemes();
        }
    } catch (error) {
        showNotification('Failed to load themes', 'error');
        console.error(error);
    }
}

function displayThemes() {
    const templateList = document.getElementById('templateList');
    const customList = document.getElementById('customList');
    
    templateList.innerHTML = '';
    customList.innerHTML = '';
    
    const templates = themes.filter(t => t.is_template);
    const custom = themes.filter(t => !t.is_template);
    
    templates.forEach(theme => {
        templateList.appendChild(createThemeItem(theme));
    });
    
    custom.forEach(theme => {
        customList.appendChild(createThemeItem(theme));
    });
}

function createThemeItem(theme) {
    const div = document.createElement('div');
    div.className = 'theme-item' + (theme.is_template ? ' template' : '');
    if (theme.is_active) div.classList.add('active');
    
    div.innerHTML = `
        <div class="theme-name">
            ${theme.theme_name}
            ${theme.is_template ? '<span class="status-badge badge-template">Template</span>' : ''}
            ${theme.is_active ? '<span class="status-badge badge-active">Active</span>' : ''}
        </div>
        <div class="theme-meta">${theme.mode} mode</div>
        <div class="color-preview">
            <div class="color-box" style="background: ${theme.primary_color}"></div>
            <div class="color-box" style="background: ${theme.secondary_color}"></div>
            <div class="color-box" style="background: ${theme.accent_color}"></div>
        </div>
    `;
    
    div.onclick = () => loadThemeToEditor(theme);
    
    return div;
}

function loadThemeToEditor(theme) {
    currentTheme = theme;
    
    document.getElementById('themeName').value = theme.theme_name;
    document.getElementById('themeMode').value = theme.mode || 'dark';
    document.getElementById('primaryColor').value = theme.primary_color;
    document.getElementById('secondaryColor').value = theme.secondary_color;
    document.getElementById('accentColor').value = theme.accent_color;
    document.getElementById('navBarColor').value = theme.nav_bar_color;
    document.getElementById('statusBarColor').value = theme.status_bar_color;
    document.getElementById('buttonStyle').value = theme.button_style || 'rounded';
    document.getElementById('iconStyle').value = theme.icon_style || 'modern';
    document.getElementById('fontFamily').value = theme.font_family || 'Roboto';
    
    updatePreview();
    
    document.querySelectorAll('.theme-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.theme-item').classList.add('active');
}

function updatePreview() {
    const theme = {
        primary_color: document.getElementById('primaryColor').value,
        secondary_color: document.getElementById('secondaryColor').value,
        accent_color: document.getElementById('accentColor').value,
        nav_bar_color: document.getElementById('navBarColor').value,
        status_bar_color: document.getElementById('statusBarColor').value,
        background_color: document.getElementById('themeMode').value === 'dark' ? '#121212' : '#fafafa',
        surface_color: document.getElementById('themeMode').value === 'dark' ? '#1e1e1e' : '#ffffff',
        text_color: document.getElementById('themeMode').value === 'dark' ? '#ffffff' : '#212121',
        font_family: document.getElementById('fontFamily').value,
        button_style: document.getElementById('buttonStyle').value
    };
    
    const statusBar = document.getElementById('previewStatusBar');
    const navBar = document.getElementById('previewNavBar');
    const content = document.getElementById('previewContent');
    const widgets = content.querySelectorAll('.preview-widget');
    const button1 = document.getElementById('previewButton1');
    const button2 = document.getElementById('previewButton2');
    
    statusBar.style.background = theme.status_bar_color;
    statusBar.style.color = theme.text_color;
    
    navBar.style.background = theme.nav_bar_color;
    navBar.style.color = theme.text_color;
    
    content.style.background = theme.background_color;
    content.style.color = theme.text_color;
    content.style.fontFamily = theme.font_family;
    
    widgets.forEach(widget => {
        widget.style.background = theme.surface_color;
    });
    
    const borderRadius = {
        'rounded': '8px',
        'sharp': '0px',
        'pill': '24px',
        'minimal': '4px'
    }[theme.button_style] || '8px';
    
    button1.style.background = theme.accent_color;
    button1.style.color = theme.text_color;
    button1.style.borderRadius = borderRadius;
    
    button2.style.background = theme.secondary_color;
    button2.style.color = theme.text_color;
    button2.style.borderRadius = borderRadius;
}

async function createNewTheme() {
    const name = prompt('Enter theme name:');
    if (!name) return;
    
    const themeData = {
        theme_name: name,
        theme_type: 'custom',
        mode: 'dark',
        primary_color: '#1a1a1a',
        secondary_color: '#2d2d2d',
        accent_color: '#00b8d4',
        background_color: '#121212',
        surface_color: '#1e1e1e',
        text_color: '#ffffff',
        nav_bar_color: '#1a1a1a',
        status_bar_color: '#000000',
        button_style: 'rounded',
        icon_style: 'modern',
        font_family: 'Roboto'
    };
    
    try {
        const response = await fetch('/api/themes', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(themeData)
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Theme created successfully!');
            await loadThemes();
            loadThemeToEditor(data.theme);
        } else {
            showNotification(data.error || 'Failed to create theme', 'error');
        }
    } catch (error) {
        showNotification('Failed to create theme', 'error');
        console.error(error);
    }
}

async function saveTheme() {
    const themeData = {
        theme_name: document.getElementById('themeName').value,
        mode: document.getElementById('themeMode').value,
        primary_color: document.getElementById('primaryColor').value,
        secondary_color: document.getElementById('secondaryColor').value,
        accent_color: document.getElementById('accentColor').value,
        nav_bar_color: document.getElementById('navBarColor').value,
        status_bar_color: document.getElementById('statusBarColor').value,
        background_color: document.getElementById('themeMode').value === 'dark' ? '#121212' : '#fafafa',
        surface_color: document.getElementById('themeMode').value === 'dark' ? '#1e1e1e' : '#ffffff',
        text_color: document.getElementById('themeMode').value === 'dark' ? '#ffffff' : '#212121',
        button_style: document.getElementById('buttonStyle').value,
        icon_style: document.getElementById('iconStyle').value,
        font_family: document.getElementById('fontFamily').value
    };
    
    try {
        let response;
        if (currentTheme && !currentTheme.is_template) {
            response = await fetch(`/api/themes/${currentTheme.id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(themeData)
            });
        } else {
            response = await fetch('/api/themes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(themeData)
            });
        }
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Theme saved successfully!');
            await loadThemes();
            currentTheme = data.theme;
        } else {
            showNotification(data.error || 'Failed to save theme', 'error');
        }
    } catch (error) {
        showNotification('Failed to save theme', 'error');
        console.error(error);
    }
}

async function applyTheme() {
    if (!currentTheme) {
        showNotification('Please select a theme first', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/themes/${currentTheme.id}/apply`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Theme applied successfully!');
            await loadThemes();
        } else {
            showNotification(data.error || 'Failed to apply theme', 'error');
        }
    } catch (error) {
        showNotification('Failed to apply theme', 'error');
        console.error(error);
    }
}

async function applySonicColors() {
    if (!currentTheme || currentTheme.is_template) {
        showNotification('Please create a custom theme first', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/themes/${currentTheme.id}/sonic-colors`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({color_scheme: 'blue'})
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Sonic colors applied!');
            loadThemeToEditor(data.theme);
        } else {
            showNotification(data.error || 'Failed to apply Sonic colors', 'error');
        }
    } catch (error) {
        showNotification('Failed to apply Sonic colors', 'error');
        console.error(error);
    }
}

async function exportTheme() {
    if (!currentTheme) {
        showNotification('Please select a theme first', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/themes/${currentTheme.id}/export`);
        const data = await response.json();
        
        if (data.ok) {
            const blob = new Blob([data.exported_data], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentTheme.theme_name}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            showNotification('Theme exported successfully!');
        } else {
            showNotification(data.error || 'Failed to export theme', 'error');
        }
    } catch (error) {
        showNotification('Failed to export theme', 'error');
        console.error(error);
    }
}

function showImportDialog() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = async (event) => {
            try {
                const themeData = event.target.result;
                
                const response = await fetch('/api/themes/import', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({theme_data: themeData})
                });
                
                const data = await response.json();
                
                if (data.ok) {
                    showNotification('Theme imported successfully!');
                    await loadThemes();
                    loadThemeToEditor(data.theme);
                } else {
                    showNotification(data.error || 'Failed to import theme', 'error');
                }
            } catch (error) {
                showNotification('Failed to import theme', 'error');
                console.error(error);
            }
        };
        
        reader.readAsText(file);
    };
    
    input.click();
}

async function uploadWallpaper() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);
    
    try {
        const response = await fetch('/api/wallpapers/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Wallpaper uploaded and resized to 2000×1200!');
            await loadWallpapers();
        } else {
            showNotification(data.error || 'Failed to upload wallpaper', 'error');
        }
    } catch (error) {
        showNotification('Failed to upload wallpaper', 'error');
        console.error(error);
    }
    
    fileInput.value = '';
}

async function loadWallpapers() {
    try {
        const response = await fetch('/api/wallpapers');
        const data = await response.json();
        
        if (data.ok) {
            wallpapers = data.wallpapers;
            displayWallpapers();
        }
    } catch (error) {
        console.error('Failed to load wallpapers:', error);
    }
}

function displayWallpapers() {
    const grid = document.getElementById('wallpaperGrid');
    grid.innerHTML = '';
    
    wallpapers.forEach(wallpaper => {
        const div = document.createElement('div');
        div.className = 'wallpaper-item';
        div.title = `${wallpaper.wallpaper_name} (${wallpaper.resized_width}×${wallpaper.resized_height})`;
        
        if (wallpaper.thumbnail_path) {
            const img = document.createElement('img');
            img.src = '/' + wallpaper.thumbnail_path;
            img.alt = wallpaper.wallpaper_name;
            div.appendChild(img);
        }
        
        grid.appendChild(div);
    });
}

function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tab).classList.add('active');
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = 'notification show' + (type === 'error' ? ' error' : '');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

document.addEventListener('DOMContentLoaded', init);

const uploadArea = document.getElementById('uploadArea');
if (uploadArea) {
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            document.getElementById('fileInput').files = files;
            uploadWallpaper();
        }
    });
}
