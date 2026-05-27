# P0 Incident Report — TaskFlow API
**Severity:** P0 — Production Down  
**Reported:** 2026-05-26 09:12 UTC  
**Service:** taskflow-api (v1.0.0, pod: taskflow-api-7d9f4b-xk2pw)  
**On-call:** You  

---

## Executive Summary

The TaskFlow API is experiencing a **cascade of production failures** affecting ~65 % of all API traffic. Users cannot create tasks with custom due dates, the priority-sorted task list endpoint crashes intermittently, and completion notifications are silently dropped. Engineering leadership has declared a P0 and engaged the on-call rotation.

---

## Observed Symptoms

| # | Symptom | Endpoint | Impact |
|---|---------|----------|--------|
| S1 | `500 Internal Server Error` when `due_date` is not `YYYY-MM-DD` | `POST /tasks` | ~30 % of new-task requests fail |
| S2 | `TypeError: '<' not supported between 'NoneType' and 'int'` | `GET /tasks?sort=priority` | Dashboard crashes for all users |
| S3 | Completion notifications never arrive in Slack/PagerDuty | `PUT /tasks/<id>/complete` | 100 % notification loss |
| S4 | Silent task-update failures — response is `404` but task exists | `PUT /tasks/<id>` | Update flow broken for 10 % of calls |
| S5 | Webhook calls hang indefinitely under slow network | `PUT /tasks/<id>/complete` | Thread pool exhaustion in staging |

---

## Stack Traces (from production-logs.txt)

### S1 — ValueError: malformed due_date
```
[2026-05-26 09:12:04] ERROR in tasks — 500 Internal Server Error
Traceback (most recent call last):
  File ".../app/routes/tasks.py", line 39, in create_task
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
ValueError: time data '31/12/2024' does not match format '%Y-%m-%d'
```

### S2 — TypeError: sort by priority with None
```
[2026-05-26 09:14:22] ERROR in tasks — 500 Internal Server Error
Traceback (most recent call last):
  File ".../app/service/task_service.py", line 62, in get_tasks_sorted_by_priority
    return sorted(tasks, key=lambda t: t["priority"])
TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

### S3 — asyncio RuntimeWarning
```
[2026-05-26 09:15:01] WARNING asyncio — coroutine 'send_completion_notification' was never awaited
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
```

### S4 — Silent update failure (no stack trace — exception swallowed)
```
[2026-05-26 09:17:45] INFO taskflow — PUT /tasks/7  →  404
# No traceback. No warning. The exception was silently swallowed in update_task().
```

### S5 — Thread hang (timeout not enforced)
```
[2026-05-26 09:19:02] ERROR notification — Failed to send notification for task 12
# Thread blocked for 4m 32s — default socket timeout, not the configured 1 s.
```

---

## Affected Code Files

| File | Bugs |
|------|------|
| `app/routes/tasks.py` | Bug #6 — no due_date validation |
| `app/service/task_service.py` | Bug #1 (None priority), Bug #2 (unawaited coroutine), Bug #3 (swallowed exception) |
| `app/client/notification_client.py` | Bug #4 (timeout not passed), Bug #5 (no retry) |
| `config.yaml` | Bug #4 root — timeout declared but unused |

---

## Resolution Checklist

- [ ] Fix Bug #6 — validate `due_date` format before parsing  
- [ ] Fix Bug #1 — guard against `None` priority in sort  
- [ ] Fix Bug #2 — properly await notification coroutine  
- [ ] Fix Bug #3 — log exception with context, don't swallow  
- [ ] Fix Bug #4 — pass `self.timeout` to `requests.post()`  
- [ ] Fix Bug #5 — add retry loop for transient `ConnectionError`  
