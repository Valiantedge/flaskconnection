from fastapi import APIRouter, HTTPException, Header, Depends, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import Agent, Workspace, Environment
from config import SessionLocal
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta

# Add HTTPBearer security scheme
bearer_scheme = HTTPBearer()
router = APIRouter(dependencies=[Security(bearer_scheme)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

class WorkspaceCreate(BaseModel):
    name: str
    customer_id: int

class EnvironmentCreate(BaseModel):
    name: str
    workspace_id: int

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

@router.post(
    "/workspaces",
    summary="Create a new workspace",
    description="Create a new workspace for a customer. Requires a unique name and customer_id."
)
def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db)):
    if db.query(Workspace).filter(Workspace.name == workspace.name).first():
        raise HTTPException(status_code=400, detail="Workspace already exists")
    new_workspace = Workspace(name=workspace.name, customer_id=workspace.customer_id)
    db.add(new_workspace)
    db.commit()
    db.refresh(new_workspace)
    return {"workspace_id": new_workspace.id, "name": new_workspace.name, "customer_id": new_workspace.customer_id}

@router.post(
    "/environments",
    summary="Create a new environment",
    description="Create a new environment within a workspace. Requires a unique name and workspace_id."
)
def create_environment(environment: EnvironmentCreate, db: Session = Depends(get_db)):
    if db.query(Environment).filter(Environment.name == environment.name, Environment.workspace_id == environment.workspace_id).first():
        raise HTTPException(status_code=400, detail="Environment already exists in this workspace")
    new_env = Environment(name=environment.name, workspace_id=environment.workspace_id)
    db.add(new_env)
    db.commit()
    db.refresh(new_env)
    return {"environment_id": new_env.id, "name": new_env.name, "workspace_id": new_env.workspace_id}

@router.get(
    "/workspaces",
    summary="List all workspaces",
    description="Get a list of all workspaces with their IDs, names, and customer IDs."
)
def list_workspaces(db: Session = Depends(get_db)):
    workspaces = db.query(Workspace).all()
    return [
        {"workspace_id": w.id, "name": w.name, "customer_id": w.customer_id}
        for w in workspaces
    ]

@router.get(
    "/environments",
    summary="List all environments",
    description="Get a list of all environments with their IDs, names, and workspace IDs."
)
def list_environments(db: Session = Depends(get_db)):
    environments = db.query(Environment).all()
    return [
        {"environment_id": e.id, "name": e.name, "workspace_id": e.workspace_id}
        for e in environments
    ]
