from core.models import FollowStatus

class FollowChecker:
    """Check follow status on Instagram."""

    def __init__(self, client):
        self.client = client

    def is_following(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        return FollowStatus.NOT_FOLLOWING
