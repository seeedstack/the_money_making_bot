from flask import Blueprint, request, jsonify

bp = Blueprint("platforms", __name__, url_prefix="/api/platforms")

@bp.route("", methods=["GET"])
def get_platforms():
    """List all platforms and status. Stub: return instagram only"""
    return jsonify({
        "platforms": [
            {"name": "instagram", "enabled": True, "status": "RUNNING"}
        ]
    }), 200

@bp.route("/<name>/enable", methods=["POST"])
def enable_platform(name):
    """Enable platform. Stub: return ok"""
    return jsonify({"name": name, "enabled": True}), 200

@bp.route("/<name>/disable", methods=["POST"])
def disable_platform(name):
    """Disable platform. Stub: return ok"""
    return jsonify({"name": name, "enabled": False}), 200
