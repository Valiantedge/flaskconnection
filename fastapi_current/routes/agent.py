from fastapi import APIRouter, HTTPException, Header, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import Agent
from config import SessionLocal
from pydantic import BaseModel
import uuid

router = APIRouter()

# Add HTTPBearer security scheme
bearer_scheme = HTTPBearer()

class AgentRegister(BaseModel):
    name: str

class AgentHeartbeat(BaseModel):
    status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_agent(agent: AgentRegister, db: Session = Depends(get_db)):
    if db.query(Agent).filter(Agent.name == agent.name).first():
        raise HTTPException(status_code=400, detail="Agent already exists")
    token = str(uuid.uuid4())
    new_agent = Agent(name=agent.name, token=token, status='active')
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return {"agent_id": new_agent.id, "token": token}

@router.post("/heartbeat")
def agent_heartbeat(
    heartbeat: AgentHeartbeat,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    agent = db.query(Agent).filter(Agent.token == token).first()
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid token")
    agent.status = heartbeat.status
    db.commit()
    return {"status": "ok"}

@router.get("/s")
def get_agents(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    # For demo, no admin check
    agents = db.query(Agent).all()
    return [{"agent_id": a.id, "status": a.status} for a in agents]
