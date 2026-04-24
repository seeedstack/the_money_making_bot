from flask import Blueprint, request, jsonify
from datetime import datetime
from db.database import Database
from sqlalchemy import text

bp = Blueprint("stats", __name__, url_prefix="/api/stats")

@bp.route("", methods=["GET"])
def get_stats():
    """Get stats for platform(s)."""
    platform = request.args.get("platform", "instagram")
    db = Database()

    with db.engine.connect() as conn:
        if platform == "all":
            rows = conn.execute(text(
                "SELECT platform, SUM(triggers_matched) as triggers, SUM(messages_sent) as messages "
                "FROM platform_daily_counts WHERE date = DATE('now') "
                "GROUP BY platform"
            )).fetchall()
            stats = [
                {
                    "platform": row[0],
                    "triggers_matched": row[1] or 0,
                    "messages_sent": row[2] or 0
                }
                for row in rows
            ]
            return jsonify({"stats": stats}), 200
        else:
            row = conn.execute(text(
                "SELECT SUM(triggers_matched) as triggers, SUM(messages_sent) as messages "
                "FROM platform_daily_counts WHERE platform = :platform AND date = DATE('now')"
            ), {"platform": platform}).fetchone()

            triggers = row[0] or 0 if row else 0
            messages = row[1] or 0 if row else 0

            return jsonify({
                "platform": platform,
                "triggers_matched": triggers,
                "messages_sent": messages
            }), 200
