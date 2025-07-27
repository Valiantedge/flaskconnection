from fastapi import Query
# New endpoint to fetch install IDs for agent
@router.get("/install-ids", summary="Get IDs for agent install command", description="Returns customer_id, workspace_id, and environment_id for the selected workspace and environment.")
def get_install_ids(
    workspace_id: int = Query(..., description="Workspace ID"),
    environment_id: int = Query(..., description="Environment ID"),
    db: Session = Depends(get_db)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    environment = db.query(Environment).filter(Environment.id == environment_id).first()
    if not workspace or not environment:
        raise HTTPException(status_code=404, detail="Workspace or Environment not found")
    return {
        "customer_id": workspace.customer_id,
        "workspace_id": workspace.id,
        "environment_id": environment.id
    }

from fastapi import APIRouter, HTTPException, Header, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import Agent
from config import SessionLocal
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta

# Add HTTPBearer security scheme
bearer_scheme = HTTPBearer()
router = APIRouter(dependencies=[Security(bearer_scheme)])



class AgentRegister(BaseModel):
    name: str
    customer_id: int
    workspace_id: int
    environment_id: int
    ip_address: str
    machine_uuid: str
    os_type: str

class AgentHeartbeat(BaseModel):
    status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/register",
    summary="Register a new agent",
    description="Register an agent with customer, workspace, and environment IDs. All fields are required: name, customer_id, workspace_id, environment_id, ip_address, machine_uuid, os_type."
)
def register_agent(agent: AgentRegister, db: Session = Depends(get_db)):
    if db.query(Agent).filter(Agent.name == agent.name).first():
        raise HTTPException(status_code=400, detail="Agent already exists")
    token = str(uuid.uuid4())
    new_agent = Agent(
        name=agent.name,
        customer_id=agent.customer_id,
        workspace_id=agent.workspace_id,
        environment_id=agent.environment_id,
        token=token,
        status='active',
        ip_address=agent.ip_address,
        machine_uuid=agent.machine_uuid,
        os_type=agent.os_type
    )
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
    agent.last_heartbeat = datetime.utcnow()
    db.commit()
    return {"status": "ok"}

@router.get("/s")
def get_agents(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    # For demo, no admin check
    agents = db.query(Agent).all()
    now = datetime.utcnow()
    offline_threshold = timedelta(minutes=2)
    return [
        {
            "agent_id": a.id,
            "status": (a.status if a.last_heartbeat and (now - a.last_heartbeat) < offline_threshold else "offline"),
            "customer_id": a.customer_id,
            "cluster_id": a.cluster_id,
            "ip_address": a.ip_address,
            "machine_uuid": a.machine_uuid,
            "os_type": a.os_type,
            "last_heartbeat": a.last_heartbeat.isoformat() if a.last_heartbeat else None
        }
        for a in agents
    ]
