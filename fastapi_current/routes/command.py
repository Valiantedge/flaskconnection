from fastapi import APIRouter, HTTPException, Header, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import Command, Agent
from config import SessionLocal
from pydantic import BaseModel

bearer_scheme = HTTPBearer()
router = APIRouter(dependencies=[Security(bearer_scheme)])

class CommandRequest(BaseModel):
    agent_id: int
    command: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
def send_command(cmd: CommandRequest, Authorization: str = Header(...), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == cmd.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    new_cmd = Command(agent_id=cmd.agent_id, command=cmd.command, status="queued")
    db.add(new_cmd)
    db.commit()
    db.refresh(new_cmd)
    return {"command_id": new_cmd.id, "status": "queued"}

@router.get("/{command_id}")
def get_command_status(command_id: int, Authorization: str = Header(...), db: Session = Depends(get_db)):
    cmd = db.query(Command).filter(Command.id == command_id).first()
    if not cmd:
        raise HTTPException(status_code=404, detail="Command not found")
    return {"status": cmd.status, "output": cmd.output}
