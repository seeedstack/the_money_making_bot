from sqlalchemy import text
from datetime import datetime

class FollowCheckRepository:
    """Query pending follow checks by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get_pending(self, platform: str) -> list:
        """Get pending checks due now."""
        with self.engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT id, platform, session_id, username, check_after, attempts, max_attempts "
                "FROM pending_follow_checks WHERE platform = :platform AND check_after <= CURRENT_TIMESTAMP "
                "AND attempts < max_attempts ORDER BY check_after ASC"
            ), {"platform": platform}).fetchall()

            return [
                {
                    "id": row[0],
                    "platform": row[1],
                    "session_id": row[2],
                    "username": row[3],
                    "check_after": row[4],
                    "attempts": row[5],
                    "max_attempts": row[6]
                }
                for row in rows
            ]

    def insert(self, platform: str, check_data: dict):
        """Insert pending check."""
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "INSERT INTO pending_follow_checks (platform, session_id, username, check_after, attempts, max_attempts) "
                "VALUES (:platform, :session_id, :username, :check_after, :attempts, :max_attempts)"
            ), {
                "platform": platform,
                "session_id": check_data["session_id"],
                "username": check_data["username"],
                "check_after": check_data["check_after"],
                "attempts": check_data.get("attempts", 0),
                "max_attempts": check_data.get("max_attempts", 10)
            })
            conn.commit()
            return result.lastrowid

    def update(self, platform: str, check_id: int, check_data: dict):
        """Update check."""
        with self.engine.connect() as conn:
            conn.execute(text(
                "UPDATE pending_follow_checks SET attempts = :attempts, check_after = :check_after "
                "WHERE id = :id AND platform = :platform"
            ), {
                "id": check_id,
                "platform": platform,
                "attempts": check_data.get("attempts"),
                "check_after": check_data.get("check_after")
            })
            conn.commit()
