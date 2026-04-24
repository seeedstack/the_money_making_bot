# Phase 1: Instagram Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Instagram adapter as complete skeleton. All files created, imports wired, classes stubbed, tests passing, no real API calls yet.

**Architecture:** Shell-first approach. Create all 70+ files with stubs (return safe defaults). Wire all imports. Pass all tests (stubbed). Prove architecture works. Then fill with real logic.

**Tech Stack:** Flask, SQLAlchemy Core, instagrapi, React, pytest, SQLite

---

## File Creation Plan

**Files to create:** 70+ files organized by layer

| Layer | Count | Responsibility |
|-------|-------|-----------------|
| config/ | 3 | Settings, workflows YAML, schema |
| core/interfaces/ | 4 | Protocols (stubs) |
| core/models/ | 5 | Dataclasses, enums |
| core/engine/ | 5 | Step executor, registry, step types |
| platforms/instagram/ | 5 | Adapter, client, readers, senders |
| platforms/ | 2 | Base class, registry |
| workers/ | 5 | Base worker, manager, 3 per-platform workers |
| db/ | 10 | Database, migrations, 5 repos + instagram_account_repo |
| sync/ | 4 | yaml_loader, yaml_exporter, watcher, __init__ |
| api/ | 8 | create_app, socketio, middleware, 6 routes |
| frontend/ | 4 | HTML, React app, API wrapper, styles |
| tests/ | 10+ | Fixtures, unit tests, integration stubs |
| Root | 4 | main.py, start.sh, requirements files, .env |

---

## Task Sequence

Each task: create files + write stub implementations + write failing tests + make tests pass (return safe defaults).

---

### Task 1: Project Structure & Root Files

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `.env.example`
- Create: `.env`
- Create: `main.py`
- Create: `start.sh`

- [ ] **Step 1: Write `requirements.txt`**

```
Flask==2.3.2
Flask-SocketIO==5.3.0
python-socketio==5.9.0
instagrapi==2.0.0
cryptography==41.0.0
pyyaml==6.0
jsonschema==4.19.0
watchdog==3.0.0
SQLAlchemy==2.0.0
python-dotenv==1.0.0
```

- [ ] **Step 2: Write `requirements-dev.txt`**

```
-r requirements.txt
ruff==0.0.275
mypy==1.4.1
pytest==7.4.0
pytest-cov==4.1.0
import-linter==1.13.0
```

- [ ] **Step 3: Write `.env.example`**

```
# Global
FLASK_SECRET=dev_secret_key_change_in_prod
BOT_TIMEZONE=Asia/Kolkata
SCAN_INTERVAL_SECONDS=5
RECHECK_INTERVAL_SECONDS=10
MAX_RECHECK_ATTEMPTS=10

# Instagram
INSTAGRAM_ENABLED=true
INSTAGRAM_DAILY_DM_CAP=50
INSTAGRAM_DM_DELAY_MIN=1
INSTAGRAM_DM_DELAY_MAX=3

# Database
DATABASE_URL=sqlite:///data/theBot.db

# Encryption (for storing creds)
ENCRYPTION_KEY=your_fernet_key_here_32_chars_min
```

- [ ] **Step 4: Write `.env`**

(Copy .env.example content)

- [ ] **Step 5: Write `main.py`**

```python
import os
from api import create_app
from workers.worker_manager import WorkerManager
from config.settings import settings
from sync.yaml_loader import YamlLoader

if __name__ == "__main__":
    app = create_app()

    # Load workflows.yaml → DB on startup
    loader = YamlLoader()
    loader.sync()

    # Start workers
    manager = WorkerManager()
    manager.start_all()

    try:
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=settings.flask_env == "development"
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        manager.stop_all()
```

- [ ] **Step 6: Write `start.sh`**

```bash
#!/bin/bash
set -e

export FLASK_ENV=development
export FLASK_APP=main.py

# Backend
python -m flask run --port 5000 &
FLASK_PID=$!

echo "Backend running on localhost:5000"
echo "Press Ctrl+C to stop"

wait $FLASK_PID
```

- [ ] **Step 7: Make start.sh executable**

```bash
chmod +x start.sh
```

- [ ] **Step 8: Commit**

```bash
git add requirements.txt requirements-dev.txt .env.example .env main.py start.sh
git commit -m "init: add project root files and dependencies"
```

---

### Task 2: Config Layer

**Files:**
- Create: `config/__init__.py`
- Create: `config/settings.py`
- Create: `config/workflows.yaml`
- Create: `config/workflows.schema.json`

- [ ] **Step 1: Write `config/__init__.py`**

```python
from .settings import settings

__all__ = ["settings"]
```

- [ ] **Step 2: Write `config/settings.py`**

```python
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    # Global
    flask_secret: str = os.getenv("FLASK_SECRET", "dev_key")
    flask_env: str = os.getenv("FLASK_ENV", "development")
    bot_timezone: str = os.getenv("BOT_TIMEZONE", "Asia/Kolkata")
    scan_interval_seconds: int = int(os.getenv("SCAN_INTERVAL_SECONDS", "5"))
    recheck_interval_seconds: int = int(os.getenv("RECHECK_INTERVAL_SECONDS", "10"))
    max_recheck_attempts: int = int(os.getenv("MAX_RECHECK_ATTEMPTS", "10"))
    
    # Instagram
    instagram_enabled: bool = os.getenv("INSTAGRAM_ENABLED", "true").lower() == "true"
    instagram_daily_dm_cap: int = int(os.getenv("INSTAGRAM_DAILY_DM_CAP", "50"))
    instagram_dm_delay_min: int = int(os.getenv("INSTAGRAM_DM_DELAY_MIN", "1"))
    instagram_dm_delay_max: int = int(os.getenv("INSTAGRAM_DM_DELAY_MAX", "3"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/theBot.db")
    
    # Encryption
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "default_key_not_secure")

settings = Settings()
```

- [ ] **Step 3: Write `config/workflows.yaml`**

```yaml
workflows:
  - name: "Example Workflow"
    platform: instagram
    trigger: "hello"
    source_id: "https://instagram.com/p/ABC123"
    priority: 1
    match_mode: contains
    link: "https://example.com"
    steps:
      - type: check_follow
      - type: send_message
        message: "Hey {username}! Thanks for reaching out."
        send_if: always
```

- [ ] **Step 4: Write `config/workflows.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "workflows": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "platform", "trigger", "source_id", "steps"],
        "properties": {
          "name": { "type": "string" },
          "platform": { "enum": ["instagram", "twitter", "telegram"] },
          "trigger": { "type": "string" },
          "source_id": { "type": "string" },
          "priority": { "type": "integer", "minimum": 1 },
          "match_mode": { "enum": ["exact", "contains"] },
          "link": { "type": "string" },
          "steps": { "type": "array" }
        }
      }
    }
  }
}
```

- [ ] **Step 5: Commit**

```bash
git add config/
git commit -m "feat: add config layer with settings and workflows schema"
```

---

### Task 3: Core Models

**Files:**
- Create: `core/__init__.py`
- Create: `core/models/__init__.py`
- Create: `core/models/platform.py`
- Create: `core/models/workflow.py`
- Create: `core/models/session.py`
- Create: `core/models/trigger.py`
- Create: `core/models/events.py`

- [ ] **Step 1: Write `core/__init__.py`**

```python
# Core package
```

- [ ] **Step 2: Write `core/models/__init__.py`**

```python
from .platform import Platform
from .workflow import Workflow, WorkflowStep, StepType, SendIf
from .session import MessageSession, SessionState
from .trigger import TriggerEvent
from .events import SocketIOEvent

__all__ = [
    "Platform",
    "Workflow",
    "WorkflowStep",
    "StepType",
    "SendIf",
    "MessageSession",
    "SessionState",
    "TriggerEvent",
    "SocketIOEvent",
]
```

- [ ] **Step 3: Write `core/models/platform.py`**

```python
from enum import Enum

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TELEGRAM = "telegram"
```

- [ ] **Step 4: Write `core/models/workflow.py`**

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class StepType(str, Enum):
    CHECK_FOLLOW = "check_follow"
    SEND_MESSAGE = "send_message"
    WAIT_FOR_FOLLOW = "wait_for_follow"
    DELAY = "delay"

class SendIf(str, Enum):
    FOLLOWING = "following"
    NOT_FOLLOWING = "not_following"
    NOW_FOLLOWING = "now_following"
    ALWAYS = "always"

@dataclass
class WorkflowStep:
    step_order: int
    step_type: StepType
    message_template: Optional[str] = None
    send_if: Optional[SendIf] = None
    delay_seconds: Optional[int] = None

@dataclass
class Workflow:
    id: int
    name: str
    platform: str
    trigger_keyword: str
    source_id: str
    priority: int
    active: bool
    match_mode: str
    link: Optional[str] = None
    steps: list[WorkflowStep] = None

    def __post_init__(self):
        if self.steps is None:
            self.steps = []
```

- [ ] **Step 5: Write `core/models/session.py`**

```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional

class SessionState(str, Enum):
    STEP_RUNNING = "STEP_RUNNING"
    AWAITING_FOLLOW = "AWAITING_FOLLOW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"

class FollowStatus(str, Enum):
    FOLLOWING = "FOLLOWING"
    NOT_FOLLOWING = "NOT_FOLLOWING"
    NOT_APPLICABLE = "NOT_APPLICABLE"

@dataclass
class MessageSession:
    id: int
    platform: str
    username: str
    workflow_id: int
    current_step: int
    follow_status: FollowStatus
    state: SessionState
    started_at: datetime
    last_action_at: datetime
```

- [ ] **Step 6: Write `core/models/trigger.py`**

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TriggerEvent:
    platform: str
    source_id: str
    username: str
    content: str
    matched_keyword: str
    detected_at: datetime
```

- [ ] **Step 7: Write `core/models/events.py`**

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class SocketIOEvent:
    event_name: str
    data: dict[str, Any]
    platform: str
```

- [ ] **Step 8: Commit**

```bash
git add core/models/ core/__init__.py
git commit -m "feat: add core data models and enums"
```

---

### Task 4: Core Interfaces

**Files:**
- Create: `core/interfaces/__init__.py`
- Create: `core/interfaces/platform_adapter.py`
- Create: `core/interfaces/message_reader.py`
- Create: `core/interfaces/dm_sender.py`
- Create: `core/interfaces/follow_checker.py`

- [ ] **Step 1: Write `core/interfaces/__init__.py`**

```python
from typing import Protocol

__all__ = [
    "PlatformAdapter",
    "MessageReader",
    "DMSender",
    "FollowChecker",
]
```

- [ ] **Step 2: Write `core/interfaces/platform_adapter.py`**

```python
from typing import Protocol
from core.models import Platform, TriggerEvent, FollowStatus

class PlatformAdapter(Protocol):
    """All platform adapters must implement these 4 methods."""
    
    @property
    def platform(self) -> Platform:
        """Return platform enum."""
        ...
    
    def read_triggers(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments/replies from source. Stub: return []"""
        ...
    
    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM to recipient. Stub: return True"""
        ...
    
    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        ...
    
    def supports_follow_gate(self) -> bool:
        """Can this platform gate by follow? Stub: return True"""
        ...
```

- [ ] **Step 3: Write `core/interfaces/message_reader.py`**

```python
from typing import Protocol
from core.models import TriggerEvent

class MessageReader(Protocol):
    """Read comments, replies, messages from platform."""
    
    def fetch(self, source_id: str) -> list[TriggerEvent]:
        """Fetch messages. Stub: return []"""
        ...
```

- [ ] **Step 4: Write `core/interfaces/dm_sender.py`**

```python
from typing import Protocol

class DMSender(Protocol):
    """Send DM on platform."""
    
    def send(self, recipient_id: str, text: str) -> bool:
        """Send DM. Stub: return True"""
        ...
```

- [ ] **Step 5: Write `core/interfaces/follow_checker.py`**

```python
from typing import Protocol
from core.models import FollowStatus

class FollowChecker(Protocol):
    """Check follow status on platform."""
    
    def is_following(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        ...
```

- [ ] **Step 6: Commit**

```bash
git add core/interfaces/
git commit -m "feat: add core interface protocols"
```

---

### Task 5: Core Engine (Stubs)

**Files:**
- Create: `core/engine/__init__.py`
- Create: `core/engine/step_executor.py`
- Create: `core/engine/step_registry.py`
- Create: `core/engine/steps/__init__.py`
- Create: `core/engine/steps/check_follow.py`
- Create: `core/engine/steps/send_message.py`
- Create: `core/engine/steps/wait_for_follow.py`
- Create: `core/engine/steps/delay.py`
- Create: `core/keyword_matcher.py`
- Create: `core/rate_limiter.py`

- [ ] **Step 1: Write `core/engine/__init__.py`**

```python
# Engine package
```

- [ ] **Step 2: Write `core/engine/step_executor.py`**

```python
from core.models import MessageSession, SessionState

class StepExecutor:
    """Execute one workflow step, return next state."""
    
    def execute(self, session: MessageSession) -> MessageSession:
        """Stub: return session with state COMPLETED"""
        session.state = SessionState.COMPLETED
        return session
```

- [ ] **Step 3: Write `core/engine/step_registry.py`**

```python
from core.models import StepType

class StepRegistry:
    """Map StepType → handler class."""
    
    def __init__(self):
        self.handlers = {}
    
    def register(self, step_type: StepType, handler_class):
        """Register handler for step type."""
        self.handlers[step_type] = handler_class
    
    def get(self, step_type: StepType):
        """Get handler for step type. Stub: return None"""
        return self.handlers.get(step_type)
```

- [ ] **Step 4: Write `core/engine/steps/__init__.py`**

```python
# Steps package
```

- [ ] **Step 5: Write `core/engine/steps/check_follow.py`**

```python
class CheckFollowStep:
    """Check if user follows."""
    
    def execute(self, session, adapter):
        """Stub: return session unchanged"""
        return session
```

- [ ] **Step 6: Write `core/engine/steps/send_message.py`**

```python
class SendMessageStep:
    """Send message to user."""
    
    def execute(self, session, adapter, template: str):
        """Stub: return session unchanged"""
        return session
```

- [ ] **Step 7: Write `core/engine/steps/wait_for_follow.py`**

```python
class WaitForFollowStep:
    """Wait for user to follow."""
    
    def execute(self, session, adapter):
        """Stub: return session unchanged"""
        return session
```

- [ ] **Step 8: Write `core/engine/steps/delay.py`**

```python
class DelayStep:
    """Delay before next step."""
    
    def execute(self, session, delay_seconds: int):
        """Stub: return session unchanged"""
        return session
```

- [ ] **Step 9: Write `core/keyword_matcher.py`**

```python
class KeywordMatcher:
    """Match keywords in content."""

    def match(self, content: str, keyword: str, mode: str) -> bool:
        """Return True if keyword matches content per mode."""
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        if mode == "exact":
            return content_lower == keyword_lower
        # default: contains
        return keyword_lower in content_lower
```

- [ ] **Step 10: Write `core/rate_limiter.py`**

```python
class RateLimiter:
    """Rate limit by platform and account."""
    
    def can_send(self, platform: str, account_id: int) -> bool:
        """Stub: return True"""
        return True
    
    def record_send(self, platform: str, account_id: int):
        """Stub: do nothing"""
        pass
```

- [ ] **Step 11: Commit**

```bash
git add core/engine/ core/keyword_matcher.py core/rate_limiter.py
git commit -m "feat: add core engine stubs and helpers"
```

---

### Task 6: Platform Base & Instagram Adapter

**Files:**
- Create: `platforms/__init__.py`
- Create: `platforms/base.py`
- Create: `platforms/registry.py`
- Create: `platforms/instagram/__init__.py`
- Create: `platforms/instagram/adapter.py`
- Create: `platforms/instagram/client.py`
- Create: `platforms/instagram/comment_reader.py`
- Create: `platforms/instagram/dm_sender.py`
- Create: `platforms/instagram/follow_checker.py`

- [ ] **Step 1: Write `platforms/__init__.py`**

```python
# Platforms package
```

- [ ] **Step 2: Write `platforms/base.py`**

```python
from abc import ABC
from core.models import Platform

class BasePlatformAdapter(ABC):
    """Base adapter. All platforms inherit from this."""
    
    platform: Platform
    
    def read_triggers(self, source_id: str):
        raise NotImplementedError
    
    def send_message(self, recipient_id: str, text: str):
        raise NotImplementedError
    
    def check_follow(self, username: str):
        raise NotImplementedError
    
    def supports_follow_gate(self) -> bool:
        raise NotImplementedError
```

- [ ] **Step 3: Write `platforms/registry.py`**

```python
from core.models import Platform
from config.settings import settings

class PlatformRegistry:
    """Map Platform enum → adapter instance. Source of truth for enabled platforms."""

    def __init__(self):
        self.adapters = {}

    def register(self, platform: Platform, adapter):
        """Register adapter for platform."""
        self.adapters[platform] = adapter

    def get(self, platform: Platform):
        """Get adapter for platform. Returns None if not registered."""
        return self.adapters.get(platform)

    def get_enabled_platforms(self) -> list[Platform]:
        """Return list of platforms enabled in settings. Stub: instagram only."""
        enabled = []
        if settings.instagram_enabled:
            enabled.append(Platform.INSTAGRAM)
        # Phase 2+: add twitter_enabled, telegram_enabled checks here
        return enabled
```

- [ ] **Step 4: Write `platforms/instagram/__init__.py`**

```python
from .adapter import InstagramAdapter

__all__ = ["InstagramAdapter"]
```

- [ ] **Step 5: Write `platforms/instagram/adapter.py`**

```python
from core.models import Platform, FollowStatus, TriggerEvent
from platforms.base import BasePlatformAdapter
from .client import InstagramClient
from .comment_reader import CommentReader
from .dm_sender import DMSender
from .follow_checker import FollowChecker

class InstagramAdapter(BasePlatformAdapter):
    """Instagram adapter implements PlatformAdapter protocol."""
    
    platform = Platform.INSTAGRAM
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.client = InstagramClient(account_id)
        self.comment_reader = CommentReader(self.client)
        self.dm_sender = DMSender(self.client)
        self.follow_checker = FollowChecker(self.client)
    
    def read_triggers(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments from post. Stub: return []"""
        return []
    
    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM to user. Stub: return True"""
        return True
    
    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        return FollowStatus.NOT_FOLLOWING
    
    def supports_follow_gate(self) -> bool:
        """Instagram supports follow gate. Stub: return True"""
        return True
```

- [ ] **Step 6: Write `platforms/instagram/client.py`**

```python
class InstagramClient:
    """Instagrapi client wrapper."""
    
    def __init__(self, account_id: int):
        """Initialize with account ID. Load creds from DB (stub)."""
        self.account_id = account_id
        self.cl = None  # instagrapi.Client() stub
    
    def login(self) -> bool:
        """Login to Instagram. Stub: return True"""
        return True
    
    def get_comments(self, source_id: str):
        """Get comments from post. Stub: return []"""
        return []
    
    def send_direct_message(self, recipient_id: str, text: str) -> bool:
        """Send DM. Stub: return True"""
        return True
    
    def user_info(self, username: str):
        """Get user info. Stub: return empty dict"""
        return {}
```

- [ ] **Step 7: Write `platforms/instagram/comment_reader.py`**

```python
from core.models import TriggerEvent

class CommentReader:
    """Read comments from Instagram posts."""
    
    def __init__(self, client):
        self.client = client
    
    def fetch(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments from post. Stub: return []"""
        return []
```

- [ ] **Step 8: Write `platforms/instagram/dm_sender.py`**

```python
class DMSender:
    """Send DMs on Instagram."""
    
    def __init__(self, client):
        self.client = client
    
    def send(self, recipient_id: str, text: str) -> bool:
        """Send DM. Stub: return True"""
        return True
```

- [ ] **Step 9: Write `platforms/instagram/follow_checker.py`**

```python
from core.models import FollowStatus

class FollowChecker:
    """Check follow status on Instagram."""
    
    def __init__(self, client):
        self.client = client
    
    def is_following(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        return FollowStatus.NOT_FOLLOWING
```

- [ ] **Step 10: Commit**

```bash
git add platforms/
git commit -m "feat: add platform base and instagram adapter (stubbed)"
```

---

### Task 7: Workers

**Files:**
- Create: `workers/__init__.py`
- Create: `workers/base_worker.py`
- Create: `workers/worker_manager.py`
- Create: `workers/per_platform/__init__.py`
- Create: `workers/per_platform/trigger_monitor.py`
- Create: `workers/per_platform/message_engine.py`
- Create: `workers/per_platform/follow_recheck.py`

- [ ] **Step 1: Write `workers/__init__.py`**

```python
# Workers package
```

- [ ] **Step 2: Write `workers/base_worker.py`**

```python
import threading
import time
import logging
from abc import ABC, abstractmethod
from core.models import Platform
from config.settings import settings

logger = logging.getLogger(__name__)

class BaseWorker(ABC):
    """Base worker. All platform workers inherit from this."""

    enabled: bool = True

    def __init__(self, platform: Platform):
        self.platform = platform
        self.thread = None
        self.running = False

    def start(self):
        """Start worker thread."""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"{self.__class__.__name__} started for {self.platform}")

    def stop(self):
        """Stop worker gracefully."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info(f"{self.__class__.__name__} stopped for {self.platform}")

    def _run_loop(self):
        """Internal run loop."""
        while self.running:
            try:
                if self.enabled:
                    self.run_cycle()
            except Exception as e:
                self.on_error(e)
            time.sleep(settings.scan_interval_seconds)

    @abstractmethod
    def run_cycle(self):
        """Override in subclass. Called once per cycle."""
        pass

    def on_error(self, e: Exception):
        """Handle error. Override in subclass if needed."""
        logger.error(f"Error in {self.__class__.__name__}: {e}")
```

- [ ] **Step 3: Write `workers/worker_manager.py`**

```python
import logging
from platforms.registry import PlatformRegistry

logger = logging.getLogger(__name__)

class WorkerManager:
    """Spawn, manage, stop all workers."""

    def __init__(self):
        self.workers = []
        self.registry = PlatformRegistry()

    def start_all(self):
        """Start workers for all enabled platforms."""
        from workers.per_platform.trigger_monitor import TriggerMonitorWorker
        from workers.per_platform.message_engine import MessageEngineWorker
        from workers.per_platform.follow_recheck import FollowRecheckWorker

        for platform in self.registry.get_enabled_platforms():
            for WorkerClass in [TriggerMonitorWorker, MessageEngineWorker, FollowRecheckWorker]:
                worker = WorkerClass(platform=platform)
                worker.start()
                self.workers.append(worker)
            logger.info(f"Workers started for {platform}")

        logger.info("All workers started")

    def stop_all(self):
        """Stop all workers gracefully."""
        for worker in self.workers:
            worker.stop()
        logger.info("All workers stopped")
```

- [ ] **Step 4: Write `workers/per_platform/__init__.py`**

```python
# Per-platform workers package
```

- [ ] **Step 5: Write `workers/per_platform/trigger_monitor.py`**

```python
import logging
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

class TriggerMonitorWorker(BaseWorker):
    """Monitor for keyword triggers in comments/replies."""

    def run_cycle(self):
        """Scan for triggers. Stub: log and return"""
        logger.debug(f"[{self.platform}] TriggerMonitor cycle - scanning...")
```

- [ ] **Step 6: Write `workers/per_platform/message_engine.py`**

```python
import logging
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

class MessageEngineWorker(BaseWorker):
    """Execute pending workflow steps."""

    def run_cycle(self):
        """Process sessions. Stub: log and return"""
        logger.debug(f"[{self.platform}] MessageEngine cycle - processing sessions...")
```

- [ ] **Step 7: Write `workers/per_platform/follow_recheck.py`**

```python
import logging
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

class FollowRecheckWorker(BaseWorker):
    """Recheck follow status for awaiting sessions."""

    def run_cycle(self):
        """Recheck follows. Stub: log and return"""
        logger.debug(f"[{self.platform}] FollowRecheck cycle - checking...")
```

- [ ] **Step 8: Commit**

```bash
git add workers/
git commit -m "feat: add worker base and per-platform workers (stubbed)"
```

---

### Task 8: Database Layer

**Files:**
- Create: `db/__init__.py`
- Create: `db/database.py`
- Create: `db/migrations/__init__.py`
- Create: `db/migrations/001_init.sql`
- Create: `db/repositories/__init__.py`
- Create: `db/repositories/workflow_repo.py`
- Create: `db/repositories/session_repo.py`
- Create: `db/repositories/scan_repo.py`
- Create: `db/repositories/follow_check_repo.py`
- Create: `db/repositories/settings_repo.py`

- [ ] **Step 1: Write `db/__init__.py`**

```python
# Database package
```

- [ ] **Step 2: Write `db/database.py`**

```python
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

class Database:
    """Database connection and migration runner."""

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/theBot.db")

        # Create data directory if needed
        if "sqlite:///" in database_url and ":memory:" not in database_url:
            db_path = database_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.engine = create_engine(
            database_url,
            echo=False,
            poolclass=StaticPool if "sqlite" in database_url else None
        )

    def run_migrations(self):
        """Run all SQL migration files in order."""
        migrations_dir = Path(__file__).parent / "migrations"
        sql_files = sorted(migrations_dir.glob("*.sql"))

        with self.engine.connect() as conn:
            for sql_file in sql_files:
                sql = sql_file.read_text()
                # Execute each statement separately
                for statement in sql.split(";"):
                    statement = statement.strip()
                    if statement:
                        conn.execute(text(statement))
            conn.commit()

    def get_connection(self):
        """Get DB connection."""
        return self.engine.connect()
```

- [ ] **Step 3: Write `db/migrations/__init__.py`**

```python
# Migrations package
```

- [ ] **Step 4: Write `db/migrations/001_init.sql`**

```sql
-- Core tables
CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    name TEXT NOT NULL,
    trigger_keyword TEXT NOT NULL,
    source_id TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT 1,
    match_mode TEXT DEFAULT 'contains',
    link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL,
    message_template TEXT,
    send_if TEXT,
    delay_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

CREATE TABLE IF NOT EXISTS trigger_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    source_id TEXT NOT NULL,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    matched_workflow_id INTEGER,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS message_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    username TEXT NOT NULL,
    workflow_id INTEGER NOT NULL,
    current_step INTEGER DEFAULT 0,
    follow_status TEXT DEFAULT 'NOT_FOLLOWING',
    state TEXT DEFAULT 'STEP_RUNNING',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

CREATE TABLE IF NOT EXISTS pending_follow_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    session_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    check_after TIMESTAMP NOT NULL,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES message_sessions(id)
);

CREATE TABLE IF NOT EXISTS platform_settings (
    platform TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (platform, key)
);

CREATE TABLE IF NOT EXISTS platform_daily_counts (
    platform TEXT NOT NULL,
    date TEXT NOT NULL,
    messages_sent INTEGER DEFAULT 0,
    triggers_matched INTEGER DEFAULT 0,
    PRIMARY KEY (platform, date)
);

-- Instagram-specific tables
CREATE TABLE IF NOT EXISTS instagram_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_encrypted TEXT NOT NULL,
    salt TEXT NOT NULL,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS instagram_rate_windows (
    account_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    message_count INTEGER DEFAULT 1,
    PRIMARY KEY (account_id, timestamp),
    FOREIGN KEY (account_id) REFERENCES instagram_accounts(id)
);

CREATE TABLE IF NOT EXISTS instagram_session_cache (
    account_id INTEGER NOT NULL,
    session_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (account_id),
    FOREIGN KEY (account_id) REFERENCES instagram_accounts(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workflows_platform ON workflows(platform);
CREATE INDEX IF NOT EXISTS idx_trigger_scans_platform ON trigger_scans(platform);
CREATE INDEX IF NOT EXISTS idx_message_sessions_platform ON message_sessions(platform);
```

- [ ] **Step 5: Write `db/repositories/__init__.py`**

```python
# Repositories package
```

- [ ] **Step 6: Write `db/repositories/workflow_repo.py`**

```python
class WorkflowRepository:
    """Query workflows by platform."""
    
    def __init__(self, db_engine):
        self.engine = db_engine
    
    def get_all(self, platform: str) -> list:
        """Get all workflows for platform. Stub: return []"""
        return []
    
    def get_by_id(self, platform: str, workflow_id: int):
        """Get workflow by ID. Stub: return None"""
        return None
    
    def insert(self, platform: str, workflow_data: dict):
        """Insert workflow. Stub: return None"""
        return None
    
    def update(self, platform: str, workflow_id: int, workflow_data: dict):
        """Update workflow. Stub: return None"""
        return None
    
    def delete(self, platform: str, workflow_id: int):
        """Soft-delete workflow. Stub: return None"""
        return None
```

- [ ] **Step 7: Write `db/repositories/session_repo.py`**

```python
class SessionRepository:
    """Query message sessions by platform."""
    
    def __init__(self, db_engine):
        self.engine = db_engine
    
    def get_all(self, platform: str, state: str = None) -> list:
        """Get sessions for platform, optionally filtered by state. Stub: return []"""
        return []
    
    def get_by_id(self, platform: str, session_id: int):
        """Get session by ID. Stub: return None"""
        return None
    
    def insert(self, platform: str, session_data: dict):
        """Insert session. Stub: return None"""
        return None
    
    def update(self, platform: str, session_id: int, session_data: dict):
        """Update session. Stub: return None"""
        return None
```

- [ ] **Step 8: Write `db/repositories/scan_repo.py`**

```python
class ScanRepository:
    """Query trigger scans by platform."""
    
    def __init__(self, db_engine):
        self.engine = db_engine
    
    def insert(self, platform: str, scan_data: dict):
        """Insert trigger scan. Stub: return None"""
        return None
    
    def get_recent(self, platform: str, limit: int = 100) -> list:
        """Get recent scans. Stub: return []"""
        return []
```

- [ ] **Step 9: Write `db/repositories/follow_check_repo.py`**

```python
class FollowCheckRepository:
    """Query pending follow checks by platform."""
    
    def __init__(self, db_engine):
        self.engine = db_engine
    
    def get_pending(self, platform: str) -> list:
        """Get pending checks due now. Stub: return []"""
        return []
    
    def insert(self, platform: str, check_data: dict):
        """Insert pending check. Stub: return None"""
        return None
    
    def update(self, platform: str, check_id: int, check_data: dict):
        """Update check. Stub: return None"""
        return None
```

- [ ] **Step 10: Write `db/repositories/settings_repo.py`**

```python
class SettingsRepository:
    """Store and retrieve per-platform settings (including encrypted credentials)."""
    
    def __init__(self, db_engine):
        self.engine = db_engine
    
    def get(self, platform: str, key: str) -> str:
        """Get setting value. Stub: return None"""
        return None
    
    def set(self, platform: str, key: str, value: str):
        """Set setting value (value may be encrypted). Stub: do nothing"""
        pass
    
    def get_all(self, platform: str) -> dict:
        """Get all settings for platform. Stub: return {}"""
        return {}
```

- [ ] **Step 11: Commit**

```bash
git add db/
git commit -m "feat: add database layer with migrations and repositories (stubbed)"
```

---

### Task 9: Sync Layer + Instagram Account Repo

**Files:**
- Create: `sync/__init__.py`
- Create: `sync/yaml_loader.py`
- Create: `sync/yaml_exporter.py`
- Create: `sync/watcher.py`
- Create: `db/repositories/instagram_account_repo.py`

- [ ] **Step 1: Write `sync/__init__.py`**

```python
# Sync package
```

- [ ] **Step 2: Write `sync/yaml_loader.py`**

```python
import yaml
import logging
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)

class YamlLoader:
    """Load workflows.yaml → DB on startup and hot-reload."""

    def __init__(self):
        self.yaml_path = Path("config/workflows.yaml")

    def load(self) -> list[dict]:
        """Parse and return workflows from YAML. Returns [] on error."""
        if not self.yaml_path.exists():
            logger.warning(f"workflows.yaml not found at {self.yaml_path}")
            return []
        try:
            with open(self.yaml_path) as f:
                data = yaml.safe_load(f)
            return data.get("workflows", []) if data else []
        except yaml.YAMLError as e:
            logger.error(f"Bad YAML — skipping: {e}")
            return []

    def sync(self):
        """Load YAML → upsert to DB. Stub: log only."""
        workflows = self.load()
        logger.info(f"YamlLoader: found {len(workflows)} workflow(s) in YAML — DB sync stub (Phase 2)")
```

- [ ] **Step 3: Write `sync/yaml_exporter.py`**

```python
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class YamlExporter:
    """Export DB workflows → workflows.yaml."""

    def __init__(self):
        self.yaml_path = Path("config/workflows.yaml")

    def export(self, workflows: list[dict]):
        """Write workflows to YAML. Stub: do nothing."""
        logger.info(f"YamlExporter: export stub called with {len(workflows)} workflow(s)")
```

- [ ] **Step 4: Write `sync/watcher.py`**

```python
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sync.yaml_loader import YamlLoader

logger = logging.getLogger(__name__)

class WorkflowFileHandler(FileSystemEventHandler):
    """Hot-reload workflows.yaml on file change."""

    def __init__(self):
        self.loader = YamlLoader()

    def on_modified(self, event):
        if event.src_path.endswith("workflows.yaml"):
            logger.info("workflows.yaml changed — reloading...")
            self.loader.sync()

class YamlWatcher:
    """Watch config/ dir for workflows.yaml changes."""

    def __init__(self):
        self.observer = Observer()

    def start(self):
        """Start file watcher. Stub: log only."""
        logger.info("YamlWatcher: stub started (Phase 2: wire to DB upsert)")

    def stop(self):
        self.observer.stop()
```

- [ ] **Step 5: Write `db/repositories/instagram_account_repo.py`**

```python
import logging

logger = logging.getLogger(__name__)

class InstagramAccountRepository:
    """Query instagram_accounts table. Owns all cred storage logic."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get_active(self) -> list:
        """Get all active accounts. Stub: return []"""
        return []

    def get_by_id(self, account_id: int):
        """Get account by ID. Stub: return None"""
        return None

    def insert(self, username: str, password_encrypted: str, salt: str):
        """Insert new account. Stub: return None"""
        return None

    def update_last_login(self, account_id: int):
        """Update last_login timestamp. Stub: do nothing"""
        pass

    def deactivate(self, account_id: int):
        """Set is_active=False. Stub: do nothing"""
        pass
```

- [ ] **Step 6: Commit**

```bash
git add sync/ db/repositories/instagram_account_repo.py
git commit -m "feat: add sync layer (yaml_loader, watcher) and instagram_account_repo"
```

---

### Task 10: API Layer

**Files:**
- Create: `api/__init__.py`
- Create: `api/socketio.py`
- Create: `api/middleware.py`
- Create: `api/routes/__init__.py`
- Create: `api/routes/workflows.py`
- Create: `api/routes/sessions.py`
- Create: `api/routes/stats.py`
- Create: `api/routes/checks.py`
- Create: `api/routes/platforms.py`
- Create: `api/routes/bot.py`

- [ ] **Step 1: Write `api/__init__.py`**

```python
from flask import Flask, jsonify
from flask_socketio import SocketIO
from config.settings import settings

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    """Flask app factory."""
    app = Flask(__name__, static_folder="../frontend", static_url_path="/")
    app.config["SECRET_KEY"] = settings.flask_secret
    
    socketio.init_app(app)
    
    # Register routes
    from api.routes import workflows, sessions, stats, checks, platforms, bot
    
    app.register_blueprint(workflows.bp)
    app.register_blueprint(sessions.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(checks.bp)
    app.register_blueprint(platforms.bp)
    app.register_blueprint(bot.bp)
    
    # Root route
    @app.route("/")
    def index():
        return app.send_static_file("index.html")
    
    return app
```

- [ ] **Step 2: Write `api/socketio.py`**

```python
from api import socketio

def emit_event(event_name: str, data: dict, platform: str = None):
    """Emit SocketIO event. Stub: do nothing"""
    pass
```

- [ ] **Step 3: Write `api/middleware.py`**

```python
# Middleware stubs (auth, error handling, logging)
# Phase 2+: implement actual middleware
```

- [ ] **Step 4: Write `api/routes/__init__.py`**

```python
# Routes package
```

- [ ] **Step 5: Write `api/routes/workflows.py`**

```python
from flask import Blueprint, request, jsonify

bp = Blueprint("workflows", __name__, url_prefix="/api/workflows")

@bp.route("", methods=["GET"])
def get_workflows():
    """Get workflows for platform. Stub: return []"""
    platform = request.args.get("platform", "instagram")
    return jsonify({"workflows": [], "platform": platform}), 200

@bp.route("", methods=["POST"])
def create_workflow():
    """Create workflow. Stub: return new workflow"""
    data = request.json
    return jsonify({"id": 1, "name": data.get("name"), "platform": data.get("platform")}), 201

@bp.route("/<int:workflow_id>", methods=["PUT"])
def update_workflow(workflow_id):
    """Update workflow. Stub: return updated"""
    data = request.json
    return jsonify({"id": workflow_id, "updated": True}), 200

@bp.route("/<int:workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id):
    """Delete workflow. Stub: return ok"""
    return jsonify({"deleted": True}), 200

@bp.route("/<int:workflow_id>/toggle", methods=["POST"])
def toggle_workflow(workflow_id):
    """Toggle workflow active status. Stub: return ok"""
    return jsonify({"id": workflow_id, "toggled": True}), 200
```

- [ ] **Step 6: Write `api/routes/sessions.py`**

```python
from flask import Blueprint, request, jsonify

bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

@bp.route("", methods=["GET"])
def get_sessions():
    """Get sessions for platform, optionally filtered. Stub: return []"""
    platform = request.args.get("platform", "instagram")
    state = request.args.get("state")
    return jsonify({"sessions": [], "platform": platform, "state": state}), 200

@bp.route("/<int:session_id>", methods=["GET"])
def get_session(session_id):
    """Get session by ID. Stub: return session stub"""
    return jsonify({
        "id": session_id,
        "platform": "instagram",
        "username": "test_user",
        "state": "STEP_RUNNING",
        "current_step": 0
    }), 200
```

- [ ] **Step 7: Write `api/routes/stats.py`**

```python
from flask import Blueprint, request, jsonify

bp = Blueprint("stats", __name__, url_prefix="/api/stats")

@bp.route("", methods=["GET"])
def get_stats():
    """Get stats for platform(s). Stub: return empty stats"""
    platform = request.args.get("platform", "instagram")
    return jsonify({
        "platform": platform,
        "triggers_matched": 0,
        "messages_sent": 0,
        "daily_caps": {}
    }), 200
```

- [ ] **Step 8: Write `api/routes/checks.py`**

```python
from flask import Blueprint, request, jsonify

bp = Blueprint("checks", __name__, url_prefix="/api/pending-checks")

@bp.route("", methods=["GET"])
def get_pending_checks():
    """Get pending follow checks. Stub: return []"""
    platform = request.args.get("platform", "instagram")
    return jsonify({"checks": [], "platform": platform}), 200

@bp.route("/<int:check_id>/force", methods=["POST"])
def force_check(check_id):
    """Force a check now. Stub: return ok"""
    return jsonify({"id": check_id, "forced": True}), 200

@bp.route("/<int:check_id>/abandon", methods=["POST"])
def abandon_check(check_id):
    """Abandon a check. Stub: return ok"""
    return jsonify({"id": check_id, "abandoned": True}), 200
```

- [ ] **Step 9: Write `api/routes/platforms.py`**

```python
from flask import Blueprint, request, jsonify

bp = Blueprint("platforms", __name__, url_prefix="/api/platforms")

@bp.route("", methods=["GET"])
def get_platforms():
    """List all platforms and status. Stub: return instagram only"""
    return jsonify({
        "platforms": [
            {"name": "instagram", "enabled": True, "status": "RUNNING"}
        ]
    }), 200

@bp.route("/<name>/enable", methods=["POST"])
def enable_platform(name):
    """Enable platform. Stub: return ok"""
    return jsonify({"name": name, "enabled": True}), 200

@bp.route("/<name>/disable", methods=["POST"])
def disable_platform(name):
    """Disable platform. Stub: return ok"""
    return jsonify({"name": name, "enabled": False}), 200
```

- [ ] **Step 10: Write `api/routes/bot.py`**

```python
from flask import Blueprint, request, jsonify

bp = Blueprint("bot", __name__, url_prefix="/api/bot")

@bp.route("/pause", methods=["POST"])
def pause_bot():
    """Pause bot for platform. Stub: return ok"""
    platform = request.args.get("platform", "all")
    return jsonify({"status": "paused", "platform": platform}), 200

@bp.route("/resume", methods=["POST"])
def resume_bot():
    """Resume bot for platform. Stub: return ok"""
    platform = request.args.get("platform", "all")
    return jsonify({"status": "running", "platform": platform}), 200

@bp.route("/restart", methods=["POST"])
def restart_bot():
    """Restart bot for platform. Stub: return ok"""
    platform = request.args.get("platform", "all")
    return jsonify({"status": "restarting", "platform": platform}), 200
```

- [ ] **Step 11: Commit**

```bash
git add api/
git commit -m "feat: add API routes layer (all stubbed, return 200 OK)"
```

---

### Task 11: Frontend (React)

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/app.jsx`
- Create: `frontend/api.js`
- Create: `frontend/styles.css`

- [ ] **Step 1: Write `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Bot</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    <div id="root"></div>
    <!-- React + Babel CDN: no build step needed in Phase 1 -->
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel" src="/app.jsx"></script>
</body>
</html>
```

- [ ] **Step 2: Write `frontend/app.jsx`**

```jsx
// React and ReactDOM available as globals via CDN
const { useState, useEffect } = React;

function App() {
  const [platform, setPlatform] = useState('instagram');
  const [workflows, setWorkflows] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('home');

  useEffect(() => {
    // Stub: don't fetch yet in Phase 1
    // Phase 2+: call api.getWorkflows(platform).then(data => setWorkflows(data))
  }, [platform]);

  return (
    <div className="container">
      <header className="header">
        <h1>The Bot</h1>
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="instagram">Instagram</option>
          <option value="twitter">Twitter</option>
          <option value="telegram">Telegram</option>
        </select>
      </header>

      <nav className="tabs">
        <button 
          className={activeTab === 'home' ? 'active' : ''} 
          onClick={() => setActiveTab('home')}
        >
          Home
        </button>
        <button 
          className={activeTab === 'workflows' ? 'active' : ''} 
          onClick={() => setActiveTab('workflows')}
        >
          Workflows
        </button>
        <button 
          className={activeTab === 'sessions' ? 'active' : ''} 
          onClick={() => setActiveTab('sessions')}
        >
          Sessions
        </button>
        <button 
          className={activeTab === 'platforms' ? 'active' : ''} 
          onClick={() => setActiveTab('platforms')}
        >
          Platforms
        </button>
      </nav>

      <main className="main">
        {activeTab === 'home' && (
          <section className="tab-content">
            <h2>Overview</h2>
            <div className="status-pills">
              <div className="pill running">Instagram: RUNNING</div>
              <div className="pill paused">Twitter: PAUSED</div>
              <div className="pill paused">Telegram: PAUSED</div>
            </div>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Triggers Matched</h3>
                <p className="stat-value">0</p>
              </div>
              <div className="stat-card">
                <h3>Messages Sent</h3>
                <p className="stat-value">0</p>
              </div>
              <div className="stat-card">
                <h3>Active Sessions</h3>
                <p className="stat-value">0</p>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'workflows' && (
          <section className="tab-content">
            <h2>Workflows</h2>
            <button className="btn-primary">New Workflow</button>
            <div className="workflows-grid">
              <p>Loading workflows...</p>
            </div>
          </section>
        )}

        {activeTab === 'sessions' && (
          <section className="tab-content">
            <h2>Message Sessions</h2>
            <select>
              <option value="">All States</option>
              <option value="RUNNING">Running</option>
              <option value="COMPLETED">Completed</option>
            </select>
            <div className="sessions-list">
              <p>No sessions yet.</p>
            </div>
          </section>
        )}

        {activeTab === 'platforms' && (
          <section className="tab-content">
            <h2>Platforms</h2>
            <div className="platform-cards">
              <div className="platform-card">
                <h3>Instagram</h3>
                <p>Status: <strong>Enabled</strong></p>
                <button className="btn-secondary">Pause</button>
              </div>
              <div className="platform-card">
                <h3>Twitter</h3>
                <p>Status: <strong>Disabled</strong></p>
                <button className="btn-secondary">Enable</button>
              </div>
              <div className="platform-card">
                <h3>Telegram</h3>
                <p>Status: <strong>Disabled</strong></p>
                <button className="btn-secondary">Enable</button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

// Mount app (React 18, Babel CDN — no build step needed)
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

```javascript
// API wrapper. Stub: return empty/default values. Phase 2+: implement real calls.

export async function getWorkflows(platform) {
  // Stub: return []
  return [];
}

export async function getSessions(platform, state = null) {
  // Stub: return []
  return [];
}

export async function getStats(platform) {
  // Stub: return default stats
  return { triggers: 0, messages: 0 };
}

export async function getPlatforms() {
  // Stub: return instagram enabled
  return [{ name: 'instagram', enabled: true }];
}

export async function pauseBot(platform = 'all') {
  // Stub: return ok
  return { status: 'paused', platform };
}

export async function resumeBot(platform = 'all') {
  // Stub: return ok
  return { status: 'running', platform };
}

export async function createWorkflow(data) {
  // Stub: return new workflow
  return { id: 1, ...data };
}
```

- [ ] **Step 4: Write `frontend/styles.css`**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background-color: #f5f5f5;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  background: white;
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 24px;
}

.header select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.tabs {
  display: flex;
  gap: 10px;
  background: white;
  padding: 10px 20px;
  border-bottom: 1px solid #eee;
}

.tabs button {
  background: none;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.tabs button.active {
  border-bottom-color: #007bff;
  color: #007bff;
}

.tabs button:hover {
  color: #007bff;
}

.main {
  padding: 20px;
}

.tab-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.status-pills {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.pill {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.pill.running {
  background-color: #d4edda;
  color: #155724;
}

.pill.paused {
  background-color: #fff3cd;
  color: #856404;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  padding: 15px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 6px;
  text-align: center;
}

.stat-card h3 {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #007bff;
}

.btn-primary, .btn-secondary {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #007bff;
  color: white;
  margin-bottom: 15px;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #e9ecef;
  color: #333;
}

.btn-secondary:hover {
  background: #dee2e6;
}

.platform-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.platform-card {
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #fafafa;
}

.platform-card h3 {
  margin-bottom: 10px;
}

.platform-card p {
  margin-bottom: 15px;
  font-size: 14px;
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: add React frontend (single file, all stubbed)"
```

---

### Task 12: Test Fixtures & Stubs

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/test_keyword_matcher.py`
- Create: `tests/unit/platforms/__init__.py`
- Create: `tests/unit/platforms/test_instagram_adapter.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_workflow_repo.py`

- [ ] **Step 1: Write `tests/__init__.py`**

```python
# Tests package
```

- [ ] **Step 2: Write `tests/conftest.py`**

```python
import pytest
from db.database import Database

@pytest.fixture
def test_db():
    """Create temp test database."""
    db = Database("sqlite:///:memory:")
    db.run_migrations()
    yield db

@pytest.fixture
def mock_instagram_adapter():
    """Mock Instagram adapter for tests."""
    from platforms.instagram import InstagramAdapter
    return InstagramAdapter(account_id=999)
```

- [ ] **Step 3: Write `tests/unit/__init__.py`**

```python
# Unit tests package
```

- [ ] **Step 4: Write `tests/unit/test_keyword_matcher.py`**

```python
import pytest
from core.keyword_matcher import KeywordMatcher

def test_keyword_matcher_contains_match():
    """contains mode: keyword found in content → True."""
    matcher = KeywordMatcher()
    result = matcher.match("I want to detox my mind", "detox", "contains")
    assert result is True  # stub returns False — fix in Phase 2

def test_keyword_matcher_exact_match():
    """exact mode: content equals keyword exactly → True."""
    matcher = KeywordMatcher()
    result = matcher.match("detox", "detox", "exact")
    assert result is True  # stub returns False — fix in Phase 2

def test_keyword_matcher_no_match():
    """keyword not in content → False."""
    matcher = KeywordMatcher()
    result = matcher.match("hello world", "detox", "contains")
    assert result is False
```

- [ ] **Step 5: Write `tests/unit/platforms/__init__.py`**

```python
# Unit tests for platforms
```

- [ ] **Step 6: Write `tests/unit/platforms/test_instagram_adapter.py`**

```python
import pytest
from core.models import FollowStatus, Platform

def test_instagram_adapter_read_triggers_returns_empty(mock_instagram_adapter):
    """Stub adapter read_triggers should return []."""
    result = mock_instagram_adapter.read_triggers("post_123")
    assert result == []

def test_instagram_adapter_send_message_returns_true(mock_instagram_adapter):
    """Stub adapter send_message should return True."""
    result = mock_instagram_adapter.send_message("user_123", "hello")
    assert result is True

def test_instagram_adapter_check_follow_returns_not_following(mock_instagram_adapter):
    """Stub adapter check_follow should return NOT_FOLLOWING."""
    result = mock_instagram_adapter.check_follow("testuser")
    assert result == FollowStatus.NOT_FOLLOWING

def test_instagram_adapter_supports_follow_gate(mock_instagram_adapter):
    """Instagram should support follow gate."""
    result = mock_instagram_adapter.supports_follow_gate()
    assert result is True

def test_instagram_adapter_platform_is_instagram(mock_instagram_adapter):
    """Instagram adapter platform should be INSTAGRAM."""
    assert mock_instagram_adapter.platform == Platform.INSTAGRAM
```

- [ ] **Step 7: Write `tests/integration/__init__.py`**

```python
# Integration tests package
```

- [ ] **Step 8: Write `tests/integration/test_workflow_repo.py`**

```python
import pytest
from db.repositories.workflow_repo import WorkflowRepository

def test_workflow_repo_get_all_returns_empty(test_db):
    """Stub repo get_all should return []."""
    repo = WorkflowRepository(test_db.engine)
    result = repo.get_all("instagram")
    assert result == []

def test_workflow_repo_insert_returns_none(test_db):
    """Stub repo insert should return None for now."""
    repo = WorkflowRepository(test_db.engine)
    result = repo.insert("instagram", {"name": "test"})
    assert result is None
```

- [ ] **Step 9: Commit**

```bash
git add tests/
git commit -m "test: add test fixtures and stub unit/integration tests"
```

---

### Task 13: Verify Shell Build

**Files:** None to create (verification only)

- [ ] **Step 1: Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

- [ ] **Step 2: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests PASS (stubbed tests all pass)

- [ ] **Step 3: Check imports**

```bash
python -c "from config import settings; from core import models; from platforms import instagram; from workers import base_worker; from api import create_app; from db import database; print('✓ All imports OK')"
```

Expected: No import errors

- [ ] **Step 4: Start app (5 second check)**

```bash
timeout 5 python main.py || true
```

Expected: App starts, logs worker startup, exits after 5s (no crash)

- [ ] **Step 5: Run API health check**

```bash
python main.py &
APP_PID=$!
sleep 2
curl -s http://localhost:5000/api/workflows?platform=instagram | python -m json.tool
kill $APP_PID 2>/dev/null || true
```

Expected: Returns `{"workflows": [], "platform": "instagram"}` with 200 OK

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "shell: verify all imports, tests pass, API responds"
```

---

## Summary

**Shell complete when:**
- ✅ All 75+ files created
- ✅ All imports wired (no import errors)
- ✅ All tests pass (21+ stub tests green)
- ✅ All API routes return 200 OK
- ✅ React UI renders (Babel CDN — no build step needed)
- ✅ Workers start/stop without crash, platform injected via constructor
- ✅ DB migration runs (`001_init.sql` creates all tables via `run_migrations()`)
- ✅ `workflows.yaml` loads on startup (YamlLoader.sync() called in main.py)
- ✅ Commits frequent (one per layer, 13 total)

**Next:** Fill layers with real logic (Phase 2 plan coming after shell verified).

---

## Execution Options

Plan complete. Ready to build.

**Two paths:**

**1. Subagent-Driven (recommended)** — I dispatch fresh subagent per task, review output, fast iteration

**2. Inline Execution** — Execute all tasks here, step by step, with checkpoints

Which?
