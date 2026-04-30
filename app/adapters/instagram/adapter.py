from app.core.models import Platform, FollowStatus, TriggerEvent
from app.adapters.base import BasePlatformAdapter
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
        """Fetch comments from post."""
        return self.comment_reader.fetch(source_id)

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM to user."""
        return self.dm_sender.send(recipient_id, text)

    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows."""
        return self.follow_checker.is_following(username)

    def supports_follow_gate(self) -> bool:
        """Instagram supports follow gate. Stub: return True"""
        return True
