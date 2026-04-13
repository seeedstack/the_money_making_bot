from flask import Blueprint, request, jsonify

bp = Blueprint("bot", __name__, url_prefix="/api/bot")

@bp.route("/pause", methods=["POST"])
def pause_bot():
    """Pause bot for platform. Stub: return ok"""
    platform = request.args.get("platform", "all")
    return jsonify({"status": "paused", "platform": platform}), 200

@bp.route("/resume", methods=["POST"])
def resume_bot():
    """Resume bot for platform. Stub: return ok"""
    platform = request.args.get("platform", "all")
    return jsonify({"status": "running", "platform": platform}), 200

@bp.route("/restart", methods=["POST"])
def restart_bot():
    """Restart bot for platform. Stub: return ok"""
    platform = request.args.get("platform", "all")
    return jsonify({"status": "restarting", "platform": platform}), 200
