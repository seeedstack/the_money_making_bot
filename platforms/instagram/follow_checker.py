from core.models import FollowStatus
from .client import InstagramClient


class FollowChecker:
    """Check follow status on Instagram."""

    def __init__(self, client: InstagramClient):
        """Init with InstagramClient."""
        self.client = client

    def is_following(self, username: str) -> FollowStatus:
        """Check if user follows account. Raise on error.

        Args:
            username: Instagram username to check

        Returns:
            FollowStatus: FOLLOWING, NOT_FOLLOWING, or NOT_APPLICABLE

        Raises:
            APIError: If client fails to fetch user info
            NetworkError: If network error occurs
        """
        user_info = self.client.get_user(username)

        # Check 'follower' field from Instagrapi response
        follower = user_info.get("follower")

        if follower is None:
            return FollowStatus.NOT_APPLICABLE
        elif follower:
            return FollowStatus.FOLLOWING
        else:
            return FollowStatus.NOT_FOLLOWING
