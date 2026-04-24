# tests/unit/platforms/twitter/test_client.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from platforms.twitter.client import TwitterClient
from platforms.twitter.errors import LoginError, APIError, NetworkError


@pytest.fixture
def mock_settings_repo():
    """Mock settings repo for credential fetching."""
    repo = Mock()
    repo.get.return_value = "test_value"
    return repo


def test_init_sets_account_id(mock_settings_repo):
    """TwitterClient stores account_id. Credentials NOT loaded in __init__."""
    with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
        client = TwitterClient(account_id=123)
        assert client.account_id == 123
        assert client.cl is None  # Not yet logged in
        # Credentials should NOT have been loaded during __init__
        mock_settings_repo.get.assert_not_called()


def test_login_success(mock_settings_repo):
    """login() initializes Tweepy client and returns True."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = [
                "api_key_value",
                "api_secret_value",
                "access_token_value",
                "access_secret_value"
            ]
            client = TwitterClient(account_id=123)
            result = client.login()

        assert result is True
        assert client.cl is mock_cl
        MockClient.assert_called_once()
        # Verify Tweepy Client was initialized with 4-part credentials
        call_args = MockClient.call_args
        assert call_args[1]['consumer_key'] == "api_key_value"
        assert call_args[1]['consumer_secret'] == "api_secret_value"
        assert call_args[1]['access_token'] == "access_token_value"
        assert call_args[1]['access_token_secret'] == "access_secret_value"


def test_login_failure_raises(mock_settings_repo):
    """login() raises LoginError on API failure."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        MockClient.side_effect = Exception("Invalid credentials")

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = [
                "bad_key",
                "bad_secret",
                "bad_token",
                "bad_token_secret"
            ]
            client = TwitterClient(account_id=123)
            with pytest.raises(LoginError):
                client.login()


def test_get_tweet_replies_returns_list(mock_settings_repo):
    """get_tweet_replies() returns list of reply data dicts."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl

        # Mock tweet replies response
        mock_tweet1 = MagicMock()
        mock_tweet1.id = 111
        mock_tweet1.text = "reply text 1"
        mock_tweet1.author_id = 999
        mock_tweet1.created_at = "2025-02-01T10:00:00Z"

        mock_tweet2 = MagicMock()
        mock_tweet2.id = 222
        mock_tweet2.text = "reply text 2"
        mock_tweet2.author_id = 888
        mock_tweet2.created_at = "2025-02-01T10:05:00Z"

        mock_cl.search_recent_tweets.return_value = MagicMock(data=[mock_tweet1, mock_tweet2])

        # Also mock user info lookups
        mock_user1_data = MagicMock()
        mock_user1_data.username = "user1"
        mock_user1_response = MagicMock()
        mock_user1_response.data = mock_user1_data

        mock_user2_data = MagicMock()
        mock_user2_data.username = "user2"
        mock_user2_response = MagicMock()
        mock_user2_response.data = mock_user2_data

        mock_cl.get_user.side_effect = [mock_user1_response, mock_user2_response]

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            replies = client.get_tweet_replies("1234567890")

        assert isinstance(replies, list)
        assert len(replies) == 2
        assert replies[0]["text"] == "reply text 1"
        assert replies[1]["username"] == "user2"


def test_get_tweet_replies_with_no_replies(mock_settings_repo):
    """get_tweet_replies() handles empty reply list."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.search_recent_tweets.return_value = MagicMock(data=None)

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            replies = client.get_tweet_replies("1234567890")

        assert isinstance(replies, list)
        assert len(replies) == 0


def test_send_dm_success(mock_settings_repo):
    """send_dm() sends DM and returns True."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.create_direct_message.return_value = MagicMock(data={'dm_event_id': 'xyz'})

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            result = client.send_dm("user123", "Hello there")

        assert result is True
        mock_cl.create_direct_message.assert_called_once()


def test_send_dm_failure_raises(mock_settings_repo):
    """send_dm() raises APIError on failure."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.create_direct_message.side_effect = Exception("DM sending failed")

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            with pytest.raises(APIError):
                client.send_dm("user123", "Hello")


def test_get_user_returns_dict(mock_settings_repo):
    """get_user() returns user dict with username and id."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl

        mock_user = MagicMock()
        mock_user.id = 987654321
        mock_user.username = "testuser"
        mock_user.public_metrics = MagicMock(followers_count=5000)
        mock_user.protected = False

        mock_cl.get_user.return_value = MagicMock(data=mock_user)

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            info = client.get_user("testuser")

        assert isinstance(info, dict)
        assert info["username"] == "testuser"
        assert info["id"] == 987654321
        assert info["followers_count"] == 5000
        assert info["protected"] is False


def test_get_user_failure_raises(mock_settings_repo):
    """get_user() raises APIError on failure."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.get_user.side_effect = Exception("User not found")

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            with pytest.raises(APIError):
                client.get_user("nonexistent")


def test_lazy_login_on_get_tweet_replies(mock_settings_repo):
    """get_tweet_replies() auto-logs in if not already logged in."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.search_recent_tweets.return_value = MagicMock(data=None)

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            # Don't call login() explicitly
            replies = client.get_tweet_replies("1234567890")

        assert isinstance(replies, list)
        assert MockClient.called


def test_is_logged_in_property(mock_settings_repo):
    """is_logged_in property returns True/False based on client state."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)

            assert client.is_logged_in is False
            client.login()
            assert client.is_logged_in is True


def test_login_loads_credentials_from_db(mock_settings_repo):
    """login() loads 4-part credentials from settings_repo at login time."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = [
                "key_from_db",
                "secret_from_db",
                "token_from_db",
                "token_secret_from_db"
            ]
            client = TwitterClient(account_id=456)
            client.login()

            # Verify settings_repo was called for all 4 credentials
            calls = mock_settings_repo.get.call_args_list
            assert calls[0][1]["key"] == "account_456_api_key"
            assert calls[1][1]["key"] == "account_456_api_secret"
            assert calls[2][1]["key"] == "account_456_access_token"
            assert calls[3][1]["key"] == "account_456_access_secret"


def test_login_credentials_not_stored(mock_settings_repo):
    """login() does not store credentials in instance after login."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()

            # Credentials should not be stored as instance variables
            assert not hasattr(client, 'api_key') or client.__dict__.get('api_key') is None
            assert not hasattr(client, 'api_secret') or client.__dict__.get('api_secret') is None
            assert not hasattr(client, 'access_token') or client.__dict__.get('access_token') is None
            assert not hasattr(client, 'access_secret') or client.__dict__.get('access_secret') is None


def test_login_network_error_raises(mock_settings_repo):
    """login() raises NetworkError on connection failure."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        MockClient.side_effect = ConnectionError("Network unreachable")

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            with pytest.raises(NetworkError):
                client.login()


def test_get_tweet_replies_network_error_raises(mock_settings_repo):
    """get_tweet_replies() raises NetworkError on connection failure."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.search_recent_tweets.side_effect = TimeoutError("Request timeout")

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            with pytest.raises(NetworkError):
                client.get_tweet_replies("1234567890")


def test_send_dm_network_error_raises(mock_settings_repo):
    """send_dm() raises NetworkError on connection failure."""
    with patch('platforms.twitter.client.tweepy.Client') as MockClient:
        mock_cl = MagicMock()
        MockClient.return_value = mock_cl
        mock_cl.create_direct_message.side_effect = OSError("Connection lost")

        with patch('platforms.twitter.client.settings_repo', mock_settings_repo):
            mock_settings_repo.get.side_effect = ["key", "secret", "token", "token_secret"]
            client = TwitterClient(account_id=123)
            client.login()
            with pytest.raises(NetworkError):
                client.send_dm("user123", "Hello")
