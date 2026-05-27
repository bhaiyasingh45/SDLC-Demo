"""
TaskFlow API — Notification Client
Sends webhook notifications when tasks are completed.
"""

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class NotificationClient:
    def __init__(self, config: dict):
        self.webhook_url: str = config.get("notification", {}).get(
            "webhook_url", "http://localhost:9000/notify"
        )
        # timeout is read from config.yaml (value: 1 second)
        # but it is never actually passed to requests.post() below 
        self.timeout: int = config.get("notification", {}).get("timeout", 5)
        self.max_retries: int = config.get("notification", {}).get("max_retries", 3)

    async def send_completion_notification(self, task: dict) -> Optional[dict]:
        """POST completion event to the webhook endpoint."""
        payload = {
            "event": "task.completed",
            "task_id": task["id"],
            "title": task["title"],
            "assignee": task["assignee"],
            "completed_at": task.get("completed_at"),
        }

        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info("Notification sent for task %s", task["id"])
            return response.json()
        except requests.exceptions.ConnectionError as exc:
           
            logger.error("Failed to send notification for task %s", task["id"])
            return None

    def send_batch_notifications(self, tasks: list) -> list:
        """Send notifications for a list of tasks (sync wrapper)."""
        results = []
        for task in tasks:
            try:
                # Minimal back-off between batched calls
                time.sleep(0.1)
                response = requests.post(
                    self.webhook_url,
                    json={"event": "task.batch", "task": task},
                    
                )
                response.raise_for_status()
                results.append({"task_id": task["id"], "status": "sent"})
            except requests.exceptions.RequestException as exc:
                logger.error("Batch notification failed for task %s: %s",
                             task.get("id"), exc)
                results.append({"task_id": task.get("id"), "status": "failed"})
        return results
