from sqlalchemy import text

class ScanRepository:
    """Query trigger scans by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def insert(self, platform: str, scan_data: dict):
        """Insert trigger scan."""
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "INSERT INTO trigger_scans (platform, source_id, username, content, matched_workflow_id) "
                "VALUES (:platform, :source_id, :username, :content, :matched_workflow_id)"
            ), {
                "platform": platform,
                "source_id": scan_data["source_id"],
                "username": scan_data["username"],
                "content": scan_data["content"],
                "matched_workflow_id": scan_data.get("matched_workflow_id")
            })
            conn.commit()
            return result.lastrowid

    def get_recent(self, platform: str, limit: int = 100) -> list:
        """Get recent scans."""
        with self.engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT id, platform, source_id, username, content, matched_workflow_id, scanned_at "
                "FROM trigger_scans WHERE platform = :platform ORDER BY scanned_at DESC LIMIT :limit"
            ), {"platform": platform, "limit": limit}).fetchall()

            return [
                {
                    "id": row[0],
                    "platform": row[1],
                    "source_id": row[2],
                    "username": row[3],
                    "content": row[4],
                    "matched_workflow_id": row[5],
                    "scanned_at": row[6]
                }
                for row in rows
            ]
