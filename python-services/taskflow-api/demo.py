"""
TaskFlow API — Incident Simulator (demo.py)

Runs a scripted sequence of API calls that reproduces all six bugs.
Use this to confirm the P0 incident is reproducible before the exercises.

Usage:
    pip install -r requirements.txt
    python demo.py
"""

import json
import sys
import threading
import time

import requests

BASE = "http://127.0.0.1:5000"


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print("="*60)


def call(method: str, path: str, **kwargs) -> requests.Response:
    url = f"{BASE}{path}"
    resp = getattr(requests, method)(url, **kwargs)
    print(f"  {method.upper()} {path}  →  {resp.status_code}")
    try:
        body = resp.json()
        print(f"  {json.dumps(body, indent=2)[:300]}")
    except Exception:
        print(f"  (non-JSON response)")
    return resp


def run_demo() -> None:
    # ------------------------------------------------------------------
    # Bug #6 — malformed due_date causes unhandled 500
    # ------------------------------------------------------------------
    print_section("Bug #6 — Malformed due_date → unhandled 500")
    call("post", "/tasks", json={
        "title": "Fix login page",
        "assignee": "alice",
        "priority": 2,
        "due_date": "31/12/2024",   # wrong format — triggers ValueError
    })

    # ------------------------------------------------------------------
    # Bug #1 — None priority causes TypeError on sorted list
    # ------------------------------------------------------------------
    print_section("Setup: create tasks, some with no priority")
    call("post", "/tasks", json={
        "title": "Write tests",
        "assignee": "bob",
        "due_date": "2024-12-31",
        # priority intentionally omitted → None
    })
    call("post", "/tasks", json={
        "title": "Deploy to staging",
        "assignee": "carol",
        "priority": 1,
        "due_date": "2024-12-30",
    })

    print_section("Bug #1 — Sort by priority with None value → TypeError 500")
    call("get", "/tasks?sort=priority")

    # ------------------------------------------------------------------
    # Bug #2 — fire-and-forget asyncio.create_task()
    # ------------------------------------------------------------------
    print_section("Bug #2 — complete_task notification silently dropped")
    call("post", "/tasks", json={
        "title": "Review PR #42",
        "assignee": "dave",
        "priority": 3,
        "due_date": "2024-11-01",
    })
    call("put", "/tasks/3/complete")
    print("  (Check logs — you will NOT see a 'Notification sent' entry)")

    # ------------------------------------------------------------------
    # Bug #3 — swallowed exception in update_task
    # ------------------------------------------------------------------
    print_section("Bug #3 — Bad update silently returns 404 (exception eaten)")
    # Pass an invalid update that causes an internal error — the 404
    # response looks like "not found" but actually hides a TypeError.
    call("put", "/tasks/99", json={"status": "completed"})

    # ------------------------------------------------------------------
    # Bug #4 & #5 — timeout not enforced, no retry on connection error
    # ------------------------------------------------------------------
    print_section("Bug #4/#5 — Notification times out / no retry (see logs)")
    # The webhook server is not running — requests.post() will block
    # until OS default socket timeout (minutes) rather than 1 s.
    print("  Attempting to complete task #2 — notification will block ...")
    t = threading.Thread(target=call, args=("put", "/tasks/2/complete"))
    t.daemon = True
    t.start()
    t.join(timeout=3)
    if t.is_alive():
        print("  ⚠️  Thread still blocked — timeout not enforced (Bug #4)")

    print("\n\nIncident simulation complete.")
    print("Open workshop/exercise-01-setup.md to begin the exercises.\n")


if __name__ == "__main__":
    # Quick connectivity check
    try:
        requests.get(f"{BASE}/tasks/stats", timeout=2)
    except requests.exceptions.ConnectionError:
        print("ERROR: TaskFlow API is not running.")
        print("Start it first with:  flask --app app run")
        sys.exit(1)

    run_demo()
