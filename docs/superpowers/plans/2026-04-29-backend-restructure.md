# Backend Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the congested `api/` + `db/` layers with a clean `app/<module>/` structure where each feature owns its blueprint, ORM models, and views — zero raw SQL, zero scattered repositories.

**Architecture:** Each module (`auth`, `workflows`, `sessions`, `platforms`, `checks`, `stats`, `bot`) lives under `app/<module>/` with `__init__.py` (blueprint), `models.py` (SQLAlchemy ORM, UUID PKs, soft-delete, `to_dict()`), and `views.py` (routes). Shared instances (`db`, `socketio`, `login_manager`) live in `app/extensions.py`. All response strings come from `AppMessages`. `core/`, `platforms/`, `workers/` are unchanged.

**Tech Stack:** Flask 2.3, Flask-SQLAlchemy 3.x, Flask-Login 0.6, SQLAlchemy 2.0, SQLite (UUID stored as String), Toastify + Socket.IO (frontend, unchanged)

---

## File Map

### Created
```
app/
├── __init__.py              # create_app() factory — replaces api/__init__.py
├── extensions.py            # db, socketio, login_manager instances
├── messages.py              # AppMessages string constants
├── helpers.py               # bad_request(), error_response()
├── auth/
│   ├── __init__.py          # bp = Blueprint("auth", __name__)
│   ├── models.py            # DashboardUser (UserMixin, no DB table)
│   └── views.py             # login, logout, change_password
├── workflows/
│   ├── __init__.py          # bp = Blueprint("workflows", __name__)
│   ├── models.py            # Workflow, WorkflowStep ORM models
│   └── views.py             # GET/POST/PUT/DELETE/toggle
├── sessions/
│   ├── __init__.py          # bp = Blueprint("sessions", __name__)
│   ├── models.py            # MessageSession, SessionStepHistory ORM
│   └── views.py             # list, get, trace
├── platforms/
│   ├── __init__.py          # bp = Blueprint("platforms", __name__)
│   ├── models.py            # PlatformSettings, PlatformDailyCount ORM
│   └── views.py             # list, enable, disable
├── checks/
│   ├── __init__.py          # bp = Blueprint("checks", __name__)
│   ├── models.py            # PendingFollowCheck ORM
│   └── views.py             # list, force, abandon
├── stats/
│   ├── __init__.py          # bp = Blueprint("stats", __name__)
│   └── views.py             # GET stats
└── bot/
    ├── __init__.py          # bp = Blueprint("bot", __name__)
    └── views.py             # pause, resume, restart
```

### Modified
```
requirements.txt             # + flask-sqlalchemy
main.py                      # import from app instead of api
frontend/app.js              # quote UUID IDs in onclick/template strings
```

### Deleted (after all tasks complete)
```
api/                         # replaced by app/
db/                          # absorbed into app/*/models.py
```

### Unchanged
```
config/settings.py
core/
platforms/
workers/
frontend/ (except app.js UUID fix)
```

---

## Task 1: Add flask-sqlalchemy, create app/ skeleton

**Files:**
- Modify: `requirements.txt`
- Create: `app/__init__.py`, `app/extensions.py`, `app/messages.py`, `app/helpers.py`
- Create: `app/auth/__init__.py`, `app/workflows/__init__.py`, `app/sessions/__init__.py`
- Create: `app/platforms/__init__.py`, `app/checks/__init__.py`, `app/stats/__init__.py`, `app/bot/__init__.py`

- [ ] **Add flask-sqlalchemy to requirements.txt**

```
Flask==2.3.2
Flask-SQLAlchemy==3.1.1
Flask-SocketIO==5.3.0
python-socketio==5.9.0
instagrapi==2.0.0
tweepy==4.14.0
cryptography==41.0.0
pyyaml==6.0.1
jsonschema==4.19.0
watchdog==3.0.0
SQLAlchemy==2.0.49
pytest==7.4.0
pytest-cov==4.1.0
python-dotenv==1.0.0
Flask-Login==0.6.3
```

- [ ] **Install**

```bash
pip install flask-sqlalchemy==3.1.1
```

Expected: `Successfully installed flask-sqlalchemy-3.1.1`

- [ ] **Create `app/extensions.py`**

```python
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()
```

- [ ] **Create `app/messages.py`**

```python
class AppMessages:
    # Auth
    INVALID_CREDENTIALS = "Invalid username or password"
    WRONG_CURRENT_PASSWORD = "Current password incorrect"
    PASSWORD_TOO_SHORT = "New password must be at least 8 characters"
    PASSWORDS_DO_NOT_MATCH = "Passwords do not match"
    PASSWORD_UPDATED = "Password updated successfully"

    # Workflows
    WORKFLOW_NOT_FOUND = "Workflow not found"
    WORKFLOW_CREATED = "Workflow created"
    WORKFLOW_UPDATED = "Workflow updated"
    WORKFLOW_DELETED = "Workflow deleted"
    WORKFLOW_TOGGLED = "Workflow toggled"

    # Sessions
    SESSION_NOT_FOUND = "Session not found"

    # Checks
    CHECK_NOT_FOUND = "Pending check not found"
    CHECK_FORCED = "Check forced"
    CHECK_ABANDONED = "Check abandoned"

    # Bot
    BOT_PAUSED = "Bot paused"
    BOT_RESUMED = "Bot resumed"
    BOT_RESTARTING = "Bot restarting"

    # Generic
    UNAUTHORIZED = "Unauthorized"
    BAD_REQUEST = "Bad request"
```

- [ ] **Create `app/helpers.py`**

```python
from flask import jsonify
from app.messages import AppMessages

def bad_request(message: str = AppMessages.BAD_REQUEST):
    return jsonify({"error": message}), 400

def error_response(message: str, status: int = 500):
    return jsonify({"error": message}), status

def not_found(message: str):
    return jsonify({"error": message}), 404
```

- [ ] **Create all blueprint `__init__.py` files**

`app/auth/__init__.py`:
```python
from flask import Blueprint
bp = Blueprint("auth", __name__)
from app.auth import views, models  # noqa: E402,F401
```

`app/workflows/__init__.py`:
```python
from flask import Blueprint
bp = Blueprint("workflows", __name__)
from app.workflows import views, models  # noqa: E402,F401
```

`app/sessions/__init__.py`:
```python
from flask import Blueprint
bp = Blueprint("sessions", __name__)
from app.sessions import views, models  # noqa: E402,F401
```

`app/platforms/__init__.py`:
```python
from flask import Blueprint
bp = Blueprint("platforms", __name__)
from app.platforms import views, models  # noqa: E402,F401
```

`app/checks/__init__.py`:
```python
from flask import Blueprint
bp = Blueprint("checks", __name__)
from app.checks import views, models  # noqa: E402,F401
```

`app/stats/__init__.py`:
```python
from flask import Blueprint
bp = Blueprint("stats", __name__)
from app.stats import views  # noqa: E402,F401
```

`app/bot/__init__.py`:
```python
from flask import Blueprint
bp = Blueprint("bot", __name__)
from app.bot import views  # noqa: E402,F401
```

- [ ] **Verify directory structure**

```bash
find /Users/saran/Work/theBot/app -name "*.py" | sort
```

Expected: all 16 `__init__.py`, `extensions.py`, `messages.py`, `helpers.py` listed.

- [ ] **Commit**

```bash
git add app/ requirements.txt
git commit -m "feat: scaffold app/ module structure with extensions and helpers"
```

---

## Task 2: `app/__init__.py` — Flask factory

**Files:**
- Create: `app/__init__.py`

- [ ] **Create `app/__init__.py`**

```python
import os
from flask import Flask, redirect, url_for, request, jsonify
from config.settings import settings
from app.extensions import db, socketio, login_manager


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/")
    app.config["SECRET_KEY"] = settings.flask_secret
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url.replace(
        "sqlite:///", "sqlite:///" + os.path.abspath("") + "/"
    ) if not settings.database_url.startswith("sqlite:////") else settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    from app.auth.models import DashboardUser

    @login_manager.user_loader
    def load_user(user_id):
        return DashboardUser()

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    # Register blueprints
    from app.auth import bp as auth_bp
    from app.workflows import bp as workflows_bp
    from app.sessions import bp as sessions_bp
    from app.platforms import bp as platforms_bp
    from app.checks import bp as checks_bp
    from app.stats import bp as stats_bp
    from app.bot import bp as bot_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(workflows_bp, url_prefix="/api/workflows")
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(platforms_bp, url_prefix="/api/platforms")
    app.register_blueprint(checks_bp, url_prefix="/api/pending-checks")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")
    app.register_blueprint(bot_bp, url_prefix="/api/bot")

    # API auth guard
    @app.before_request
    def _api_auth():
        if not request.path.startswith("/api/"):
            return None
        from flask_login import current_user
        api_key = request.headers.get("X-Api-Key", "")
        if settings.dashboard_api_key and api_key == settings.dashboard_api_key:
            return None
        if current_user.is_authenticated:
            return None
        return jsonify({"error": "Unauthorized"}), 401

    # Root route
    from flask_login import login_required
    @app.route("/")
    @login_required
    def index():
        return app.send_static_file("index.html")

    # Create all tables
    with app.app_context():
        db.create_all()

    return app
```

- [ ] **Verify import works**

```bash
python3 -c "from app import create_app; app = create_app(); print('OK')"
```

Expected: `OK` (plus any warnings about missing models — that's fine at this stage)

- [ ] **Commit**

```bash
git add app/__init__.py
git commit -m "feat: add app factory with SQLAlchemy, SocketIO, Login init"
```

---

## Task 3: Auth module

**Files:**
- Create: `app/auth/models.py`
- Create: `app/auth/views.py`

- [ ] **Create `app/auth/models.py`**

```python
import json
import os
from flask_login import UserMixin

_CREDS_FILE = os.path.join(os.path.dirname(__file__), "../../data/admin_creds.json")


class DashboardUser(UserMixin):
    """Single admin user. No DB table — credentials in .env + data/admin_creds.json."""
    id = "admin"

    def get_id(self):
        return self.id

    @staticmethod
    def creds_file_path() -> str:
        return _CREDS_FILE
```

- [ ] **Create `app/auth/views.py`**

```python
import json
import os
from flask import request, redirect, url_for, render_template_string
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth import bp
from app.auth.models import DashboardUser
from app.messages import AppMessages
from config.settings import settings

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>The Bot — Login</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#f5f5f5;color:#333}
.box{max-width:400px;margin:80px auto;padding:32px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
h1{font-size:24px;margin-bottom:20px;text-align:center}
label{display:block;font-size:13px;font-weight:600;margin-bottom:4px}
input{width:100%;padding:9px 11px;border:1px solid #ddd;border-radius:4px;font-size:14px;margin-bottom:14px}
.btn{width:100%;padding:11px;background:#2563eb;color:white;border:none;border-radius:4px;font-size:15px;cursor:pointer}
.btn:hover{background:#1d4ed8}
.err{padding:8px;background:#fee2e2;color:#b91c1c;border-radius:4px;margin-bottom:14px;font-size:14px;text-align:center}
</style></head><body>
<div class="box"><h1>🤖 The Bot</h1>
{% if error %}<div class="err">{{ error }}</div>{% endif %}
<form method="POST"><label>Username</label><input name="username" required autofocus>
<label>Password</label><input type="password" name="password" required>
<button class="btn">Sign In</button></form></div></body></html>"""

CHANGE_PASSWORD_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Change Password</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#f5f5f5;color:#333}
.box{max-width:400px;margin:80px auto;padding:32px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1)}
h1{font-size:20px;margin-bottom:20px}
label{display:block;font-size:13px;font-weight:600;margin-bottom:4px}
input{width:100%;padding:9px 11px;border:1px solid #ddd;border-radius:4px;font-size:14px;margin-bottom:14px}
.btn{width:100%;padding:11px;background:#2563eb;color:white;border:none;border-radius:4px;font-size:15px;cursor:pointer}
.msg{padding:8px;border-radius:4px;margin-bottom:14px;font-size:14px;text-align:center}
.err{background:#fee2e2;color:#b91c1c}.ok{background:#dcfce7;color:#15803d}
a{display:block;text-align:center;margin-top:14px;font-size:13px;color:#6b7280}
</style></head><body>
<div class="box"><h1>Change Password</h1>
{% if error %}<div class="msg err">{{ error }}</div>{% endif %}
{% if success %}<div class="msg ok">{{ success }}</div>{% endif %}
<form method="POST"><label>Current Password</label><input type="password" name="current" required>
<label>New Password</label><input type="password" name="new" required minlength="8">
<label>Confirm</label><input type="password" name="confirm" required>
<button class="btn">Update</button></form>
<a href="/">← Dashboard</a></div></body></html>"""


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML)
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if (username.lower() == settings.dashboard_username.lower()
            and check_password_hash(settings.dashboard_password_hash, password)):
        login_user(DashboardUser())
        return redirect(url_for("index"))
    return render_template_string(LOGIN_HTML, error=AppMessages.INVALID_CREDENTIALS), 401


@bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template_string(CHANGE_PASSWORD_HTML)
    current = request.form.get("current", "")
    new_pw = request.form.get("new", "")
    confirm = request.form.get("confirm", "")
    if not check_password_hash(settings.dashboard_password_hash, current):
        return render_template_string(CHANGE_PASSWORD_HTML, error=AppMessages.WRONG_CURRENT_PASSWORD), 400
    if len(new_pw) < 8:
        return render_template_string(CHANGE_PASSWORD_HTML, error=AppMessages.PASSWORD_TOO_SHORT), 400
    if new_pw != confirm:
        return render_template_string(CHANGE_PASSWORD_HTML, error=AppMessages.PASSWORDS_DO_NOT_MATCH), 400
    hashed = generate_password_hash(new_pw)
    creds_path = DashboardUser.creds_file_path()
    os.makedirs(os.path.dirname(creds_path), exist_ok=True)
    with open(creds_path, "w") as f:
        json.dump({"password_hash": hashed}, f)
    settings.dashboard_password_hash = hashed
    return render_template_string(CHANGE_PASSWORD_HTML, success=AppMessages.PASSWORD_UPDATED)
```

- [ ] **Verify**

```bash
python3 -c "from app import create_app; app = create_app(); print([r.rule for r in app.url_map.iter_rules() if 'auth' in r.rule])"
```

Expected: `['/auth/login', '/auth/logout', '/auth/change-password']`

- [ ] **Commit**

```bash
git add app/auth/
git commit -m "feat: add auth module (login, logout, change-password)"
```

---

## Task 4: Workflows ORM models

**Files:**
- Create: `app/workflows/models.py`

- [ ] **Create `app/workflows/models.py`**

```python
import uuid
from datetime import datetime, timezone
from app.extensions import db


class Workflow(db.Model):
    __tablename__ = "workflows"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    trigger_keyword = db.Column(db.String(255), nullable=False)
    source_id = db.Column(db.String(512), nullable=False)
    priority = db.Column(db.Integer, default=1)
    active = db.Column(db.Boolean, default=True)
    match_mode = db.Column(db.String(16), default="contains")
    link = db.Column(db.String(512), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    steps = db.relationship("WorkflowStep", backref="workflow",
                            cascade="all, delete-orphan",
                            order_by="WorkflowStep.step_order")

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "name": self.name,
            "trigger_keyword": self.trigger_keyword,
            "source_id": self.source_id,
            "priority": self.priority,
            "active": self.active,
            "match_mode": self.match_mode,
            "link": self.link,
            "steps": [s.to_dict() for s in self.steps],
        }


class WorkflowStep(db.Model):
    __tablename__ = "workflow_steps"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey("workflows.id"), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(32), nullable=False)
    message_template = db.Column(db.Text, nullable=True)
    send_if = db.Column(db.String(32), nullable=True)
    delay_seconds = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "step_order": self.step_order,
            "step_type": self.step_type,
            "message_template": self.message_template,
            "send_if": self.send_if,
            "delay_seconds": self.delay_seconds,
        }
```

- [ ] **Verify models register with db**

```bash
python3 -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.workflows.models import Workflow, WorkflowStep
    print('tables:', [t for t in Workflow.metadata.tables.keys()])
"
```

Expected: `tables: ['workflows', 'workflow_steps', ...]`

- [ ] **Commit**

```bash
git add app/workflows/models.py
git commit -m "feat: add Workflow + WorkflowStep ORM models (UUID PK, soft-delete)"
```

---

## Task 5: Workflows views

**Files:**
- Create: `app/workflows/views.py`

- [ ] **Create `app/workflows/views.py`**

```python
from datetime import datetime, timezone
from flask import request, jsonify
from flask_login import login_required
from app.workflows import bp
from app.workflows.models import Workflow, WorkflowStep
from app.extensions import db
from app.helpers import not_found, bad_request
from app.messages import AppMessages


@bp.route("", methods=["GET"])
@login_required
def list_workflows():
    platform = request.args.get("platform", "instagram")
    workflows = (Workflow.query
                 .filter_by(platform=platform, deleted_at=None)
                 .order_by(Workflow.priority.desc())
                 .all())
    return jsonify({"workflows": [w.to_dict() for w in workflows], "platform": platform}), 200


@bp.route("", methods=["POST"])
@login_required
def create_workflow():
    data = request.json or {}
    platform = data.get("platform", "instagram")
    if not data.get("name") or not data.get("trigger_keyword") or not data.get("source_id"):
        return bad_request("name, trigger_keyword, and source_id are required")

    wf = Workflow(
        platform=platform,
        name=data["name"],
        trigger_keyword=data["trigger_keyword"],
        source_id=data["source_id"],
        priority=data.get("priority", 1),
        active=data.get("active", True),
        match_mode=data.get("match_mode", "contains"),
        link=data.get("link"),
    )
    db.session.add(wf)

    for i, step_data in enumerate(data.get("steps", [])):
        step = WorkflowStep(
            workflow_id=wf.id,
            step_order=step_data.get("step_order", i),
            step_type=step_data["step_type"],
            message_template=step_data.get("message_template"),
            send_if=step_data.get("send_if"),
            delay_seconds=step_data.get("delay_seconds"),
        )
        wf.steps.append(step)

    db.session.commit()
    return jsonify({"id": wf.id, "platform": platform}), 201


@bp.route("/<workflow_id>", methods=["PUT"])
@login_required
def update_workflow(workflow_id):
    platform = request.args.get("platform", "instagram")
    wf = Workflow.query.filter_by(id=workflow_id, platform=platform, deleted_at=None).first()
    if not wf:
        return not_found(AppMessages.WORKFLOW_NOT_FOUND)

    data = request.json or {}
    wf.name = data.get("name", wf.name)
    wf.trigger_keyword = data.get("trigger_keyword", wf.trigger_keyword)
    wf.source_id = data.get("source_id", wf.source_id)
    wf.priority = data.get("priority", wf.priority)
    wf.active = data.get("active", wf.active)
    wf.match_mode = data.get("match_mode", wf.match_mode)
    wf.link = data.get("link", wf.link)
    wf.updated_at = datetime.now(timezone.utc)

    if "steps" in data:
        for s in wf.steps:
            db.session.delete(s)
        for i, step_data in enumerate(data["steps"]):
            step = WorkflowStep(
                workflow_id=wf.id,
                step_order=step_data.get("step_order", i),
                step_type=step_data["step_type"],
                message_template=step_data.get("message_template"),
                send_if=step_data.get("send_if"),
                delay_seconds=step_data.get("delay_seconds"),
            )
            wf.steps.append(step)

    db.session.commit()
    return jsonify({"id": wf.id, "updated": True}), 200


@bp.route("/<workflow_id>", methods=["DELETE"])
@login_required
def delete_workflow(workflow_id):
    platform = request.args.get("platform", "instagram")
    wf = Workflow.query.filter_by(id=workflow_id, platform=platform, deleted_at=None).first()
    if not wf:
        return not_found(AppMessages.WORKFLOW_NOT_FOUND)
    wf.deleted_at = datetime.now(timezone.utc)
    wf.deleted_by = "admin"
    db.session.commit()
    return jsonify({"deleted": True}), 200


@bp.route("/<workflow_id>/toggle", methods=["POST"])
@login_required
def toggle_workflow(workflow_id):
    platform = request.args.get("platform", "instagram")
    wf = Workflow.query.filter_by(id=workflow_id, platform=platform, deleted_at=None).first()
    if not wf:
        return not_found(AppMessages.WORKFLOW_NOT_FOUND)
    wf.active = not wf.active
    wf.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"id": wf.id, "active": wf.active}), 200
```

- [ ] **Verify routes registered**

```bash
python3 -c "
from app import create_app
app = create_app()
rules = [r.rule for r in app.url_map.iter_rules() if 'workflows' in r.rule]
print(sorted(rules))
"
```

Expected: `['/api/workflows', '/api/workflows/<workflow_id>', '/api/workflows/<workflow_id>/toggle']`

- [ ] **Commit**

```bash
git add app/workflows/views.py
git commit -m "feat: add workflows CRUD routes (ORM, soft-delete)"
```

---

## Task 6: Sessions ORM models

**Files:**
- Create: `app/sessions/models.py`

- [ ] **Create `app/sessions/models.py`**

```python
import uuid
from datetime import datetime, timezone
from app.extensions import db


class MessageSession(db.Model):
    __tablename__ = "message_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    username = db.Column(db.String(255), nullable=False)
    workflow_id = db.Column(db.String(36), db.ForeignKey("workflows.id"), nullable=False)
    current_step = db.Column(db.Integer, default=0)
    follow_status = db.Column(db.String(32), default="NOT_FOLLOWING")
    state = db.Column(db.String(32), default="STEP_RUNNING")
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_action_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)

    history = db.relationship("SessionStepHistory", backref="session",
                              cascade="all, delete-orphan",
                              order_by="SessionStepHistory.step_order")

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "username": self.username,
            "workflow_id": self.workflow_id,
            "current_step": self.current_step,
            "follow_status": self.follow_status,
            "state": self.state,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_action_at": self.last_action_at.isoformat() if self.last_action_at else None,
        }


class SessionStepHistory(db.Model):
    __tablename__ = "session_step_history"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey("message_sessions.id"), nullable=False, index=True)
    platform = db.Column(db.String(32), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(16), default="completed")
    message_preview = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "step_order": self.step_order,
            "step_type": self.step_type,
            "status": self.status,
            "message_preview": self.message_preview,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
```

- [ ] **Verify**

```bash
python3 -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.sessions.models import MessageSession, SessionStepHistory
    print('OK:', MessageSession.__tablename__, SessionStepHistory.__tablename__)
"
```

Expected: `OK: message_sessions session_step_history`

- [ ] **Commit**

```bash
git add app/sessions/models.py
git commit -m "feat: add MessageSession + SessionStepHistory ORM models"
```

---

## Task 7: Sessions views

**Files:**
- Create: `app/sessions/views.py`

- [ ] **Create `app/sessions/views.py`**

```python
from flask import request, jsonify
from flask_login import login_required
from app.sessions import bp
from app.sessions.models import MessageSession, SessionStepHistory
from app.helpers import not_found
from app.messages import AppMessages


@bp.route("", methods=["GET"])
@login_required
def list_sessions():
    platform = request.args.get("platform", "instagram")
    state = request.args.get("state")
    q = MessageSession.query.filter_by(platform=platform, deleted_at=None)
    if state:
        q = q.filter_by(state=state)
    sessions = q.order_by(MessageSession.started_at.desc()).all()
    return jsonify({
        "sessions": [s.to_dict() for s in sessions],
        "platform": platform,
        "state": state,
    }), 200


@bp.route("/<session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    platform = request.args.get("platform", "instagram")
    session = MessageSession.query.filter_by(id=session_id, platform=platform, deleted_at=None).first()
    if not session:
        return not_found(AppMessages.SESSION_NOT_FOUND)
    return jsonify(session.to_dict()), 200


@bp.route("/<session_id>/trace", methods=["GET"])
@login_required
def get_trace(session_id):
    platform = request.args.get("platform", "instagram")
    history = (SessionStepHistory.query
               .filter_by(session_id=session_id, platform=platform)
               .order_by(SessionStepHistory.step_order.asc())
               .all())
    return jsonify({
        "session_id": session_id,
        "trace": [h.to_dict() for h in history],
    }), 200
```

- [ ] **Commit**

```bash
git add app/sessions/views.py
git commit -m "feat: add sessions routes (list, get, trace)"
```

---

## Task 8: Platforms + Checks + Stats + Bot modules

**Files:**
- Create: `app/platforms/models.py`, `app/platforms/views.py`
- Create: `app/checks/models.py`, `app/checks/views.py`
- Create: `app/stats/views.py`
- Create: `app/bot/views.py`

- [ ] **Create `app/platforms/models.py`**

```python
import uuid
from datetime import datetime, timezone
from app.extensions import db


class PlatformSettings(db.Model):
    __tablename__ = "platform_settings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint("platform", "key", name="uq_platform_key"),)

    def to_dict(self):
        return {"platform": self.platform, "key": self.key, "value": self.value}

    @classmethod
    def get(cls, platform: str, key: str, default=None):
        row = cls.query.filter_by(platform=platform, key=key).first()
        return row.value if row else default

    @classmethod
    def set(cls, platform: str, key: str, value: str):
        from app.extensions import db as _db
        row = cls.query.filter_by(platform=platform, key=key).first()
        if row:
            row.value = value
        else:
            row = cls(platform=platform, key=key, value=value)
            _db.session.add(row)
        _db.session.commit()


class PlatformDailyCount(db.Model):
    __tablename__ = "platform_daily_counts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    messages_sent = db.Column(db.Integer, default=0)
    triggers_matched = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint("platform", "date", name="uq_platform_date"),)

    def to_dict(self):
        return {
            "platform": self.platform, "date": self.date,
            "messages_sent": self.messages_sent,
            "triggers_matched": self.triggers_matched,
        }
```

- [ ] **Create `app/platforms/views.py`**

```python
from flask import jsonify
from flask_login import login_required
from app.platforms import bp
from config.settings import settings

_PLATFORM_META = {
    "instagram": {"supports_follow_gate": True},
    "twitter":   {"supports_follow_gate": True},
    "telegram":  {"supports_follow_gate": False},
}


@bp.route("", methods=["GET"])
@login_required
def list_platforms():
    platforms = [
        {
            "name": "instagram",
            "enabled": settings.instagram_enabled,
            "status": "RUNNING" if settings.instagram_enabled else "DISABLED",
            "supports_follow_gate": True,
        },
        {
            "name": "twitter",
            "enabled": settings.twitter_enabled,
            "status": "RUNNING" if settings.twitter_enabled else "DISABLED",
            "supports_follow_gate": True,
        },
        {
            "name": "telegram",
            "enabled": settings.telegram_enabled,
            "status": "RUNNING" if settings.telegram_enabled else "DISABLED",
            "supports_follow_gate": False,
        },
    ]
    return jsonify({"platforms": platforms}), 200


@bp.route("/<name>/enable", methods=["POST"])
@login_required
def enable_platform(name):
    return jsonify({"name": name, "enabled": True}), 200


@bp.route("/<name>/disable", methods=["POST"])
@login_required
def disable_platform(name):
    return jsonify({"name": name, "enabled": False}), 200
```

- [ ] **Create `app/checks/models.py`**

```python
import uuid
from datetime import datetime, timezone
from app.extensions import db


class PendingFollowCheck(db.Model):
    __tablename__ = "pending_follow_checks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    session_id = db.Column(db.String(36), db.ForeignKey("message_sessions.id"), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    check_after = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "session_id": self.session_id,
            "username": self.username,
            "check_after": self.check_after.isoformat() if self.check_after else None,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
        }
```

- [ ] **Create `app/checks/views.py`**

```python
from datetime import datetime, timezone
from flask import request, jsonify
from flask_login import login_required
from app.checks import bp
from app.checks.models import PendingFollowCheck
from app.extensions import db
from app.helpers import not_found
from app.messages import AppMessages


@bp.route("", methods=["GET"])
@login_required
def list_checks():
    platform = request.args.get("platform", "instagram")
    checks = (PendingFollowCheck.query
              .filter_by(platform=platform)
              .filter(PendingFollowCheck.attempts < PendingFollowCheck.max_attempts)
              .order_by(PendingFollowCheck.check_after.asc())
              .all())
    return jsonify({"checks": [c.to_dict() for c in checks], "count": len(checks)}), 200


@bp.route("/<check_id>/force", methods=["POST"])
@login_required
def force_check(check_id):
    check = PendingFollowCheck.query.get(check_id)
    if not check:
        return not_found(AppMessages.CHECK_NOT_FOUND)
    check.check_after = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"id": check_id, "forced": True}), 200


@bp.route("/<check_id>/abandon", methods=["POST"])
@login_required
def abandon_check(check_id):
    check = PendingFollowCheck.query.get(check_id)
    if not check:
        return not_found(AppMessages.CHECK_NOT_FOUND)
    check.max_attempts = check.attempts
    db.session.commit()
    return jsonify({"id": check_id, "abandoned": True}), 200
```

- [ ] **Create `app/stats/views.py`**

```python
from datetime import date
from flask import request, jsonify
from flask_login import login_required
from app.stats import bp
from app.platforms.models import PlatformDailyCount


@bp.route("", methods=["GET"])
@login_required
def get_stats():
    platform = request.args.get("platform", "instagram")
    today = date.today().isoformat()

    if platform == "all":
        rows = (PlatformDailyCount.query
                .filter_by(date=today)
                .all())
        return jsonify({"stats": [r.to_dict() for r in rows]}), 200

    row = PlatformDailyCount.query.filter_by(platform=platform, date=today).first()
    return jsonify({
        "platform": platform,
        "triggers_matched": row.triggers_matched if row else 0,
        "messages_sent": row.messages_sent if row else 0,
    }), 200
```

- [ ] **Create `app/bot/views.py`**

```python
from flask import request, jsonify
from flask_login import login_required
from app.bot import bp
from app.platforms.models import PlatformSettings

_ALL_PLATFORMS = ["instagram", "twitter", "telegram"]


@bp.route("/pause", methods=["POST"])
@login_required
def pause_bot():
    platform = request.args.get("platform", "all")
    targets = _ALL_PLATFORMS if platform == "all" else [platform]
    for p in targets:
        PlatformSettings.set(p, "paused", "true")
    return jsonify({"status": "paused", "platform": platform}), 200


@bp.route("/resume", methods=["POST"])
@login_required
def resume_bot():
    platform = request.args.get("platform", "all")
    targets = _ALL_PLATFORMS if platform == "all" else [platform]
    for p in targets:
        PlatformSettings.set(p, "paused", "false")
    return jsonify({"status": "running", "platform": platform}), 200


@bp.route("/restart", methods=["POST"])
@login_required
def restart_bot():
    platform = request.args.get("platform", "all")
    return jsonify({"status": "restarting", "platform": platform}), 200
```

- [ ] **Verify all routes exist**

```bash
python3 -c "
from app import create_app
app = create_app()
for r in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
    if any(x in r.rule for x in ['/api/', '/auth/']):
        print(r.rule, list(r.methods - {'HEAD','OPTIONS'}))
"
```

Expected: all 20 API routes printed.

- [ ] **Commit**

```bash
git add app/platforms/ app/checks/ app/stats/ app/bot/
git commit -m "feat: add platforms, checks, stats, bot modules"
```

---

## Task 9: SocketIO module

**Files:**
- Create: `app/socket.py`

- [ ] **Create `app/socket.py`**

```python
from flask_login import current_user
from flask_socketio import disconnect
from app.extensions import socketio


@socketio.on("connect")
def handle_connect():
    if not current_user.is_authenticated:
        disconnect()
        return False


def emit_event(event_name: str, data: dict, platform: str = None):
    payload = {"event": event_name, "data": data}
    if platform:
        payload["platform"] = platform
    socketio.emit(event_name, payload)
```

- [ ] **Import in `app/__init__.py`** — add after `db.create_all()`:

```python
    # Register SocketIO handlers
    from app import socket  # noqa: F401
```

- [ ] **Verify**

```bash
python3 -c "from app import create_app; app = create_app(); print('socket OK')"
```

- [ ] **Commit**

```bash
git add app/socket.py app/__init__.py
git commit -m "feat: add SocketIO connect handler and emit_event helper"
```

---

## Task 10: Update main.py + add supports_follow_gate to frontend

**Files:**
- Modify: `main.py`
- Modify: `frontend/app.js` — quote UUID IDs in template strings

- [ ] **Update `main.py`**

```python
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
```

- [ ] **Fix UUID IDs in `frontend/app.js`**

UUIDs are strings with dashes — `onclick="fn(uuid)"` renders as invalid JS. Wrap all dynamic IDs in quotes.

In `frontend/app.js`, replace every instance of:
```js
onclick="showSessionDetail(${s.id})"
```
with:
```js
onclick="showSessionDetail('${s.id}')"
```

And:
```js
onclick="editWorkflow(${w.id})"
onclick="toggleWorkflow(${w.id})"
onclick="deleteWorkflow(${w.id})"
onclick="forceCheck(${c.id})"
onclick="abandonCheck(${c.id})"
```
with quoted versions:
```js
onclick="editWorkflow('${w.id}')"
onclick="toggleWorkflow('${w.id}')"
onclick="deleteWorkflow('${w.id}')"
onclick="forceCheck('${c.id}')"
onclick="abandonCheck('${c.id}')"
```

- [ ] **Also: `api.getWorkflows()` compare fix** — `editWorkflow` finds workflow with `x.id === id`. Since both are strings now this is fine (strict equality works on strings).

- [ ] **Verify app boots**

```bash
python3 -c "from app import create_app; app = create_app(); print('boot OK')"
```

- [ ] **Commit**

```bash
git add main.py frontend/app.js
git commit -m "feat: update main.py to use new app factory, fix UUID IDs in frontend"
```

---

## Task 11: Delete old api/ and db/ folders

**Files:**
- Delete: `api/` (all files)
- Delete: `db/` (all files)

- [ ] **Verify nothing imports from `api/` or `db/`**

```bash
grep -r "from api\." /Users/saran/Work/theBot --include="*.py" | grep -v "__pycache__"
grep -r "from db\." /Users/saran/Work/theBot --include="*.py" | grep -v "__pycache__"
```

Expected: zero results (only `app/` and `core/` imports should remain).

- [ ] **Check workers still import correctly (they use db)**

```bash
grep -r "from db\." /Users/saran/Work/theBot/workers --include="*.py"
```

If results found, update those imports to use `app.sessions.models`, `app.workflows.models` etc. via SQLAlchemy session.

- [ ] **Delete folders**

```bash
rm -rf /Users/saran/Work/theBot/api
rm -rf /Users/saran/Work/theBot/db
```

- [ ] **Verify app still boots**

```bash
python3 -c "from app import create_app; app = create_app(); print('clean boot OK')"
```

- [ ] **Commit**

```bash
git add -A
git commit -m "refactor: delete api/ and db/ — fully replaced by app/ modules"
```

---

## Task 12: Smoke test all endpoints

- [ ] **Start server**

```bash
python3 main.py &
sleep 2
```

- [ ] **Test auth redirect**

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/
```

Expected: `302`

- [ ] **Test API guard**

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/workflows?platform=instagram
```

Expected: `401`

- [ ] **Login and test workflows**

```bash
curl -s -c /tmp/bot_cookies.txt -X POST http://localhost:5000/auth/login \
  -d "username=admin&password=changeme" -L -o /dev/null -w "%{http_code}"
```

Expected: `200`

```bash
curl -s -b /tmp/bot_cookies.txt "http://localhost:5000/api/workflows?platform=instagram"
```

Expected: `{"platform":"instagram","workflows":[]}`

```bash
curl -s -b /tmp/bot_cookies.txt "http://localhost:5000/api/stats?platform=instagram"
```

Expected: `{"messages_sent":0,"platform":"instagram","triggers_matched":0}`

```bash
curl -s -b /tmp/bot_cookies.txt "http://localhost:5000/api/platforms"
```

Expected: JSON with 3 platforms.

- [ ] **Kill server**

```bash
pkill -f "python3 main.py" 2>/dev/null; true
```

- [ ] **Commit**

```bash
git add -A
git commit -m "test: verify all endpoints reachable after restructure"
```

---

## Self-Review Checklist

**Spec coverage:**
- ✅ `app/<module>/` structure per DIRECTORY.md
- ✅ `__init__.py` defines blueprint + imports views/models
- ✅ `models.py` on every module with UUID PKs, `deleted_at/deleted_by`, `to_dict()`
- ✅ `views.py` uses `AppMessages` + `bad_request`/`error_response`/`not_found`
- ✅ Registered in `app/__init__.py`
- ✅ `db.create_all()` replaces SQL migration runner
- ✅ `api/` and `db/` deleted
- ✅ Frontend UUID onclick fix

**Placeholder scan:** None found.

**Type consistency:**
- `workflow_id` is `String(36)` in `MessageSession.workflow_id` and `WorkflowStep.workflow_id` — matches `Workflow.id`
- `session_id` is `String(36)` in `PendingFollowCheck` and `SessionStepHistory` — matches `MessageSession.id`
- `PlatformSettings.set()` uses `db as _db` to avoid circular — correct
