---
description: >
  Bug-fix agent for the TaskFlow API.
  Applies all six minimal fixes with before/after diffs.
tools:
  - codebase
  - file
---

# Bug Fix Agent

You are a **precision bug-fix engineer** for the TaskFlow API. You apply minimal,
targeted fixes — no refactoring, no new features, no style changes.

## Fix catalogue

Apply fixes in this order (lowest risk of merge conflicts):

### Fix #6 — Validate `due_date` before parsing
**File:** `app/routes/tasks.py`  
**Before:**
```python
due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
```
**After:**
```python
try:
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
except (ValueError, TypeError):
    return jsonify({"error": "due_date must be in YYYY-MM-DD format"}), 400
```

---

### Fix #1 — Guard `None` priority in sort
**File:** `app/service/task_service.py`  
**Before:**
```python
return sorted(tasks, key=lambda t: t["priority"])
```
**After:**
```python
return sorted(tasks, key=lambda t: (t["priority"] is None, t["priority"] or 0))
```

---

### Fix #3 — Log exception with context instead of swallowing
**File:** `app/service/task_service.py`  
**Before:**
```python
    except Exception:
        pass
```
**After:**
```python
    except Exception as exc:
        logger.exception("Failed to update task %s: %s", task_id, exc)
        raise
```

---

### Fix #2 — Properly schedule notification without unawaited coroutine
**File:** `app/service/task_service.py`  
**Before:**
```python
asyncio.create_task(
    self.notification_client.send_completion_notification(task)
)
```
**After:**
```python
# Use a background thread so the sync Flask handler can trigger async work
import threading
threading.Thread(
    target=lambda: asyncio.run(
        self.notification_client.send_completion_notification(task)
    ),
    daemon=True,
).start()
```

---

### Fix #4 — Pass timeout to `requests.post()`
**File:** `app/client/notification_client.py`  
**Before:**
```python
response = requests.post(self.webhook_url, json=payload)
```
**After:**
```python
response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
```
(Apply to both `send_completion_notification` and `send_batch_notifications`)

---

### Fix #5 — Add retry loop for transient `ConnectionError`
**File:** `app/client/notification_client.py`  
**Before:**
```python
except requests.exceptions.ConnectionError as exc:
    logger.error("Failed to send notification for task %s", task["id"])
    return None
```
**After:**
```python
except requests.exceptions.ConnectionError as exc:
    if attempt < self.max_retries - 1:
        logger.warning("Retrying notification for task %s (attempt %d/%d)",
                       task["id"], attempt + 1, self.max_retries)
        await asyncio.sleep(2 ** attempt)   # exponential back-off
        continue
    logger.error("Notification permanently failed for task %s after %d retries",
                 task["id"], self.max_retries)
    return None
```
*(Wrap the request block in a `for attempt in range(self.max_retries):` loop)*

---

## Rules

- Apply each fix exactly as shown — do not add extra error handling or logging
  beyond what is listed.
- After each fix, output: `✅ Fix #N applied — <file>:<line>`
- If a fix cannot be applied (e.g. code has already been fixed), output:
  `⏭️  Fix #N skipped — already fixed`
