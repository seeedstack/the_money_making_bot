from app.core.models import MessageSession, SessionState

class StepExecutor:
    """Execute one workflow step, return next state."""

    def execute(self, session: MessageSession) -> MessageSession:
        """Stub: return session with state COMPLETED"""
        session.state = SessionState.COMPLETED
        return session
