class DMSender:
    """Send DMs on Instagram."""

    def __init__(self, client):
        self.client = client

    def send(self, recipient_id: str, text: str) -> bool:
        """Send DM. Stub: return True"""
        return True
