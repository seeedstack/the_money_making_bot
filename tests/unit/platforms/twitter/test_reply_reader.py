# tests/unit/platforms/twitter/test_reply_reader.py

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from platforms.twitter.reply_reader import ReplyReader
from core.models.trigger import TriggerEvent
from core.models.platform import Platform


@pytest.fixture
def mock_twitter_client():
    """Mock TwitterClient for reply reader testing."""
    client = Mock()
    return client


@pytest.fixture
def reply_reader(mock_twitter_client):
    """Create ReplyReader instance with mocked client."""
    with patch('platforms.twitter.reply_reader.TwitterClient') as MockClient:
        MockClient.return_value = mock_twitter_client
        reader = ReplyReader(account_id=123)
        reader.client = mock_twitter_client
        return reader


def test_fetch_with_valid_tweet_id_returns_trigger_events(reply_reader, mock_twitter_client):
    """fetch() parses tweet replies and returns TriggerEvent list."""
    tweet_id = "1234567890"

    # Mock reply data from TwitterClient
    mock_twitter_client.get_tweet_replies.return_value = [
        {
            "id": 111,
            "username": "user1",
            "text": "This is a test reply",
            "created_at": "2025-02-01T10:00:00Z"
        },
        {
            "id": 222,
            "username": "user2",
            "text": "Another reply here",
            "created_at": "2025-02-01T10:05:00Z"
        }
    ]

    trigger_events = reply_reader.fetch(tweet_id)

    assert isinstance(trigger_events, list)
    assert len(trigger_events) == 2
    assert all(isinstance(event, TriggerEvent) for event in trigger_events)


def test_fetch_parses_username_text_timestamp(reply_reader, mock_twitter_client):
    """fetch() correctly parses username, text, and timestamp from reply dict."""
    tweet_id = "1234567890"

    mock_twitter_client.get_tweet_replies.return_value = [
        {
            "id": 111,
            "username": "alice",
            "text": "Hello world",
            "created_at": "2025-02-01T10:30:45Z"
        }
    ]

    events = reply_reader.fetch(tweet_id)

    assert len(events) == 1
    event = events[0]
    assert event.username == "alice"
    assert event.content == "Hello world"
    assert isinstance(event.detected_at, datetime)
    assert event.platform == Platform.TWITTER.value


def test_fetch_with_defensive_dict_access(reply_reader, mock_twitter_client):
    """fetch() uses .get() with defaults for missing dict keys."""
    tweet_id = "1234567890"

    # Missing some optional keys
    mock_twitter_client.get_tweet_replies.return_value = [
        {
            "id": 111,
            "username": "bob",
            # Missing "text" key
            "created_at": "2025-02-01T10:00:00Z"
        },
        {
            "username": "charlie",
            "text": "Good reply",
            # Missing "created_at" key
        }
    ]

    # Should not raise exception, should use default values
    events = reply_reader.fetch(tweet_id)

    # First reply missing text
    assert events[0].content == ""  # Default empty string
    # Second reply missing timestamp
    assert events[1].detected_at is not None  # Should have a default datetime


def test_fetch_with_empty_tweet_id_returns_empty_list(reply_reader, mock_twitter_client):
    """fetch() with empty string tweet_id returns empty list without API call."""
    mock_twitter_client.get_tweet_replies.return_value = []

    result = reply_reader.fetch("")

    assert result == []
    mock_twitter_client.get_tweet_replies.assert_not_called()


def test_fetch_with_none_tweet_id_returns_empty_list(reply_reader, mock_twitter_client):
    """fetch() with None tweet_id returns empty list without API call."""
    mock_twitter_client.get_tweet_replies.return_value = []

    result = reply_reader.fetch(None)

    assert result == []
    mock_twitter_client.get_tweet_replies.assert_not_called()


def test_fetch_with_empty_reply_list_returns_empty_list(reply_reader, mock_twitter_client):
    """fetch() with no replies returns empty list."""
    tweet_id = "1234567890"
    mock_twitter_client.get_tweet_replies.return_value = []

    result = reply_reader.fetch(tweet_id)

    assert result == []
    assert isinstance(result, list)
