# platforms/instagram/dm_sender.py

from .client import InstagramClient


class DMSender:
    """Send DMs on Instagram."""

    def __init__(self, client: InstagramClient):
        """Initialize with InstagramClient.

        Args:
            client: InstagramClient instance
        """
        self.client = client

    def send(self, recipient_id: str, text: str) -> bool:
        """Send DM. Raises on error (engine handles retries).

        Args:
            recipient_id: Instagram user ID or username
            text: Message text

        Returns:
            True on success

        Raises:
            APIError: If send fails (from InstagramClient)
            NetworkError: If network error occurs (from InstagramClient)
        """
        return self.client.send_dm(recipient_id, text)
