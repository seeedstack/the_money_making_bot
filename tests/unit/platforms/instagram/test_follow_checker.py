# tests/unit/platforms/instagram/test_follow_checker.py

import pytest
from unittest.mock import Mock
from core.models import FollowStatus
from platforms.instagram.follow_checker import FollowChecker


def test_is_following_returns_following():
    """is_following() returns FOLLOWING when account follows."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 123,
        "username": "testuser",
        "is_private": False,
        "follower_count": 100,
        "follower": True
    }

    checker = FollowChecker(mock_client)
    result = checker.is_following("testuser")

    assert result == FollowStatus.FOLLOWING


def test_is_following_returns_not_following():
    """is_following() returns NOT_FOLLOWING when account doesn't follow."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 123,
        "username": "testuser",
        "follower": False
    }

    checker = FollowChecker(mock_client)
    result = checker.is_following("testuser")

    assert result == FollowStatus.NOT_FOLLOWING


def test_is_following_returns_not_applicable_on_missing_field():
    """is_following() returns NOT_APPLICABLE if 'follower' field missing."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 123,
        "username": "testuser"
        # 'follower' field missing
    }

    checker = FollowChecker(mock_client)
    result = checker.is_following("testuser")

    assert result == FollowStatus.NOT_APPLICABLE


def test_is_following_returns_not_applicable_on_none():
    """is_following() returns NOT_APPLICABLE if 'follower' field is None."""
    mock_client = Mock()
    mock_client.get_user.return_value = {
        "id": 123,
        "username": "testuser",
        "follower": None
    }

    checker = FollowChecker(mock_client)
    result = checker.is_following("testuser")

    assert result == FollowStatus.NOT_APPLICABLE


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
    mock_client.get_user.return_value = {"follower": True}

    checker = FollowChecker(mock_client)
    checker.is_following("someuser")

    mock_client.get_user.assert_called_once_with("someuser")
