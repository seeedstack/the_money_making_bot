from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional

class SessionState(str, Enum):
    STEP_RUNNING = "STEP_RUNNING"
    AWAITING_FOLLOW = "AWAITING_FOLLOW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"

class FollowStatus(str, Enum):
    FOLLOWING = "FOLLOWING"
    NOT_FOLLOWING = "NOT_FOLLOWING"
    NOT_APPLICABLE = "NOT_APPLICABLE"

@dataclass
class MessageSession:
    id: int
    platform: str
    username: str
    workflow_id: int
    current_step: int
    follow_status: FollowStatus
    state: SessionState
    started_at: datetime
    last_action_at: datetime
