
from fastapi import APIRouter, Body
import os

router = APIRouter()


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
    # Here you would add logic to check if this agent should execute the command
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "created": path, "agent_id": agent_id, "customer_id": customer_id, "environment_id": environment_id}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/api/agent/create-directory")
async def create_directory(payload: dict = Body(...)):
    path = payload.get("path")
    if not path or not isinstance(path, str):
        return {"status": "error", "detail": "Missing or invalid 'path'"}
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "created": path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
