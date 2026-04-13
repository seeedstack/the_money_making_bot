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
