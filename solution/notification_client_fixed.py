"""
TaskFlow API — SOLUTION: notification_client.py (Bug #4 and #5 fixed)
DO NOT read this until you have completed Exercises 02–06.
"""

import asyncio
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
        self.timeout: int = config.get("notification", {}).get("timeout", 5)
        self.max_retries: int = config.get("notification", {}).get("max_retries", 3)

    async def send_completion_notification(self, task: dict) -> Optional[dict]:
        """FIX #4 + #5: pass timeout and add exponential-back-off retry."""
        payload = {
            "event": "task.completed",
            "task_id": task["id"],
            "title": task["title"],
            "assignee": task["assignee"],
            "completed_at": task.get("completed_at"),
        }

        for attempt in range(self.max_retries):
            try:
                # FIX #4: timeout=self.timeout is now passed
                response = requests.post(
                    self.webhook_url, json=payload, timeout=self.timeout
                )
                response.raise_for_status()
                logger.info("Notification sent for task %s", task["id"])
                return response.json()
            except requests.exceptions.ConnectionError as exc:
                # FIX #5: retry with exponential back-off instead of giving up
                if attempt < self.max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning(
                        "Retrying notification for task %s (attempt %d/%d, wait=%ds): %s",
                        task["id"], attempt + 1, self.max_retries, wait, exc,
                    )
                    await asyncio.sleep(wait)
                else:
                    logger.exception(
                        "Notification permanently failed for task %s after %d retries",
                        task["id"], self.max_retries,
                    )
                    return None
            except requests.exceptions.RequestException as exc:
                logger.exception("Notification failed for task %s: %s", task["id"], exc)
                return None

        return None

    def send_batch_notifications(self, tasks: list) -> list:
        results = []
        for task in tasks:
            try:
                time.sleep(0.1)
                # FIX #4 applied here too
                response = requests.post(
                    self.webhook_url,
                    json={"event": "task.batch", "task": task},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                results.append({"task_id": task["id"], "status": "sent"})
            except requests.exceptions.RequestException as exc:
                logger.exception("Batch notification failed for task %s: %s",
                                 task.get("id"), exc)
                results.append({"task_id": task.get("id"), "status": "failed"})
        return results
