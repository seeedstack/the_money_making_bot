from flask import Blueprint, request, jsonify
from config.settings import settings
from core.models.platform import Platform

bp = Blueprint("platforms", __name__, url_prefix="/api/platforms")

@bp.route("", methods=["GET"])
def get_platforms():
    """List all platforms and status."""
    platforms = []

    platforms.append({
        "name": "instagram",
        "enabled": settings.instagram_enabled,
        "status": "RUNNING" if settings.instagram_enabled else "DISABLED"
    })
    platforms.append({
        "name": "twitter",
        "enabled": settings.twitter_enabled,
        "status": "RUNNING" if settings.twitter_enabled else "DISABLED"
    })
    platforms.append({
        "name": "telegram",
        "enabled": settings.telegram_enabled,
        "status": "RUNNING" if settings.telegram_enabled else "DISABLED"
    })

    return jsonify({"platforms": platforms}), 200

@bp.route("/<name>/enable", methods=["POST"])
def enable_platform(name):
    """Enable platform (stub)."""
    return jsonify({"name": name, "enabled": True}), 200

@bp.route("/<name>/disable", methods=["POST"])
def disable_platform(name):
    """Disable platform (stub)."""
    return jsonify({"name": name, "enabled": False}), 200
