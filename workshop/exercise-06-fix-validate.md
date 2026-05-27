# Exercise 06 — Fix All Bugs & Validate with Agent Mode

**Duration:** ~15 minutes  
**Feature:** Agent Mode (multi-step edits), `bug-fix-agent`, Copilot CLI test scaffolding  
**Goal:** Apply all six fixes using the `bug-fix-agent` and the Copilot CLI, then
generate a regression test suite and confirm a green run.

---

## Background

**Agent Mode** in VS Code Copilot lets Copilot make multi-file edits autonomously.
Combined with the `bug-fix-agent`, you can apply all fixes in a single conversational
turn. The Copilot CLI then scaffolds tests so you don't have to write them manually.

---

## Step 6.1 — Switch to Agent Mode

1. Open Copilot Chat (`Ctrl+Alt+I`).
2. Set the mode dropdown to **Agent**.
3. Select the **bug-fix-agent** from the agent picker.

---

## Step 6.2 — Apply all six fixes

Type:

```
Apply all six fixes from the fix catalogue to the TaskFlow API codebase. 
Start with Fix #6, then #1, #3, #2, #4, #5 in that order.
For each fix, show the before/after diff and confirm it was applied.
```

The agent will:
1. Read each file using MCP filesystem tools.
2. Apply the minimal change defined in its fix catalogue.
3. Output a confirmation for each fix.

Review the diffs in VS Code's Source Control panel before accepting.

---

## Step 6.3 — Verify fixes manually with curl

After the agent applies each fix, run the corresponding curl command:

**Fix #6 — due_date validation:**
```bash
# Should return 400, not 500
curl -s -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","assignee":"alice","due_date":"bad-date"}' | python -m json.tool
# Expected: {"error": "due_date must be in YYYY-MM-DD format"}
```

**Fix #1 — None priority sort:**
```bash
# Create a task with no priority
curl -s -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"No priority task","assignee":"bob","due_date":"2024-12-31"}'

# Now sort — should return 200, not 500
curl -s http://localhost:5000/tasks?sort=priority | python -m json.tool
```

**Fix #2 — Notification (check logs):**
```bash
curl -s -X PUT http://localhost:5000/tasks/1/complete
# Check Flask terminal — should NOT show "coroutine was never awaited" warning
```

**Fix #3 — Exception logged:**
```bash
curl -s -X PUT http://localhost:5000/tasks/999 \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}'
# Check Flask terminal — should now show a logger.exception() line
```

**Fix #4 — Timeout enforced:**
```bash
# This is best verified in code review — confirm requests.post(..., timeout=self.timeout)
grep -n "requests.post" python-services/taskflow-api/app/client/notification_client.py
```

**Fix #5 — Retry logic:**
```bash
# Review code — confirm retry loop with exponential back-off
grep -A 10 "ConnectionError" python-services/taskflow-api/app/client/notification_client.py
```

---

## Step 6.4 — Generate regression tests with Copilot CLI

```bash
cd python-services/taskflow-api

copilot suggest "Generate a pytest test file for the TaskFlow API that covers: \
   1. POST /tasks with invalid due_date returns 400, \
   2. GET /tasks?sort=priority with None priority returns 200, \
   3. PUT /tasks/<id>/complete returns 200 and task is marked completed"
  "Generate a pytest test file for the TaskFlow API that covers: \
   1. POST /tasks with invalid due_date returns 400, \
   2. GET /tasks?sort=priority with None priority returns 200, \
   3. PUT /tasks/<id>/complete returns 200 and task is marked completed"
```

Save the suggested code to `tests/test_taskflow.py` and run it:

```bash
pip install pytest
pytest tests/test_taskflow.py -v
```

All tests should pass (green run).

---

## Step 6.5 — Re-run the incident simulator

```bash
python demo.py
```

This time, **all requests should succeed** with 2xx responses and no stack traces.

---

## Step 6.6 — Write a post-incident summary with Copilot

In Copilot Chat:

```
#codebase

Write a post-incident summary for the TaskFlow API P0 in the format:
- What happened (2 sentences)
- Root causes (numbered list)  
- Fixes applied (numbered list with file and line)
- Prevention measures (3 bullet points)
```

Save the output to `observability/post-incident-report.md`.

---

## ✅ Done when

- All six fixes are applied and confirmed with curl commands.
- `python demo.py` shows zero 500 errors.
- `pytest tests/test_taskflow.py` is green.
- You have a `post-incident-report.md` in `observability/`.

---

## Workshop Complete!

You have used **all five Copilot debugging capabilities**:

> **⚡ Want to go further?** Try the optional [Exercise 07 — Build a Copilot SDK Error Chat Assistant](exercise-07-copilot-sdk-chat.md) to embed Copilot directly in a Python app using the official SDK.

| Capability | Exercise | What you did |
|-----------|---------|-------------|
| Copilot CLI | 02 | `gh copilot explain` and `suggest` from the terminal |
| MCP tools | 03 | Agent Mode reading files and terminal output directly |
| Custom Agents | 04 | Built and ran `log-analysis-agent`, `root-cause-agent`, created a new agent |
| Skills & Plugins | 05 | `#file`, `#codebase`, `#selection`, `@terminal`, secret scanning, code review |
| Agent Mode (fix) | 06 | Multi-file fix via `bug-fix-agent` + Copilot CLI test generation |

---

## Reference

- [Agent Mode](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-chat-in-your-ide)
- [gh copilot suggest](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line/using-github-copilot-in-the-command-line)
- [Copilot for testing](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-chat-in-your-ide)
