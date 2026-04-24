import os
from api import create_app
from workers.worker_manager import WorkerManager
from config.settings import settings

if __name__ == "__main__":
    app = create_app()

    # Start workers
    manager = WorkerManager()
    manager.start_all()

    try:
        app.run(
            host="0.0.0.0",
            port=5010,
            debug=settings.flask_env == "development"
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        manager.stop_all()
