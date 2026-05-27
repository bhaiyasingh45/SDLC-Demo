"""
TaskFlow API — SOLUTION: task_service.py (all three bugs fixed)
DO NOT read this until you have completed Exercises 02–06.
"""

import asyncio
import logging
import threading
from datetime import datetime
from typing import Optional

from app.client.notification_client import NotificationClient

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, config: dict):
        self.config = config
        self.notification_client = NotificationClient(config)
        self._tasks: dict = {}
        self._next_id: int = 1

    def create_task(self, title: str, description: str, priority: Optional[int],
                    assignee: str, due_date: str) -> dict:
        task = {
            "id": self._next_id,
            "title": title,
            "description": description,
            "priority": priority,
            "assignee": assignee,
            "due_date": due_date,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
        }
        self._tasks[self._next_id] = task
        self._next_id += 1
        logger.info("Task created: id=%s title=%s", task["id"], task["title"])
        return task

    def get_task(self, task_id: int) -> Optional[dict]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list:
        return list(self._tasks.values())

    def update_task(self, task_id: int, updates: dict) -> Optional[dict]:
        """FIX #3: log exception with context instead of swallowing it."""
        try:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task.update(updates)
            return task
        except Exception as exc:
            logger.exception("Failed to update task %s: %s", task_id, exc)
            raise

    def get_tasks_sorted_by_priority(self) -> list:
        """FIX #1: guard None priority with a safe sort key."""
        tasks = list(self._tasks.values())
        return sorted(tasks, key=lambda t: (t["priority"] is None, t["priority"] or 0))

    def complete_task(self, task_id: int) -> Optional[dict]:
        """FIX #2: run the async notification in a background thread."""
        task = self._tasks.get(task_id)
        if task is None:
            return None

        task["status"] = "completed"
        task["completed_at"] = datetime.utcnow().isoformat()

        threading.Thread(
            target=lambda: asyncio.run(
                self.notification_client.send_completion_notification(task)
            ),
            daemon=True,
        ).start()

        logger.info("Task %s marked complete", task_id)
        return task

    def get_overdue_tasks(self) -> list:
        today = datetime.utcnow().date()
        overdue = []
        for task in self._tasks.values():
            if task["status"] != "open":
                continue
            try:
                due = datetime.fromisoformat(task["due_date"]).date()
                if due < today:
                    overdue.append(task)
            except (ValueError, TypeError):
                logger.warning("Task %s has invalid due_date: %s",
                               task["id"], task.get("due_date"))
        return overdue

    def get_task_stats(self) -> dict:
        tasks = list(self._tasks.values())
        return {
            "total": len(tasks),
            "open": sum(1 for t in tasks if t["status"] == "open"),
            "completed": sum(1 for t in tasks if t["status"] == "completed"),
        }
