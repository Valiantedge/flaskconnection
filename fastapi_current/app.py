from fastapi import FastAPI
from routes import auth, agent, command
from websocket import server as ws_server
from ansible_api import long_command

from models import Base
from config import engine



# Define OpenAPI tags for custom order in Swagger UI
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

app = FastAPI(openapi_tags=openapi_tags)

# Routers (ordered for logical SaaS onboarding flow)
app.include_router(agent.router, prefix="/api/agent")
app.include_router(auth.router, prefix="/api/user")
app.include_router(command.router, prefix="/api/command")
app.include_router(long_command.router, prefix="/api/ansible")
app.include_router(ws_server.router)

# Automatically create tables if they do not exist
Base.metadata.create_all(engine)
