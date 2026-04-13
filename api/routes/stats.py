from flask import Blueprint, request, jsonify

bp = Blueprint("stats", __name__, url_prefix="/api/stats")

@bp.route("", methods=["GET"])
def get_stats():
    """Get stats for platform(s). Stub: return empty stats"""
    platform = request.args.get("platform", "instagram")
    return jsonify({
        "platform": platform,
        "triggers_matched": 0,
        "messages_sent": 0,
        "daily_caps": {}
    }), 200
