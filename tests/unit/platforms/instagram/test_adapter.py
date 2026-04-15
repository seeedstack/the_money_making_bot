# tests/unit/platforms/instagram/test_adapter.py

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from core.models import Platform, FollowStatus, TriggerEvent
from platforms.instagram.adapter import InstagramAdapter


@pytest.fixture
def mock_client():
    """Mock InstagramClient for testing."""
    client = Mock()
    client.get_comments.return_value = []
    client.send_dm.return_value = True
    client.get_user.return_value = {"follower": True}
    return client


@pytest.fixture
def adapter_with_mock_client(mock_client):
    """InstagramAdapter with mocked client."""
    with patch('platforms.instagram.adapter.InstagramClient', return_value=mock_client):
        adapter = InstagramAdapter(account_id=999)
        # Replace the client with our mock
        adapter.client = mock_client
        # Also need to update the components' client refs
        adapter.comment_reader.client = mock_client
        adapter.dm_sender.client = mock_client
        adapter.follow_checker.client = mock_client
        return adapter


class TestInstagramAdapterIntegration:
    """Test InstagramAdapter integration with all components."""

    def test_read_triggers_calls_comment_reader(self, adapter_with_mock_client):
        """read_triggers() calls comment_reader.fetch()."""
        now = datetime.now()
        adapter_with_mock_client.client.get_comments.return_value = [
            {
                "username": "testuser",
                "text": "hello comment",
                "timestamp": now
            }
        ]

        result = adapter_with_mock_client.read_triggers("https://instagram.com/p/ABC123")

        assert len(result) == 1
        assert result[0].username == "testuser"
        assert result[0].content == "hello comment"
        assert result[0].platform == Platform.INSTAGRAM

    def test_read_triggers_returns_empty_list_when_no_comments(self, adapter_with_mock_client):
        """read_triggers() returns empty list when no comments."""
        adapter_with_mock_client.client.get_comments.return_value = []

        result = adapter_with_mock_client.read_triggers("https://instagram.com/p/ABC123")

        assert result == []

    def test_send_message_calls_dm_sender(self, adapter_with_mock_client):
        """send_message() calls dm_sender.send()."""
        adapter_with_mock_client.client.send_dm.return_value = True

        result = adapter_with_mock_client.send_message("user123", "Hello world")

        assert result is True
        adapter_with_mock_client.client.send_dm.assert_called_once_with("user123", "Hello world")

    def test_send_message_propagates_dm_sender_exceptions(self, adapter_with_mock_client):
        """send_message() propagates exceptions from dm_sender."""
        from platforms.instagram.errors import APIError
        adapter_with_mock_client.client.send_dm.side_effect = APIError("Send failed")

        with pytest.raises(APIError):
            adapter_with_mock_client.send_message("user123", "Hello")

    def test_check_follow_calls_follow_checker(self, adapter_with_mock_client):
        """check_follow() calls follow_checker.is_following()."""
        adapter_with_mock_client.client.get_user.return_value = {"follower": True}

        result = adapter_with_mock_client.check_follow("testuser")

        assert result == FollowStatus.FOLLOWING
        adapter_with_mock_client.client.get_user.assert_called_once_with("testuser")

    def test_check_follow_returns_not_following(self, adapter_with_mock_client):
        """check_follow() returns NOT_FOLLOWING when user doesn't follow."""
        adapter_with_mock_client.client.get_user.return_value = {"follower": False}

        result = adapter_with_mock_client.check_follow("testuser")

        assert result == FollowStatus.NOT_FOLLOWING

    def test_check_follow_returns_not_applicable(self, adapter_with_mock_client):
        """check_follow() returns NOT_APPLICABLE when follower field missing."""
        adapter_with_mock_client.client.get_user.return_value = {"id": 123}

        result = adapter_with_mock_client.check_follow("testuser")

        assert result == FollowStatus.NOT_APPLICABLE

    def test_check_follow_propagates_follow_checker_exceptions(self, adapter_with_mock_client):
        """check_follow() propagates exceptions from follow_checker."""
        adapter_with_mock_client.client.get_user.side_effect = Exception("API error")

        with pytest.raises(Exception):
            adapter_with_mock_client.check_follow("testuser")

    def test_adapter_has_correct_platform(self, adapter_with_mock_client):
        """InstagramAdapter.platform should be INSTAGRAM."""
        assert adapter_with_mock_client.platform == Platform.INSTAGRAM

    def test_adapter_supports_follow_gate(self, adapter_with_mock_client):
        """InstagramAdapter supports follow gate."""
        assert adapter_with_mock_client.supports_follow_gate() is True

    def test_adapter_initializes_all_components(self, adapter_with_mock_client):
        """InstagramAdapter initializes all 4 components."""
        assert adapter_with_mock_client.comment_reader is not None
        assert adapter_with_mock_client.dm_sender is not None
        assert adapter_with_mock_client.follow_checker is not None
        assert adapter_with_mock_client.client is not None

    def test_read_triggers_with_multiple_comments(self, adapter_with_mock_client):
        """read_triggers() handles multiple comments correctly."""
        now = datetime.now()
        adapter_with_mock_client.client.get_comments.return_value = [
            {
                "username": "user1",
                "text": "first comment",
                "timestamp": now
            },
            {
                "username": "user2",
                "text": "second comment",
                "timestamp": now
            },
            {
                "username": "user3",
                "text": "third comment",
                "timestamp": now
            }
        ]

        result = adapter_with_mock_client.read_triggers("post_id")

        assert len(result) == 3
        assert result[0].username == "user1"
        assert result[1].username == "user2"
        assert result[2].username == "user3"

    def test_send_message_with_special_characters(self, adapter_with_mock_client):
        """send_message() handles special characters in message text."""
        adapter_with_mock_client.client.send_dm.return_value = True

        text = "Hey! 🎉 Check this: https://example.com"
        result = adapter_with_mock_client.send_message("user123", text)

        assert result is True
        adapter_with_mock_client.client.send_dm.assert_called_once_with("user123", text)

    def test_read_triggers_propagates_comment_reader_exceptions(self, adapter_with_mock_client):
        """read_triggers() propagates exceptions from comment_reader."""
        adapter_with_mock_client.client.get_comments.side_effect = Exception("API error")

        with pytest.raises(Exception):
            adapter_with_mock_client.read_triggers("post_id")
