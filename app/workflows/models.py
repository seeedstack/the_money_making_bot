import uuid
from datetime import datetime, timezone
from app.extensions import db


class Workflow(db.Model):
    __tablename__ = "workflows"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    trigger_keyword = db.Column(db.String(255), nullable=False)
    source_id = db.Column(db.String(512), nullable=False)
    priority = db.Column(db.Integer, default=1)
    active = db.Column(db.Boolean, default=True)
    match_mode = db.Column(db.String(16), default="contains")
    link = db.Column(db.String(512), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    steps = db.relationship("WorkflowStep", backref="workflow",
                            cascade="all, delete-orphan",
                            order_by="WorkflowStep.step_order")

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "name": self.name,
            "trigger_keyword": self.trigger_keyword,
            "source_id": self.source_id,
            "priority": self.priority,
            "active": self.active,
            "match_mode": self.match_mode,
            "link": self.link,
            "steps": [s.to_dict() for s in self.steps],
        }


class WorkflowStep(db.Model):
    __tablename__ = "workflow_steps"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = db.Column(db.String(36), db.ForeignKey("workflows.id"), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(32), nullable=False)
    message_template = db.Column(db.Text, nullable=True)
    send_if = db.Column(db.String(32), nullable=True)
    delay_seconds = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "step_order": self.step_order,
            "step_type": self.step_type,
            "message_template": self.message_template,
            "send_if": self.send_if,
            "delay_seconds": self.delay_seconds,
        }
