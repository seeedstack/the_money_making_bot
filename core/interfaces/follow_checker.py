from typing import Protocol
from core.models import FollowStatus

class FollowChecker(Protocol):
    """Check follow status on platform."""

    def is_following(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        ...
