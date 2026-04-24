from flask import Blueprint, request, jsonify
from db.database import Database
from db.repositories.session_repo import SessionRepository

bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

def get_repo():
    db = Database()
    return SessionRepository(db.engine)

@bp.route("", methods=["GET"])
def get_sessions():
    """Get sessions for platform, optionally filtered."""
    platform = request.args.get("platform", "instagram")
    state = request.args.get("state")
    repo = get_repo()
    sessions = repo.get_all(platform, state)
    return jsonify({
        "sessions": [
            {
                "id": s.id,
                "platform": s.platform,
                "username": s.username,
                "workflow_id": s.workflow_id,
                "current_step": s.current_step,
                "follow_status": s.follow_status.value if hasattr(s.follow_status, 'value') else s.follow_status,
                "state": s.state.value,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "last_action_at": s.last_action_at.isoformat() if s.last_action_at else None
            }
            for s in sessions
        ],
        "platform": platform,
        "state": state
    }), 200

@bp.route("/<int:session_id>", methods=["GET"])
def get_session(session_id):
    """Get session by ID."""
    platform = request.args.get("platform", "instagram")
    repo = get_repo()
    session = repo.get_by_id(platform, session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify({
        "id": session.id,
        "platform": session.platform,
        "username": session.username,
        "workflow_id": session.workflow_id,
        "current_step": session.current_step,
        "follow_status": session.follow_status.value if hasattr(session.follow_status, 'value') else session.follow_status,
        "state": session.state.value,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "last_action_at": session.last_action_at.isoformat() if session.last_action_at else None
    }), 200
