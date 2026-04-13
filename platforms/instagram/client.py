class InstagramClient:
    """Instagrapi client wrapper."""

    def __init__(self, account_id: int):
        """Initialize with account ID. Load creds from DB (stub)."""
        self.account_id = account_id
        self.cl = None  # instagrapi.Client() stub

    def login(self) -> bool:
        """Login to Instagram. Stub: return True"""
        return True

    def get_comments(self, source_id: str):
        """Get comments from post. Stub: return []"""
        return []

    def send_direct_message(self, recipient_id: str, text: str) -> bool:
        """Send DM. Stub: return True"""
        return True

    def user_info(self, username: str):
        """Get user info. Stub: return empty dict"""
        return {}
