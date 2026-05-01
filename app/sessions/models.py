import uuid
from datetime import datetime, timezone
from app.extensions import db


class MessageSession(db.Model):
    __tablename__ = "message_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    username = db.Column(db.String(255), nullable=False)
    workflow_id = db.Column(db.String(36), db.ForeignKey("workflows.id"), nullable=False)
    current_step = db.Column(db.Integer, default=0)
    follow_status = db.Column(db.String(32), default="NOT_FOLLOWING")
    state = db.Column(db.String(32), default="STEP_RUNNING")
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_action_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                               onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = db.Column(db.DateTime, nullable=True)

    history = db.relationship("SessionStepHistory", backref="session",
                              cascade="all, delete-orphan",
                              order_by="SessionStepHistory.step_order")

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "username": self.username,
            "workflow_id": self.workflow_id,
            "current_step": self.current_step,
            "follow_status": self.follow_status,
            "state": self.state,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_action_at": self.last_action_at.isoformat() if self.last_action_at else None,
        }


class SessionStepHistory(db.Model):
    __tablename__ = "session_step_history"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey("message_sessions.id"), nullable=False, index=True)
    platform = db.Column(db.String(32), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(16), default="completed")
    message_preview = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "step_order": self.step_order,
            "step_type": self.step_type,
            "status": self.status,
            "message_preview": self.message_preview,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
