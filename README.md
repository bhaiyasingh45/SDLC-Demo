# TaskFlow API — Debugging with GitHub Copilot Agents

> **Workshop** · ~60 minutes · 6 exercises  
> Audience: Developers and platform engineers  
> Prerequisites: VS Code, GitHub Copilot license, Python 3.12+, GitHub CLI

---

## Objective

You are the **on-call engineer** responding to a P0 production incident on
**TaskFlow** — a live task management REST API. Six bugs are causing intermittent
500 errors, silent notification failures, and thread-pool exhaustion.

Your mission: use **five different GitHub Copilot capabilities** to diagnose and
fix every bug before the service degrades further.

---

## The Incident

| Bug | Symptom | File | Impact |
|-----|---------|------|--------|
| #1 | `TypeError` sorting tasks with `None` priority | `task_service.py` | Dashboard 500 for all users |
| #2 | `asyncio.create_task()` never awaited | `task_service.py` | 100% notification loss |
| #3 | Exception swallowed with no logging | `task_service.py` | Silent update failures |
| #4 | Timeout configured but never passed to `requests.post()` | `notification_client.py` | Thread-pool exhaustion |
| #5 | No retry on transient `ConnectionError` | `notification_client.py` | Permanent notification loss on flaky network |
| #6 | `due_date` parsed without validation | `routes/tasks.py` | 500 on any malformed date |

Full details: [`observability/incident-report.md`](observability/incident-report.md)

---

## Workshop Map — 6 Exercises in 60 Minutes

| # | Exercise | Copilot Feature | Duration |
|---|----------|----------------|----------|
| 01 | [Setup & Environment](workshop/exercise-01-setup.md) | Bootstrap | 5 min |
| 02 | [Debug with Copilot CLI](workshop/exercise-02-cli-debugging.md) | Standalone `copilot` CLI — plan, review, fleet | 10 min |
| 03 | [MCP-Powered Debugging](workshop/exercise-03-mcp-debugging.md) | GitHub MCP Server — search, issues, file lookup | 10 min |
| 04 | [Custom Agents for Root Cause Analysis](workshop/exercise-04-custom-agents.md) | `.agent.md` custom agents — use & build | 10 min |
| 05 | [Agent Skills & Advanced Security](workshop/exercise-05-skills-plugins.md) | `SKILL.md` agent skills + Advanced Security plugin | 10 min |
| 06 | [Fix All Bugs & Validate](workshop/exercise-06-fix-validate.md) | Agent Mode + `bug-fix-agent` + Copilot CLI tests | 15 min |

---

## Copilot Features Covered

| Feature | Exercises | What you learn |
|---------|-----------|---------------|
| **Copilot CLI** (`copilot`) | 02, 06 | Agentic terminal sessions — plan mode, fleet, model switching, test scaffolding |
| **GitHub MCP Server** | 03 | Search GitHub, create issues, and look up files directly from Copilot Chat |
| **Custom Agents** (`.agent.md`) | 04 | Package reusable debugging expertise as code; build new agents from scratch |
| **Agent Skills** (`SKILL.md`) | 05 | Encode team conventions as discoverable skills Copilot loads automatically |
| **Advanced Security Plugin** | 05 | Secret scanning + VS Code Code Review |
| **Agent Mode** (multi-file edits) | 06 | Autonomous multi-file fix with `bug-fix-agent` |

---

## Project Structure

```
.github/
  agents/
    debug-agent.agent.md          ← General on-call assistant
    log-analysis-agent.agent.md   ← Logs → Bug Inventory
    root-cause-agent.agent.md     ← Symptom → exact code origin
    bug-fix-agent.agent.md        ← Apply all 6 fixes with diffs
  copilot-instructions.md         ← Auto-loaded Copilot context

python-services/
  taskflow-api/
    app/
      service/task_service.py     ← Bugs #1, #2, #3
      client/notification_client.py ← Bugs #4, #5
      routes/tasks.py             ← Bug #6
      __init__.py                 ← Flask application factory
    config.yaml                   ← Bug #4 root (timeout unused)
    requirements.txt
    demo.py                       ← P0 incident simulator

observability/
  incident-report.md              ← P0 alert + stack traces
  production-logs.txt             ← Raw server logs from incident window

workshop/
  exercise-01-setup.md
  exercise-02-cli-debugging.md
  exercise-03-mcp-debugging.md
  exercise-04-custom-agents.md
  exercise-05-skills-plugins.md
  exercise-06-fix-validate.md

solution/                         ← Reference fixes (read AFTER exercises)
  task_service_fixed.py
  notification_client_fixed.py
  tasks_fixed.py
```

---

## Quick Start

```bash
# 1. Open this folder in VS Code
# 2. Install dependencies
cd python-services/taskflow-api
pip install -r requirements.txt

# 3. Start the API
flask --app app run

# 4. In a second terminal — reproduce the P0
python demo.py

# 5. Open workshop/exercise-01-setup.md to begin
```

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.12+ | [python.org](https://www.python.org/downloads/) |
| VS Code | Latest | [code.visualstudio.com](https://code.visualstudio.com/) |
| GitHub Copilot extension | Latest | VS Code Extensions panel |
| Copilot CLI | Latest | `winget install GitHub.Copilot` (Windows) · `brew install copilot-cli` (macOS) · `npm i -g @github/copilot` |
| Node.js | 22+ (CLI only) | [nodejs.org](https://nodejs.org/) |

---

## Custom Agents

Four agents live in `.github/agents/`. The exercises guide you through
using them and building a fifth (`notification-agent`) from scratch in Exercise 04.

| Agent | Purpose | Used in |
|-------|---------|---------|
| `debug-agent` | General debugging assistant | Reference |
| `log-analysis-agent` | Logs → structured Bug Inventory | Exercise 04 |
| `root-cause-agent` | Symptom → exact code origin with evidence | Exercise 04 |
| `bug-fix-agent` | Apply all 6 minimal fixes with diffs | Exercise 06 |

---

## References

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [Copilot CLI](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line/using-github-copilot-in-the-command-line)
- [Custom Agents](https://docs.github.com/en/copilot/customizing-copilot/reusing-prompts-and-instructions-in-github-copilot)
- [MCP with Copilot](https://docs.github.com/en/copilot/customizing-copilot/using-model-context-protocol-with-github-copilot)
- [Agent Mode](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-chat-in-your-ide)
- [Code Review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review)

---

