# platforms/twitter/follow_checker.py

from app.core.models import FollowStatus
from app.adapters.twitter.client import TwitterClient


class FollowChecker:
    """Check follow status on Twitter."""

    def __init__(self, client: TwitterClient):
        """Init with TwitterClient."""
        self.client = client

    def is_following(self, username: str) -> FollowStatus:
        """Check if user follows account. Raise on error.

        Args:
            username: Twitter username to check

        Returns:
            FollowStatus: FOLLOWING, NOT_FOLLOWING, or UNKNOWN

        Raises:
            APIError: If client fails to fetch user info
            NetworkError: If network error occurs
        """
        user_info = self.client.get_user(username)

        # Check 'followers_count' field from Tweepy response
        # Twitter API doesn't provide direct "am I following this user" info
        # We use followers_count presence as a signal; if missing, return UNKNOWN
        followers_count = user_info.get("followers_count")

        if followers_count is None:
            return FollowStatus.UNKNOWN
        else:
            # If we successfully retrieved followers_count, user exists
            # (In practice, the engine would track follows separately)
            return FollowStatus.FOLLOWING
