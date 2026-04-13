import logging
from core.models import Platform
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

class FollowRecheckWorker(BaseWorker):
    """Recheck follow status for awaiting sessions."""

    platform = Platform.INSTAGRAM

    def run_cycle(self):
        """Recheck follows. Stub: log and return"""
        logger.debug(f"[{self.platform}] FollowRecheck cycle - checking...")
