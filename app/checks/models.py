import uuid
from datetime import datetime, timezone
from app.extensions import db


class PendingFollowCheck(db.Model):
    __tablename__ = "pending_follow_checks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    session_id = db.Column(db.String(36), db.ForeignKey("message_sessions.id"), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    check_after = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "session_id": self.session_id,
            "username": self.username,
            "check_after": self.check_after.isoformat() if self.check_after else None,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
        }
