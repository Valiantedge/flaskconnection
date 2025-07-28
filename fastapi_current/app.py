from fastapi import FastAPI
from routes import auth, agent, command, agent_test, agent_create_dir  # Import agent_test and agent_create_dir routers
from websocket import server as ws_server
from ansible_api import long_command

from models import Base
from config import engine



# Define OpenAPI tags for custom order in docs and ReDoc
openapi_tags = [
    {"name": "1. User Sign Up", "description": "Customer sign up (creates customer and admin user)"},
    {"name": "2. User Sign In", "description": "Login User"},
    {"name": "3. User Management", "description": "Register a new user for a customer"},
    {"name": "4. Workspace & Environment", "description": "Workspace and environment management"},
    {"name": "5. Agent Management", "description": "Agent registration and management"},
    {"name": "6. Customer Management", "description": "Customer details"},
    {"name": "7. Command Execution", "description": "Send and get command status"},
    {"name": "8. Ansible", "description": "Run long Ansible commands"},
]

app = FastAPI(
    openapi_tags=openapi_tags,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Routers (ordered for logical SaaS onboarding flow)
app.include_router(agent.router, prefix="/api/agent")
app.include_router(auth.router, prefix="/api/user")
app.include_router(command.router, prefix="/api/command")
app.include_router(long_command.router, prefix="/api/ansible")
app.include_router(ws_server.router)
app.include_router(agent_test.router)  # Include agent_test router
app.include_router(agent_create_dir.router)  # Register the new endpoint

# Automatically create tables if they do not exist
Base.metadata.create_all(engine)
