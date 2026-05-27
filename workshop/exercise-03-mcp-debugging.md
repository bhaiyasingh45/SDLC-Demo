# Exercise 03 — MCP-Powered Debugging with GitHub MCP Server

**Duration:** ~10 minutes  
**Feature:** Model Context Protocol (MCP) — GitHub MCP Server  
**Goal:** Configure the GitHub MCP server, then use it inside VS Code Copilot to
search GitHub for similar bug patterns, create tracking issues for the P0 incident,
and pull context from GitHub directly into your debugging session.

---

## Background

**Model Context Protocol (MCP)** lets Copilot call external tools during a chat
session. The **GitHub MCP Server** exposes GitHub's API as Copilot tools — so you
can search repos, read files from GitHub, create issues, and list pull requests
without leaving VS Code.

In this exercise you will:
1. Configure the GitHub MCP server locally.
2. Use GitHub MCP tools to research similar bugs on GitHub.
3. Create P0 incident issues directly from Copilot Chat.
4. Cross-reference your codebase with open-source patterns.

---

## Step 3.1 — Configure the GitHub MCP Server


**Latest approach — install via Copilot Chat:**
1. Open **Copilot Chat** (`Ctrl+Alt+I`).
2. Click the **Settings** (gear) icon in the chat panel.
3. Select **MCP Servers** → **Browse Marketplace**.
4. Search for **GitHub MCP** and click **Install**.
5. VS Code adds the server entry automatically — no manual `mcp.json` editing needed.

---

## Step 3.2 — Verify the GitHub MCP tools are active

1. Open Copilot Chat (`Ctrl+Alt+I`) and switch to **Agent Mode**.
2. Click the **tools** icon (wrench) in the chat input bar.
3. You should see GitHub tools listed, including:
   - `github_search_code`
   - `github_list_issues`
   - `github_create_issue`
   - `github_get_file_contents`
   - `github_search_repositories`

If the tools are not listed, check that the GitHub MCP server is installed and the token was entered.

---

## Step 3.3 — Search GitHub for the asyncio bug pattern

Use the GitHub MCP search tool to research Bug #2 (fire-and-forget `asyncio.create_task`):

```
Using the github_search_code tool, search GitHub for Python code that uses 
asyncio.create_task inside a Flask route handler. Show me examples of how 
other projects handle this pattern correctly.
```

Copilot will call `github_search_code` and return real-world code examples showing
the correct pattern (e.g. using `threading.Thread` or a background task queue instead).

---

## Step 3.4 — Search for the requests timeout anti-pattern

```
Using #search_code, find Python projects that fixed a missing timeout 
on requests.post() calls to a webhook URL. Show me before/after diffs if possible.
```

This gives you community-validated examples of Bug #4's fix — passing
`timeout=self.timeout` — reinforced by real open-source code.

---

## Step 3.5 — Create a GitHub issue for the P0 incident

Using the GitHub MCP create-issue tool, file the incident:

```
Read observability/incident-report.md, then use #issue_write to create 
a GitHub issue in this repository titled "P0: TaskFlow API — 6 production bugs"
with a body that summarises all 6 bugs, their severity, and affected files.
Add the label "bug" and "P0".
```

Copilot will read the incident report and call `#issue_write`. Confirm the
issue URL it returns — you now have a tracked incident on GitHub.

---

## Step 3.6 — List open issues and cross-reference with bugs

```
Use #list_issues to list all open issues in this repository.
For each issue, check whether it corresponds to one of the 6 known bugs 
from observability/incident-report.md.
```

This demonstrates how the GitHub MCP tool can bridge your local codebase context
with the GitHub issue tracker — useful for on-call triage.

---

## Step 3.7 — Fetch a reference fix from an open-source repo

```
Use #get_file_contents to read the file 
psf/requests/blob/main/src/requests/adapters.py
and show me how the requests library itself handles connection timeouts and retries.
```

Copilot fetches the file directly from GitHub via MCP and explains the
`HTTPAdapter` retry strategy — giving you a reference implementation for Bug #5.

---

## ✅ Done when

- The GitHub MCP server is configured and its tools appear in Agent Mode.
- You used `search_code` to find real-world fixes for at least one bug.
- You created a P0 issue on GitHub from Copilot Chat.

**→ Proceed to [Exercise 04](exercise-04-custom-agents.md)**

---

## Reference

- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [MCP overview — GitHub Docs](https://docs.github.com/en/copilot/customizing-copilot/using-model-context-protocol-with-github-copilot)
- [VS Code MCP configuration](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)
