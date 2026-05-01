from flask import jsonify
from flask_login import login_required
from app.platforms import bp
from config.settings import settings


@bp.route("", methods=["GET"])
@login_required
def list_platforms():
    platforms = [
        {
            "name": "instagram",
            "enabled": settings.instagram_enabled,
            "status": "RUNNING" if settings.instagram_enabled else "DISABLED",
            "supports_follow_gate": True,
        },
        {
            "name": "twitter",
            "enabled": settings.twitter_enabled,
            "status": "RUNNING" if settings.twitter_enabled else "DISABLED",
            "supports_follow_gate": True,
        },
        {
            "name": "telegram",
            "enabled": settings.telegram_enabled,
            "status": "RUNNING" if settings.telegram_enabled else "DISABLED",
            "supports_follow_gate": False,
        },
    ]
    return jsonify({"platforms": platforms}), 200


@bp.route("/<name>/enable", methods=["POST"])
@login_required
def enable_platform(name):
    return jsonify({"name": name, "enabled": True}), 200


@bp.route("/<name>/disable", methods=["POST"])
@login_required
def disable_platform(name):
    return jsonify({"name": name, "enabled": False}), 200
