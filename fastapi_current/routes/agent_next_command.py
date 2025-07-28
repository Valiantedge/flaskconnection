from fastapi import APIRouter, Query
from models import Command
from config import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/agent/next-command")
async def next_command(agent_id: int = Query(...)):
    db = next(get_db())
    cmd = db.query(Command).filter(Command.agent_id == agent_id, Command.status == "queued").order_by(Command.id.asc()).first()
    if cmd:
        # Optionally, mark as in-progress
        cmd.status = "in_progress"
        db.commit()
        return {"command": cmd.command, "command_id": cmd.id}
    return {"command": None, "command_id": None}
