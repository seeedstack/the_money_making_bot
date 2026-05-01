class RateLimiter:
    """Rate limit by platform and account."""

    def can_send(self, platform: str, account_id: int) -> bool:
        """Stub: return True"""
        return True

    def record_send(self, platform: str, account_id: int):
        """Stub: do nothing"""
        pass
