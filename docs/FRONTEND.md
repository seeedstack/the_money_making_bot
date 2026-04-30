# theBot Frontend — Implementation Reference

## Stack

| Concern | Solution |
|---------|----------|
| Framework | Vanilla JS (no build step, no bundler) |
| Realtime | Socket.IO 4.7.2 (CDN) |
| Notifications | Toastify-JS (CDN) |
| Auth | Flask-Login session cookie (server-enforced) |
| Styling | Plain CSS with CSS custom properties (dark mode) |
| HTTP | `window.api` — thin fetch wrapper in `api.js` |

---

## File Map

```
frontend/
├── index.html      — Shell, CDN imports, modal HTML, tab skeleton
├── styles.css      — All CSS, including dark mode vars and component styles
├── api.js          — HTTP client: window.api global object
└── app.js          — All UI logic: state, events, render functions
```

No build pipeline. Flask serves `frontend/` as static at `/`.
`index.html` → loads `api.js` then `app.js` in order (dependency: `window.api` must exist before `app.js` runs).

---

## Auth Flow

Server enforces auth. Frontend is secondary.

1. Any request to `/api/*` without valid session → `401`
2. `api.js fetch_()` catches 401 → `window.location.href = '/auth/login'`
3. `/` route is `@login_required` → redirects to `/auth/login` if not authed
4. `/auth/logout` (POST) → clears Flask-Login session → redirects to `/auth/login`
5. `/auth/change-password` (GET/POST, login-required) → validates current pw, saves hash to `data/admin_creds.json`

**Frontend does zero auth logic.** No JWT, no token storage. Pure session cookie.

---

## HTTP Client (`api.js`)

Exposes a single global: `window.api`.

```js
window.api = {
  getWorkflows(platform)           → { workflows: [...] }
  createWorkflow(platform, data)   → { id, platform }
  updateWorkflow(platform, id, data)
  deleteWorkflow(platform, id)
  toggleWorkflow(platform, id)

  getSessions(platform, state?)    → { sessions: [...], count: N }
  getSession(id, platform)         → session object
  getSessionTrace(id, platform)    → { session_id, trace: [...] }

  getStats(platform)               → { triggers_matched, messages_sent, platform }

  getPlatforms()                   → { platforms: [...] }
  enablePlatform(name)
  disablePlatform(name)

  getPendingChecks(platform)       → { checks: [...], count: N }
  forceCheck(id)
  abandonCheck(id)

  pauseBot(platform?)
  resumeBot(platform?)
  restartBot(platform?)
}
```

**All calls pass `?platform=` — never call without it.**

Error handling in `fetch_()`:
- 401 → redirect to login (no throw)
- Any other non-ok → throws `Error` with `.status`
- Callers wrap in try/catch → call `toast(msg, 'error')`

---

## Global State (`app.js`)

```js
let currentPlatform = 'instagram'  // drives all API calls
let workflowCache = {}             // id → { name, steps[] }
let allWorkflows  = []             // full workflow objects (for search)
let editingWorkflowId = null       // null = create, N = edit
let socket = null                  // Socket.IO instance
let workerState = {}               // platform → { error? }
let allSessions = []               // current page's full dataset
let sessionPage = 0                // current page index (0-based)
const SESSION_PAGE_SIZE = 20
```

### workflowCache

Populated on every `loadWorkflows()` call.

```js
workflowCache[id] = { name: "Detox Guide", steps: [ { step_type, send_if, message_template }, ... ] }
```

Used by:
- `workflowName(id)` → display name in session rows
- `stepLabel(workflowId, stepIndex)` → `"2: send_message"` in session detail
- `showSessionDetail()` → message template preview + step progress bar

**If workflows haven't been loaded for the current platform, workflowCache is empty → session rows show `#id` instead of name.** Load order: load workflows first, then sessions, or accept the fallback.

---

## Tab System

```js
// HTML: <button class="tab-btn" data-tab="home">
// JS: click → remove .active from all tabs + contents → add .active to clicked
// → call loadTabData(tabId)
```

`loadTabData(tabId)` routes to the correct load function(s).

### Adding a New Tab

1. Add `<button class="tab-btn" data-tab="mytab">` in `index.html`
2. Add `<div id="mytab" class="tab-content">` with content skeleton
3. Add `case 'mytab': await loadMyTab(); break;` in `loadTabData()`
4. Implement `async function loadMyTab() { ... }` following the pattern:
   ```js
   async function loadMyTab() {
       setLoading('myTabLoading', true);
       try {
           const data = await api.getSomething(currentPlatform);
           document.getElementById('myBody').innerHTML = data.items.map(...).join('');
       } catch (e) {
           toast('Failed to load X', 'error');
       } finally {
           setLoading('myTabLoading', false);
       }
   }
   ```
5. Platform select change auto-calls `loadTabData` for the active tab — no extra wiring needed

---

## SocketIO

Initialised once in `initSocketIO()` on `DOMContentLoaded`.

```js
socket = io();  // connects to same origin, transport negotiated
```

### Wired Events

| Event | Action |
|-------|--------|
| `trigger_matched` | addFeedItem + loadStats() |
| `message_sent` | addFeedItem + loadStats() |
| `follow_detected` | addFeedItem |
| `session_completed` | addFeedItem + loadStats() |
| `session_failed` | addFeedItem + loadStats() |
| `daily_cap_hit` | toast warning |
| `platform_error` | workerState[platform].error = detail + toast |

All events carry a `platform` field. Feed items show platform in brackets.

### Adding a New Event

```js
socket.on('my_event', d => {
    addFeedItem(`[${d.platform}] ${d.detail}`, 'info');
    // optionally refresh data
});
```

Server emits via `api/socketio.py → emit_event(event_name, data, platform)`.

---

## Dark Mode

Implemented with CSS custom properties. **No JS class toggling on individual elements.**

```css
:root {
  --bg: #f5f5f5;        --surface: #ffffff;
  --border: #eeeeee;    --text: #333333;
  --text-muted: #6b7280; --primary: #007bff;
  --card-bg: #f9f9f9;   --input-border: #d1d5db;
  --table-hover: #fafafa;
}

body.dark {
  --bg: #111827;        --surface: #1f2937;
  --border: #374151;    --text: #f9fafb;
  --text-muted: #9ca3af; --primary: #3b82f6;
  --card-bg: #1f2937;   --input-border: #4b5563;
  --table-hover: #273344;
}
```

Toggle: `document.body.classList.toggle('dark')` + `localStorage.setItem('darkMode', '1'|'0')`.

**Rule: all new CSS must use `var(--...)` for colors, backgrounds, and borders. Never hardcode `#fff` or `#333` in component styles.**

---

## Pagination (Sessions)

```
allSessions[]  ← full dataset from API
sessionPage    ← current page index
SESSION_PAGE_SIZE = 20

loadSessions() → fills allSessions → calls renderSessionsPage()
renderSessionsPage() → slices allSessions → writes tbody + pagination bar
```

Prev/Next buttons call `renderSessionsPage()` directly (no API call).
State filter change resets `sessionPage = 0` before `loadSessions()`.

---

## Workflow Search

Client-side only. No API call on keypress.

```
allWorkflows[] ← set in loadWorkflows()
search input oninput → renderWorkflows(allWorkflows, query)
renderWorkflows() → filters by name + trigger_keyword → writes grid
```

Search is case-insensitive substring match on `name` and `trigger_keyword`.

**Gotcha:** `workflowCache` stores `{name, steps}` only. `allWorkflows` stores full objects needed for `renderWorkflows()`. Both must be populated together in `loadWorkflows()`.

---

## Session Detail Modal

Opens on `tr.clickable` row click → `showSessionDetail(id)`.

Fires two parallel requests:
```js
const [s, traceData] = await Promise.all([
    api.getSession(id, currentPlatform),
    api.getSessionTrace(id, currentPlatform).catch(() => ({ trace: [] }))
]);
```

Trace fetch failures are silenced (`.catch`) — detail still renders without trace.

Shows:
1. Session metadata (username, state, platform, workflow, follow status, timestamps)
2. Current step label + message template preview (from `workflowCache`)
3. Step progress bar (dots + lines, green=done / blue=active / gray=pending)
4. Execution trace timeline (from `session_step_history` DB table)

**Trace is empty until `StepExecutor` calls `repo.log_step()` — this is not yet wired.**

---

## Workflow Modal (Create / Edit)

`showCreateWorkflow()` → sets `editingWorkflowId = null`, resets form, adds one blank step.
`editWorkflow(id)` → fetches from `allWorkflows`, populates form, sets `editingWorkflowId = id`.

Steps are dynamic DOM nodes. Each step has:
- `select.step-type` → `onStepTypeChange()` hides/shows message textarea + send_if select
- `select.step-send-if`
- `textarea.step-message`

On save → `saveWorkflow(e)`:
1. Validates name + trigger + sourceId (toast + return if empty)
2. Collects steps from DOM
3. POST (create) or PUT (edit) via `api`
4. On success → `closeWorkflowModal()` + `loadWorkflows()`

---

## Toast Utility

```js
toast(msg, type)
// type: 'info' | 'success' | 'error' | 'warning'
```

Colors:
- info → `#2563eb` (blue)
- success → `#16a34a` (green)
- error → `#dc2626` (red)
- warning → `#d97706` (amber)

Duration: 3500ms. Top-right corner.

---

## Worker Health Pills

Platform cards show per-worker pills: `trigger`, `engine`, `recheck` (recheck hidden for Telegram).

State comes from `workerState[platform]` — populated only by `platform_error` SocketIO events.
Default (no errors received) → all pills show green (`pill-ok`).
On `platform_error` → `workerState[platform] = { error: detail }` → all pills go red (`pill-error`).

**No polling. No API call. Error state only clears on page refresh.**

---

## Pending Checks Tab Visibility

Tab `<button id="checksTabBtn">` is hidden by default (`style="display:none"`).

`loadPlatforms()` evaluates:
```js
const hasFollowPlatform = data.platforms.some(p => p.enabled && p.name !== 'telegram');
document.getElementById('checksTabBtn').style.display = hasFollowPlatform ? '' : 'none';
```

Telegram has no follow concept → never contributes to showing the tab.

---

## Gotchas

| Gotcha | Detail |
|--------|--------|
| **workflowCache empty** | Sessions loaded before workflows → names show as `#id`. Load workflows first or accept fallback. |
| **api.js must load before app.js** | `<script src="/api.js">` must precede `<script src="/app.js">` in HTML — `window.api` must exist. |
| **ES module exports removed** | `api.js` was previously `export async function ...`. It is now a plain script with `window.api = {...}`. Do not re-add `export`. |
| **getWorkflows returns wrapped** | Returns `{ workflows: [] }`, not a raw array. `getStats` returns a flat object. Be consistent when adding new endpoints. |
| **getSession needs platform** | `GET /api/sessions/:id` requires `?platform=` — backend defaults to `instagram` if missing, will silently return wrong data. |
| **Trace always empty** | `session_step_history` table exists but nothing writes to it. Wire `repo.log_step()` in `StepExecutor.execute()`. |
| **Worker state never clears** | `workerState[platform].error` persists until page reload. Add explicit clear on `session_completed` or heartbeat if needed. |
| **Dark mode new styles** | Any new CSS component must use `var(--surface)`, `var(--border)`, `var(--text)` etc. — not hardcoded hex values. |
| **Pagination resets** | Always set `sessionPage = 0` before calling `loadSessions()` on filter change, platform change, or manual refresh. |

---

## Extension Checklist

**Add a new API call:**
1. Add method to `window.api` in `api.js`
2. Return `{ key: [...] }` wrapped object (never raw array)
3. Always accept/pass `platform` param

**Add a new SocketIO event:**
1. `socket.on('event_name', handler)` in `initSocketIO()`
2. Server emits via `emit_event()` in `api/socketio.py`

**Add a new tab:**
1. Tab button + content div in `index.html`
2. `case` in `loadTabData()`
3. Load function following setLoading/try/catch/finally pattern
4. New CSS uses `var(--...)` vars only

**Add a new modal:**
1. Modal HTML in `index.html` (overlay + box structure)
2. Open/close functions in `app.js`
3. Overlay `onclick` → close function
4. Use existing `.modal`, `.modal-box`, `.modal-header`, `.modal-footer` classes
