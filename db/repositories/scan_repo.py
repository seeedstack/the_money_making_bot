class ScanRepository:
    """Query trigger scans by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def insert(self, platform: str, scan_data: dict):
        """Insert trigger scan. Stub: return None"""
        return None

    def get_recent(self, platform: str, limit: int = 100) -> list:
        """Get recent scans. Stub: return []"""
        return []
