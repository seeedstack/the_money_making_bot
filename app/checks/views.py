from datetime import datetime, timezone
from flask import request, jsonify
from flask_login import login_required
from app.checks import bp
from app.checks.models import PendingFollowCheck
from app.extensions import db
from app.helpers import not_found
from app.messages import AppMessages


@bp.route("", methods=["GET"])
@login_required
def list_checks():
    platform = request.args.get("platform", "instagram")
    checks = (PendingFollowCheck.query
              .filter_by(platform=platform)
              .filter(PendingFollowCheck.attempts < PendingFollowCheck.max_attempts)
              .order_by(PendingFollowCheck.check_after.asc())
              .all())
    return jsonify({"checks": [c.to_dict() for c in checks], "count": len(checks)}), 200


@bp.route("/<check_id>/force", methods=["POST"])
@login_required
def force_check(check_id):
    check = db.session.get(PendingFollowCheck, check_id)
    if not check:
        return not_found(AppMessages.CHECK_NOT_FOUND)
    check.check_after = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"id": check_id, "forced": True}), 200


@bp.route("/<check_id>/abandon", methods=["POST"])
@login_required
def abandon_check(check_id):
    check = db.session.get(PendingFollowCheck, check_id)
    if not check:
        return not_found(AppMessages.CHECK_NOT_FOUND)
    check.max_attempts = check.attempts
    db.session.commit()
    return jsonify({"id": check_id, "abandoned": True}), 200
