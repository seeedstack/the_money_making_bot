import pytest
from db.database import Database

@pytest.fixture
def test_db():
    """Create temp test database."""
    db = Database("sqlite:///:memory:")
    db.run_migrations()
    yield db

@pytest.fixture
def mock_instagram_adapter():
    """Mock Instagram adapter for tests."""
    from platforms.instagram import InstagramAdapter
    return InstagramAdapter(account_id=999)
