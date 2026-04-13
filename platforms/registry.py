from core.models import Platform

class PlatformRegistry:
    """Map Platform enum → adapter instance."""

    def __init__(self):
        self.adapters = {}

    def register(self, platform: Platform, adapter):
        """Register adapter for platform."""
        self.adapters[platform] = adapter

    def get(self, platform: Platform):
        """Get adapter for platform. Stub: return None"""
        return self.adapters.get(platform)
