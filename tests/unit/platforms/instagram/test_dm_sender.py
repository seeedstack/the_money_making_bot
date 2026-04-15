# tests/unit/platforms/instagram/test_dm_sender.py

import pytest
from unittest.mock import Mock
from platforms.instagram.dm_sender import DMSender
from platforms.instagram.errors import APIError, NetworkError


def test_send_returns_true_on_success():
    """send() returns True when DM sends successfully."""
    mock_client = Mock()
    mock_client.send_dm.return_value = True

    sender = DMSender(mock_client)
    result = sender.send("user123", "Hello world")

    assert result is True
    mock_client.send_dm.assert_called_once_with("user123", "Hello world")


def test_send_raises_on_api_error():
    """send() raises APIError when send fails."""
    mock_client = Mock()
    mock_client.send_dm.side_effect = APIError("Send failed")

    sender = DMSender(mock_client)
    with pytest.raises(APIError):
        sender.send("user123", "Hello")


def test_send_raises_on_network_error():
    """send() raises NetworkError on network failure."""
    mock_client = Mock()
    mock_client.send_dm.side_effect = NetworkError("Network error")

    sender = DMSender(mock_client)
    with pytest.raises(NetworkError):
        sender.send("user123", "Hello")


def test_send_with_empty_text():
    """send() handles empty text (pass through to client)."""
    mock_client = Mock()
    mock_client.send_dm.return_value = True

    sender = DMSender(mock_client)
    result = sender.send("user123", "")

    assert result is True
    mock_client.send_dm.assert_called_once_with("user123", "")


def test_send_with_special_characters():
    """send() handles special characters and emojis."""
    mock_client = Mock()
    mock_client.send_dm.return_value = True

    sender = DMSender(mock_client)
    text = "Hey! 🎉 Check this out: https://example.com"
    result = sender.send("user123", text)

    assert result is True
    mock_client.send_dm.assert_called_once_with("user123", text)


def test_send_calls_client_with_correct_args():
    """send() passes recipient_id and text to client.send_dm()."""
    mock_client = Mock()
    mock_client.send_dm.return_value = True

    sender = DMSender(mock_client)
    sender.send("recipient_123", "Test message")

    mock_client.send_dm.assert_called_once_with("recipient_123", "Test message")


def test_send_preserves_exception_message():
    """send() propagates original exception from client."""
    mock_client = Mock()
    error = APIError("Recipient not found")
    mock_client.send_dm.side_effect = error

    sender = DMSender(mock_client)
    with pytest.raises(APIError) as exc_info:
        sender.send("user123", "Hello")

    assert str(exc_info.value) == "Recipient not found"
