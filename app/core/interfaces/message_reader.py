from typing import Protocol
from app.core.models import TriggerEvent

class MessageReader(Protocol):
    """Read comments, replies, messages from platform."""

    def fetch(self, source_id: str) -> list[TriggerEvent]:
        """Fetch messages. Stub: return []"""
        ...
