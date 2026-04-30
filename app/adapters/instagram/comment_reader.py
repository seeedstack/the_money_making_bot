from app.core.models import TriggerEvent, Platform
from .client import InstagramClient


class CommentReader:
    """Read comments from Instagram posts."""

    def __init__(self, client: InstagramClient):
        """Init with InstagramClient.

        Args:
            client: InstagramClient instance for fetching comments
        """
        self.client = client

    def fetch(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments from post and return as TriggerEvent list.

        Args:
            source_id: Instagram post URL (https://instagram.com/p/ABC123) or post ID

        Returns:
            List of TriggerEvent objects (empty if no comments)

        Raises:
            ValueError: If source_id is invalid format or empty
            APIError: If client fails to fetch comments
        """
        if not source_id:
            raise ValueError("source_id cannot be empty")

        comments = self.client.get_comments(source_id)

        events = []
        for comment in comments:
            # Validate comment structure
            if not isinstance(comment, dict):
                continue

            # Safe dict access with defaults
            event = TriggerEvent(
                username=comment.get("username", "unknown"),
                content=comment.get("text", ""),
                detected_at=comment.get("timestamp"),
                source_id=source_id,
                platform=Platform.INSTAGRAM,
                matched_keyword=""  # Will be set by keyword matcher later
            )
            events.append(event)

        return events
