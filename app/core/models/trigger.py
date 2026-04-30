from dataclasses import dataclass
from datetime import datetime

@dataclass
class TriggerEvent:
    platform: str
    source_id: str
    username: str
    content: str
    matched_keyword: str
    detected_at: datetime
