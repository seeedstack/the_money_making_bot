from app.core.models import StepType

class StepRegistry:
    """Map StepType → handler class."""

    def __init__(self):
        self.handlers = {}

    def register(self, step_type: StepType, handler_class):
        """Register handler for step type."""
        self.handlers[step_type] = handler_class

    def get(self, step_type: StepType):
        """Get handler for step type. Stub: return None"""
        return self.handlers.get(step_type)
