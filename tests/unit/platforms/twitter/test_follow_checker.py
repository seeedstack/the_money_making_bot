# tests/unit/platforms/twitter/test_follow_checker.py

import pytest
from unittest.mock import Mock
from app.core.models import FollowStatus
from app.adapters.twitter.follow_checker import FollowChecker


def test_is_following_returns_following():
    """is_following() returns FOLLOWING when followers_count present."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": "123456",
        "username": "testuser",
        "protected": False,
        "followers_count": 100
    }

    checker = FollowChecker(mock_client)
    result = checker.is_following("testuser")

    assert result == FollowStatus.FOLLOWING


def test_is_following_returns_unknown_on_missing_field():
    """is_following() returns UNKNOWN if 'followers_count' field missing."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": "123456",
        "username": "testuser"
        # 'followers_count' field missing
    }

    checker = FollowChecker(mock_client)
    result = checker.is_following("testuser")

    assert result == FollowStatus.UNKNOWN


def test_is_following_returns_unknown_on_none():
    """is_following() returns UNKNOWN if 'followers_count' field is None."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": "123456",
        "username": "testuser",
        "followers_count": None
    }

    checker = FollowChecker(mock_client)
    result = checker.is_following("testuser")

    assert result == FollowStatus.UNKNOWN


def test_is_following_raises_on_error():
    """is_following() raises exception on client error."""
    mock_client = Mock()
    mock_client.get_user.side_effect = Exception("API error")

    checker = FollowChecker(mock_client)
    with pytest.raises(Exception):
        checker.is_following("testuser")


def test_is_following_calls_client_get_user():
    """is_following() calls client.get_user() with username."""
    mock_client = Mock()
    mock_client.get_user.return_value = {"followers_count": 50}

    checker = FollowChecker(mock_client)
    checker.is_following("someuser")

    mock_client.get_user.assert_called_once_with("someuser")
