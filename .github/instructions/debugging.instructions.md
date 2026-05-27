---
applyTo: "**"
---
# TaskFlow API — Debugging Conventions

You are assisting engineers debugging the TaskFlow API (Python 3.12, Flask 3.x).

## Investigation Order
When asked to debug a production error, always follow this sequence:
1. Read `observability/production-logs.txt` for the raw error.
2. Locate the stack frame in `app/service/`, `app/client/`, or `app/routes/`.
3. Check `config.yaml` — timeout, URL, and retry values live there.
4. Confirm the fix does not expose raw tracebacks to HTTP clients.

## Code Conventions
- Use `logger.exception(...)` (not `logger.error`) inside `except` blocks — it includes the full stack trace.
- Return `{"error": "..."}` JSON for all HTTP error responses — never expose Python tracebacks.
- All public service methods should return `None` (not raise) when a resource is not found.
- Never hardcode URLs, timeouts, or retry counts — read them from `config.yaml`.

## Fix Checklist
For every bug fix, confirm:
- [ ] The fix is minimal (no unrelated changes).
- [ ] `logger.exception` is used if logging inside an `except` block.
- [ ] No raw exception message reaches the HTTP response.
- [ ] A `curl` command is suggested to verify the fix.
