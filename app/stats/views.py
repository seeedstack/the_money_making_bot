from datetime import date
from flask import request, jsonify
from flask_login import login_required
from app.stats import bp
from app.platforms.models import PlatformDailyCount


@bp.route("", methods=["GET"])
@login_required
def get_stats():
    platform = request.args.get("platform", "instagram")
    today = date.today().isoformat()

    if platform == "all":
        rows = PlatformDailyCount.query.filter_by(date=today).all()
        return jsonify({"stats": [r.to_dict() for r in rows]}), 200

    row = PlatformDailyCount.query.filter_by(platform=platform, date=today).first()
    return jsonify({
        "platform": platform,
        "triggers_matched": row.triggers_matched if row else 0,
        "messages_sent": row.messages_sent if row else 0,
    }), 200
