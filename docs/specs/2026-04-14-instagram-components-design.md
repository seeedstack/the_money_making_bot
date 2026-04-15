# Instagram Components Design
**Date:** 2026-04-14  
**Status:** Design approved  
**Scope:** InstagramClient, CommentReader, DMSender, FollowChecker

---

## Overview
Implement 4 real Instagram integration components using Instagrapi SDK. Each component raises exceptions on error; engine handles retry logic.

---

## InstagramClient

**Purpose:** Session factory. Maintain persistent Instagrapi client session.

**Interface:**
```python
class InstagramClient:
    def __init__(self, account_id: int)
    def login() -> bool
    def get_comments(source_id: str) -> list[dict]
    def send_dm(recipient_id: str, text: str) -> bool
    def get_user(username: str) -> dict
```

**Behavior:**
- Load credentials from DB (account_id → username/password) on init
- Initialize Instagrapi client on first login() call
- Keep session alive across calls (thread-safe via lock if needed)
- Auto-reconnect on session expire (lazy reconnect on next call)
- Raise LoginError, NetworkError, APIError on failures

**Storage:** Credentials fetched from DB via settings_repo (platform=instagram, key=account_<id>_user, account_<id>_pass)

---

## CommentReader

**Purpose:** Parse post comments into TriggerEvent objects.

**Interface:**
```python
class CommentReader:
    def __init__(self, client: InstagramClient)
    def fetch(source_id: str) -> list[TriggerEvent]
```

**Behavior:**
- source_id = Instagram post URL (format: https://instagram.com/p/ABC123)
- Fetch comments via client.get_comments() (handles pagination internally)
- Parse each comment: extract username, text, timestamp
- Build TriggerEvent per comment (username, content, timestamp, source_id)
- Return list of ALL comments (not paginated to caller)
- Raise on fetch/parse errors (engine retries)

**TriggerEvent format:** (from core/models)
```python
@dataclass
class TriggerEvent:
    username: str
    content: str
    timestamp: datetime
    source_id: str
    platform: Platform
```

---

## DMSender

**Purpose:** Send DMs via Instagram.

**Interface:**
```python
class DMSender:
    def __init__(self, client: InstagramClient)
    def send(recipient_id: str, text: str) -> bool
```

**Behavior:**
- recipient_id = Instagram user ID (numeric, preferred) or username (fallback)
- Send DM via client.send_dm()
- Return True on success
- Raise on send failure (engine retries)
- No rate limiting here (engine.rate_limiter handles it)

---

## FollowChecker

**Purpose:** Check follow status.

**Interface:**
```python
class FollowChecker:
    def __init__(self, client: InstagramClient)
    def is_following(username: str) -> FollowStatus
```

**Behavior:**
- Check if username follows account via client.get_user()
- Return FollowStatus enum: FOLLOWING | NOT_FOLLOWING | UNKNOWN
- UNKNOWN = API returned unexpected state
- Raise on check errors (engine retries)

**FollowStatus enum:** (from core/models)
```python
class FollowStatus(Enum):
    FOLLOWING = "following"
    NOT_FOLLOWING = "not_following"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"  # Telegram only
```

---

## Architecture

```
InstagramAdapter
  ├── InstagramClient (session factory)
  │   └── Instagrapi client (single persistent connection)
  │
  ├── CommentReader (client) → read_triggers()
  ├── DMSender (client) → send_message()
  └── FollowChecker (client) → check_follow()
```

All 4 components share single InstagramClient instance. No cross-component state.

---

## Error Handling

- InstagramClient: Raise LoginError, NetworkError, APIError
- CommentReader: Raise CommentFetchError (wraps InstagramClient exceptions)
- DMSender: Raise DMSendError (wraps InstagramClient exceptions)
- FollowChecker: Raise FollowCheckError (wraps InstagramClient exceptions)

Engine's step_executor catches all exceptions → logs → retries via pending_follow_checks or message_sessions queue.

---

## DB Dependencies

- **settings_repo:** Fetch account_<id>_user, account_<id>_pass for InstagramClient.login()
- No writes from these components (read-only)

---

## Testing

Unit tests mock InstagramClient. No real API calls in tests.

Integration tests use mock Instagrapi client or sandbox account (if available).

---

## Dependencies

- Instagrapi: `pip install instagrapi`
- Core models: TriggerEvent, FollowStatus, Platform (already defined)
- Core interfaces: PlatformAdapter (already defined)

---

## Success Criteria

- [x] Design approved
- [ ] All 4 components implement interfaces
- [ ] Unit tests mock InstagramClient
- [ ] InstagramAdapter methods call components correctly
- [ ] Error handling bubbles exceptions to engine
- [ ] Credentials loaded from DB (not hardcoded)
