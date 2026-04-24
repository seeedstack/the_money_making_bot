# tests/unit/platforms/twitter/test_dm_sender.py

import pytest
from unittest.mock import Mock
from platforms.twitter.dm_sender import DMSender
from platforms.twitter.errors import APIError, NetworkError


def test_send_returns_true_on_success():
    """send() returns True when DM sends successfully."""
    mock_client = Mock()
    mock_client.send_dm.return_value = True

    sender = DMSender(mock_client)
    result = sender.send("user_123", "Hello world")

    assert result is True
    mock_client.send_dm.assert_called_once_with("user_123", "Hello world")


def test_send_raises_on_api_error():
    """send() raises APIError when send fails."""
    mock_client = Mock()
    mock_client.send_dm.side_effect = APIError("Send failed")

    sender = DMSender(mock_client)
    with pytest.raises(APIError):
        sender.send("user_123", "Hello")


def test_send_raises_on_network_error():
    """send() raises NetworkError on network failure."""
    mock_client = Mock()
    mock_client.send_dm.side_effect = NetworkError("Network error")

    sender = DMSender(mock_client)
    with pytest.raises(NetworkError):
        sender.send("user_123", "Hello")


def test_send_with_empty_text():
    """send() handles empty text (pass through to client)."""
    mock_client = Mock()
    mock_client.send_dm.return_value = True

    sender = DMSender(mock_client)
    result = sender.send("user_123", "")

    assert result is True
    mock_client.send_dm.assert_called_once_with("user_123", "")
