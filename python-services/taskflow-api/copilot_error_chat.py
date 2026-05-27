import asyncio
from pathlib import Path
 
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType
from copilot.session import PermissionHandler
 
 
def read_text_or_empty(path: Path, max_chars: int = 4000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:max_chars]
 
 
async def main() -> None:
    service_root = Path(__file__).resolve().parent
    repo_root = service_root.parent.parent
 
    logs_path = repo_root / "observability" / "production-logs.txt"
    report_path = repo_root / "observability" / "incident-report.md"
 
    logs_preview = read_text_or_empty(logs_path)
    report_preview = read_text_or_empty(report_path)
 
    async with CopilotClient() as client:
        async with await client.create_session(
            model="gpt-4.1",
            streaming=True,
            working_directory=str(repo_root),
            on_permission_request=PermissionHandler.approve_all,
            system_message={
                "content": (
                    "You are the TaskFlow API on-call copilot. "
                    "Help debug production errors safely. "
                    "Do not expose raw Python tracebacks to clients. "
                    "Recommend minimal code fixes and include validation curl commands."
                )
            },
        ) as session:
 
            def on_event(event) -> None:
                if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                    delta = event.data.delta_content or ""
                    print(delta, end="", flush=True)
                elif event.type == SessionEventType.SESSION_IDLE:
                    print()
 
            session.on(on_event)
 
            print("TaskFlow Error Chat (type 'exit' to quit)")
            print("Try: Why did GET /tasks?sort=priority fail in production?")
 
            context_blob = (
                "Context for this repo:\n"
                "--- incident-report.md (preview) ---\n"
                f"{report_preview}\n\n"
                "--- production-logs.txt (preview) ---\n"
                f"{logs_preview}\n"
            )
 
            while True:
                user_input = input("\nYou: ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "exit":
                    break
 
                prompt = (
                    f"{context_blob}\n"
                    "Question:\n"
                    f"{user_input}\n\n"
                    "Please answer with:\n"
                    "1) probable root cause\n"
                    "2) exact file/function to inspect\n"
                    "3) minimal safe fix\n"
                    "4) one curl command to validate\n"
                )
 
                print("Assistant: ", end="", flush=True)
                await session.send_and_wait(prompt)
 
 
if __name__ == "__main__":
    asyncio.run(main())