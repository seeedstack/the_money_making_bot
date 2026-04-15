import pytest
from unittest.mock import Mock, patch
from core.models import FollowStatus, Platform
from platforms.instagram.adapter import InstagramAdapter


@pytest.fixture
def mock_instagram_adapter_with_client():
    """Mock Instagram adapter with mocked client."""
    with patch('platforms.instagram.adapter.InstagramClient') as mock_client_class:
        mock_client = Mock()
        mock_client.get_comments.return_value = []
        mock_client.send_dm.return_value = True
        mock_client.get_user.return_value = {"follower": False}
        mock_client_class.return_value = mock_client

        adapter = InstagramAdapter(account_id=999)
        # Ensure components use the mocked client
        adapter.comment_reader.client = mock_client
        adapter.dm_sender.client = mock_client
        adapter.follow_checker.client = mock_client
        return adapter


def test_instagram_adapter_read_triggers_returns_empty(mock_instagram_adapter_with_client):
    """Adapter read_triggers should return [] when no comments."""
    result = mock_instagram_adapter_with_client.read_triggers("post_123")
    assert result == []


def test_instagram_adapter_send_message_returns_true(mock_instagram_adapter_with_client):
    """Adapter send_message should return True on success."""
    result = mock_instagram_adapter_with_client.send_message("user_123", "hello")
    assert result is True


def test_instagram_adapter_check_follow_returns_not_following(mock_instagram_adapter_with_client):
    """Adapter check_follow should return NOT_FOLLOWING."""
    result = mock_instagram_adapter_with_client.check_follow("testuser")
    assert result == FollowStatus.NOT_FOLLOWING


def test_instagram_adapter_supports_follow_gate(mock_instagram_adapter_with_client):
    """Instagram should support follow gate."""
    result = mock_instagram_adapter_with_client.supports_follow_gate()
    assert result is True


def test_instagram_adapter_platform_is_instagram(mock_instagram_adapter_with_client):
    """Instagram adapter platform should be INSTAGRAM."""
    assert mock_instagram_adapter_with_client.platform == Platform.INSTAGRAM
