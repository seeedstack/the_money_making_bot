from flask import request, jsonify
from flask_login import login_required
from app.sessions import bp
from app.sessions.models import MessageSession, SessionStepHistory
from app.helpers import not_found
from app.messages import AppMessages


@bp.route("", methods=["GET"])
@login_required
def list_sessions():
    platform = request.args.get("platform", "instagram")
    state = request.args.get("state")
    q = MessageSession.query.filter_by(platform=platform, deleted_at=None)
    if state:
        q = q.filter_by(state=state)
    sessions = q.order_by(MessageSession.started_at.desc()).all()
    return jsonify({
        "sessions": [s.to_dict() for s in sessions],
        "platform": platform,
        "state": state,
    }), 200


@bp.route("/<session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    platform = request.args.get("platform", "instagram")
    session = MessageSession.query.filter_by(id=session_id, platform=platform, deleted_at=None).first()
    if not session:
        return not_found(AppMessages.SESSION_NOT_FOUND)
    return jsonify(session.to_dict()), 200


@bp.route("/<session_id>/trace", methods=["GET"])
@login_required
def get_trace(session_id):
    platform = request.args.get("platform", "instagram")
    history = (SessionStepHistory.query
               .filter_by(session_id=session_id, platform=platform)
               .order_by(SessionStepHistory.step_order.asc())
               .all())
    return jsonify({
        "session_id": session_id,
        "trace": [h.to_dict() for h in history],
    }), 200
