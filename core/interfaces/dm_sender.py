from typing import Protocol

class DMSender(Protocol):
    """Send DM on platform."""

    def send(self, recipient_id: str, text: str) -> bool:
        """Send DM. Stub: return True"""
        ...
