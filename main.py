from app import create_app
from app.extensions import socketio
from app.workers.worker_manager import WorkerManager
from config.settings import settings

app = create_app()

if __name__ == "__main__":
    manager = WorkerManager()
    manager.start_all()

    try:
        socketio.run(app, host="0.0.0.0", port=5010, debug=settings.flask_env == "development",
                     allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
        manager.stop_all()
