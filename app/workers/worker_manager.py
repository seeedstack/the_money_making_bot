import logging
from app.core.models import Platform
from config.settings import settings

logger = logging.getLogger(__name__)

class WorkerManager:
    """Spawn, manage, stop all workers."""

    def __init__(self):
        self.workers = []

    def start_all(self):
        """Start workers for all enabled platforms."""
        if settings.instagram_enabled:
            from app.workers.per_platform.trigger_monitor import TriggerMonitorWorker
            from app.workers.per_platform.message_engine import MessageEngineWorker
            from app.workers.per_platform.follow_recheck import FollowRecheckWorker

            trigger = TriggerMonitorWorker()
            message = MessageEngineWorker()
            follow = FollowRecheckWorker()

            for worker in [trigger, message, follow]:
                worker.start()
                self.workers.append(worker)

        logger.info("All workers started")

    def stop_all(self):
        """Stop all workers gracefully."""
        for worker in self.workers:
            worker.stop()
        logger.info("All workers stopped")
