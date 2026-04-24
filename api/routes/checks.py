from flask import Blueprint, request, jsonify
from db.database import Database
from db.repositories.follow_check_repo import FollowCheckRepository
from datetime import datetime

bp = Blueprint("checks", __name__, url_prefix="/api/pending-checks")

def get_repo():
    db = Database()
    return FollowCheckRepository(db.engine)

@bp.route("", methods=["GET"])
def get_pending_checks():
    """Get pending follow checks."""
    platform = request.args.get("platform", "instagram")
    repo = get_repo()
    checks = repo.get_pending(platform)
    return jsonify({
        "checks": checks,
        "platform": platform,
        "count": len(checks)
    }), 200

@bp.route("/<int:check_id>/force", methods=["POST"])
def force_check(check_id):
    """Force a check now."""
    platform = request.args.get("platform", "instagram")
    repo = get_repo()
    repo.update(platform, check_id, {"check_after": datetime.now()})
    return jsonify({"id": check_id, "forced": True}), 200

@bp.route("/<int:check_id>/abandon", methods=["POST"])
def abandon_check(check_id):
    """Abandon a check (set max attempts = current attempts)."""
    platform = request.args.get("platform", "instagram")
    db = Database()
    with db.engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text(
            "UPDATE pending_follow_checks SET max_attempts = attempts WHERE id = :id AND platform = :platform"
        ), {"id": check_id, "platform": platform})
        conn.commit()
    return jsonify({"id": check_id, "abandoned": True}), 200
