from fastapi import FastAPI
from routes import auth, agent, command
from websocket import server as ws_server
from ansible_api import long_command

from models import Base
from config import engine

app = FastAPI()

# Routers
app.include_router(auth.router, prefix="/api/user")
app.include_router(agent.router, prefix="/api/agent")
app.include_router(command.router, prefix="/api/command")
app.include_router(ws_server.router)
app.include_router(long_command.router, prefix="/api/ansible")

# Automatically create tables if they do not exist
Base.metadata.create_all(engine)
