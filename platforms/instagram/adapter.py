from core.models import Platform, FollowStatus, TriggerEvent
from platforms.base import BasePlatformAdapter
from .client import InstagramClient
from .comment_reader import CommentReader
from .dm_sender import DMSender
from .follow_checker import FollowChecker

class InstagramAdapter(BasePlatformAdapter):
    """Instagram adapter implements PlatformAdapter protocol."""

    platform = Platform.INSTAGRAM

    def __init__(self, account_id: int):
        self.account_id = account_id
        self.client = InstagramClient(account_id)
        self.comment_reader = CommentReader(self.client)
        self.dm_sender = DMSender(self.client)
        self.follow_checker = FollowChecker(self.client)

    def read_triggers(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments from post. Stub: return []"""
        return []

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM to user. Stub: return True"""
        return True

    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        return FollowStatus.NOT_FOLLOWING

    def supports_follow_gate(self) -> bool:
        """Instagram supports follow gate. Stub: return True"""
        return True
