class WorkflowRepository:
    """Query workflows by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get_all(self, platform: str) -> list:
        """Get all workflows for platform. Stub: return []"""
        return []

    def get_by_id(self, platform: str, workflow_id: int):
        """Get workflow by ID. Stub: return None"""
        return None

    def insert(self, platform: str, workflow_data: dict):
        """Insert workflow. Stub: return None"""
        return None

    def update(self, platform: str, workflow_id: int, workflow_data: dict):
        """Update workflow. Stub: return None"""
        return None

    def delete(self, platform: str, workflow_id: int):
        """Soft-delete workflow. Stub: return None"""
        return None
