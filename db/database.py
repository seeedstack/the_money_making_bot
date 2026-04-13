import os
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

class Database:
    """Database connection and migration runner."""

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/the-bot.db")

        # Create data directory if needed
        if "sqlite:///" in database_url:
            db_path = database_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.engine = create_engine(
            database_url,
            echo=False,
            poolclass=StaticPool if "sqlite" in database_url else None
        )

    def run_migrations(self):
        """Run all migrations. Stub: do nothing"""
        pass

    def get_connection(self):
        """Get DB connection."""
        return self.engine.connect()
