from flask import request, jsonify
from flask_login import login_required
from app.bot import bp
from app.platforms.models import PlatformSettings

_ALL_PLATFORMS = ["instagram", "twitter", "telegram"]


@bp.route("/pause", methods=["POST"])
@login_required
def pause_bot():
    platform = request.args.get("platform", "all")
    targets = _ALL_PLATFORMS if platform == "all" else [platform]
    for p in targets:
        PlatformSettings.set(p, "paused", "true")
    return jsonify({"status": "paused", "platform": platform}), 200


@bp.route("/resume", methods=["POST"])
@login_required
def resume_bot():
    platform = request.args.get("platform", "all")
    targets = _ALL_PLATFORMS if platform == "all" else [platform]
    for p in targets:
        PlatformSettings.set(p, "paused", "false")
    return jsonify({"status": "running", "platform": platform}), 200


@bp.route("/restart", methods=["POST"])
@login_required
def restart_bot():
    platform = request.args.get("platform", "all")
    return jsonify({"status": "restarting", "platform": platform}), 200
