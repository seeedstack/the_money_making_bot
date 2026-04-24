# platforms/twitter/dm_sender.py

from platforms.twitter.client import TwitterClient


class DMSender:
    """Send DMs on Twitter."""

    def __init__(self, client: TwitterClient):
        """Initialize with TwitterClient.

        Args:
            client: TwitterClient instance
        """
        self.client = client

    def send(self, recipient_id: str, text: str) -> bool:
        """Send DM. Raises on error (engine handles retries).

        Args:
            recipient_id: Twitter user ID or username
            text: Message text

        Returns:
            True on success

        Raises:
            APIError: If send fails (from TwitterClient)
            NetworkError: If network error occurs (from TwitterClient)
        """
        return self.client.send_dm(recipient_id, text)
