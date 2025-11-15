const API_BASE = window.location.origin;

function showResponse(elementId, message, isError = false) {
    const element = document.getElementById(elementId);
    element.className = 'response show ' + (isError ? 'error' : 'success');
    element.textContent = message;
    setTimeout(() => {
        element.className = 'response';
    }, 5000);
}

function setCommand(command) {
    document.getElementById('commandInput').value = command;
}

async function executeCommand() {
    const command = document.getElementById('commandInput').value.trim();
    if (!command) {
        showResponse('commandResponse', 'Please enter a command', true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/command/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });

        const data = await response.json();

        if (data.ok) {
            const resultText = data.result.response || 'Command executed';
            const processingTime = data.processing_time_ms.toFixed(2);
            showResponse('commandResponse', `${resultText} (${processingTime}ms)`, false);
            loadHistory();
            loadStats();
        } else {
            showResponse('commandResponse', data.error || 'Command failed', true);
        }
    } catch (error) {
        showResponse('commandResponse', `Error: ${error.message}`, true);
    }
}

async function parseCommand() {
    const command = document.getElementById('commandInput').value.trim();
    if (!command) {
        showResponse('commandResponse', 'Please enter a command', true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/command/parse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command, use_context: true })
        });

        const data = await response.json();

        if (data.ok) {
            const parsed = data.parsed;
            const message = `Intent: ${parsed.intent}\nService: ${parsed.service}\nEntities: ${JSON.stringify(parsed.entities, null, 2)}`;
            showResponse('commandResponse', message, false);
        } else {
            showResponse('commandResponse', data.error || 'Parse failed', true);
        }
    } catch (error) {
        showResponse('commandResponse', `Error: ${error.message}`, true);
    }
}

async function updateWakeWordSettings() {
    const wakeWord = document.getElementById('wakeWordInput').value.trim();
    const sensitivity = parseFloat(document.getElementById('sensitivitySlider').value);

    try {
        const response = await fetch(`${API_BASE}/api/wake-word/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ wake_word: wakeWord || undefined, sensitivity })
        });

        const data = await response.json();

        if (data.ok) {
            if (wakeWord) {
                document.getElementById('currentWakeWord').textContent = wakeWord;
            }
            showResponse('wakeWordResponse', 'Wake word settings updated', false);
        } else {
            showResponse('wakeWordResponse', data.error || 'Update failed', true);
        }
    } catch (error) {
        showResponse('wakeWordResponse', `Error: ${error.message}`, true);
    }
}

async function testWakeWord() {
    const testPhrase = document.getElementById('commandInput').value.trim() || 
                      document.getElementById('currentWakeWord').textContent;

    try {
        const response = await fetch(`${API_BASE}/api/wake-word/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ test_phrase: testPhrase })
        });

        const data = await response.json();

        if (data.ok) {
            const result = data.result;
            const message = `Detected: ${result.detected}\nConfidence: ${result.confidence}\n${result.recommendation || ''}`;
            showResponse('wakeWordResponse', message, !result.detected);
        } else {
            showResponse('wakeWordResponse', data.error || 'Test failed', true);
        }
    } catch (error) {
        showResponse('wakeWordResponse', `Error: ${error.message}`, true);
    }
}

function updateSensitivity(value) {
    document.getElementById('sensitivityValue').textContent = value;
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();

        if (data.ok) {
            const dbStats = data.database;
            document.getElementById('totalCommands').textContent = dbStats.total_commands;
            document.getElementById('successRate').textContent = `${dbStats.success_rate.toFixed(1)}%`;
            document.getElementById('customCommands').textContent = dbStats.active_custom_commands;
            document.getElementById('activeMacros').textContent = dbStats.active_macros;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/history?limit=20`);
        const data = await response.json();

        if (data.ok) {
            const listElement = document.getElementById('historyList');
            listElement.innerHTML = '';

            if (data.history.length === 0) {
                listElement.innerHTML = '<p>No command history yet</p>';
                return;
            }

            data.history.forEach(item => {
                const div = document.createElement('div');
                div.className = `history-item ${item.success ? '' : 'error'}`;
                div.innerHTML = `
                    <div class="command">${item.raw_command}</div>
                    <div class="intent">Intent: ${item.parsed_intent || 'unknown'} | Service: ${item.service_called || 'none'}</div>
                    <div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">${new Date(item.timestamp).toLocaleString()}</div>
                `;
                listElement.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

async function clearContext() {
    try {
        const response = await fetch(`${API_BASE}/api/context/clear`, { method: 'POST' });
        const data = await response.json();

        if (data.ok) {
            alert('Context history cleared');
        }
    } catch (error) {
        console.error('Error clearing context:', error);
    }
}

async function loadCustomCommands() {
    try {
        const response = await fetch(`${API_BASE}/api/custom-commands`);
        const data = await response.json();

        if (data.ok) {
            const listElement = document.getElementById('customCommandsList');
            listElement.innerHTML = '';

            if (data.commands.length === 0) {
                listElement.innerHTML = '<p>No custom commands yet</p>';
                return;
            }

            data.commands.forEach(cmd => {
                const div = document.createElement('div');
                div.className = 'command-item';
                div.innerHTML = `
                    <div>
                        <strong>${cmd.command_name}</strong>
                        <div style="font-size: 0.9em; opacity: 0.8;">Triggers: ${cmd.trigger_phrases.join(', ')}</div>
                    </div>
                    <button onclick="deleteCustomCommand(${cmd.id})" class="danger">Delete</button>
                `;
                listElement.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error loading custom commands:', error);
    }
}

async function createCustomCommand() {
    const name = document.getElementById('newCommandName').value.trim();
    const trigger = document.getElementById('newCommandTrigger').value.trim();
    const actionType = document.getElementById('newCommandActionType').value;

    if (!name || !trigger) {
        showResponse('createCommandResponse', 'Please fill in all fields', true);
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/custom-commands`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command_name: name,
                trigger_phrases: [trigger],
                action_type: actionType,
                action_config: {}
            })
        });

        const data = await response.json();

        if (data.ok) {
            showResponse('createCommandResponse', 'Custom command created', false);
            document.getElementById('newCommandName').value = '';
            document.getElementById('newCommandTrigger').value = '';
            loadCustomCommands();
        } else {
            showResponse('createCommandResponse', data.error || 'Creation failed', true);
        }
    } catch (error) {
        showResponse('createCommandResponse', `Error: ${error.message}`, true);
    }
}

async function deleteCustomCommand(commandId) {
    if (!confirm('Are you sure you want to delete this command?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/custom-commands/${commandId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.ok) {
            loadCustomCommands();
        } else {
            alert(data.error || 'Delete failed');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function loadMacros() {
    try {
        const response = await fetch(`${API_BASE}/api/macros`);
        const data = await response.json();

        if (data.ok) {
            const listElement = document.getElementById('macrosList');
            listElement.innerHTML = '';

            if (data.macros.length === 0) {
                listElement.innerHTML = '<p>No macros yet</p>';
                return;
            }

            data.macros.forEach(macro => {
                const div = document.createElement('div');
                div.className = 'command-item';
                div.innerHTML = `
                    <div>
                        <strong>${macro.macro_name}</strong>
                        <div style="font-size: 0.9em; opacity: 0.8;">Trigger: "${macro.trigger_phrase}"</div>
                        <div style="font-size: 0.9em; opacity: 0.8;">${macro.actions.length} actions</div>
                    </div>
                    <div>
                        <button onclick="executeMacro(${macro.id})" class="success">Execute</button>
                        <button onclick="deleteMacro(${macro.id})" class="danger">Delete</button>
                    </div>
                `;
                listElement.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error loading macros:', error);
    }
}

async function createMacro() {
    const name = document.getElementById('newMacroName').value.trim();
    const trigger = document.getElementById('newMacroTrigger').value.trim();

    if (!name || !trigger) {
        showResponse('createMacroResponse', 'Please fill in all fields', true);
        return;
    }

    const actions = [
        { intent: 'lighting_control', entities: { mode: 'night' }, service: 'lighting' },
        { intent: 'climate_control', entities: { temperature: '70' }, service: 'climate' }
    ];

    try {
        const response = await fetch(`${API_BASE}/api/macros`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                macro_name: name,
                trigger_phrase: trigger,
                actions: actions
            })
        });

        const data = await response.json();

        if (data.ok) {
            showResponse('createMacroResponse', 'Macro created with sample actions', false);
            document.getElementById('newMacroName').value = '';
            document.getElementById('newMacroTrigger').value = '';
            loadMacros();
        } else {
            showResponse('createMacroResponse', data.error || 'Creation failed', true);
        }
    } catch (error) {
        showResponse('createMacroResponse', `Error: ${error.message}`, true);
    }
}

async function executeMacro(macroId) {
    try {
        const response = await fetch(`${API_BASE}/api/macros/${macroId}/execute`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.ok) {
            alert(`Macro "${data.macro_name}" executed: ${data.actions_executed} actions`);
        } else {
            alert(data.error || 'Execution failed');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function deleteMacro(macroId) {
    if (!confirm('Are you sure you want to delete this macro?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/macros/${macroId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.ok) {
            loadMacros();
        } else {
            alert(data.error || 'Delete failed');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function checkServices() {
    try {
        const response = await fetch(`${API_BASE}/api/services/status`);
        const data = await response.json();

        if (data.ok) {
            const statusElement = document.getElementById('servicesStatus');
            statusElement.innerHTML = '';

            const services = data.services;
            for (const [name, status] of Object.entries(services)) {
                const div = document.createElement('div');
                div.style.marginBottom = '10px';
                div.innerHTML = `
                    <span class="status-indicator ${status.ok ? 'online' : 'offline'}"></span>
                    <strong>${name}</strong>: ${status.ok ? 'Online' : 'Offline'}
                `;
                statusElement.appendChild(div);
            }

            const summary = document.createElement('p');
            summary.style.marginTop = '15px';
            summary.innerHTML = `<strong>${data.healthy} of ${data.total} services online</strong>`;
            statusElement.appendChild(summary);
        }
    } catch (error) {
        console.error('Error checking services:', error);
    }
}

function switchTab(tabId) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

document.getElementById('commandInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        executeCommand();
    }
});

window.addEventListener('load', () => {
    loadStats();
    loadHistory();
    loadCustomCommands();
    loadMacros();
});
