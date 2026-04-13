from flask import Flask, jsonify
from flask_socketio import SocketIO
from config.settings import settings

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    """Flask app factory."""
    app = Flask(__name__, static_folder="../frontend", static_url_path="/")
    app.config["SECRET_KEY"] = settings.flask_secret

    socketio.init_app(app)

    # Register routes
    from api.routes import workflows, sessions, stats, checks, platforms, bot

    app.register_blueprint(workflows.bp)
    app.register_blueprint(sessions.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(checks.bp)
    app.register_blueprint(platforms.bp)
    app.register_blueprint(bot.bp)

    # Root route
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app
