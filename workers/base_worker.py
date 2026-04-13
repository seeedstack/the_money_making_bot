import threading
import time
import logging
from abc import ABC, abstractmethod
from core.models import Platform

logger = logging.getLogger(__name__)

class BaseWorker(ABC):
    """Base worker. All platform workers inherit from this."""

    platform: Platform
    enabled: bool = True

    def __init__(self):
        self.thread = None
        self.running = False

    def start(self):
        """Start worker thread."""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"{self.__class__.__name__} started for {self.platform}")

    def stop(self):
        """Stop worker gracefully."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info(f"{self.__class__.__name__} stopped for {self.platform}")

    def _run_loop(self):
        """Internal run loop."""
        while self.running:
            try:
                if self.enabled:
                    self.run_cycle()
            except Exception as e:
                self.on_error(e)
            time.sleep(1)

    @abstractmethod
    def run_cycle(self):
        """Override in subclass. Called once per cycle."""
        pass

    def on_error(self, e: Exception):
        """Handle error. Override in subclass if needed."""
        logger.error(f"Error in {self.__class__.__name__}: {e}")
