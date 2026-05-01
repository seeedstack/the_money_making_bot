# platforms/twitter/adapter.py

from app.core.models import Platform, FollowStatus, TriggerEvent
from app.adapters.base import BasePlatformAdapter
from app.adapters.twitter.client import TwitterClient
from app.adapters.twitter.reply_reader import ReplyReader
from app.adapters.twitter.dm_sender import DMSender
from app.adapters.twitter.follow_checker import FollowChecker


class TwitterAdapter(BasePlatformAdapter):
    """Twitter adapter implements PlatformAdapter protocol."""

    platform = Platform.TWITTER

    def __init__(self, account_id: int):
        """Initialize TwitterAdapter with all components.

        Args:
            account_id: Twitter account ID
        """
        self.account_id = account_id
        self.client = TwitterClient(account_id)
        self.reply_reader = ReplyReader(self.client)
        self.dm_sender = DMSender(self.client)
        self.follow_checker = FollowChecker(self.client)

    def read_triggers(self, source_id: str) -> list[TriggerEvent]:
        """Fetch replies from tweet.

        Args:
            source_id: Tweet ID string

        Returns:
            List of TriggerEvent objects from tweet replies
        """
        return self.reply_reader.fetch(source_id)

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM to user.

        Args:
            recipient_id: Twitter user ID
            text: Message text

        Returns:
            True on success

        Raises:
            APIError: If send fails
            NetworkError: If network error occurs
        """
        return self.dm_sender.send(recipient_id, text)

    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows.

        Args:
            username: Twitter username to check

        Returns:
            FollowStatus: FOLLOWING, NOT_FOLLOWING, or UNKNOWN
        """
        return self.follow_checker.is_following(username)

    def supports_follow_gate(self) -> bool:
        """Twitter supports follow gate.

        Returns:
            True (Twitter has follow functionality)
        """
        return True
