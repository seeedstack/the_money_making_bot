# tests/unit/platforms/instagram/test_client.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.adapters.instagram.client import InstagramClient
from app.adapters.instagram.errors import LoginError, APIError, NetworkError


@pytest.fixture
def mock_settings_repo():
    """Mock settings repo for credential fetching."""
    repo = Mock()
    repo.get.return_value = "test_user"
    return repo


def test_init_sets_account_id(mock_settings_repo):
    """InstagramClient stores account_id. Credentials NOT loaded in __init__."""
    with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
        client = InstagramClient(account_id=123)
        assert client.account_id == 123
        assert client.cl is None  # Not yet logged in
        # Credentials should NOT have been loaded during __init__
        mock_settings_repo.get.assert_not_called()


def test_login_success(mock_settings_repo):
    """login() initializes Instagrapi client and returns True."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            result = client.login()

        assert result is True
        assert client.cl is mock_cl
        MockClient.assert_called_once()
        mock_cl.login.assert_called_once_with("test_user", "test_pass")


def test_login_failure_raises(mock_settings_repo):
    """login() raises LoginError on API failure."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.side_effect = Exception("Bad password")

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            with pytest.raises(LoginError):
                client.login()


def test_get_comments_returns_list(mock_settings_repo):
    """get_comments() returns list of comment dicts."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        # Mock media.comments
        mock_comment = MagicMock()
        mock_comment.user.username = "user1"
        mock_comment.text = "hello"
        mock_comment.taken_at = "2025-02-01T10:00:00"

        mock_media = MagicMock()
        mock_media.comments = [mock_comment]
        mock_cl.media_info.return_value = mock_media

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()
            comments = client.get_comments("https://instagram.com/p/ABC123")

        assert isinstance(comments, list)
        assert len(comments) == 1
        assert comments[0]["username"] == "user1"
        assert comments[0]["text"] == "hello"


def test_get_comments_with_post_id(mock_settings_repo):
    """get_comments() handles post ID directly."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        mock_media = MagicMock()
        mock_media.comments = []
        mock_cl.media_info.return_value = mock_media

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()
            comments = client.get_comments("ABC123")

        assert isinstance(comments, list)
        mock_cl.media_info.assert_called_once_with("ABC123")


def test_send_dm_success(mock_settings_repo):
    """send_dm() sends DM and returns True."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None
        mock_cl.send_direct_message.return_value = None

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()
            result = client.send_dm("user123", "Hello")

        assert result is True
        mock_cl.send_direct_message.assert_called_once_with("user123", "Hello")


def test_send_dm_failure_raises(mock_settings_repo):
    """send_dm() raises APIError on failure."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None
        mock_cl.send_direct_message.side_effect = Exception("DM failed")

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()
            with pytest.raises(APIError):
                client.send_dm("user123", "Hello")


def test_get_user_returns_dict(mock_settings_repo):
    """get_user() returns user dict."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        mock_user = MagicMock()
        mock_user.id = 12345
        mock_user.username = "testuser"
        mock_user.is_private = False
        mock_user.follower_count = 1000
        mock_user.follower = True

        mock_cl.user_info_by_username.return_value = mock_user

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()
            info = client.get_user("testuser")

        assert isinstance(info, dict)
        assert info["username"] == "testuser"
        assert info["id"] == 12345
        assert info["is_private"] is False
        assert info["follower_count"] == 1000
        assert info["follower"] is True


def test_get_user_failure_raises(mock_settings_repo):
    """get_user() raises APIError on failure."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None
        mock_cl.user_info_by_username.side_effect = Exception("User not found")

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()
            with pytest.raises(APIError):
                client.get_user("testuser")


def test_lazy_login_on_get_comments(mock_settings_repo):
    """get_comments() auto-logs in if not already logged in."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        mock_media = MagicMock()
        mock_media.comments = []
        mock_cl.media_info.return_value = mock_media

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass", "test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            # Don't call login() explicitly
            comments = client.get_comments("ABC123")

        assert isinstance(comments, list)
        assert mock_cl.login.called


def test_is_logged_in_property(mock_settings_repo):
    """is_logged_in property returns True/False based on client state."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)

            assert client.is_logged_in is False
            client.login()
            assert client.is_logged_in is True


def test_extract_post_id_from_url(mock_settings_repo):
    """_extract_post_id() parses /p/, /reel/, /tv/, /stories/ URLs."""
    with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
        client = InstagramClient(account_id=123)

        # Test /p/ URL
        assert client._extract_post_id("https://instagram.com/p/ABC123") == "ABC123"
        assert client._extract_post_id("https://instagram.com/p/ABC123/") == "ABC123"

        # Test /reel/ URL
        assert client._extract_post_id("https://instagram.com/reel/XYZ789") == "XYZ789"

        # Test /tv/ URL
        assert client._extract_post_id("https://instagram.com/tv/TV123") == "TV123"

        # Test /stories/ URL
        assert client._extract_post_id("https://instagram.com/stories/STORY456") == "STORY456"


def test_extract_post_id_from_raw_id(mock_settings_repo):
    """_extract_post_id() returns raw ID if already in ID format."""
    with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
        client = InstagramClient(account_id=123)

        assert client._extract_post_id("ABC123") == "ABC123"
        assert client._extract_post_id("ABC-123_xyz") == "ABC-123_xyz"


def test_extract_post_id_invalid_url_raises(mock_settings_repo):
    """_extract_post_id() raises ValueError for invalid URL format."""
    with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
        client = InstagramClient(account_id=123)

        # URL with no /p/, /reel/, /tv/, /stories/ pattern
        with pytest.raises(ValueError):
            client._extract_post_id("https://instagram.com/invalid/URL123")

        # Invalid ID format (contains special chars not in alphanumeric/dash/underscore)
        with pytest.raises(ValueError):
            client._extract_post_id("not-a-valid-id!")


def test_get_comments_invalid_url_raises(mock_settings_repo):
    """get_comments() raises ValueError for invalid URL format."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()

            with pytest.raises(ValueError):
                client.get_comments("https://instagram.com/invalid/ABC123")


def test_login_loads_credentials_from_db(mock_settings_repo):
    """login() loads credentials from settings_repo at login time."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["username_from_db", "password_from_db"]
            client = InstagramClient(account_id=456)
            client.login()

            # Verify settings_repo was called during login, not __init__
            calls = mock_settings_repo.get.call_args_list
            assert calls[0][1]["key"] == "account_456_user"
            assert calls[1][1]["key"] == "account_456_pass"
            mock_cl.login.assert_called_once_with("username_from_db", "password_from_db")


def test_login_credentials_not_stored(mock_settings_repo):
    """login() does not store credentials in instance after login."""
    with patch('platforms.instagram.client.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.login.return_value = None

        with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["test_user", "test_pass"]
            client = InstagramClient(account_id=123)
            client.login()

            # Credentials should not be stored as instance variables
            assert not hasattr(client, 'username') or client.__dict__.get('username') is None
            assert not hasattr(client, 'password') or client.__dict__.get('password') is None


def test_login_db_failure_raises(mock_settings_repo):
    """login() raises LoginError if credential loading fails."""
    mock_settings_repo.get.side_effect = Exception("DB connection failed")

    with patch('platforms.instagram.client.settings_repo', mock_settings_repo):
        client = InstagramClient(account_id=123)
        with pytest.raises(LoginError):
            client.login()
