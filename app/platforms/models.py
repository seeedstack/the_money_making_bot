import uuid
from datetime import datetime, timezone
from app.extensions import db


class PlatformSettings(db.Model):
    __tablename__ = "platform_settings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False, index=True)
    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint("platform", "key", name="uq_platform_key"),)

    def to_dict(self):
        return {"platform": self.platform, "key": self.key, "value": self.value}

    @classmethod
    def get(cls, platform: str, key: str, default=None):
        row = cls.query.filter_by(platform=platform, key=key).first()
        return row.value if row else default

    @classmethod
    def set(cls, platform: str, key: str, value: str):
        from app.extensions import db as _db
        row = cls.query.filter_by(platform=platform, key=key).first()
        if row:
            row.value = value
        else:
            row = cls(platform=platform, key=key, value=value)
            _db.session.add(row)
        _db.session.commit()


class PlatformDailyCount(db.Model):
    __tablename__ = "platform_daily_counts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    platform = db.Column(db.String(32), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    messages_sent = db.Column(db.Integer, default=0)
    triggers_matched = db.Column(db.Integer, default=0)

    __table_args__ = (db.UniqueConstraint("platform", "date", name="uq_platform_date"),)

    def to_dict(self):
        return {
            "platform": self.platform, "date": self.date,
            "messages_sent": self.messages_sent,
            "triggers_matched": self.triggers_matched,
        }
