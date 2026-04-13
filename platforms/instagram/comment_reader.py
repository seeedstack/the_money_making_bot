from core.models import TriggerEvent

class CommentReader:
    """Read comments from Instagram posts."""

    def __init__(self, client):
        self.client = client

    def fetch(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments from post. Stub: return []"""
        return []
