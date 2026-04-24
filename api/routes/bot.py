from flask import Blueprint, request, jsonify
from db.database import Database
from db.repositories.settings_repo import SettingsRepository

bp = Blueprint("bot", __name__, url_prefix="/api/bot")

def get_settings_repo():
    db = Database()
    return SettingsRepository(db.engine)

@bp.route("/pause", methods=["POST"])
def pause_bot():
    """Pause bot for platform."""
    platform = request.args.get("platform", "all")
    repo = get_settings_repo()

    if platform == "all":
        for p in ["instagram", "twitter", "telegram"]:
            repo.set(p, "paused", "true")
    else:
        repo.set(platform, "paused", "true")

    return jsonify({"status": "paused", "platform": platform}), 200

@bp.route("/resume", methods=["POST"])
def resume_bot():
    """Resume bot for platform."""
    platform = request.args.get("platform", "all")
    repo = get_settings_repo()

    if platform == "all":
        for p in ["instagram", "twitter", "telegram"]:
            repo.set(p, "paused", "false")
    else:
        repo.set(platform, "paused", "false")

    return jsonify({"status": "running", "platform": platform}), 200

@bp.route("/restart", methods=["POST"])
def restart_bot():
    """Restart bot for platform (stub)."""
    platform = request.args.get("platform", "all")
    return jsonify({"status": "restarting", "platform": platform}), 200
