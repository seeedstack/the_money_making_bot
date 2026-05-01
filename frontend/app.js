let currentPlatform = 'instagram';
let platformCache = [];
let workflowCache = {};
let allWorkflows = [];
let editingWorkflowId = null;
let socket = null;
let workerState = {};
let allSessions = [];
let sessionPage = 0;
const SESSION_PAGE_SIZE = 20;
let feedItemCount = 0;

/* ============================================================
   UTILITIES
   ============================================================ */
function setLoading(id, on) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle('active', !!on);
}

function toast(msg, type = 'info') {
  const colors = {
    info:    { bg: 'var(--info)',  cls: 'toast-info' },
    success: { bg: 'var(--ok)',    cls: 'toast-success' },
    error:   { bg: 'var(--err)',   cls: 'toast-error' },
    warning: { bg: 'var(--warn)', cls: 'toast-warning' },
  };
  const c = colors[type] || colors.info;
  Toastify({
    text: msg,
    duration: 3500,
    gravity: 'top',
    position: 'right',
    className: c.cls,
    style: { background: getCss(c.bg) },
  }).showToast();
}

function getCss(name) {
  if (!name.startsWith('var(')) return name;
  const v = name.slice(4, -1);
  return getComputedStyle(document.documentElement).getPropertyValue(v).trim() || '#2563eb';
}

function fmtTime(ts) {
  const d = new Date(ts);
  return [d.getHours(), d.getMinutes(), d.getSeconds()].map(n => String(n).padStart(2, '0')).join(':');
}

function fmtRelative(ts) {
  if (!ts) return '—';
  const s = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (s < 60) return s + 's ago';
  if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago';
  return Math.floor(s / 86400) + 'd ago';
}

function shortId(id) { return '#' + (id || '').slice(-6); }
function platformGlyph(p) { return (p || '?')[0].toUpperCase(); }
function escapeHtml(s) {
  return String(s || '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );
}

function workflowName(id) { return workflowCache[id]?.name || shortId(id); }
function stepLabel(workflowId, stepIndex) {
  const wf = workflowCache[workflowId];
  if (!wf || stepIndex == null) return `—`;
  const s = wf.steps[stepIndex];
  return s ? `${stepIndex}: ${s.step_type}` : `step ${stepIndex}`;
}

function stateClass(state) {
  const map = {
    COMPLETED: 'ok', completed: 'ok',
    FAILED: 'err', failed: 'err', abandoned: 'err',
    TIMED_OUT: 'warn', timed_out: 'warn',
    STEP_RUNNING: 'info', active: 'info',
    AWAITING_FOLLOW: 'warn', awaiting_follow: 'warn', awaiting_reply: 'warn',
  };
  return map[state] || 'info';
}

function normalizeState(state) {
  const map = {
    STEP_RUNNING: 'running',
    AWAITING_FOLLOW: 'awaiting_follow',
    COMPLETED: 'completed',
    FAILED: 'failed',
    TIMED_OUT: 'timed_out',
  };
  return map[state] || (state || '').toLowerCase();
}

/* ============================================================
   THEME
   ============================================================ */
function applyTheme() {
  document.body.classList.toggle('dark', localStorage.getItem('darkMode') === '1');
}

function toggleTheme() {
  const dark = !document.body.classList.contains('dark');
  document.body.classList.toggle('dark', dark);
  localStorage.setItem('darkMode', dark ? '1' : '0');
}

applyTheme();

/* ============================================================
   PLATFORM SELECT
   ============================================================ */
function renderPlatformSelect() {
  const enabled = platformCache.filter(p => p.enabled);
  const wrap = document.getElementById('platformSelect');
  if (!wrap) return;
  wrap.innerHTML = enabled.map(p => `
    <button data-platform="${p.name}" class="${p.name === currentPlatform ? 'active' : ''}">
      <span class="platform-glyph"></span>${p.name}
    </button>
  `).join('');
  wrap.querySelectorAll('button').forEach(b => {
    b.onclick = () => {
      currentPlatform = b.dataset.platform;
      renderPlatformSelect();
      document.querySelectorAll('.crumbPlatformLabel, #crumbPlatform').forEach(e => e.textContent = currentPlatform);
      const active = document.querySelector('.tab-btn.active')?.dataset.tab;
      if (active) loadTabData(active);
    };
  });
  document.querySelectorAll('.crumbPlatformLabel, #crumbPlatform').forEach(e => e.textContent = currentPlatform);
}

/* ============================================================
   TABS
   ============================================================ */
function setActiveTab(id) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === id));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === id));
  loadTabData(id);
}

async function loadTabData(id) {
  switch (id) {
    case 'home':      await Promise.all([loadStats(), loadWorkerHealth(), loadTodaySummary()]); break;
    case 'workflows': await loadWorkflows(); break;
    case 'sessions':  await loadWorkflows(); await loadSessions(); break;
    case 'platforms': await loadPlatforms(); break;
    case 'checks':    await loadChecks(); break;
  }
}

/* ============================================================
   HOME — stats, feed, worker pills, today
   ============================================================ */
async function loadStats() {
  setLoading('feedLoading', true);
  try {
    const s = await api.getStats(currentPlatform);
    const row = document.getElementById('statRow');
    if (!row) return;
    const sparkPath = (vals) => {
      const max = Math.max(...vals, 1);
      const pts = vals.map((v, i) => `${i * (60 / (vals.length - 1))},${22 - (v / max) * 20}`).join(' ');
      return `<polyline fill="none" stroke="currentColor" stroke-width="1.5" points="${pts}"/>`;
    };
    const fakeSpark = () => Array.from({ length: 8 }, () => Math.random() * 0.7 + 0.3);
    row.innerHTML = `
      <div class="stat signature">
        <div class="label">Triggers matched</div>
        <div class="value">${(s.triggers_matched || 0).toLocaleString()}</div>
        <div class="delta"><span class="up">↑</span> today</div>
        <svg class="spark" viewBox="0 0 60 22">${sparkPath(fakeSpark())}</svg>
      </div>
      <div class="stat">
        <div class="label">Messages sent</div>
        <div class="value">${(s.messages_sent || 0).toLocaleString()}</div>
        <div class="delta">last 24h</div>
        <svg class="spark" viewBox="0 0 60 22">${sparkPath(fakeSpark())}</svg>
      </div>
      <div class="stat">
        <div class="label">Follows detected</div>
        <div class="value">${(s.follows_detected || 0).toLocaleString()}</div>
        <div class="delta">${currentPlatform === 'telegram' ? 'n/a on telegram' : 'last 24h'}</div>
        <svg class="spark" viewBox="0 0 60 22">${sparkPath(fakeSpark())}</svg>
      </div>
      <div class="stat">
        <div class="label">Sessions completed</div>
        <div class="value">${(s.completed || s.sessions_completed || 0).toLocaleString()}</div>
        <div class="delta">last 24h</div>
        <svg class="spark" viewBox="0 0 60 22">${sparkPath(fakeSpark())}</svg>
      </div>
    `;
  } catch (e) { toast('Failed to load stats', 'error'); }
  finally { setLoading('feedLoading', false); }
}

async function loadWorkerHealth() {
  const list = document.getElementById('workerList');
  const metaEl = document.getElementById('workerMeta');
  const enabled = platformCache.filter(p => p.enabled);
  if (metaEl) metaEl.textContent = `${enabled.length} platform${enabled.length === 1 ? '' : 's'} enabled`;
  if (!list) return;
  if (!enabled.length) {
    list.innerHTML = '<div class="card-pad" style="color:var(--text-muted);font-size:13px;">No platforms enabled</div>';
    return;
  }
  list.innerHTML = enabled.map(p => {
    const errored = !!workerState[p.name]?.error;
    const workers = ['trigger', 'engine'];
    if (p.name !== 'telegram') workers.push('recheck');
    const pills = workers.map(w =>
      errored
        ? `<span class="pill err"><span class="dot"></span>${w}</span>`
        : `<span class="pill ok"><span class="dot"></span>${w}</span>`
    ).join('');
    return `<div class="worker-row">
      <div class="name"><span class="platform-chip">${platformGlyph(p.name)}</span>${p.name}</div>
      <div class="worker-pills">${pills}</div>
    </div>`;
  }).join('');
}

async function loadTodaySummary() {
  const todayEl = document.getElementById('todayDate');
  const activeEl = document.getElementById('todayActive');
  const capEl = document.getElementById('todayCap');
  const openEl = document.getElementById('todayOpen');
  const platformEl = document.getElementById('todayPlatform');

  if (todayEl) todayEl.textContent = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const p = platformCache.find(x => x.name === currentPlatform);
  const activeWfs = allWorkflows.filter(w => w.active).length;
  const totalWfs = allWorkflows.length;
  if (activeEl) activeEl.textContent = totalWfs ? `${activeWfs} / ${totalWfs}` : '—';
  if (capEl) capEl.textContent = p?.daily_dm_cap ? `—/${p.daily_dm_cap}` : '∞';
  if (openEl) openEl.textContent = '—';
  if (platformEl) platformEl.textContent = currentPlatform;
}

function addFeedItem(text, level = 'info', meta = '') {
  const feed = document.getElementById('feed');
  if (!feed) return;
  const empty = feed.querySelector('.feed-empty');
  if (empty) empty.remove();
  feedItemCount++;
  const countEl = document.getElementById('homeFeedCount');
  if (countEl) countEl.textContent = feedItemCount;

  const glyphMap = { success: '✓', error: '!', warning: '△', info: '•' };
  const item = document.createElement('div');
  item.className = `feed-item ${level}`;
  item.innerHTML = `
    <div class="time mono">${fmtTime(Date.now())}</div>
    <div class="glyph">${glyphMap[level] || '•'}</div>
    <div class="text">${text}${meta ? `<div class="meta">${meta}</div>` : ''}</div>
    <span class="platform-tag">${currentPlatform}</span>
  `;
  feed.prepend(item);
  while (feed.children.length > 40) feed.lastElementChild.remove();
}

/* ============================================================
   WORKFLOWS
   ============================================================ */
async function loadWorkflows() {
  setLoading('workflowsLoading', true);
  try {
    const r = await api.getWorkflows(currentPlatform);
    allWorkflows = r.workflows;
    workflowCache = {};
    for (const w of allWorkflows) workflowCache[w.id] = { name: w.name, steps: w.steps || [] };
    const countEl = document.getElementById('workflowCount');
    if (countEl) countEl.textContent = allWorkflows.length;
    if (document.getElementById('workflowGrid')) renderWorkflows(allWorkflows, document.getElementById('wfSearch')?.value || '');
  } catch (e) { toast('Failed to load workflows', 'error'); }
  finally { setLoading('workflowsLoading', false); }
}

function renderWorkflows(list, query = '') {
  const grid = document.getElementById('workflowGrid');
  if (!grid) return;
  const q = query.trim().toLowerCase();
  const filtered = q
    ? list.filter(w => (w.name || '').toLowerCase().includes(q) || (w.trigger_keyword || '').toLowerCase().includes(q))
    : list;
  const countEl = document.getElementById('wfCountLabel');
  if (countEl) countEl.textContent = q ? `${filtered.length} of ${list.length}` : `${list.length} workflow${list.length === 1 ? '' : 's'}`;

  if (!filtered.length) {
    grid.innerHTML = `<div class="empty" style="grid-column:1/-1"><div class="glyph">✦</div><h4>No workflows</h4><p>${q ? 'No matches for "' + escapeHtml(q) + '"' : 'Click <em>New workflow</em> to create one.'}</p></div>`;
    return;
  }
  grid.innerHTML = filtered.map(w => {
    const isActive = w.active;
    const stepPills = (w.steps || []).slice(0, 4).map(s => `<span class="step-pill">${s.step_type}</span>`).join('<span class="arrow">→</span>');
    const more = (w.steps || []).length > 4 ? `<span class="step-pill">+${w.steps.length - 4}</span>` : '';
    return `
    <div class="wf-card">
      <div class="head">
        <div>
          <div class="name">${escapeHtml(w.name)}</div>
          <div class="id mono">${shortId(w.id)}</div>
        </div>
        <label class="switch" onclick="event.stopPropagation()">
          <input type="checkbox" ${isActive ? 'checked' : ''} onchange="toggleWorkflowAction('${w.id}')">
          <span class="switch-track"></span>
        </label>
      </div>
      <div class="trigger">
        <span style="color:var(--text-muted)">on</span>
        <span class="kw">"${escapeHtml(w.trigger_keyword)}"</span>
        <span style="color:var(--text-muted); margin-left:auto;">→ ${escapeHtml(w.source_id || '')}</span>
      </div>
      <div class="steps">${stepPills}${more}</div>
      <div class="footer">
        <span class="pill ${isActive ? 'ok' : ''}"><span class="dot"></span>${isActive ? 'live' : 'paused'}</span>
        <div class="actions">
          <button class="btn ghost sm" onclick="editWorkflow('${w.id}')">Edit</button>
        </div>
      </div>
    </div>`;
  }).join('');
}

async function toggleWorkflowAction(id) {
  try {
    await api.toggleWorkflow(currentPlatform, id);
    const w = allWorkflows.find(w => w.id === id);
    if (w) w.active = !w.active;
    renderWorkflows(allWorkflows, document.getElementById('wfSearch')?.value || '');
    toast(`Workflow ${w?.active ? 'enabled' : 'paused'}`, 'success');
  } catch (e) { toast('Toggle failed', 'error'); }
}

function showCreateWorkflow() {
  editingWorkflowId = null;
  document.getElementById('wfModalTitle').textContent = 'New workflow';
  document.getElementById('wfModalMeta').textContent = `creating · platform=${currentPlatform}`;
  document.getElementById('wfDeleteBtn').style.display = 'none';
  document.getElementById('wfName').value = '';
  document.getElementById('wfTrigger').value = '';
  document.getElementById('wfSource').value = '';
  document.getElementById('wfCap').value = '';
  document.getElementById('stepList').innerHTML = '';
  addStep();
  document.getElementById('workflowModal').classList.add('active');
}

function editWorkflow(id) {
  const w = allWorkflows.find(x => x.id === id);
  if (!w) return;
  editingWorkflowId = id;
  document.getElementById('wfModalTitle').textContent = 'Edit workflow';
  document.getElementById('wfModalMeta').textContent = `editing ${shortId(id)} · platform=${currentPlatform}`;
  document.getElementById('wfDeleteBtn').style.display = '';
  document.getElementById('wfName').value = w.name || '';
  document.getElementById('wfTrigger').value = w.trigger_keyword || '';
  document.getElementById('wfSource').value = w.source_id || '';
  document.getElementById('wfCap').value = w.daily_cap || '';
  document.getElementById('stepList').innerHTML = '';
  (w.steps || []).forEach(s => addStep(s));
  document.getElementById('workflowModal').classList.add('active');
}

function closeWorkflowModal() {
  document.getElementById('workflowModal').classList.remove('active');
}

function addStep(preset) {
  const list = document.getElementById('stepList');
  const idx = list.children.length;
  const types = ['send_message', 'wait_for_follow', 'check_follow', 'delay'];
  const sendIfs = ['always', 'on_follow', 'not_following', 'now_following'];
  const t = preset?.step_type || 'send_message';
  const sif = preset?.send_if || 'always';
  const msg = preset?.message_template || '';
  const div = document.createElement('div');
  div.className = 'step-card';
  div.innerHTML = `
    <span class="step-num">${idx + 1}</span>
    <button class="remove-step" type="button" title="Remove" onclick="removeStep(this)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </button>
    <div class="step-head">
      <select class="step-type" onchange="onStepTypeChange(this)">
        ${types.map(x => `<option value="${x}" ${x === t ? 'selected' : ''}>${x}</option>`).join('')}
      </select>
      <select class="step-send-if">
        ${sendIfs.map(x => `<option value="${x}" ${x === sif ? 'selected' : ''}>${x}</option>`).join('')}
      </select>
    </div>
    <div class="step-body">
      <textarea class="step-message" placeholder="Message template — supports {{username}}…">${escapeHtml(msg)}</textarea>
    </div>
  `;
  list.appendChild(div);
  onStepTypeChange(div.querySelector('.step-type'));
}

function removeStep(btn) {
  btn.closest('.step-card').remove();
  document.querySelectorAll('#stepList .step-card').forEach((c, i) => c.querySelector('.step-num').textContent = i + 1);
}

function onStepTypeChange(sel) {
  const card = sel.closest('.step-card');
  const t = sel.value;
  card.querySelector('.step-message').style.display = t === 'send_message' ? '' : 'none';
  card.querySelector('.step-send-if').style.display = (t === 'send_message' || t === 'check_follow') ? '' : 'none';
}

async function saveWorkflow(e) {
  e.preventDefault();
  const name = document.getElementById('wfName').value.trim();
  const trigger = document.getElementById('wfTrigger').value.trim();
  const source = document.getElementById('wfSource').value.trim();
  const cap = parseInt(document.getElementById('wfCap').value) || 0;
  if (!name || !trigger || !source) { toast('Fill in name, trigger and source', 'warning'); return; }
  const steps = [...document.querySelectorAll('#stepList .step-card')].map(c => ({
    step_type: c.querySelector('.step-type').value,
    send_if: c.querySelector('.step-send-if').value,
    message_template: c.querySelector('.step-message').value,
  }));
  if (!steps.length) { toast('Add at least one step', 'warning'); return; }
  try {
    if (editingWorkflowId) {
      await api.updateWorkflow(currentPlatform, editingWorkflowId, { name, trigger_keyword: trigger, source_id: source, daily_cap: cap, steps });
      toast('Workflow saved', 'success');
    } else {
      await api.createWorkflow(currentPlatform, { name, trigger_keyword: trigger, source_id: source, daily_cap: cap, steps });
      toast('Workflow created', 'success');
    }
    closeWorkflowModal();
    await loadWorkflows();
  } catch (err) { toast('Save failed', 'error'); }
}

async function deleteCurrentWorkflow() {
  if (!editingWorkflowId) return;
  if (!confirm('Delete this workflow? This cannot be undone.')) return;
  try {
    await api.deleteWorkflow(currentPlatform, editingWorkflowId);
    toast('Workflow deleted', 'success');
    closeWorkflowModal();
    await loadWorkflows();
  } catch (e) { toast('Delete failed', 'error'); }
}

/* ============================================================
   SESSIONS
   ============================================================ */
async function loadSessions() {
  setLoading('sessionsLoading', true);
  sessionPage = 0;
  try {
    const state = document.getElementById('stateFilter').value;
    const r = await api.getSessions(currentPlatform, state || null);
    allSessions = r.sessions;
    const countEl = document.getElementById('sessionCount');
    const totalEl = document.getElementById('sessionTotalLabel');
    if (countEl) countEl.textContent = r.count;
    if (totalEl) totalEl.textContent = `${r.count} session${r.count === 1 ? '' : 's'}`;
    renderSessionsPage();
  } catch (e) { toast('Failed to load sessions', 'error'); }
  finally { setLoading('sessionsLoading', false); }
}

function renderSessionsPage() {
  const tbody = document.getElementById('sessionBody');
  if (!tbody) return;
  const start = sessionPage * SESSION_PAGE_SIZE;
  const slice = allSessions.slice(start, start + SESSION_PAGE_SIZE);
  if (!slice.length) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty" style="border:0; background:transparent;"><div class="glyph">∅</div><h4>No sessions</h4><p>No sessions match the current filter.</p></div></td></tr>`;
  } else {
    tbody.innerHTML = slice.map(s => {
      const sc = stateClass(s.state);
      const ns = normalizeState(s.state);
      const steps = workflowCache[s.workflow_id]?.steps || [];
      const totalSteps = steps.length || s.total_steps || 0;
      return `
      <tr class="clickable" onclick="showSessionDetail('${s.id}')">
        <td class="id-cell">${shortId(s.id)}</td>
        <td class="user-cell">@${escapeHtml(s.username)}</td>
        <td>${escapeHtml(workflowName(s.workflow_id))}</td>
        <td><span class="pill ${sc}"><span class="dot"></span>${ns}</span></td>
        <td class="mono" style="color:var(--text-muted); font-size:12px;">${(s.current_step ?? 0)}/${totalSteps}</td>
        <td style="color:var(--text-muted); font-size:12.5px;">${fmtRelative(s.started_at)}</td>
      </tr>`;
    }).join('');
  }
  const pager = document.getElementById('sessionPager');
  if (!pager) return;
  const totalPages = Math.max(1, Math.ceil(allSessions.length / SESSION_PAGE_SIZE));
  pager.innerHTML = `
    <span>Page ${sessionPage + 1} of ${totalPages} · ${allSessions.length} rows</span>
    <span class="pager-actions">
      <button class="btn secondary sm" onclick="prevSessionPage()" ${sessionPage === 0 ? 'disabled' : ''}>Prev</button>
      <button class="btn secondary sm" onclick="nextSessionPage()" ${sessionPage >= totalPages - 1 ? 'disabled' : ''}>Next</button>
    </span>
  `;
}

function prevSessionPage() { if (sessionPage > 0) { sessionPage--; renderSessionsPage(); } }
function nextSessionPage() {
  const total = Math.ceil(allSessions.length / SESSION_PAGE_SIZE);
  if (sessionPage < total - 1) { sessionPage++; renderSessionsPage(); }
}

async function showSessionDetail(id) {
  const modal = document.getElementById('sessionModal');
  const body = document.getElementById('sessionModalBody');
  body.innerHTML = `<div class="skeleton" style="height:40px; margin-bottom:14px;"></div><div class="skeleton" style="height:80px; margin-bottom:14px;"></div><div class="skeleton" style="height:120px;"></div>`;
  document.getElementById('sessionModalTitle').textContent = 'Session ' + shortId(id);
  document.getElementById('sessionModalMeta').textContent = id;
  modal.classList.add('active');
  try {
    const [s, traceData] = await Promise.all([
      api.getSession(id, currentPlatform),
      api.getSessionTrace(id, currentPlatform).catch(() => ({ trace: [] }))
    ]);
    if (!s) { body.innerHTML = '<div class="empty"><h4>Session not found</h4></div>'; return; }
    const steps = workflowCache[s.workflow_id]?.steps || [];
    const totalSteps = steps.length;
    const currentStep = s.current_step ?? 0;
    const sc = stateClass(s.state);
    const ns = normalizeState(s.state);

    const dots = [];
    for (let i = 0; i < totalSteps; i++) {
      const dotCls = i < currentStep ? 'done' : (i === currentStep && s.state !== 'COMPLETED') ? 'active' : '';
      dots.push(`<div class="dot ${dotCls}">${i + 1}</div>`);
      if (i < totalSteps - 1) dots.push(`<div class="seg ${i < currentStep ? 'done' : ''}"></div>`);
    }

    const curStepObj = steps[currentStep];
    const tplPreview = curStepObj?.message_template
      ? `<div class="card-pad" style="background:var(--code-bg); border-radius:6px; font-family:var(--font-mono); font-size:12.5px; line-height:1.5;">${escapeHtml(curStepObj.message_template)}</div>`
      : `<div class="card-pad" style="color:var(--text-muted); font-size:13px;">No message template for this step.</div>`;

    const trace = traceData.trace || [];
    body.innerHTML = `
      <div class="meta-grid">
        <div class="meta-row"><span class="k">User</span><span class="v">@${escapeHtml(s.username)}</span></div>
        <div class="meta-row"><span class="k">State</span><span class="v"><span class="pill ${sc}"><span class="dot"></span>${ns}</span></span></div>
        <div class="meta-row"><span class="k">Platform</span><span class="v mono">${s.platform}</span></div>
        <div class="meta-row"><span class="k">Workflow</span><span class="v">${escapeHtml(workflowName(s.workflow_id))}</span></div>
        <div class="meta-row"><span class="k">Follow status</span><span class="v">${s.follow_status || '—'}</span></div>
        <div class="meta-row"><span class="k">Started</span><span class="v mono">${s.started_at ? new Date(s.started_at).toLocaleString() : '—'}</span></div>
      </div>

      <div class="section-title">Step progress · ${stepLabel(s.workflow_id, currentStep)}</div>
      <div class="progress-bar">${dots.join('')}</div>
      ${tplPreview}

      <div class="section-title">Execution trace</div>
      <div class="trace">
        ${trace.length
          ? trace.map(t => {
              const lvl = t.status === 'completed' ? 'ok' : t.status === 'failed' ? 'err' : 'warn';
              const ts = t.executed_at || t.ts;
              return `
              <div class="trace-row ${lvl}">
                <div class="ts">${ts ? fmtTime(new Date(ts).getTime()) : '—'}</div>
                <div class="body">
                  <div class="label">${escapeHtml(t.step_type || t.label || '')}</div>
                  <div class="detail">${escapeHtml(t.message_preview || t.detail || '')}</div>
                </div>
              </div>`;
            }).join('')
          : '<div class="empty" style="border:0; background:transparent;"><p>No trace events yet.</p></div>'}
      </div>
    `;
  } catch (e) {
    body.innerHTML = '<div class="empty"><h4>Failed to load session</h4></div>';
    toast('Failed to load session', 'error');
  }
}

function closeSessionModal() { document.getElementById('sessionModal').classList.remove('active'); }

/* ============================================================
   PLATFORMS
   ============================================================ */
async function loadPlatforms() {
  setLoading('platformsLoading', true);
  try {
    const r = await api.getPlatforms();
    platformCache = r.platforms;
    const grid = document.getElementById('platformsGrid');
    if (grid) {
      grid.innerHTML = r.platforms.map(p => `
        <div class="platform-card" data-platform="${p.name}">
          <div class="ribbon"></div>
          <div class="head">
            <div class="title">
              <div class="glyph">${platformGlyph(p.name)}</div>
              <div>
                <div class="name">${p.name}</div>
                <div class="sub">${p.enabled ? 'enabled · workers running' : 'disabled · workers stopped'}</div>
              </div>
            </div>
            <label class="switch">
              <input type="checkbox" ${p.enabled ? 'checked' : ''} onchange="togglePlatform('${p.name}', this.checked)">
              <span class="switch-track"></span>
            </label>
          </div>
          <div class="stats-mini">
            <div><div class="v">${p.sessions_open ?? '—'}</div><div class="l">Open</div></div>
            <div><div class="v">${p.sent_today ?? '—'}</div><div class="l">Sent today</div></div>
            <div><div class="v">${p.daily_dm_cap || p.daily_cap || '∞'}</div><div class="l">Daily cap</div></div>
          </div>
        </div>
      `).join('');
    }
    const hasFollowPlatform = r.platforms.some(p => p.enabled && p.name !== 'telegram');
    const checksBtn = document.getElementById('checksTabBtn');
    if (checksBtn) checksBtn.style.display = hasFollowPlatform ? '' : 'none';
    renderPlatformSelect();
  } catch (e) { toast('Failed to load platforms', 'error'); }
  finally { setLoading('platformsLoading', false); }
}

async function togglePlatform(name, on) {
  try {
    if (on) await api.enablePlatform(name); else await api.disablePlatform(name);
    toast(`${name} ${on ? 'enabled' : 'disabled'}`, on ? 'success' : 'info');
    if (!on && currentPlatform === name) {
      const next = platformCache.find(p => p.enabled && p.name !== name);
      if (next) currentPlatform = next.name;
    }
    await loadPlatforms();
    await loadWorkerHealth();
  } catch (e) { toast('Toggle failed', 'error'); }
}

/* ============================================================
   PENDING CHECKS
   ============================================================ */
async function loadChecks() {
  setLoading('checksLoading', true);
  try {
    const r = await api.getPendingChecks(currentPlatform);
    const countEl = document.getElementById('checkCount');
    if (countEl) countEl.textContent = r.count;
    const tbody = document.getElementById('checksBody');
    if (!tbody) return;
    if (!r.checks.length) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty" style="border:0; background:transparent;"><div class="glyph">✓</div><h4>All clear</h4><p>No pending follow checks.</p></div></td></tr>`;
    } else {
      tbody.innerHTML = r.checks.map(c => `
        <tr>
          <td class="id-cell">${shortId(c.id)}</td>
          <td class="user-cell">@${escapeHtml(c.username)}</td>
          <td class="id-cell">${c.session_id ? shortId(c.session_id) : '—'}</td>
          <td style="color:var(--text-muted); font-size:12.5px;">${c.check_after ? new Date(c.check_after).toLocaleString() : '—'}</td>
          <td class="mono" style="color:var(--text-muted); font-size:12px;">—</td>
          <td class="mono" style="font-size:12px;">${c.attempts} / ${c.max_attempts}</td>
          <td><div class="check-actions">
            <button class="btn secondary sm" onclick="forceCheckAction('${c.id}')">Force</button>
            <button class="btn danger sm" onclick="abandonCheckAction('${c.id}')">Abandon</button>
          </div></td>
        </tr>
      `).join('');
    }
  } catch (e) { toast('Failed to load pending checks', 'error'); }
  finally { setLoading('checksLoading', false); }
}

async function forceCheckAction(id) {
  try { await api.forceCheck(id); toast('Forced check', 'success'); await loadChecks(); }
  catch (e) { toast('Force failed', 'error'); }
}

async function abandonCheckAction(id) {
  try { await api.abandonCheck(id); toast('Check abandoned', 'info'); await loadChecks(); }
  catch (e) { toast('Abandon failed', 'error'); }
}

/* ============================================================
   BOT ACTIONS
   ============================================================ */
async function botAction(kind) {
  try {
    if (kind === 'pause')   { await api.pauseBot(currentPlatform);   toast('Bot paused', 'warning'); setBotStatus(false); }
    if (kind === 'resume')  { await api.resumeBot(currentPlatform);   toast('Bot resumed', 'success'); setBotStatus(true); }
    if (kind === 'restart') { toast('Restarting…', 'info'); await api.restartBot(currentPlatform); toast('Bot restarted', 'success'); setBotStatus(true); }
  } catch (e) { toast('Action failed', 'error'); }
}

function setBotStatus(running) {
  const el = document.getElementById('botStatus');
  if (!el) return;
  el.classList.toggle('paused', !running);
  const label = document.getElementById('botStatusLabel');
  if (label) label.textContent = running ? 'running' : 'paused';
}

/* ============================================================
   SOCKET.IO
   ============================================================ */
function initSocketIO() {
  try {
    socket = io();

    socket.on('connect', () => {
      addFeedItem('Socket.IO connected', 'success');
    });
    socket.on('connect_error', () => console.warn('SocketIO connect failed'));

    socket.on('trigger_matched', d => {
      addFeedItem(`<span class="who">@${escapeHtml(d.username)}</span> triggered <code>${escapeHtml(d.keyword)}</code> — ${escapeHtml(d.workflow_name)}`, 'info', `event=trigger_matched`);
      if (document.querySelector('.tab-btn.active')?.dataset.tab === 'home') loadStats();
    });
    socket.on('message_sent', d => {
      addFeedItem(`Sent message to <span class="who">@${escapeHtml(d.username)}</span> (step ${d.step_order})`, 'success');
    });
    socket.on('follow_detected', d => {
      addFeedItem(`<span class="who">@${escapeHtml(d.username)}</span> followed — advancing workflow`, 'success');
    });
    socket.on('session_completed', d => {
      addFeedItem(`<span class="who">@${escapeHtml(d.username)}</span> session completed`, 'success');
      if (document.querySelector('.tab-btn.active')?.dataset.tab === 'home') loadStats();
    });
    socket.on('session_failed', d => {
      addFeedItem(`<span class="who">@${escapeHtml(d.username)}</span> session failed: ${escapeHtml(d.reason)}`, 'error');
    });
    socket.on('daily_cap_hit', d => {
      toast(`Daily cap hit on ${d.platform} — ${d.queued_count} queued`, 'warning');
    });
    socket.on('platform_error', d => {
      workerState[d.platform] = { error: d.detail };
      toast(`${d.platform} error: ${d.detail}`, 'error');
      loadWorkerHealth();
    });
  } catch (e) {
    console.warn('SocketIO init failed:', e);
  }
}

/* ============================================================
   BOOT
   ============================================================ */
document.addEventListener('DOMContentLoaded', async () => {
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.addEventListener('click', () => setActiveTab(b.dataset.tab));
  });

  document.getElementById('themeToggle').onclick = toggleTheme;

  document.getElementById('wfSearch').addEventListener('input', e => {
    renderWorkflows(allWorkflows, e.target.value);
  });

  document.getElementById('stateFilter').addEventListener('change', () => {
    sessionPage = 0;
    loadSessions();
  });

  window.addEventListener('keydown', e => {
    if (e.key === 'Escape') { closeWorkflowModal(); closeSessionModal(); }
  });

  await loadPlatforms();
  await loadTabData('home');
  initSocketIO();
});
