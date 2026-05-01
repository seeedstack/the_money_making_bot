# theBot UI Rebuild TODO

## AUTH ✅
- [x] Login page
- [x] Session store (Flask-Login)
- [x] Auth middleware on /api/*
- [x] SocketIO auth
- [x] Dashboard guard → login redirect
- [x] Logout button
- [x] Change password — /auth/change-password, persists to data/admin_creds.json

## BLOCKERS ✅
- [x] Workflow create/edit modal (no more alert())
- [x] SocketIO listeners wired (7 events)
- [x] Loading states on all tabs
- [x] Error boundaries → toast everywhere
- [x] api.js ES module bug fixed
- [x] api.js return value bugs fixed

## CRITICAL ✅
- [x] Toast notifications (Toastify)
- [x] Platform filter on sessions tab
- [x] Session detail modal (click row)
- [x] Workflow steps visible (details expand)
- [x] Real-time stat updates via SocketIO

## IMPORTANT ✅
- [x] State color badges
- [x] Workflow names in tables
- [x] Modal form validation
- [x] Pending checks tab visibility
- [x] Session step label (N: step_type + message preview)

## NICE-TO-HAVE ✅
- [x] Workflow search/filter
- [x] Pagination (sessions, 20/page)
- [x] Execution trace timeline (DB + API + UI)
- [x] Dark mode (CSS vars + localStorage)
- [x] Worker health pills on platform cards

---

## What's Left

### Engine wiring (not started)
- [ ] StepExecutor.execute() — currently stub, needs real step dispatch
- [ ] Call repo.log_step() in engine after each step (trace table ready)
- [ ] Workers (TriggerMonitorWorker, MessageEngineWorker, FollowRecheckWorker) — stubs only
- [ ] Platform adapters (Instagram/Twitter/Telegram) — not connected

### Platform adapters
- [ ] Instagram adapter — InstaPy/Selenium wiring
- [ ] Twitter adapter — Tweepy v2 wiring
- [ ] Telegram adapter — python-telegram-bot wiring

### Config / YAML sync
- [ ] YAML loader + schema validation
- [ ] watchdog hot-reload
- [ ] YAML ↔ DB sync on startup

### Tests
- [ ] Unit tests for keyword matcher, step executor, rate limiter
- [ ] Platform adapter unit tests (mock adapters)
- [ ] Integration tests for workflow repo, message engine
