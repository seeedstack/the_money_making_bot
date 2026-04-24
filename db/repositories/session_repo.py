from sqlalchemy import text
from core.models.session import MessageSession, SessionState

class SessionRepository:
    """Query message sessions by platform."""

    def __init__(self, db_engine):
        self.engine = db_engine

    def get_all(self, platform: str, state: str = None) -> list:
        """Get sessions for platform, optionally filtered by state."""
        with self.engine.connect() as conn:
            query = "SELECT id, platform, username, workflow_id, current_step, follow_status, state, started_at, last_action_at FROM message_sessions WHERE platform = :platform"
            params = {"platform": platform}

            if state:
                query += " AND state = :state"
                params["state"] = state

            query += " ORDER BY started_at DESC"
            rows = conn.execute(text(query), params).fetchall()

            return [
                MessageSession(
                    id=row[0],
                    platform=row[1],
                    username=row[2],
                    workflow_id=row[3],
                    current_step=row[4],
                    follow_status=row[5],
                    state=SessionState(row[6]),
                    started_at=row[7],
                    last_action_at=row[8]
                )
                for row in rows
            ]

    def get_by_id(self, platform: str, session_id: int):
        """Get session by ID."""
        with self.engine.connect() as conn:
            row = conn.execute(text(
                "SELECT id, platform, username, workflow_id, current_step, follow_status, state, started_at, last_action_at "
                "FROM message_sessions WHERE id = :id AND platform = :platform"
            ), {"id": session_id, "platform": platform}).fetchone()

            if not row:
                return None

            return MessageSession(
                id=row[0],
                platform=row[1],
                username=row[2],
                workflow_id=row[3],
                current_step=row[4],
                follow_status=row[5],
                state=SessionState(row[6]),
                started_at=row[7],
                last_action_at=row[8]
            )

    def insert(self, platform: str, session_data: dict):
        """Insert session."""
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "INSERT INTO message_sessions (platform, username, workflow_id, current_step, follow_status, state) "
                "VALUES (:platform, :username, :workflow_id, :current_step, :follow_status, :state)"
            ), {
                "platform": platform,
                "username": session_data["username"],
                "workflow_id": session_data["workflow_id"],
                "current_step": session_data.get("current_step", 0),
                "follow_status": session_data.get("follow_status", "NOT_FOLLOWING"),
                "state": session_data.get("state", "STEP_RUNNING")
            })
            conn.commit()
            return result.lastrowid

    def update(self, platform: str, session_id: int, session_data: dict):
        """Update session."""
        with self.engine.connect() as conn:
            conn.execute(text(
                "UPDATE message_sessions SET current_step = :current_step, follow_status = :follow_status, state = :state, last_action_at = CURRENT_TIMESTAMP "
                "WHERE id = :id AND platform = :platform"
            ), {
                "id": session_id,
                "platform": platform,
                "current_step": session_data.get("current_step"),
                "follow_status": session_data.get("follow_status"),
                "state": session_data.get("state")
            })
            conn.commit()
