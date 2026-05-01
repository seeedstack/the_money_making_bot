from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class StepType(str, Enum):
    CHECK_FOLLOW = "check_follow"
    SEND_MESSAGE = "send_message"
    WAIT_FOR_FOLLOW = "wait_for_follow"
    DELAY = "delay"

class SendIf(str, Enum):
    FOLLOWING = "following"
    NOT_FOLLOWING = "not_following"
    NOW_FOLLOWING = "now_following"
    ALWAYS = "always"

@dataclass
class WorkflowStep:
    step_order: int
    step_type: StepType
    message_template: Optional[str] = None
    send_if: Optional[SendIf] = None
    delay_seconds: Optional[int] = None

@dataclass
class Workflow:
    id: int
    name: str
    platform: str
    trigger_keyword: str
    source_id: str
    priority: int
    active: bool
    match_mode: str
    link: Optional[str] = None
    steps: list = field(default_factory=list)
