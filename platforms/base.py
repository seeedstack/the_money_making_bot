from abc import ABC
from core.models import Platform

class BasePlatformAdapter(ABC):
    """Base adapter. All platforms inherit from this."""

    platform: Platform

    def read_triggers(self, source_id: str):
        raise NotImplementedError

    def send_message(self, recipient_id: str, text: str):
        raise NotImplementedError

    def check_follow(self, username: str):
        raise NotImplementedError

    def supports_follow_gate(self) -> bool:
        raise NotImplementedError
