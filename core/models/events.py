from dataclasses import dataclass
from typing import Any

@dataclass
class SocketIOEvent:
    event_name: str
    data: dict[str, Any]
    platform: str
