from flask import Blueprint, request, jsonify

bp = Blueprint("checks", __name__, url_prefix="/api/pending-checks")

@bp.route("", methods=["GET"])
def get_pending_checks():
    """Get pending follow checks. Stub: return []"""
    platform = request.args.get("platform", "instagram")
    return jsonify({"checks": [], "platform": platform}), 200

@bp.route("/<int:check_id>/force", methods=["POST"])
def force_check(check_id):
    """Force a check now. Stub: return ok"""
    return jsonify({"id": check_id, "forced": True}), 200

@bp.route("/<int:check_id>/abandon", methods=["POST"])
def abandon_check(check_id):
    """Abandon a check. Stub: return ok"""
    return jsonify({"id": check_id, "abandoned": True}), 200
