from flask import Blueprint, request, jsonify

bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

@bp.route("", methods=["GET"])
def get_sessions():
    """Get sessions for platform, optionally filtered. Stub: return []"""
    platform = request.args.get("platform", "instagram")
    state = request.args.get("state")
    return jsonify({"sessions": [], "platform": platform, "state": state}), 200

@bp.route("/<int:session_id>", methods=["GET"])
def get_session(session_id):
    """Get session by ID. Stub: return session stub"""
    return jsonify({
        "id": session_id,
        "platform": "instagram",
        "username": "test_user",
        "state": "STEP_RUNNING",
        "current_step": 0
    }), 200
