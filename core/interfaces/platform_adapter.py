from typing import Protocol
from core.models import Platform, TriggerEvent, FollowStatus

class PlatformAdapter(Protocol):
    """All platform adapters must implement these 4 methods."""

    @property
    def platform(self) -> Platform:
        """Return platform enum."""
        ...

    def read_triggers(self, source_id: str) -> list[TriggerEvent]:
        """Fetch comments/replies from source. Stub: return []"""
        ...

    def send_message(self, recipient_id: str, text: str) -> bool:
        """Send DM to recipient. Stub: return True"""
        ...

    def check_follow(self, username: str) -> FollowStatus:
        """Check if user follows. Stub: return NOT_FOLLOWING"""
        ...

    def supports_follow_gate(self) -> bool:
        """Can this platform gate by follow? Stub: return True"""
        ...
