# tests/unit/platforms/instagram/test_comment_reader.py

import pytest
from datetime import datetime
from unittest.mock import Mock
from app.core.models import TriggerEvent, Platform
from app.adapters.instagram.comment_reader import CommentReader
from app.adapters.instagram.errors import APIError


def test_fetch_returns_trigger_events():
    """fetch() returns list of TriggerEvent objects."""
    mock_client = Mock()
    now = datetime.now()
    mock_client.get_comments.return_value = [
        {
            "username": "user1",
            "text": "hello",
            "timestamp": now
        },
        {
            "username": "user2",
            "text": "world",
            "timestamp": now
        }
    ]

    reader = CommentReader(mock_client)
    events = reader.fetch("https://instagram.com/p/ABC123")

    assert len(events) == 2
    assert all(isinstance(e, TriggerEvent) for e in events)
    assert events[0].username == "user1"
    assert events[0].content == "hello"
    assert events[0].platform == Platform.INSTAGRAM
    assert events[0].source_id == "https://instagram.com/p/ABC123"
    assert events[0].detected_at == now


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


def test_fetch_preserves_all_comment_data():
    """fetch() preserves all data from comments."""
    mock_client = Mock()
    now = datetime.now()
    mock_client.get_comments.return_value = [
        {
            "username": "testuser",
            "text": "This is a test comment with emoji 🎉",
            "timestamp": now
        }
    ]

    reader = CommentReader(mock_client)
    events = reader.fetch("ABC123")

    assert len(events) == 1
    event = events[0]
    assert event.username == "testuser"
    assert event.content == "This is a test comment with emoji 🎉"
    assert event.detected_at == now
    assert event.source_id == "ABC123"
    assert event.platform == Platform.INSTAGRAM


def test_fetch_raises_on_empty_source_id():
    """fetch() raises ValueError on empty source_id."""
    mock_client = Mock()
    reader = CommentReader(mock_client)

    with pytest.raises(ValueError):
        reader.fetch("")


def test_fetch_raises_on_none_source_id():
    """fetch() raises ValueError on None source_id."""
    mock_client = Mock()
    reader = CommentReader(mock_client)

    with pytest.raises(ValueError):
        reader.fetch(None)


def test_fetch_handles_malformed_comments():
    """fetch() handles malformed comment dicts gracefully."""
    mock_client = Mock()
    mock_client.get_comments.return_value = [
        {"username": "user1", "text": "good"},  # Good
        "not_a_dict",  # Malformed — should be skipped
        {"username": "user2"},  # Missing "text" — should use default
    ]

    reader = CommentReader(mock_client)
    events = reader.fetch("https://instagram.com/p/ABC123")

    # Should skip malformed, handle missing keys with defaults
    assert len(events) == 2
    assert events[0].username == "user1"
    assert events[0].content == "good"
    assert events[1].username == "user2"
    assert events[1].content == ""  # Default for missing "text"


def test_fetch_handles_missing_username():
    """fetch() uses 'unknown' for missing username field."""
    mock_client = Mock()
    mock_client.get_comments.return_value = [
        {
            "text": "comment without username",
            "timestamp": datetime.now()
        }
    ]

    reader = CommentReader(mock_client)
    events = reader.fetch("https://instagram.com/p/ABC123")

    assert len(events) == 1
    assert events[0].username == "unknown"
    assert events[0].content == "comment without username"


def test_fetch_handles_missing_timestamp():
    """fetch() handles missing timestamp gracefully."""
    mock_client = Mock()
    mock_client.get_comments.return_value = [
        {
            "username": "user1",
            "text": "comment without timestamp"
        }
    ]

    reader = CommentReader(mock_client)
    events = reader.fetch("https://instagram.com/p/ABC123")

    assert len(events) == 1
    assert events[0].username == "user1"
    assert events[0].detected_at is None
