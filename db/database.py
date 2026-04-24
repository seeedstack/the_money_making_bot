import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

class Database:
    """Database connection and migration runner."""

    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/theBot.db")

        # Create data directory if needed
        if "sqlite:///" in database_url:
            db_path = database_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.engine = create_engine(
            database_url,
            echo=False,
            poolclass=StaticPool if "sqlite" in database_url else None
        )
        self.migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")

    def run_migrations(self):
        """Run all migrations in order."""
        migration_files = sorted([
            f for f in os.listdir(self.migrations_dir)
            if f.endswith(".sql")
        ])

        with self.engine.connect() as conn:
            for migration_file in migration_files:
                path = os.path.join(self.migrations_dir, migration_file)
                with open(path, "r") as f:
                    sql = f.read()

                statements = [s.strip() for s in sql.split(";") if s.strip()]
                for stmt in statements:
                    conn.execute(text(stmt))

            conn.commit()

    def get_connection(self):
        """Get DB connection."""
        return self.engine.connect()
