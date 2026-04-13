import pytest
from db.repositories.workflow_repo import WorkflowRepository

def test_workflow_repo_get_all_returns_empty(test_db):
    """Stub repo get_all should return []."""
    repo = WorkflowRepository(test_db.engine)
    result = repo.get_all("instagram")
    assert result == []

def test_workflow_repo_insert_returns_none(test_db):
    """Stub repo insert should return None for now."""
    repo = WorkflowRepository(test_db.engine)
    result = repo.insert("instagram", {"name": "test"})
    assert result is None
