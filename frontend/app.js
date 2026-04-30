let currentPlatform = 'instagram';
let workflowCache = {};   // id → { name, steps }
let allWorkflows = [];    // full workflow objects for search
let editingWorkflowId = null;
let socket = null;
let workerState = {};     // platform → { trigger, engine, recheck }

// pagination
let sessionPage = 0;
const SESSION_PAGE_SIZE = 20;
let allSessions = [];

// ── Utilities ──────────────────────────────────────────────────────────────

function toast(msg, type = 'info') {
    const bg = { info: '#2563eb', success: '#16a34a', error: '#dc2626', warning: '#d97706' };
    Toastify({
        text: msg,
        duration: 3500,
        gravity: 'top',
        position: 'right',
        backgroundColor: bg[type] || bg.info,
        stopOnFocus: true,
    }).showToast();
}

function setLoading(id, on) {
    const el = document.getElementById(id);
    if (el) el.style.display = on ? 'block' : 'none';
}

function stateClass(state) {
    return { COMPLETED: 'state-completed', FAILED: 'state-failed', STEP_RUNNING: 'state-running',
             AWAITING_FOLLOW: 'state-waiting', TIMED_OUT: 'state-timeout' }[state] || 'state-default';
}

function workflowName(id) {
    return workflowCache[id]?.name || `#${id}`;
}

function stepLabel(workflowId, stepIndex) {
    const steps = workflowCache[workflowId]?.steps;
    if (!steps || stepIndex == null) return stepIndex ?? '—';
    const s = steps[stepIndex];
    return s ? `${stepIndex + 1}: ${s.step_type}` : `Step ${stepIndex}`;
}

function addFeedItem(msg, type = 'info') {
    const feed = document.getElementById('liveFeed');
    if (!feed) return;
    const item = document.createElement('div');
    item.className = `feed-item feed-${type}`;
    item.textContent = `${new Date().toLocaleTimeString()} — ${msg}`;
    feed.insertBefore(item, feed.firstChild);
    if (feed.children.length > 30) feed.removeChild(feed.lastChild);
}

// ── Dark mode ──────────────────────────────────────────────────────────────

function initDarkMode() {
    if (localStorage.getItem('darkMode') === '1') {
        document.body.classList.add('dark');
        document.getElementById('darkToggle').textContent = '☀';
    }
}

function toggleDarkMode() {
    const on = document.body.classList.toggle('dark');
    localStorage.setItem('darkMode', on ? '1' : '0');
    document.getElementById('darkToggle').textContent = on ? '☀' : '🌙';
}

// ── SocketIO ───────────────────────────────────────────────────────────────

function initSocketIO() {
    socket = io();

    socket.on('connect', () => console.log('SocketIO connected'));
    socket.on('connect_error', () => console.warn('SocketIO failed'));

    socket.on('trigger_matched', d => {
        addFeedItem(`[${d.platform}] Trigger "${d.keyword}" matched for @${d.username} (${d.workflow_name})`, 'trigger');
        loadStats();
    });
    socket.on('message_sent', d => {
        addFeedItem(`[${d.platform}] Message sent to @${d.username} (step ${d.step_order})`, 'message');
        loadStats();
    });
    socket.on('follow_detected', d => {
        addFeedItem(`[${d.platform}] @${d.username} followed (waited ${d.waited_seconds}s)`, 'follow');
    });
    socket.on('session_completed', d => {
        addFeedItem(`[${d.platform}] Session complete for @${d.username} (${d.workflow_name})`, 'success');
        loadStats();
    });
    socket.on('session_failed', d => {
        addFeedItem(`[${d.platform}] Session failed for @${d.username}: ${d.reason}`, 'error');
        loadStats();
    });
    socket.on('daily_cap_hit', d => {
        toast(`[${d.platform}] Daily cap hit — ${d.queued_count} queued`, 'warning');
    });
    socket.on('platform_error', d => {
        workerState[d.platform] = { error: d.detail };
        toast(`[${d.platform}] Error: ${d.detail}`, 'error');
    });
}

// ── Tab routing ────────────────────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', e => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        const tabId = e.target.dataset.tab;
        document.getElementById(tabId).classList.add('active');
        loadTabData(tabId);
    });
});

document.getElementById('platformSelect').addEventListener('change', e => {
    currentPlatform = e.target.value;
    loadTabData(document.querySelector('.tab-content.active').id);
});

document.getElementById('stateFilter').addEventListener('change', () => {
    sessionPage = 0;
    loadSessions();
});

async function loadTabData(tabId) {
    switch (tabId) {
        case 'home':      await Promise.all([loadStats(), loadRecentSessions()]); break;
        case 'platforms': await loadPlatforms(); break;
        case 'workflows': await loadWorkflows(); break;
        case 'sessions':  sessionPage = 0; await loadSessions(); break;
        case 'checks':    await loadChecks(); break;
    }
}

// ── Stats ──────────────────────────────────────────────────────────────────

async function loadStats() {
    try {
        const data = await api.getStats(currentPlatform);
        document.getElementById('triggersCount').textContent = data.triggers_matched ?? 0;
        document.getElementById('messagesCount').textContent = data.messages_sent ?? 0;
    } catch (e) {
        console.error('Stats load failed:', e);
    }
}

// ── Recent Sessions ────────────────────────────────────────────────────────

async function loadRecentSessions() {
    setLoading('recentSessionsLoading', true);
    try {
        const data = await api.getSessions(currentPlatform);
        const rows = data.sessions.slice(0, 5);
        document.getElementById('sessionsCount').textContent = data.count;
        document.getElementById('recentSessionsBody').innerHTML = rows.length
            ? rows.map(s => `
                <tr class="clickable" onclick="showSessionDetail('${s.id}')">
                    <td>@${s.username}</td>
                    <td>${workflowName(s.workflow_id)}</td>
                    <td><span class="state-badge ${stateClass(s.state)}">${s.state}</span></td>
                    <td>${new Date(s.started_at).toLocaleString()}</td>
                </tr>`).join('')
            : '<tr><td colspan="4" class="empty-row">No sessions</td></tr>';
    } catch (e) {
        toast('Failed to load sessions', 'error');
    } finally {
        setLoading('recentSessionsLoading', false);
    }
}

// ── Platforms ──────────────────────────────────────────────────────────────

async function loadPlatforms() {
    setLoading('platformsLoading', true);
    try {
        const data = await api.getPlatforms();
        const hasFollowPlatform = data.platforms.some(p => p.enabled && p.name !== 'telegram');
        document.getElementById('checksTabBtn').style.display = hasFollowPlatform ? '' : 'none';

        document.getElementById('platformsList').innerHTML = data.platforms.map(p => {
            const ws = workerState[p.name] || {};
            const workerBadges = p.enabled
                ? `<div class="worker-pills">
                    <span class="worker-pill ${ws.error ? 'pill-error' : 'pill-ok'}">trigger</span>
                    <span class="worker-pill ${ws.error ? 'pill-error' : 'pill-ok'}">engine</span>
                    ${p.name !== 'telegram' ? `<span class="worker-pill ${ws.error ? 'pill-error' : 'pill-ok'}">recheck</span>` : ''}
                   </div>`
                : '';
            return `<div class="platform-card ${p.enabled ? 'enabled' : 'disabled'}">
                <div class="platform-card-header">
                    <h3>${p.name.toUpperCase()}</h3>
                    <span class="badge ${p.enabled ? 'badge-active' : 'badge-inactive'}">
                        ${p.status || (p.enabled ? 'RUNNING' : 'DISABLED')}
                    </span>
                </div>
                ${workerBadges}
                <button onclick="togglePlatform('${p.name}', ${p.enabled})">
                    ${p.enabled ? 'Disable' : 'Enable'}
                </button>
            </div>`;
        }).join('') || '<p class="empty-row">No platforms configured</p>';
    } catch (e) {
        toast('Failed to load platforms', 'error');
    } finally {
        setLoading('platformsLoading', false);
    }
}

async function togglePlatform(name, isEnabled) {
    try {
        if (isEnabled) {
            await api.disablePlatform(name);
            toast(`${name} disabled`, 'info');
        } else {
            await api.enablePlatform(name);
            toast(`${name} enabled`, 'success');
        }
        loadPlatforms();
    } catch (e) {
        toast(`Failed to toggle ${name}`, 'error');
    }
}

// ── Workflows ──────────────────────────────────────────────────────────────

async function loadWorkflows() {
    setLoading('workflowsLoading', true);
    try {
        const data = await api.getWorkflows(currentPlatform);
        workflowCache = {};
        allWorkflows = data.workflows;
        data.workflows.forEach(w => {
            workflowCache[w.id] = { name: w.name, steps: w.steps || [] };
        });
        renderWorkflows(allWorkflows, document.getElementById('workflowSearch')?.value || '');
    } catch (e) {
        toast('Failed to load workflows', 'error');
    } finally {
        setLoading('workflowsLoading', false);
    }
}

function renderWorkflows(workflows, query) {
    const filtered = query
        ? workflows.filter(w =>
            w.name.toLowerCase().includes(query.toLowerCase()) ||
            w.trigger_keyword.toLowerCase().includes(query.toLowerCase()))
        : workflows;

    document.getElementById('workflowsList').innerHTML = filtered.length
        ? filtered.map(w => `
            <div class="workflow-card ${w.active ? '' : 'inactive'}">
                <div class="workflow-card-header">
                    <h3>${w.name}</h3>
                    <span class="badge ${w.active ? 'badge-active' : 'badge-inactive'}">
                        ${w.active ? 'Active' : 'Paused'}
                    </span>
                </div>
                <p><strong>Trigger:</strong> <code>${w.trigger_keyword}</code></p>
                <p><strong>Mode:</strong> ${w.match_mode} &nbsp;|&nbsp; <strong>Priority:</strong> ${w.priority}</p>
                <details class="steps-details">
                    <summary>${(w.steps || []).length} step(s)</summary>
                    <ol class="steps-list">
                        ${(w.steps || []).map(s =>
                            `<li><code>${s.step_type}</code>${s.send_if ? ` [${s.send_if}]` : ''}${s.message_template ? `<br><span class="step-msg">${s.message_template}</span>` : ''}</li>`
                        ).join('')}
                    </ol>
                </details>
                <div class="workflow-actions">
                    <button onclick="editWorkflow('${w.id}')">Edit</button>
                    <button onclick="toggleWorkflow('${w.id}')">${w.active ? 'Pause' : 'Resume'}</button>
                    <button class="btn-danger" onclick="deleteWorkflow('${w.id}')">Delete</button>
                </div>
            </div>`).join('')
        : `<p class="empty-row">${query ? 'No workflows match "' + query + '"' : 'No workflows for this platform'}</p>`;
}

async function toggleWorkflow(id) {
    try {
        await api.toggleWorkflow(currentPlatform, id);
        toast('Workflow toggled', 'success');
        loadWorkflows();
    } catch (e) {
        toast('Failed to toggle workflow', 'error');
    }
}

async function deleteWorkflow(id) {
    if (!confirm('Delete this workflow? Sessions already in progress will continue.')) return;
    try {
        await api.deleteWorkflow(currentPlatform, id);
        toast('Workflow deleted', 'info');
        loadWorkflows();
    } catch (e) {
        toast('Failed to delete workflow', 'error');
    }
}

// ── Sessions + Pagination ──────────────────────────────────────────────────

async function loadSessions() {
    setLoading('sessionsLoading', true);
    try {
        const state = document.getElementById('stateFilter').value;
        const data = await api.getSessions(currentPlatform, state || null);
        allSessions = data.sessions;
        renderSessionsPage();
    } catch (e) {
        toast('Failed to load sessions', 'error');
    } finally {
        setLoading('sessionsLoading', false);
    }
}

function renderSessionsPage() {
    const total = allSessions.length;
    const pages = Math.ceil(total / SESSION_PAGE_SIZE) || 1;
    sessionPage = Math.min(sessionPage, pages - 1);
    const slice = allSessions.slice(sessionPage * SESSION_PAGE_SIZE, (sessionPage + 1) * SESSION_PAGE_SIZE);

    document.getElementById('sessionsBody').innerHTML = slice.length
        ? slice.map(s => `
            <tr class="clickable" onclick="showSessionDetail('${s.id}')">
                <td>@${s.username}</td>
                <td>${workflowName(s.workflow_id)}</td>
                <td><span class="state-badge ${stateClass(s.state)}">${s.state}</span></td>
                <td>${stepLabel(s.workflow_id, s.current_step)}</td>
                <td>${s.follow_status || '—'}</td>
                <td>${new Date(s.started_at).toLocaleString()}</td>
            </tr>`).join('')
        : '<tr><td colspan="6" class="empty-row">No sessions found</td></tr>';

    document.getElementById('sessionsPagination').innerHTML = total > SESSION_PAGE_SIZE ? `
        <span class="page-info">Page ${sessionPage + 1} of ${pages} (${total} total)</span>
        <button onclick="sessionPage=Math.max(0,sessionPage-1);renderSessionsPage()" ${sessionPage === 0 ? 'disabled' : ''}>← Prev</button>
        <button onclick="sessionPage=Math.min(${pages-1},sessionPage+1);renderSessionsPage()" ${sessionPage >= pages-1 ? 'disabled' : ''}>Next →</button>
    ` : '';
}

// ── Pending Checks ─────────────────────────────────────────────────────────

async function loadChecks() {
    setLoading('checksLoading', true);
    try {
        const data = await api.getPendingChecks(currentPlatform);
        document.getElementById('checksCount').textContent = data.count;
        document.getElementById('checksBody').innerHTML = data.checks.length
            ? data.checks.map(c => `
                <tr>
                    <td>@${c.username}</td>
                    <td>${c.session_id}</td>
                    <td>${new Date(c.check_after).toLocaleString()}</td>
                    <td>${c.attempts}/${c.max_attempts}</td>
                    <td>
                        <button onclick="forceCheck('${c.id}')">Force</button>
                        <button onclick="abandonCheck('${c.id}')">Abandon</button>
                    </td>
                </tr>`).join('')
            : '<tr><td colspan="5" class="empty-row">No pending checks</td></tr>';
    } catch (e) {
        toast('Failed to load checks', 'error');
    } finally {
        setLoading('checksLoading', false);
    }
}

async function forceCheck(id) {
    try {
        await api.forceCheck(id);
        toast('Check forced', 'success');
        loadChecks();
    } catch (e) {
        toast('Failed to force check', 'error');
    }
}

async function abandonCheck(id) {
    if (!confirm('Abandon this check?')) return;
    try {
        await api.abandonCheck(id);
        toast('Check abandoned', 'info');
        loadChecks();
    } catch (e) {
        toast('Failed to abandon check', 'error');
    }
}

// ── Bot Control ────────────────────────────────────────────────────────────

async function pauseBot() {
    try {
        await api.pauseBot(currentPlatform);
        toast(`Bot paused for ${currentPlatform}`, 'info');
    } catch (e) {
        toast('Failed to pause bot', 'error');
    }
}

async function resumeBot() {
    try {
        await api.resumeBot(currentPlatform);
        toast(`Bot resumed for ${currentPlatform}`, 'success');
    } catch (e) {
        toast('Failed to resume bot', 'error');
    }
}

// ── Session Detail Modal ───────────────────────────────────────────────────

async function showSessionDetail(id) {
    document.getElementById('sessionModal').style.display = 'flex';
    document.getElementById('sessionDetail').innerHTML = '<p class="empty-row">Loading...</p>';
    try {
        const [s, traceData] = await Promise.all([
            api.getSession(id, currentPlatform),
            api.getSessionTrace(id, currentPlatform).catch(() => ({ trace: [] }))
        ]);

        const steps = workflowCache[s.workflow_id]?.steps || [];
        const currentIdx = s.current_step ?? -1;
        const trace = traceData.trace || [];

        // Current step message preview
        const curStep = steps[currentIdx];
        const msgPreview = curStep?.message_template
            ? `<div class="detail-row"><strong>Step Message:</strong>
               <span class="step-msg-preview">${curStep.message_template}</span></div>`
            : '';

        // Step progress bar
        const progressHtml = steps.length
            ? `<div class="step-progress">
                ${steps.map((st, i) => {
                    let cls = 'step-prog-pending';
                    if (i < currentIdx) cls = 'step-prog-done';
                    else if (i === currentIdx) cls = 'step-prog-active';
                    return `<div class="step-prog-item ${cls}">
                        <div class="step-prog-dot"></div>
                        <div class="step-prog-label">${st.step_type}${st.send_if ? `<br><small>${st.send_if}</small>` : ''}</div>
                    </div>`;
                }).join('<div class="step-prog-line"></div>')}
               </div>`
            : '';

        // Execution trace timeline
        const traceHtml = trace.length
            ? `<div class="trace-timeline">
                ${trace.map(t => `
                    <div class="trace-item trace-${t.status}">
                        <div class="trace-dot"></div>
                        <div class="trace-body">
                            <div class="trace-header">
                                <code>${t.step_type}</code>
                                <span class="trace-status trace-status-${t.status}">${t.status}</span>
                                <span class="trace-time">${new Date(t.executed_at).toLocaleTimeString()}</span>
                            </div>
                            ${t.message_preview ? `<div class="trace-msg">${t.message_preview}</div>` : ''}
                        </div>
                    </div>`).join('')}
               </div>`
            : '<p class="empty-row" style="margin-top:8px;">No execution history yet</p>';

        document.getElementById('sessionDetail').innerHTML = `
            <div class="detail-row"><strong>Username:</strong> @${s.username}</div>
            <div class="detail-row"><strong>Platform:</strong> ${s.platform}</div>
            <div class="detail-row"><strong>Workflow:</strong> ${workflowName(s.workflow_id)}</div>
            <div class="detail-row"><strong>State:</strong>
                <span class="state-badge ${stateClass(s.state)}">${s.state}</span>
            </div>
            <div class="detail-row"><strong>Current Step:</strong> ${stepLabel(s.workflow_id, s.current_step)}</div>
            ${msgPreview}
            <div class="detail-row"><strong>Follow Status:</strong> ${s.follow_status || '—'}</div>
            <div class="detail-row"><strong>Started:</strong> ${new Date(s.started_at).toLocaleString()}</div>
            <div class="detail-row"><strong>Last Action:</strong> ${s.last_action_at ? new Date(s.last_action_at).toLocaleString() : '—'}</div>
            ${progressHtml ? `<div class="detail-row" style="margin-top:12px;"><strong>Step Progress</strong></div>${progressHtml}` : ''}
            <div class="detail-row" style="margin-top:16px;"><strong>Execution Trace</strong></div>
            ${traceHtml}`;
    } catch (e) {
        document.getElementById('sessionDetail').innerHTML = '<p class="error-text">Failed to load session detail.</p>';
    }
}

function closeSessionModal() {
    document.getElementById('sessionModal').style.display = 'none';
}

// ── Workflow Modal ─────────────────────────────────────────────────────────

function showCreateWorkflow() {
    editingWorkflowId = null;
    document.getElementById('workflowModalTitle').textContent = 'Create Workflow';
    document.getElementById('workflowForm').reset();
    document.getElementById('wfSteps').innerHTML = '';
    addStep();
    document.getElementById('workflowModal').style.display = 'flex';
}

async function editWorkflow(id) {
    editingWorkflowId = id;
    document.getElementById('workflowModalTitle').textContent = 'Edit Workflow';
    try {
        const data = await api.getWorkflows(currentPlatform);
        const w = data.workflows.find(x => x.id === id);
        if (!w) { toast('Workflow not found', 'error'); return; }

        document.getElementById('wfName').value = w.name || '';
        document.getElementById('wfTrigger').value = w.trigger_keyword || '';
        document.getElementById('wfSourceId').value = w.source_id || '';
        document.getElementById('wfLink').value = w.link || '';
        document.getElementById('wfMatchMode').value = w.match_mode || 'contains';
        document.getElementById('wfPriority').value = w.priority || 1;

        document.getElementById('wfSteps').innerHTML = '';
        (w.steps || [{ step_type: 'send_message', send_if: 'always', message_template: '' }])
            .forEach(s => addStep(s));

        document.getElementById('workflowModal').style.display = 'flex';
    } catch (e) {
        toast('Failed to load workflow data', 'error');
    }
}

function addStep(data = {}) {
    const container = document.getElementById('wfSteps');
    const idx = container.children.length;
    const div = document.createElement('div');
    div.className = 'step-row';
    div.innerHTML = `
        <div class="step-row-header">
            <span>Step ${idx + 1}</span>
            <button type="button" class="step-remove" onclick="this.closest('.step-row').remove(); renumberSteps()">✕</button>
        </div>
        <div class="step-fields">
            <select class="step-type" onchange="onStepTypeChange(this)">
                <option value="check_follow" ${data.step_type === 'check_follow' ? 'selected' : ''}>check_follow</option>
                <option value="send_message" ${(data.step_type === 'send_message' || !data.step_type) ? 'selected' : ''}>send_message</option>
                <option value="wait_for_follow" ${data.step_type === 'wait_for_follow' ? 'selected' : ''}>wait_for_follow</option>
                <option value="delay" ${data.step_type === 'delay' ? 'selected' : ''}>delay</option>
            </select>
            <select class="step-send-if">
                <option value="always" ${(data.send_if === 'always' || !data.send_if) ? 'selected' : ''}>always</option>
                <option value="following" ${data.send_if === 'following' ? 'selected' : ''}>following</option>
                <option value="not_following" ${data.send_if === 'not_following' ? 'selected' : ''}>not_following</option>
                <option value="now_following" ${data.send_if === 'now_following' ? 'selected' : ''}>now_following</option>
            </select>
        </div>
        <textarea class="step-message" placeholder="Message template — use {username}, {link}">${data.message_template || ''}</textarea>`;
    container.appendChild(div);
    onStepTypeChange(div.querySelector('.step-type'));
}

function onStepTypeChange(select) {
    const row = select.closest('.step-row');
    const msg = row.querySelector('.step-message');
    const sendIf = row.querySelector('.step-send-if');
    msg.style.display = select.value === 'send_message' ? 'block' : 'none';
    sendIf.style.display = (select.value === 'send_message' || select.value === 'check_follow') ? '' : 'none';
}

function renumberSteps() {
    document.querySelectorAll('#wfSteps .step-row').forEach((row, i) => {
        row.querySelector('.step-row-header span').textContent = `Step ${i + 1}`;
    });
}

function closeWorkflowModal() {
    document.getElementById('workflowModal').style.display = 'none';
}

async function saveWorkflow(e) {
    e.preventDefault();
    const name = document.getElementById('wfName').value.trim();
    const trigger = document.getElementById('wfTrigger').value.trim();
    const sourceId = document.getElementById('wfSourceId').value.trim();
    if (!name || !trigger || !sourceId) {
        toast('Name, trigger keyword, and source ID are required', 'warning');
        return;
    }

    const steps = Array.from(document.querySelectorAll('#wfSteps .step-row')).map(row => ({
        step_type: row.querySelector('.step-type').value,
        send_if: row.querySelector('.step-send-if').value,
        message_template: row.querySelector('.step-message').value.trim() || null,
    }));

    const payload = {
        name,
        trigger_keyword: trigger,
        source_id: sourceId,
        link: document.getElementById('wfLink').value.trim() || null,
        match_mode: document.getElementById('wfMatchMode').value,
        priority: parseInt(document.getElementById('wfPriority').value) || 1,
        steps,
    };

    try {
        if (editingWorkflowId) {
            await api.updateWorkflow(currentPlatform, editingWorkflowId, payload);
            toast('Workflow updated', 'success');
        } else {
            await api.createWorkflow(currentPlatform, payload);
            toast('Workflow created', 'success');
        }
        closeWorkflowModal();
        loadWorkflows();
    } catch (e) {
        toast('Failed to save workflow', 'error');
    }
}

// ── Init ───────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initSocketIO();
    loadTabData('home');
});
