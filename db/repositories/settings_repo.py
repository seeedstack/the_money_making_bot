from sqlalchemy import text

class SettingsRepository:
    """Store and retrieve per-platform settings (including encrypted credentials)."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get(self, platform: str, key: str) -> str:
        """Get setting value."""
        with self.engine.connect() as conn:
            row = conn.execute(text(
                "SELECT value FROM platform_settings WHERE platform = :platform AND key = :key"
            ), {"platform": platform, "key": key}).fetchone()
            return row[0] if row else None

    def set(self, platform: str, key: str, value: str):
        """Set setting value (value may be encrypted)."""
        with self.engine.connect() as conn:
            conn.execute(text(
                "INSERT INTO platform_settings (platform, key, value) VALUES (:platform, :key, :value) "
                "ON CONFLICT(platform, key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP"
            ), {"platform": platform, "key": key, "value": value})
            conn.commit()

    def get_all(self, platform: str) -> dict:
        """Get all settings for platform."""
        with self.engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT key, value FROM platform_settings WHERE platform = :platform"
            ), {"platform": platform}).fetchall()
            return {row[0]: row[1] for row in rows}
