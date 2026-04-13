class SessionRepository:
    """Query message sessions by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get_all(self, platform: str, state: str = None) -> list:
        """Get sessions for platform, optionally filtered by state. Stub: return []"""
        return []

    def get_by_id(self, platform: str, session_id: int):
        """Get session by ID. Stub: return None"""
        return None

    def insert(self, platform: str, session_data: dict):
        """Insert session. Stub: return None"""
        return None

    def update(self, platform: str, session_id: int, session_data: dict):
        """Update session. Stub: return None"""
        return None
