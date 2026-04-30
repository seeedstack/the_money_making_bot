# tests/unit/platforms/twitter/test_adapter.py

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from app.core.models import Platform, FollowStatus, TriggerEvent
from app.adapters.twitter.adapter import TwitterAdapter


@pytest.fixture
def mock_client():
    """Mock TwitterClient for testing."""
    client = Mock()
    client.get_tweet_replies.return_value = []
    client.send_dm.return_value = True
    client.get_user.return_value = {"followers_count": 100}
    return client


@pytest.fixture
def adapter_with_mock_client(mock_client):
    """TwitterAdapter with mocked client."""
    with patch('platforms.twitter.adapter.TwitterClient', return_value=mock_client):
        adapter = TwitterAdapter(account_id=999)
        # Replace the client with our mock
        adapter.client = mock_client
        # Also need to update the components' client refs
        adapter.reply_reader.client = mock_client
        adapter.dm_sender.client = mock_client
        adapter.follow_checker.client = mock_client
        return adapter


class TestTwitterAdapterIntegration:
    """Test TwitterAdapter integration with all components."""

    def test_read_triggers_calls_reply_reader(self, adapter_with_mock_client):
        """read_triggers() calls reply_reader.fetch()."""
        now = datetime.now()
        adapter_with_mock_client.client.get_tweet_replies.return_value = [
            {
                "id": "111",
                "username": "testuser",
                "author_id": "123",
                "text": "hello reply",
                "created_at": now.isoformat()
            }
        ]

        result = adapter_with_mock_client.read_triggers("1234567890")

        assert len(result) == 1
        assert result[0].username == "testuser"
        assert result[0].content == "hello reply"
        assert result[0].platform == Platform.TWITTER

    def test_read_triggers_returns_empty_list_when_no_replies(self, adapter_with_mock_client):
        """read_triggers() returns empty list when no replies."""
        adapter_with_mock_client.client.get_tweet_replies.return_value = []

        result = adapter_with_mock_client.read_triggers("1234567890")

        assert result == []

    def test_read_triggers_with_invalid_source_id(self, adapter_with_mock_client):
        """read_triggers() handles None source_id gracefully."""
        result = adapter_with_mock_client.read_triggers(None)

        assert result == []

    def test_read_triggers_with_empty_source_id(self, adapter_with_mock_client):
        """read_triggers() handles empty source_id gracefully."""
        result = adapter_with_mock_client.read_triggers("")

        assert result == []

    def test_send_message_calls_dm_sender(self, adapter_with_mock_client):
        """send_message() calls dm_sender.send()."""
        adapter_with_mock_client.client.send_dm.return_value = True

        result = adapter_with_mock_client.send_message("user_123", "Hello world")

        assert result is True
        adapter_with_mock_client.client.send_dm.assert_called_once_with("user_123", "Hello world")

    def test_send_message_propagates_dm_sender_exceptions(self, adapter_with_mock_client):
        """send_message() propagates exceptions from dm_sender."""
        from app.adapters.twitter.errors import APIError
        adapter_with_mock_client.client.send_dm.side_effect = APIError("Send failed")

        with pytest.raises(APIError):
            adapter_with_mock_client.send_message("user_123", "Hello")

    def test_check_follow_calls_follow_checker(self, adapter_with_mock_client):
        """check_follow() calls follow_checker.is_following()."""
        adapter_with_mock_client.client.get_user.return_value = {"followers_count": 100}

        result = adapter_with_mock_client.check_follow("testuser")

        assert result == FollowStatus.FOLLOWING
        adapter_with_mock_client.client.get_user.assert_called_once_with("testuser")

    def test_check_follow_returns_unknown_on_missing_followers(self, adapter_with_mock_client):
        """check_follow() returns UNKNOWN when followers_count missing."""
        adapter_with_mock_client.client.get_user.return_value = {"id": "123"}

        result = adapter_with_mock_client.check_follow("testuser")

        assert result == FollowStatus.UNKNOWN

    def test_check_follow_propagates_follow_checker_exceptions(self, adapter_with_mock_client):
        """check_follow() propagates exceptions from follow_checker."""
        adapter_with_mock_client.client.get_user.side_effect = Exception("API error")

        with pytest.raises(Exception):
            adapter_with_mock_client.check_follow("testuser")

    def test_adapter_has_correct_platform(self, adapter_with_mock_client):
        """TwitterAdapter.platform should be TWITTER."""
        assert adapter_with_mock_client.platform == Platform.TWITTER

    def test_adapter_supports_follow_gate(self, adapter_with_mock_client):
        """TwitterAdapter supports follow gate."""
        assert adapter_with_mock_client.supports_follow_gate() is True

    def test_adapter_initializes_all_components(self, adapter_with_mock_client):
        """TwitterAdapter initializes all 4 components."""
        assert adapter_with_mock_client.reply_reader is not None
        assert adapter_with_mock_client.dm_sender is not None
        assert adapter_with_mock_client.follow_checker is not None
        assert adapter_with_mock_client.client is not None

    def test_read_triggers_with_multiple_replies(self, adapter_with_mock_client):
        """read_triggers() handles multiple replies correctly."""
        now = datetime.now()
        adapter_with_mock_client.client.get_tweet_replies.return_value = [
            {
                "id": "111",
                "username": "user1",
                "author_id": "1",
                "text": "first reply",
                "created_at": now.isoformat()
            },
            {
                "id": "222",
                "username": "user2",
                "author_id": "2",
                "text": "second reply",
                "created_at": now.isoformat()
            },
            {
                "id": "333",
                "username": "user3",
                "author_id": "3",
                "text": "third reply",
                "created_at": now.isoformat()
            }
        ]

        result = adapter_with_mock_client.read_triggers("1234567890")

        assert len(result) == 3
        assert result[0].username == "user1"
        assert result[1].username == "user2"
        assert result[2].username == "user3"

    def test_send_message_with_special_characters(self, adapter_with_mock_client):
        """send_message() handles special characters in message text."""
        adapter_with_mock_client.client.send_dm.return_value = True

        text = "Hey! 🔥 Check this: https://example.com"
        result = adapter_with_mock_client.send_message("user_123", text)

        assert result is True
        adapter_with_mock_client.client.send_dm.assert_called_once_with("user_123", text)

    def test_read_triggers_propagates_reply_reader_exceptions(self, adapter_with_mock_client):
        """read_triggers() propagates exceptions from reply_reader."""
        adapter_with_mock_client.client.get_tweet_replies.side_effect = Exception("API error")

        with pytest.raises(Exception):
            adapter_with_mock_client.read_triggers("tweet_id")
