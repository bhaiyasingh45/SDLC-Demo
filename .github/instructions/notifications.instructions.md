---
applyTo: "app/client/**"
---
# Notification Client Conventions

When reviewing or fixing the notification client:
- The `timeout` value MUST be read from `self.timeout` (set via config.yaml), never hardcoded.
- All `requests` calls MUST pass `timeout=self.timeout`.
- On `ConnectionError`, log with `logger.exception` and return `None` — do NOT silently pass.
- Retry logic should use exponential backoff with a max of 3 attempts.
- Never swallow exceptions silently with bare `except: pass`.
