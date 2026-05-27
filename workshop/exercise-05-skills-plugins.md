# Exercise 05 — Agent Skills & Advanced Security Plugins

**Duration:** ~10 minutes  
**Feature:** Agent Skills (`SKILL.md`), Advanced Security plugin (secret scanning)  
**Goal:** Author a `SKILL.md` agent skill that encodes your team's debugging
conventions, use it to guide Copilot through a structured incident investigation,
then run the Advanced Security secret-scanning plugin against the TaskFlow codebase.

---

## Background

**Agent Skills** are the open standard ([agentskills.io](https://agentskills.io)) — folders
containing a `SKILL.md` file plus optional scripts and resources. Copilot reads the
`description` in the frontmatter to decide when the skill is relevant.

```
.github/skills/
└── my-skill-name/       ← subdirectory name: lowercase, hyphenated
    └── SKILL.md         ← MUST be named exactly SKILL.md
```

`SKILL.md` frontmatter structure:

```markdown
---
name: my-skill-name          # required — unique, lowercase, hyphens
description: What this skill does and WHEN Copilot should use it.
---
Your instructions here...
```

---

## Step 5.1 — Create a Debugging Skill

Create the directory `.github/skills/taskflow-debugging/` and inside it create
`SKILL.md`:

```markdown
---
name: taskflow-debugging
description: Guide for debugging the TaskFlow API. Use this when asked to investigate production errors, review bug fixes, or check code against TaskFlow conventions.
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
```

Your directory should look like:

```
.github/skills/
└── taskflow-debugging/
    └── SKILL.md
```


---

## Step 5.2 — Verify the skill is active

Open Copilot Chat (`Ctrl+Alt+I`) in **Agent Mode** and ask:

```
Debug the TaskFlow API — what conventions should I follow?
```

Expected: Because the prompt matches the skill's `description`, Copilot loads
`taskflow-debugging/SKILL.md` and cites the investigation order and code conventions
without you pasting anything. This confirms the skill is being discovered correctly.

> **Note:** Skills are loaded on-demand based on your prompt, not automatically on
> every message. If Copilot doesn't use the skill, add context: _"Using TaskFlow
> debugging conventions, review…"_

---

## Step 5.3 — Use the skill to diagnose Bug #3 (swallowed exception)

Open `app/service/task_service.py`. In Copilot Chat (Agent Mode):

```
Using the taskflow-debugging skill, review the update_task method in 
#file:python-services/taskflow-api/app/service/task_service.py

Does it follow our conventions? What happens if an exception is raised 
inside the try block?
```

Expected: Copilot detects `except Exception: pass` (Bug #3), flags it as violating
the `logger.exception` convention from the skill, and suggests the correct fix.

---

## Step 5.4 — Use the skill to review Bug #6 (unguarded date input)

```
Using the taskflow-debugging skill, review the route that creates a task in
#file:python-services/taskflow-api/app/routes/tasks.py

It parses a due_date string with strptime. Does this follow the fix checklist?
What would happen if the caller sends a bad date like "25-12-2024"?
```

Expected: Copilot applies the fix checklist, flags the missing `try/except`, notes
that the raw `ValueError` must not reach the HTTP response, and suggests a
`{"error": "Invalid due_date format. Use YYYY-MM-DD."}` response.

---

## Step 5.5 — Create a second, targeted skill for notification debugging

Create `.github/skills/notification-client/SKILL.md`:

```markdown
---
name: notification-client
description: Conventions for reviewing and fixing the TaskFlow notification client. Use when asked to review or debug app/client/notification_client.py.
---
# Notification Client Conventions

When reviewing or fixing the notification client:
- The `timeout` value MUST be read from `self.timeout` (set via config.yaml), never hardcoded.
- All `requests` calls MUST pass `timeout=self.timeout`.
- On `ConnectionError`, log with `logger.exception` and return `None` — do NOT silently pass.
- Retry logic should use exponential backoff with a max of 3 attempts.
- Never swallow exceptions silently with bare `except: pass`.
```

Test it:

```
Using the notification-client skill, review the send_completion_notification 
method in #file:python-services/taskflow-api/app/client/notification_client.py

List every convention violation.
```

Expected: Copilot finds Bug #4 (missing `timeout=`) and Bug #5 (no retry, bare
`except`) and maps each violation to a rule in the skill.

---

## Step 5.6 — Run the Advanced Security secret-scanning plugin

Copilot's **Advanced Security** plugin exposes GitHub secret scanning as an
agent tool. Use it to check the TaskFlow codebase for accidentally committed
credentials, tokens, or API keys.

Navigate to the "**Open Customizations**" on the top right of the chat pane and click on the "**plugins**" tab. You should see the "Advanced Security" plugin listed there. If it's not already enabled, click on "**Browse Marketplace**" to find and enable the "Advanced Security" plugin.

In Copilot Chat (**Agent Mode**), ask:

```
/advanced-security:secret-scanning Using the secret scanning tool, scan the TaskFlow API codebase for any
hardcoded secrets, tokens, API keys, or credentials. Report each finding
with the file path and line number.
```

Copilot will invoke `run_secret_scanning` and return a structured report. For
each finding:
- Note the file and line.
- Confirm whether it is a real secret or a test fixture.
- If real, rotate the credential immediately and move it to `config.yaml` or
  an environment variable.

> **Why this matters for TaskFlow:** `config.yaml` holds the notification
> webhook URL and could contain tokens. Confirming no secrets are hardcoded
> in source files is part of the P0 fix checklist.

---

## Step 5.7 — Run the dependency-scanning plugin

Also in Agent Mode:

```
/dependency-scanning:scan Scan the TaskFlow API dependencies in
python-services/taskflow-api/requirements.txt for known CVEs.
List any vulnerabilities with their severity and recommended fix version.
```

Copilot invokes the Dependabot/advisory-database tool and returns a CVE list.
Note any high/critical findings — these would be added to the post-incident
report in Exercise 06.

---

## ✅ Done when

- You created `.github/skills/taskflow-debugging/SKILL.md` with correct `name` and `description` frontmatter.
- Copilot loaded the skill and cited its conventions when asked to debug TaskFlow.
- You used the skill to find Bug #3 and Bug #6 violations.
- You created a second skill (`notification-client`) for the notification layer.
- Secret scanning returned a clean report (or findings were noted for remediation).
- Dependency scanning identified any CVEs in `requirements.txt`.

**→ Proceed to [Exercise 06](exercise-06-fix-validate.md)**

---

## Reference

- [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/add-skills)
- [Awesome GitHub Copilot skills](https://awesome-copilot.github.com/skills/)
- [Agent Skills open standard](https://agentskills.io/specification)
- [About secret scanning](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning)
- [Dependabot and dependency scanning](https://docs.github.com/en/code-security/dependabot/working-with-dependabot)
