
from fastapi import APIRouter, Body
from models import Command
from config import SessionLocal
from sqlalchemy.orm import Session
import os

router = APIRouter()


@router.post("/api/agent/create-directory")
async def create_directory(payload: dict = Body(...)):
    agent_id = payload.get("agent_id")
    customer_id = payload.get("customer_id")
    environment_id = payload.get("environment_id")
    path = payload.get("path")
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
        return {"status": "error", "detail": "Missing or invalid 'path'"}
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "created": path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
