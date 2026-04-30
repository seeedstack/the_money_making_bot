from flask_login import current_user
from flask_socketio import disconnect
from app.extensions import socketio


@socketio.on("connect")
def handle_connect():
    if not current_user.is_authenticated:
        disconnect()
        return False


def emit_event(event_name: str, data: dict, platform: str = None):
    payload = {"event": event_name, "data": data}
    if platform:
        payload["platform"] = platform
    socketio.emit(event_name, payload)
