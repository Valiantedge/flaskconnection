from fastapi import APIRouter, Body, Depends
from fastapi.responses import PlainTextResponse
from models import Command
from config import SessionLocal
import subprocess

router = APIRouter()

# Add missing get_db function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/api/agent/create-directory")
async def create_directory(payload: dict = Body(...)):
    agent_id = payload.get("agent_id")
    customer_id = payload.get("customer_id")
    environment_id = payload.get("environment_id")
    path = payload.get("path")
    missing = [k for k in ("agent_id", "customer_id", "environment_id", "path") if not payload.get(k)]
    if missing:
        return {"status": "error", "detail": f"Missing fields: {', '.join(missing)}"}
    if not isinstance(path, str):
        return {"status": "error", "detail": "'path' must be a string"}
    db = next(get_db())
    # Store the command for the agent to pick up
    cmd = Command(
        agent_id=agent_id,
        command=f"mkdir {path}",
        status="queued"
    )
    db.add(cmd)
    db.commit()
    db.refresh(cmd)
    return {"status": "queued", "command_id": cmd.id, "agent_id": agent_id, "customer_id": customer_id, "environment_id": environment_id, "path": path}

@router.post("/api/agent/run-command", response_class=PlainTextResponse)
async def run_command(payload: dict = Body(...), db=Depends(get_db)):
    command = payload.get("command")
    if not command or not isinstance(command, str):
        return "Missing or invalid 'command' field (must be a string)"
    try:
        # Run the command and capture output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        return output
    except Exception as e:
        return str(e)
