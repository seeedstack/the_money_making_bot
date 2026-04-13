class FollowCheckRepository:
    """Query pending follow checks by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get_pending(self, platform: str) -> list:
        """Get pending checks due now. Stub: return []"""
        return []

    def insert(self, platform: str, check_data: dict):
        """Insert pending check. Stub: return None"""
        return None

    def update(self, platform: str, check_id: int, check_data: dict):
        """Update check. Stub: return None"""
        return None
