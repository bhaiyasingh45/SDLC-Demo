# Exercise 04 — Custom Agents for Root Cause Analysis

**Duration:** ~10 minutes  
**Feature:** Custom Copilot Agents (`.agent.md` files)  
**Goal:** Build and use two custom agents to perform structured log analysis and
root-cause investigation — reusable expertise packaged as code.

---

## Background

**Custom Agents** (`.github/agents/*.agent.md`) are reusable AI personas committed
to the repository. Each agent has a focused purpose, a defined output format, and
access to specific tools. Unlike ad-hoc Copilot Chat, agents produce consistent,
structured results you can run repeatedly.

This repository ships four ready-made agents:

| Agent | File | Purpose |
|-------|------|---------|
| Debug Agent | `debug-agent.agent.md` | General debugging assistant |
| Log Analysis Agent | `log-analysis-agent.agent.md` | Parse logs → Bug Inventory |
| Root Cause Agent | `root-cause-agent.agent.md` | Trace symptom → exact code origin |
| Bug Fix Agent | `bug-fix-agent.agent.md` | Apply minimal fixes with diffs |

---

## Step 4.1 — Inspect the existing agents

Open `#file:.github/agents/log-analysis-agent.agent.md` and read through it. Notice:

- The `tools:` block controls which MCP tools the agent can call.
- The output format is explicitly defined so the agent always returns the same structure.
- Instructions are written to constrain the agent to only report evidence-backed findings.

---

## Step 4.2 — Run the Log Analysis Agent

In Copilot Chat (Agent Mode), switch to the **log-analysis-agent**:

1. Click the agent selector (drop-down in the chat input).
2. Select **log-analysis-agent**.
3. Type:

```
Analyse the production logs and produce the Bug Inventory.
```

The agent will:
1. Read `observability/production-logs.txt`.
2. Cross-reference with source files.
3. Return the structured Bug Inventory table.

---

## Step 4.3 — Run the Root Cause Agent

Switch to **root-cause-agent** and ask:

```
The GET /tasks?sort=priority endpoint returns 500. Trace the root cause.
```

Expected output follows the root-cause template defined in the agent file, including
the exact failing line and evidence from logs.

---

## Step 4.4 — Build your own agent from scratch

Create a new agent file:

**File:** `.github/agents/notification-agent.agent.md`

Use the following prompt in Copilot Chat to generate it:

```
/create-agent Create a custom Copilot agent called "notification-agent" that specialises in 
diagnosing notification delivery failures in the TaskFlow API. 
It should read the notification_client.py file, check for missing timeout and 
retry logic, and output a structured health report. 
Use the same format as the existing agents in .github/agents/.
```

Review the generated file, then invoke it:

```
@notification-agent Check the notification client for reliability issues.
```

---

## Step 4.5 — Commit the new agent

```bash
git add .github/agents/notification-agent.agent.md
git commit -m "feat: add notification-agent for webhook reliability debugging"
```

This demonstrates that agents are **first-class code artifacts** — versioned,
reviewable, and reusable across the team.

---

## ✅ Done when

- You ran `log-analysis-agent` and received a Bug Inventory.
- You ran `root-cause-agent` for Bug #1 or Bug #2.
- You created a custom `notification-agent.agent.md`.

**→ Proceed to [Exercise 05](exercise-05-skills-plugins.md)**

---

## Reference

- [Custom agents in VS Code](https://docs.github.com/en/copilot/customizing-copilot/reusing-prompts-and-instructions-in-github-copilot)
- [Agent Mode overview](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-chat-in-your-ide)
