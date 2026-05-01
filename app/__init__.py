import os
from flask import Flask, redirect, url_for, request, jsonify
from config.settings import settings
from app.extensions import db, socketio, login_manager


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/")
    app.config["SECRET_KEY"] = settings.flask_secret

    db_url = settings.database_url
    if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"):
        db_url = "sqlite:///" + os.path.abspath(db_url[len("sqlite:///"):])
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    from app.auth.models import DashboardUser

    @login_manager.user_loader
    def load_user(user_id):
        return DashboardUser()

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("auth.login"))

    from app.auth import bp as auth_bp
    from app.workflows import bp as workflows_bp
    from app.sessions import bp as sessions_bp
    from app.platforms import bp as platforms_bp
    from app.checks import bp as checks_bp
    from app.stats import bp as stats_bp
    from app.bot import bp as bot_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(workflows_bp, url_prefix="/api/workflows")
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(platforms_bp, url_prefix="/api/platforms")
    app.register_blueprint(checks_bp, url_prefix="/api/pending-checks")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")
    app.register_blueprint(bot_bp, url_prefix="/api/bot")

    @app.before_request
    def _api_auth():
        if not request.path.startswith("/api/"):
            return None
        from flask_login import current_user
        api_key = request.headers.get("X-Api-Key", "")
        if settings.dashboard_api_key and api_key == settings.dashboard_api_key:
            return None
        if current_user.is_authenticated:
            return None
        return jsonify({"error": "Unauthorized"}), 401

    from flask_login import login_required

    @app.route("/")
    @login_required
    def index():
        return app.send_static_file("index.html")

    from app import socket  # noqa: F401

    with app.app_context():
        db.create_all()

    return app
