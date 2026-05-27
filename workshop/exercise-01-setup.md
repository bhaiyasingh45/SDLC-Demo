# Exercise 01 — Setup & Environment

**Duration:** ~5 minutes  
**Feature:** Prerequisites, project bootstrap  
**Goal:** Get the TaskFlow API running and confirm the P0 incident is reproducible.

---

## 1.1 Prerequisites checklist

| Tool | Minimum version | Check command |
|------|----------------|---------------|
| Python | 3.12+ | `python --version` |
| pip | 23+ | `pip --version` |
| VS Code | Latest | — |
| GitHub Copilot extension | Latest | Extensions panel |
| Node.js | 22+ | `node --version` |
| Copilot CLI | Latest | `copilot --version` |

> **Note:** The old `gh copilot` extension is **retired**. The new Copilot CLI


Install Copilot CLI if missing:

```powershell
# Windows — WinGet (recommended)
winget install GitHub.Copilot
```

```bash
# macOS / Linux — Homebrew
brew install copilot-cli

# macOS / Linux — install script
curl -fsSL https://gh.io/copilot-install | bash
```

```bash
# All platforms — npm (requires Node.js 22+)
npm install -g @github/copilot
```

On first launch, authenticate with `/login` when prompted:

```bash
copilot          # launches the interactive CLI
# > /login      # follow on-screen instructions
copilot --version   # confirm it works
```

---

## 1.2 Clone and install

```bash
# 1. Open the workshop folder in VS Code (already done if you're reading this)

# 2. Install Python dependencies
cd python-services/taskflow-api
pip install -r requirements.txt

# 3. Start the API
flask --app app run
# Expected: * Running on http://127.0.0.1:5000
```

---

## 1.3 Reproduce the P0 incident

Open a **second terminal** and run the incident simulator:

```bash
cd python-services/taskflow-api
python demo.py
```

You should see **five failures** printed to the terminal. The API terminal will show
stack traces for the 500 errors.

> **Tip:** Read `observability/incident-report.md` for the full stack traces and
> symptom table before starting Exercise 02.

---

## 1.4 Explore the project with Copilot Chat

Open Copilot Chat (`Ctrl+Alt+I`) and try:

```
`#codebase` What does the TaskFlow API do and which files contain bugs?
```

Copilot will use `#codebase` context to summarise the project and point to the
buggy files. This is a preview of the skills you'll use in Exercise 05.

---

## ✅ Done when

- `flask --app app run` starts without errors.
- `python demo.py` prints at least three HTTP 500 responses.
- You have read `observability/incident-report.md`.

**→ Proceed to [Exercise 02](exercise-02-cli-debugging.md)**
