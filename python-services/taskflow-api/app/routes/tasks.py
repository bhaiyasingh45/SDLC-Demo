"""
TaskFlow API — Routes
Flask blueprint for the /tasks REST endpoints.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from app.service.task_service import TaskService

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# Injected by the application factory (app/__init__.py)
_task_service: TaskService = None  # type: ignore


def init_routes(service: TaskService) -> None:
    global _task_service
    _task_service = service


# -----------------------------------------------------------------------
# POST /tasks — create a new task
# -----------------------------------------------------------------------
@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["title", "assignee"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

   
    due_date_str = data.get("due_date", "")
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")  

    task = _task_service.create_task(
        title=data["title"],
        description=data.get("description", ""),
        priority=data.get("priority"),       
        assignee=data["assignee"],
        due_date=due_date.isoformat(),
    )
    return jsonify(task), 201


# -----------------------------------------------------------------------
# GET /tasks — list all tasks (optionally sorted by priority)
# -----------------------------------------------------------------------
@tasks_bp.route("", methods=["GET"])
def list_tasks():
    sort_by_priority = request.args.get("sort") == "priority"
    if sort_by_priority:
       
        tasks = _task_service.get_tasks_sorted_by_priority()
    else:
        tasks = _task_service.list_tasks()
    return jsonify(tasks), 200


# -----------------------------------------------------------------------
# GET /tasks/<task_id> — get a single task
# -----------------------------------------------------------------------
@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    task = _task_service.get_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200


# -----------------------------------------------------------------------
# PUT /tasks/<task_id>/complete — mark task as completed
# -----------------------------------------------------------------------
@tasks_bp.route("/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id: int):
    task = _task_service.complete_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task completed", "task": task}), 200


# -----------------------------------------------------------------------
# PUT /tasks/<task_id> — update task fields
# -----------------------------------------------------------------------
@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id: int):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    task = _task_service.update_task(task_id, data)

    if task is None:
        return jsonify({"error": "Task not found or update failed"}), 404
    return jsonify(task), 200


# -----------------------------------------------------------------------
# GET /tasks/stats — aggregate statistics
# -----------------------------------------------------------------------
@tasks_bp.route("/stats", methods=["GET"])
def task_stats():
    return jsonify(_task_service.get_task_stats()), 200


# -----------------------------------------------------------------------
# GET /tasks/overdue — list overdue tasks
# -----------------------------------------------------------------------
@tasks_bp.route("/overdue", methods=["GET"])
def overdue_tasks():
    return jsonify(_task_service.get_overdue_tasks()), 200
