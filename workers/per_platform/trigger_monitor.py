import logging
from core.models import Platform
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

class TriggerMonitorWorker(BaseWorker):
    """Monitor for keyword triggers in comments/replies."""

    platform = Platform.INSTAGRAM

    def run_cycle(self):
        """Scan for triggers. Stub: log and return"""
        logger.debug(f"[{self.platform}] TriggerMonitor cycle - scanning...")
