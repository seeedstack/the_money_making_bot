let currentPlatform = 'instagram';
let refreshInterval = null;

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        const tabId = e.target.dataset.tab;
        document.getElementById(tabId).classList.add('active');
        loadTabData(tabId);
    });
});

// Platform select
document.getElementById('platformSelect').addEventListener('change', (e) => {
    currentPlatform = e.target.value;
    loadTabData(document.querySelector('.tab-content.active').id);
});

async function loadTabData(tabId) {
    switch(tabId) {
        case 'home':
            await loadStats();
            await loadRecentSessions();
            break;
        case 'platforms':
            await loadPlatforms();
            break;
        case 'workflows':
            await loadWorkflows();
            break;
        case 'sessions':
            await loadSessions();
            break;
        case 'checks':
            await loadChecks();
            break;
    }
}

async function loadStats() {
    try {
        const data = await api.getStats(currentPlatform);
        document.getElementById('triggersCount').textContent = data.triggers_matched || 0;
        document.getElementById('messagesCount').textContent = data.messages_sent || 0;
    } catch(e) {
        console.error('Failed to load stats:', e);
    }
}

async function loadRecentSessions() {
    try {
        const data = await api.getSessions(currentPlatform, 'STEP_RUNNING');
        const tbody = document.getElementById('recentSessionsBody');
        tbody.innerHTML = data.sessions.slice(0, 5).map(s => `
            <tr>
                <td>${s.username}</td>
                <td>${s.workflow_id}</td>
                <td>${s.state}</td>
                <td>${new Date(s.started_at).toLocaleString()}</td>
            </tr>
        `).join('');
        document.getElementById('sessionsCount').textContent = data.sessions.length;
    } catch(e) {
        console.error('Failed to load sessions:', e);
    }
}

async function loadPlatforms() {
    try {
        const data = await api.getPlatforms();
        const html = data.platforms.map(p => `
            <div class="platform-card ${p.enabled ? 'enabled' : 'disabled'}">
                <h3>${p.name.toUpperCase()}</h3>
                <p>Status: ${p.status}</p>
                <button onclick="togglePlatform('${p.name}')">${p.enabled ? 'Disable' : 'Enable'}</button>
            </div>
        `).join('');
        document.getElementById('platformsList').innerHTML = html;
    } catch(e) {
        console.error('Failed to load platforms:', e);
    }
}

async function loadWorkflows() {
    try {
        const data = await api.getWorkflows(currentPlatform);
        const html = data.workflows.map(w => `
            <div class="workflow-card">
                <h3>${w.name}</h3>
                <p><strong>Trigger:</strong> ${w.trigger_keyword}</p>
                <p><strong>Mode:</strong> ${w.match_mode}</p>
                <p><strong>Steps:</strong> ${w.steps.length}</p>
                <p><strong>Priority:</strong> ${w.priority}</p>
                <div class="workflow-actions">
                    <button onclick="editWorkflow(${w.id})">Edit</button>
                    <button onclick="toggleWorkflow(${w.id})">Toggle</button>
                    <button onclick="deleteWorkflow(${w.id})">Delete</button>
                </div>
            </div>
        `).join('');
        document.getElementById('workflowsList').innerHTML = html;
    } catch(e) {
        console.error('Failed to load workflows:', e);
    }
}

async function loadSessions() {
    try {
        const state = document.getElementById('stateFilter').value;
        const data = await api.getSessions(currentPlatform, state);
        const tbody = document.getElementById('sessionsBody');
        tbody.innerHTML = data.sessions.map(s => `
            <tr>
                <td>${s.id}</td>
                <td>${s.username}</td>
                <td>${s.workflow_id}</td>
                <td>${s.state}</td>
                <td>${s.current_step}</td>
                <td>${s.follow_status}</td>
                <td>${new Date(s.started_at).toLocaleString()}</td>
            </tr>
        `).join('');
    } catch(e) {
        console.error('Failed to load sessions:', e);
    }
}

async function loadChecks() {
    try {
        const data = await api.getPendingChecks(currentPlatform);
        const tbody = document.getElementById('checksBody');
        tbody.innerHTML = data.checks.map(c => `
            <tr>
                <td>${c.id}</td>
                <td>${c.username}</td>
                <td>${c.session_id}</td>
                <td>${new Date(c.check_after).toLocaleString()}</td>
                <td>${c.attempts}/${c.max_attempts}</td>
                <td>
                    <button onclick="forceCheck(${c.id})">Force</button>
                    <button onclick="abandonCheck(${c.id})">Abandon</button>
                </td>
            </tr>
        `).join('');
        document.getElementById('checksCount').textContent = data.count;
    } catch(e) {
        console.error('Failed to load checks:', e);
    }
}

// Actions
async function pauseBot() {
    await api.pauseBot(currentPlatform);
    alert('Bot paused for ' + currentPlatform);
}

async function resumeBot() {
    await api.resumeBot(currentPlatform);
    alert('Bot resumed for ' + currentPlatform);
}

async function toggleWorkflow(id) {
    await api.toggleWorkflow(currentPlatform, id);
    loadWorkflows();
}

async function deleteWorkflow(id) {
    if(confirm('Delete workflow?')) {
        await api.deleteWorkflow(currentPlatform, id);
        loadWorkflows();
    }
}

async function forceCheck(id) {
    await api.forceCheck(currentPlatform, id);
    loadChecks();
}

async function abandonCheck(id) {
    if(confirm('Abandon check?')) {
        await api.abandonCheck(currentPlatform, id);
        loadChecks();
    }
}

function showCreateWorkflow() {
    alert('Create workflow UI stub');
}

function editWorkflow(id) {
    alert('Edit workflow UI stub');
}

function togglePlatform(name) {
    alert(`Toggle platform ${name} (stub)`);
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadTabData('home');
});
