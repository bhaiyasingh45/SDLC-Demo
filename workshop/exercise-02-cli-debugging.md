# Exercise 02 — Debug with GitHub Copilot CLI

**Duration:** ~10 minutes  
**Feature:** GitHub Copilot CLI (`copilot`) — agentic terminal debugging  
**Goal:** Use the modern Copilot CLI to investigate the P0 incident, build a
bug-fix plan, and navigate the codebase — entirely from the terminal.

---

## Background

**GitHub Copilot CLI** (`copilot`) is a terminal-native AI coding agent. It is
fully agentic: it can read files, run shell commands, write code, and work
autonomously across a persistent session — all from your terminal.

Key commands used in this exercise:

| Command / Mode | What it does |
|----------------|-------------|
| `copilot` | Start an interactive agentic session |
| `/plan <request>` | Create a structured plan before making changes |
| `/review` | Run a structured code review on current branch changes |
| `/context` | Show context window usage breakdown |
| `/model` | Switch model mid-session (Opus 4.5, Sonnet 4.5, Auto) |
| `/session` | Show current session info and token usage |
| `/session files` | List temporary artefacts created this session |
| `Shift+Tab` | Toggle plan mode on/off |
| `--allow-tool` flag | Pre-approve tool categories (e.g. `shell(git:*)`) |
| `/fleet` | Spin up parallel agent instances to work on multiple tasks simultaneously |


---

## Step 2.1 — Start the CLI

Open a terminal at the repo root and launch Copilot CLI:

```bash
copilot
```

If this is your first time, follow the `/login` prompt to authenticate with GitHub.
You are now in an agentic session — all subsequent steps run from inside this session.

---

## Step 2.2 — Investigate the production logs

Ask Copilot to read and analyse the logs directly (no copy-paste needed):

```
Read observability/production-logs.txt and summarise every distinct error type.
Group them by severity and show the line numbers where each first appears.
```

Copilot will read the file with its shell tool and return a structured error inventory.

---

## Step 2.3 — Use Plan Mode to design a bug-fix strategy

Switch to plan mode with `Shift+Tab`, or use the `/plan` command:

```
/plan The TaskFlow API has 6 production bugs described in observability/incident-report.md.
Read the report and create a fix plan with one checkbox per bug, ordered by severity.
```

Copilot will:
1. Read `incident-report.md`.
2. Ask any clarifying questions.
3. Produce a `plan.md` saved to your session folder.

Review the plan — use `Ctrl+Y` to open it in your editor if needed.

---

## Step 2.4 — Bug investigation: find the missing timeout

From inside the Copilot CLI session:

```
Search all Python files under python-services/ for calls to requests.post()
that do NOT pass a timeout argument. Show the file path and line number for each.
```

Copilot will run a shell search and flag `notification_client.py` as the culprit.
This is **Bug #4**.

---

## Step 2.5 — Explore the sort-priority bug interactively

```
Read python-services/taskflow-api/app/service/task_service.py.
Find the line that sorts tasks by priority and explain why it raises a TypeError
when any task has a null priority value.
```

Copilot will locate the `sorted(tasks, key=lambda t: t["priority"])` line and
explain the `NoneType` comparison failure — **Bug #1**.

---

## Step 2.6 — Check session context and switch models (optional)

```
/context
```

See how many tokens your conversation is using. If you want deeper reasoning for the next step:

```
/model
```

Select **Claude Opus 4.5** for complex multi-file analysis, or keep **Auto** for speed.

---

## Step 2.7 — Use `/review` to catch issues before committing

The `/review` command runs a structured code review on your current branch changes.
Use it to catch any remaining problems in your bug fixes before you commit.

Inside the Copilot CLI session:

```
/review Focus on potential bugs and security issues in the TaskFlow API changes.
```

For a deeper review using two models as reviewers:

```
/review Use two different models to review the changes in my current branch
against main. Focus on missing error handling, bare except blocks, and any
place where raw exception messages could reach an HTTP response.
```

Copilot will:
1. Diff your working branch against `main`.
2. Run both models as independent reviewers.
3. Report findings with file + line references.

Expected findings: it should flag `except Exception: pass` (Bug #3) and the missing
`timeout=` argument (Bug #4) if those files have been edited.

---

## Step 2.8 — Use `/fleet` for parallel bug analysis *(if available on your plan)*

`/fleet` spins up multiple parallel agent instances. Use it to analyse all 6 bugs
simultaneously instead of one at a time:

```
/fleet Analyse the TaskFlow API for all 6 bugs described in observability/incident-report.md.
Assign one bug per agent. Each agent should: read the relevant source file, identify the
root cause, and propose a minimal fix. Collect all findings into a single summary.
```

Copilot will:
1. Spawn one agent instance per bug.
2. Run all analyses in parallel.
3. Return a consolidated report with root cause + fix for each bug.

Compare the time and depth of results against the sequential investigation you did in Steps 2.4–2.5.

---

## ✅ Done when

- You used Copilot CLI to read and summarise `production-logs.txt` without copy-pasting.
- You used `/plan` to produce a structured bug-fix plan.
- You used the CLI to locate Bug #4 (missing timeout) and Bug #1 (sort TypeError).
- You ran `/review` and received at least one inline finding on the TaskFlow codebase.
- *(Bonus)* You used `/fleet` to run parallel bug analysis across all 6 bugs.

**→ Proceed to [Exercise 03](exercise-03-mcp-debugging.md)**

---

## Reference

- [Copilot CLI Best Practices](https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices)
- [Copilot CLI Command Reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- [About GitHub Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli)
