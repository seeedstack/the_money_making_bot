# Phase 1: Instagram Adapter — Design Spec

**Date:** 2026-04-12  
**Phase:** 1  
**Platform:** Instagram (instagrapi)  
**Approach:** Shell-first skeleton

---

## Overview

Build Instagram adapter as complete skeleton. All files created. All imports wired. All classes stubbed (return safe defaults). API returns 200 OK. React UI renders blank. Workers can start (no-op). Then fill layers with real logic.

**Success:** Code compiles, imports work, tests run green, all endpoints respond, UI loads, workers start/stop without crash.

---

## Stack

| Layer | Tech |
|-------|------|
| Backend | Flask + Flask-SocketIO |
| DB | SQLite (Phase 1) → PostgreSQL-ready (SQLAlchemy Core) |
| Instagram SDK | instagrapi (modern, maintained) |
| Frontend | React (single file, bundled w/ backend) |
| Creds | DB encrypted (cryptography lib) |
| Workers | Python threads (BaseWorker pattern) |
| Tests | pytest (mocked by default, real tests optional) |
| Start | Single shell script (backend + frontend) |

---

## Architecture

**Core principle:** Platform adapter pattern. Instagram code isolated in `platforms/instagram/`. Core engine knows nothing about Instagram. Swap adapter = zero core changes.

**Flow:**
1. **Workers** poll for triggers via adapter
2. **Adapter** calls Instagram (stub → safe default)
3. **Engine** executes workflow steps
4. **API** exposes endpoints (stub → 200 OK)
5. **React UI** displays state

**Stubs return:**
- `read_triggers()` → `[]`
- `send_message()` → `True`
- `check_follow()` → `FollowStatus.NOT_FOLLOWING`
- API routes → `{status: 200}` + stub data

---

## File Structure

```
the-bot/
├── config/
│   ├── settings.py              # Load .env → typed Settings
│   ├── workflows.yaml           # Workflow definitions (stub)
│   └── workflows.schema.json    # Validation schema
├── core/
│   ├── interfaces/              # Protocols (all stubbed)
│   │   ├── platform_adapter.py
│   │   ├── message_reader.py
│   │   ├── dm_sender.py
│   │   └── follow_checker.py
│   ├── models/
│   │   ├── platform.py          # enum: INSTAGRAM
│   │   ├── workflow.py
│   │   ├── session.py
│   │   ├── trigger.py
│   │   └── events.py
│   ├── engine/
│   │   ├── step_executor.py     # Stub: returns next state
│   │   ├── step_registry.py     # Maps StepType → handler
│   │   └── steps/               # One file per step type
│   │       ├── check_follow.py
│   │       ├── send_message.py
│   │       ├── wait_for_follow.py
│   │       └── delay.py
│   ├── keyword_matcher.py       # Stub: match logic
│   └── rate_limiter.py          # Stub: rate limiting
├── platforms/
│   ├── base.py                  # BasePlatformAdapter (ABC)
│   ├── registry.py              # Maps Platform enum → adapter
│   └── instagram/
│       ├── adapter.py           # Implements PlatformAdapter
│       ├── client.py            # instagrapi factory
│       ├── comment_reader.py    # Stub: fetch comments
│       ├── dm_sender.py         # Stub: send DM
│       └── follow_checker.py    # Stub: check follow
├── workers/
│   ├── base_worker.py           # BaseWorker (ABC, thread-based)
│   ├── worker_manager.py        # Spawn/stop all workers
│   └── per_platform/
│       ├── trigger_monitor.py   # Scan for keywords
│       ├── message_engine.py    # Run workflow steps
│       └── follow_recheck.py    # Recheck follow status
├── db/
│   ├── database.py              # Connection pool, migration runner
│   ├── migrations/
│   │   └── 001_init.sql         # Core + Instagram-specific tables
│   └── repositories/
│       ├── workflow_repo.py     # Workflow queries
│       ├── session_repo.py      # Session queries
│       ├── scan_repo.py         # Trigger scan queries
│       ├── follow_check_repo.py # Follow check queries
│       └── settings_repo.py     # Creds storage (encrypted)
├── api/
│   ├── __init__.py              # create_app() factory
│   ├── socketio.py              # SocketIO instance
│   ├── middleware.py            # Auth, error handlers
│   └── routes/
│       ├── workflows.py         # GET, POST, PUT, DEL
│       ├── sessions.py          # GET, filter by state
│       ├── stats.py             # GET aggregates
│       ├── checks.py            # GET pending follow checks
│       ├── platforms.py         # GET, enable/disable
│       └── bot.py               # POST pause|resume
├── frontend/
│   ├── index.html               # React root
│   ├── app.jsx                  # All components (stub)
│   └── api.js                   # Fetch wrapper
├── tests/
│   ├── conftest.py              # pytest fixtures
│   ├── unit/
│   │   ├── test_keyword_matcher.py
│   │   └── platforms/
│   │       └── test_instagram_adapter.py
│   └── integration/
│       └── test_workflow_repo.py
├── main.py                      # Entry: create_app() + WorkerManager.start_all()
├── start.sh                     # Single script: backend + frontend
├── requirements.txt
├── requirements-dev.txt
├── .env
├── .env.example
└── CLAUDE.md
```

---

## Database Schema

**Core tables** (all have `platform` column):

| Table | Key Columns | Purpose |
|-------|-----------|---------|
| `workflows` | id, platform, name, trigger_keyword, source_id, priority, active, match_mode | Workflow definitions |
| `workflow_steps` | id, workflow_id, step_order, step_type, message_template, send_if, delay_seconds | Workflow steps |
| `trigger_scans` | id, platform, source_id, username, content, matched_workflow_id, scanned_at | Scanned triggers (history) |
| `message_sessions` | id, platform, username, workflow_id, current_step, follow_status, state, started_at, last_action_at | Workflow execution state |
| `pending_follow_checks` | id, platform, session_id, username, check_after, attempts, max_attempts | Follow recheck queue |
| `platform_settings` | platform, key, value | Per-platform config (rate caps, delays) |
| `platform_daily_counts` | platform, date, messages_sent, triggers_matched | Daily stats |

**Instagram-specific tables:**

| Table | Key Columns | Purpose |
|-------|-----------|---------|
| `instagram_accounts` | id, username, password_encrypted, salt, last_login, is_active | Account credentials (encrypted) |
| `instagram_rate_windows` | account_id, timestamp, message_count | 15-min rate window tracking |
| `instagram_session_cache` | account_id, session_hash, created_at | Session state cache |

---

## Core Interfaces (All Stubbed)

**PlatformAdapter Protocol:**
```python
class PlatformAdapter(Protocol):
    platform: Platform
    
    def read_triggers(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments/replies. Stub: return []"""
        ...
    
    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM. Stub: return True"""
        ...
    
    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        ...
    
    def supports_follow_gate(self) -> bool:
        """Can platform gate by follow? Stub: return True"""
        ...
```

All other interfaces (MessageReader, DMSender, FollowChecker) follow same pattern: one method, stub return.

---

## Instagram Adapter Structure

**adapter.py** — orchestrator:
- Constructor: loads creds from DB, init client
- `read_triggers()` → calls `comment_reader.fetch()` → returns `[]` (stub)
- `send_message()` → calls `dm_sender.send()` → returns `True` (stub)
- `check_follow()` → calls `follow_checker.is_following()` → returns `NOT_FOLLOWING` (stub)
- `supports_follow_gate()` → returns `True`

**client.py** — instagrapi wrapper:
- Constructor: take account_id, load creds from DB (encrypted), init instagrapi.Client()
- `login()` → decrypt creds, call `cl.login()`, cache session → stub returns `True`
- Helper methods for adapter to call (stub implementations)

**comment_reader.py** — fetch comments:
- `fetch(source_id: str)` → call `client.get_comments()` → parse → return list[TriggerEvent]
- Stub: return `[]`

**dm_sender.py** — send DM:
- `send(recipient_id: str, text: str)` → call `client.send_direct_message()`
- Stub: return `True`

**follow_checker.py** — check follow:
- `is_following(username: str)` → call `client.user_info()` → check follow status
- Stub: return `FollowStatus.NOT_FOLLOWING`

---

## Workers

All inherit `BaseWorker` (ABC). Each runs own thread.

**BaseWorker:**
- Attributes: `platform`, `enabled` (read from DB)
- Methods: `start()`, `stop()`, `run_cycle()` (abstract), `on_error()`
- Behavior: spawn thread, loop `run_cycle()` with backoff on error, graceful shutdown

**TriggerMonitorWorker:**
- `run_cycle()`: fetch active workflows → call `adapter.read_triggers(source_id)` for each → save matches to `trigger_scans` table
- Stub: log "scanning", sleep 5s, return

**MessageEngineWorker:**
- `run_cycle()`: fetch pending sessions from `message_sessions` (state != COMPLETED|FAILED|TIMED_OUT) → call `step_executor.execute()` for each
- Stub: log "processing", sleep 5s, return

**FollowRecheckWorker:**
- `run_cycle()`: fetch pending checks from `pending_follow_checks` where `check_after < NOW()` → call `adapter.check_follow()` for each → update session state
- Stub: log "rechecking", sleep 5s, return

**WorkerManager:**
- `start_all()`: spawn 3 workers per enabled platform
- `stop_all()`: graceful shutdown all workers

---

## API Endpoints (Core Set)

All return 200 OK. Stub responses unless noted.

| Endpoint | Method | Stub Response | Real Logic (Phase 2+) |
|----------|--------|---------------|----------------------|
| `/api/workflows?platform=instagram` | GET | `[]` | Fetch from DB |
| `/api/workflows` | POST | `{id: 1}` | Insert workflow |
| `/api/workflows/:id` | PUT | `{id: 1, updated: true}` | Update workflow |
| `/api/workflows/:id` | DELETE | `{deleted: true}` | Soft-delete |
| `/api/sessions?platform=instagram` | GET | `[]` | Fetch sessions |
| `/api/sessions/:id` | GET | `{id: 1, state: "RUNNING"}` | Fetch one session |
| `/api/stats?platform=instagram` | GET | `{triggers: 0, messages: 0}` | Query daily counts |
| `/api/pending-checks?platform=instagram` | GET | `[]` | Fetch pending checks |
| `/api/bot/pause?platform=instagram` | POST | `{status: "paused"}` | Set worker enabled=False |
| `/api/bot/resume?platform=instagram` | POST | `{status: "running"}` | Set worker enabled=True |
| `/api/platforms` | GET | `[{name: "instagram", enabled: true}]` | List all platforms |

**SocketIO events** (stubbed, no emit until real logic):
- `trigger_matched`
- `message_sent`
- `follow_detected`
- `session_completed`
- `platform_error`

---

## React UI

**Single file: `frontend/app.jsx`**

Components (all in one file):
- `<App>` — main container, platform switcher, tab router
- `<HomeTab>` — stat cards, platform pills (RUNNING|PAUSED|ERROR)
- `<WorkflowsTab>` — workflow list, stub form (disabled)
- `<SessionsTab>` — session list, state filter
- `<PlatformsTab>` — platform status, enable/disable buttons

**api.js** (fetch wrapper):
```javascript
export async function getWorkflows(platform) { return []; }
export async function getSessions(platform, state) { return []; }
export async function getStats(platform) { return {triggers: 0, messages: 0}; }
export async function getPlatforms() { return [{name: "instagram", enabled: true}]; }
```

**Stub behavior:**
- Renders without data fetches
- Buttons clickable but no-op (will wire to API in Phase 2)
- Shows "Loading..." placeholders

---

## Start Script

**`start.sh`** — single command, starts backend + frontend:

```bash
#!/bin/bash
set -e

# Backend (Flask)
export FLASK_ENV=development
export FLASK_APP=main.py
python -m flask run --port 5000 &
FLASK_PID=$!

# Frontend: bundled with backend (serve from Flask static/)
# (No separate npm dev server in Phase 1)

echo "Backend running on localhost:5000"
echo "Frontend on localhost:5000 (served by Flask)"
echo "Press Ctrl+C to stop"

wait $FLASK_PID
```

**Usage:** `./start.sh`

---

## Testing Strategy

**Unit tests** (mocked):
- Mock all adapters (comment_reader, dm_sender, follow_checker)
- Test repos in isolation
- Test step executor with stub adapters
- Fast, safe, zero Instagram calls
- Command: `pytest tests/unit -v`

**Integration tests** (real DB, fake adapters):
- Use temp SQLite DB
- Real repos, real migrations
- Fake adapters (return stubs)
- Test workflows end-to-end (without Instagram calls)
- Command: `pytest tests/integration -v`

**End-to-end tests** (optional, real Instagram):
- Only run if `INSTA_TEST_ACCOUNT=true` env set
- Use dummy Instagram account
- Test real comment scraping, DM sending, follow checking
- Skipped by default (CI doesn't run these)
- Command: `INSTA_TEST_ACCOUNT=true pytest tests/e2e -v`

**Example test:**
```python
def test_instagram_adapter_stub_returns_empty_list():
    adapter = InstagramAdapter(account_id=999)
    result = adapter.read_triggers("post_123")
    assert result == []
```

---

## Env Vars

**.env (phase 1 stub):**
```
FLASK_SECRET=dev_secret_key_change_in_prod
BOT_TIMEZONE=Asia/Kolkata
SCAN_INTERVAL_SECONDS=5
RECHECK_INTERVAL_SECONDS=10
MAX_RECHECK_ATTEMPTS=10

INSTAGRAM_ENABLED=true
INSTAGRAM_DAILY_DM_CAP=50
INSTAGRAM_DM_DELAY_MIN=1
INSTAGRAM_DM_DELAY_MAX=3

DATABASE_URL=sqlite:///data/the-bot.db
```

(Instagram username/password NOT in env — stored encrypted in DB)

---

## Success Criteria (Shell Phase)

- ✅ Code compiles (`python -m py_compile` all files)
- ✅ All imports work (`python -c "from config import settings; from platforms import instagram; from core import engine"`)
- ✅ Tests run green (`pytest tests/ -v` — all pass)
- ✅ All API routes respond with 200 OK (`curl http://localhost:5000/api/workflows?platform=instagram`)
- ✅ React UI loads (`http://localhost:5000` shows "The Bot" title + platform pills)
- ✅ Workers start/stop without crash (`main.py` runs, workers spawn, no exceptions)
- ✅ DB migration runs (`001_init.sql` creates all tables)

---

## Next Phase

Once shell is complete and green:
1. Fill `instagram/` adapter with real instagrapi calls
2. Fill workers with real logic
3. Fill API routes with DB queries
4. Wire React UI to API endpoints
5. Add real tests (not just stubs)

Each fill = new planning cycle.

---

## Notes

- **Encrypted credentials:** Use `cryptography.fernet` to encrypt/decrypt passwords in DB. Key from `.env`.
- **Platform isolation:** Instagram code never imported outside `platforms/instagram/`. Core engine remains platform-agnostic.
- **Thread safety:** Use `threading.Lock` for shared DB access. SQLAlchemy handles connection pooling.
- **Error handling:** Phase 1 = stubs return safe defaults. Phase 2+ = real error handling.
- **Logging:** All modules log to `logs/<platform>/<worker>.log`. Use stdlib `logging`.
