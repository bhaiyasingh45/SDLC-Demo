# TaskFlow API — Copilot Instructions

You are assisting engineers working on the **TaskFlow API** — a Python Flask task
management service currently experiencing a P0 production incident.

## Repository context

- **Language:** Python 3.12, Flask 3.x
- **Structure:** `app/service/`, `app/client/`, `app/routes/`
- **Known incident:** Six bugs cause intermittent 500 errors, silent notification
  failures, and thread-pool exhaustion. See `observability/incident-report.md`.

## Coding conventions

- Use `logger.exception(...)` (not `logger.error(...)`) when logging inside an
  `except` block — this includes the stack trace automatically.
- All public service methods should return `None` rather than raising when a
  resource is not found.
- Never expose raw Python tracebacks to HTTP clients — return `{"error": "..."}` JSON.
- Config values live in `config.yaml` — never hardcode URLs, timeouts, or retries.

## When asked to fix a bug

1. Show the **before** and **after** diff.
2. Explain why the old code was wrong in one sentence.
3. Suggest a `curl` command to verify the fix.

## Agents available

- `debug-agent` — general debugging assistant
- `log-analysis-agent` — reads production logs and produces a Bug Inventory
- `root-cause-agent` — traces symptoms to root causes
- `bug-fix-agent` — applies all fixes with minimal diffs

## MCP context

When MCP filesystem tools are available, prefer reading files directly rather
than asking the engineer to paste content.
