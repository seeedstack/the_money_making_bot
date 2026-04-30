import logging
from app.core.models import Platform
from app.workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

class MessageEngineWorker(BaseWorker):
    """Execute pending workflow steps."""

    platform = Platform.INSTAGRAM

    def run_cycle(self):
        """Process sessions. Stub: log and return"""
        logger.debug(f"[{self.platform}] MessageEngine cycle - processing sessions...")
