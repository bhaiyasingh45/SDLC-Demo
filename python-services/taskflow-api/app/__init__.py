"""TaskFlow API — Application Factory"""

import logging
import yaml
from flask import Flask, jsonify

from app.routes.tasks import tasks_bp, init_routes
from app.service.task_service import TaskService


def create_app(config_path: str = "config.yaml") -> Flask:
    app = Flask(__name__)

    # Load YAML config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )

    # Wire up service and routes
    service = TaskService(config)
    init_routes(service)
    app.register_blueprint(tasks_bp)

    @app.get("/")
    def root():
        return jsonify({
            "service": "taskflow-api",
            "status": "ok",
            "endpoints": [
                "/tasks",
                "/tasks/stats",
                "/tasks/overdue",
                "/health",
            ],
        }), 200

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app
