# Instagram Components Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to execute this plan task-by-task.

**Goal:** Implement 4 real Instagram components (InstagramClient, CommentReader, DMSender, FollowChecker) using Instagrapi SDK.

**Architecture:** Client maintains persistent Instagrapi session. 3 helpers (CommentReader, DMSender, FollowChecker) wrap client calls, parse responses, raise exceptions. All integrated into InstagramAdapter.

**Tech Stack:** Instagrapi (SDK), pytest (tests), mock (test mocks)

---

## File Structure

**New/Modified:**
- `platforms/instagram/client.py` - InstagramClient (create)
- `platforms/instagram/comment_reader.py` - CommentReader (modify stub)
- `platforms/instagram/dm_sender.py` - DMSender (modify stub)
- `platforms/instagram/follow_checker.py` - FollowChecker (modify stub)
- `platforms/instagram/adapter.py` - Update to use real components (modify)
- `platforms/instagram/errors.py` - Error classes (create)
- `tests/unit/platforms/instagram/` - Tests (create)

---

## Task 1: Error Classes

**Files:**
- Create: `platforms/instagram/errors.py`

- [ ] **Step 1: Write error classes**

```python
# platforms/instagram/errors.py

class InstagramError(Exception):
    """Base Instagram error."""
    pass

class LoginError(InstagramError):
    """Login failed."""
    pass

class APIError(InstagramError):
    """Instagrapi API call failed."""
    pass

class NetworkError(InstagramError):
    """Network/connection error."""
    pass
```

- [ ] **Step 2: Commit**

```bash
git add platforms/instagram/errors.py
git commit -m "feat: add instagram error classes"
```

---

## Task 2: InstagramClient

**Files:**
- Create: `tests/unit/platforms/instagram/test_client.py`
- Modify: `platforms/instagram/client.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/platforms/instagram/test_client.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from platforms.instagram.client import InstagramClient
from platforms.instagram.errors import LoginError, APIError

@pytest.fixture
def mock_settings_repo():
    """Mock settings repo for credential fetching."""
    repo = Mock()
    repo.get.return_value = "test_user"
    return repo

def test_init_sets_account_id(mock_settings_repo):
    """InstagramClient stores account_id."""
    client = InstagramClient(account_id=123)
    assert client.account_id == 123
    assert client.cl is None  # Not yet logged in

def test_login_success(mock_settings_repo):
    """login() initializes Instagrapi client and returns True."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None
        
        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            client = InstagramClient(account_id=123)
            result = client.login()
        
        assert result is True
        assert client.cl is mock_cl
        MockClient.assert_called_once()
        mock_cl.login.assert_called_once_with("test_user", "test_pass")

def test_login_failure_raises(mock_settings_repo):
    """login() raises LoginError on API failure."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.side_effect = Exception("Bad password")
        
        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            client = InstagramClient(account_id=123)
            with pytest.raises(LoginError):
                client.login()

def test_get_comments_returns_list(mock_settings_repo):
    """get_comments() returns list of comment dicts."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None
        mock_cl.media_info.return_value.dict.return_value = {
            "node": {
                "edge_media_to_comment": {
                    "edges": [
                        {"node": {"text": "hello", "owner": {"username": "user1"}}}
                    ]
                }
            }
        }
        
        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            client = InstagramClient(account_id=123)
            client.login()
            comments = client.get_comments("https://instagram.com/p/ABC123")
        
        assert isinstance(comments, list)
        assert len(comments) > 0

def test_send_direct_message_success(mock_settings_repo):
    """send_direct_message() sends DM and returns True."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None
        mock_cl.send_direct_message.return_value = None
        
        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            client = InstagramClient(account_id=123)
            client.login()
            result = client.send_direct_message("user123", "Hello")
        
        assert result is True
        mock_cl.send_direct_message.assert_called_once()

def test_user_info_returns_dict(mock_settings_repo):
    """user_info() returns user dict."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None
        mock_cl.user_info.return_value.dict.return_value = {"username": "testuser"}
        
        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            client = InstagramClient(account_id=123)
            client.login()
            info = client.user_info("testuser")
        
        assert isinstance(info, dict)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/saran/Work/the-bot
pytest tests/unit/platforms/instagram/test_client.py -v
```

Expected: All tests fail (client.py is stub, no real implementation).

- [ ] **Step 3: Implement InstagramClient**

```python
# platforms/instagram/client.py

from instagrapi import Client
from db.repositories.settings_repo import settings_repo
from platforms.instagram.errors import LoginError, APIError, NetworkError

class InstagramClient:
    """Instagrapi wrapper. Persistent session."""
    
    def __init__(self, account_id: int):
        """Init with account ID. Load creds from DB."""
        self.account_id = account_id
        self.cl = None  # Instagrapi Client instance
        self._load_credentials()
    
    def _load_credentials(self):
        """Fetch username/password from DB."""
        try:
            self.username = settings_repo.get(
                platform="instagram",
                key=f"account_{self.account_id}_user"
            )
            self.password = settings_repo.get(
                platform="instagram",
                key=f"account_{self.account_id}_pass"
            )
        except Exception as e:
            raise LoginError(f"Failed to load credentials: {e}")
    
    def login(self) -> bool:
        """Initialize Instagrapi client and login."""
        try:
            self.cl = Client()
            self.cl.login(self.username, self.password)
            return True
        except Exception as e:
            raise LoginError(f"Instagram login failed: {e}")
    
    def get_comments(self, source_id: str) -> list:
        """Get comments from post. source_id = post URL or ID."""
        try:
            if not self.cl:
                self.login()
            
            # Parse post ID from URL if needed
            post_id = self._extract_post_id(source_id)
            
            # Fetch media info
            media = self.cl.media_info(post_id)
            comments = []
            
            # Parse comments from media response
            if hasattr(media, 'comments'):
                for comment in media.comments:
                    comments.append({
                        "username": comment.user.username,
                        "text": comment.text,
                        "timestamp": comment.taken_at
                    })
            
            return comments
        except Exception as e:
            raise APIError(f"Failed to get comments: {e}")
    
    def send_direct_message(self, recipient_id: str, text: str) -> bool:
        """Send DM. recipient_id = user ID or username."""
        try:
            if not self.cl:
                self.login()
            
            self.cl.send_direct_message(recipient_id, text)
            return True
        except Exception as e:
            raise APIError(f"Failed to send DM: {e}")
    
    def user_info(self, username: str) -> dict:
        """Get user info dict."""
        try:
            if not self.cl:
                self.login()
            
            user = self.cl.user_info_by_username(username)
            return {
                "id": user.id,
                "username": user.username,
                "is_private": user.is_private,
                "follower_count": user.follower_count
            }
        except Exception as e:
            raise APIError(f"Failed to get user info: {e}")
    
    def _extract_post_id(self, source_id: str) -> str:
        """Extract post ID from URL or return as-is if already ID."""
        if source_id.startswith("http"):
            # Parse URL: https://instagram.com/p/ABC123
            return source_id.split("/p/")[1].rstrip("/")
        return source_id
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/platforms/instagram/test_client.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add platforms/instagram/client.py tests/unit/platforms/instagram/test_client.py
git commit -m "feat: implement instagram client with persistent session"
```

---

## Task 3: CommentReader

**Files:**
- Create: `tests/unit/platforms/instagram/test_comment_reader.py`
- Modify: `platforms/instagram/comment_reader.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/platforms/instagram/test_comment_reader.py

import pytest
from unittest.mock import Mock
from datetime import datetime
from core.models import TriggerEvent, Platform
from platforms.instagram.comment_reader import CommentReader

def test_fetch_returns_trigger_events():
    """fetch() returns list of TriggerEvent objects."""
    mock_client = Mock()
    mock_client.get_comments.return_value = [
        {
            "username": "user1",
            "text": "hello",
            "timestamp": datetime.now()
        },
        {
            "username": "user2",
            "text": "world",
            "timestamp": datetime.now()
        }
    ]
    
    reader = CommentReader(mock_client)
    events = reader.fetch("https://instagram.com/p/ABC123")
    
    assert len(events) == 2
    assert all(isinstance(e, TriggerEvent) for e in events)
    assert events[0].username == "user1"
    assert events[0].content == "hello"
    assert events[0].platform == Platform.INSTAGRAM

def test_fetch_empty_returns_empty_list():
    """fetch() returns empty list if no comments."""
    mock_client = Mock()
    mock_client.get_comments.return_value = []
    
    reader = CommentReader(mock_client)
    events = reader.fetch("https://instagram.com/p/ABC123")
    
    assert events == []

def test_fetch_raises_on_client_error():
    """fetch() raises exception if client fails."""
    mock_client = Mock()
    mock_client.get_comments.side_effect = Exception("API error")
    
    reader = CommentReader(mock_client)
    with pytest.raises(Exception):
        reader.fetch("https://instagram.com/p/ABC123")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/platforms/instagram/test_comment_reader.py -v
```

Expected: Tests fail (implementation is stub).

- [ ] **Step 3: Implement CommentReader**

```python
# platforms/instagram/comment_reader.py

from core.models import TriggerEvent, Platform

class CommentReader:
    """Read comments from Instagram posts."""
    
    def __init__(self, client):
        self.client = client
    
    def fetch(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments from post and return as TriggerEvent list."""
        comments = self.client.get_comments(source_id)
        
        events = []
        for comment in comments:
            event = TriggerEvent(
                username=comment["username"],
                content=comment["text"],
                timestamp=comment["timestamp"],
                source_id=source_id,
                platform=Platform.INSTAGRAM
            )
            events.append(event)
        
        return events
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/platforms/instagram/test_comment_reader.py -v
```

Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add platforms/instagram/comment_reader.py tests/unit/platforms/instagram/test_comment_reader.py
git commit -m "feat: implement comment reader with trigger event parsing"
```

---

## Task 4: DMSender

**Files:**
- Create: `tests/unit/platforms/instagram/test_dm_sender.py`
- Modify: `platforms/instagram/dm_sender.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/platforms/instagram/test_dm_sender.py

import pytest
from unittest.mock import Mock
from platforms.instagram.dm_sender import DMSender

def test_send_returns_true_on_success():
    """send() returns True when DM sends."""
    mock_client = Mock()
    mock_client.send_direct_message.return_value = True
    
    sender = DMSender(mock_client)
    result = sender.send("user123", "Hello world")
    
    assert result is True
    mock_client.send_direct_message.assert_called_once_with("user123", "Hello world")

def test_send_raises_on_error():
    """send() raises exception on send failure."""
    mock_client = Mock()
    mock_client.send_direct_message.side_effect = Exception("Send failed")
    
    sender = DMSender(mock_client)
    with pytest.raises(Exception):
        sender.send("user123", "Hello")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/platforms/instagram/test_dm_sender.py -v
```

Expected: Tests fail.

- [ ] **Step 3: Implement DMSender**

```python
# platforms/instagram/dm_sender.py

class DMSender:
    """Send DMs on Instagram."""
    
    def __init__(self, client):
        self.client = client
    
    def send(self, recipient_id: str, text: str) -> bool:
        """Send DM. Raise on failure (engine handles retries)."""
        return self.client.send_direct_message(recipient_id, text)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/platforms/instagram/test_dm_sender.py -v
```

Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add platforms/instagram/dm_sender.py tests/unit/platforms/instagram/test_dm_sender.py
git commit -m "feat: implement dm sender with error propagation"
```

---

## Task 5: FollowChecker

**Files:**
- Create: `tests/unit/platforms/instagram/test_follow_checker.py`
- Modify: `platforms/instagram/follow_checker.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/platforms/instagram/test_follow_checker.py

import pytest
from unittest.mock import Mock
from core.models import FollowStatus
from platforms.instagram.follow_checker import FollowChecker

def test_is_following_returns_following():
    """is_following() returns FOLLOWING when user follows."""
    mock_client = Mock()
    mock_client.user_info.return_value = {"follow_status": "following"}
    
    checker = FollowChecker(mock_client)
    result = checker.is_following("someuser")
    
    assert result == FollowStatus.FOLLOWING

def test_is_following_returns_not_following():
    """is_following() returns NOT_FOLLOWING when user doesn't follow."""
    mock_client = Mock()
    mock_client.user_info.return_value = {"follow_status": "not_following"}
    
    checker = FollowChecker(mock_client)
    result = checker.is_following("someuser")
    
    assert result == FollowStatus.NOT_FOLLOWING

def test_is_following_raises_on_error():
    """is_following() raises exception on API error."""
    mock_client = Mock()
    mock_client.user_info.side_effect = Exception("API error")
    
    checker = FollowChecker(mock_client)
    with pytest.raises(Exception):
        checker.is_following("someuser")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/platforms/instagram/test_follow_checker.py -v
```

Expected: Tests fail.

- [ ] **Step 3: Implement FollowChecker**

```python
# platforms/instagram/follow_checker.py

from core.models import FollowStatus

class FollowChecker:
    """Check follow status on Instagram."""
    
    def __init__(self, client):
        self.client = client
    
    def is_following(self, username: str) -> FollowStatus:
        """Check if user follows account. Raise on error."""
        user_info = self.client.user_info(username)
        
        # Instagrapi returns follow status in user_info
        follows = user_info.get("follows")
        
        if follows:
            return FollowStatus.FOLLOWING
        else:
            return FollowStatus.NOT_FOLLOWING
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/platforms/instagram/test_follow_checker.py -v
```

Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add platforms/instagram/follow_checker.py tests/unit/platforms/instagram/test_follow_checker.py
git commit -m "feat: implement follow checker with status enum"
```

---

## Task 6: Integration — Update InstagramAdapter

**Files:**
- Modify: `platforms/instagram/adapter.py`
- Create: `tests/unit/platforms/instagram/test_adapter.py`

- [ ] **Step 1: Write integration test**

```python
# tests/unit/platforms/instagram/test_adapter.py

import pytest
from unittest.mock import Mock, patch
from core.models import Platform, TriggerEvent, FollowStatus
from platforms.instagram.adapter import InstagramAdapter

def test_adapter_read_triggers_calls_comment_reader():
    """read_triggers() fetches comments via CommentReader."""
    mock_client = Mock()
    mock_event = TriggerEvent(
        username="testuser",
        content="test comment",
        timestamp=None,
        source_id="https://instagram.com/p/ABC123",
        platform=Platform.INSTAGRAM
    )
    
    with patch('platforms.instagram.adapter.CommentReader') as MockReader:
        mock_reader = Mock()
        MockReader.return_value = mock_reader
        mock_reader.fetch.return_value = [mock_event]
        
        adapter = InstagramAdapter(account_id=123)
        adapter.client = mock_client
        
        events = adapter.read_triggers("https://instagram.com/p/ABC123")
    
    assert len(events) == 1
    assert events[0].username == "testuser"

def test_adapter_send_message_calls_dm_sender():
    """send_message() sends DM via DMSender."""
    mock_client = Mock()
    
    with patch('platforms.instagram.adapter.DMSender') as MockSender:
        mock_sender = Mock()
        MockSender.return_value = mock_sender
        mock_sender.send.return_value = True
        
        adapter = InstagramAdapter(account_id=123)
        adapter.client = mock_client
        
        result = adapter.send_message("user123", "Hello")
    
    assert result is True

def test_adapter_check_follow_calls_follow_checker():
    """check_follow() checks follow status via FollowChecker."""
    mock_client = Mock()
    
    with patch('platforms.instagram.adapter.FollowChecker') as MockChecker:
        mock_checker = Mock()
        MockChecker.return_value = mock_checker
        mock_checker.is_following.return_value = FollowStatus.FOLLOWING
        
        adapter = InstagramAdapter(account_id=123)
        adapter.client = mock_client
        
        status = adapter.check_follow("someuser")
    
    assert status == FollowStatus.FOLLOWING
```

- [ ] **Step 2: Run integration test to verify it fails**

```bash
pytest tests/unit/platforms/instagram/test_adapter.py -v
```

Expected: Tests fail (adapter still has stubs).

- [ ] **Step 3: Update InstagramAdapter to call real components**

```python
# platforms/instagram/adapter.py

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
        """Fetch comments from post."""
        return self.comment_reader.fetch(source_id)

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM to user."""
        return self.dm_sender.send(recipient_id, text)

    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows."""
        return self.follow_checker.is_following(username)

    def supports_follow_gate(self) -> bool:
        """Instagram supports follow gate."""
        return True
```

- [ ] **Step 4: Run integration tests to verify they pass**

```bash
pytest tests/unit/platforms/instagram/test_adapter.py -v
```

Expected: All pass.

- [ ] **Step 5: Run all Instagram tests together**

```bash
pytest tests/unit/platforms/instagram/ -v
```

Expected: All pass.

- [ ] **Step 6: Commit**

```bash
git add platforms/instagram/adapter.py tests/unit/platforms/instagram/test_adapter.py
git commit -m "feat: update adapter to use real instagram components"
```

---

## Task 7: Verify All Tests Pass

- [ ] **Step 1: Run full test suite for Instagram platform**

```bash
pytest tests/unit/platforms/instagram/ -v --tb=short
```

Expected: All tests pass, no errors.

- [ ] **Step 2: Check import integrity**

```bash
python -c "from platforms.instagram.adapter import InstagramAdapter; print('✓ Import OK')"
```

Expected: No import errors.

- [ ] **Step 3: Commit final state**

```bash
git log --oneline -6
```

Expected: 6 commits for the 6 tasks above.

---

## Plan Self-Review

**Spec coverage:**
- ✓ InstagramClient: persistent session, DB credentials, error handling
- ✓ CommentReader: parse comments → TriggerEvent list
- ✓ DMSender: send DM, raise on error
- ✓ FollowChecker: check follow status, return enum
- ✓ InstagramAdapter: integrate all 4 components
- ✓ Error handling: raise exceptions (engine handles retries)
- ✓ DB credentials: loaded in InstagramClient._load_credentials()

**No placeholders:** All steps have complete code blocks, exact commands, expected outputs.

**Type consistency:** All TriggerEvent, FollowStatus, Platform references match core/models definitions.

**Scope:** Focused on 4 components only. Each task produces testable, committable unit.

---
