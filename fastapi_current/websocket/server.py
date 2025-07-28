from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
import asyncio
from sqlalchemy.orm import Session
from models import Agent, Command
from config import SessionLocal
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Store connected UI/admin clients
ui_clients = set()


# Track connected agent websockets in memory, keyed by (agent_id, customer_id, environment_id)
connected_agents = {}


from fastapi import Query

@router.websocket("/ws/agent/{agent_id}")
async def websocket_command(websocket: WebSocket, agent_id: int, customer_id: int = Query(...), environment_id: int = Query(...)):
    await websocket.accept()
    key = (agent_id, customer_id, environment_id)
    connected_agents[key] = websocket
    print(f"[DEBUG] Agent {key} connected via websocket. connected_agents={list(connected_agents.keys())}", flush=True)
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            if not command or not isinstance(command, str):
                await websocket.send_text("Missing or invalid 'command' field (must be a string)\n")
                continue
            print(f"[DEBUG] Executing command for agent {key}: {command}", flush=True)
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                await websocket.send_text(line.decode())
            await process.wait()
            await websocket.send_text("[END]")
    except WebSocketDisconnect:
        print(f"[DEBUG] Agent {key} disconnected from websocket.", flush=True)
        pass
    finally:
        connected_agents.pop(key, None)
        print(f"[DEBUG] Agent {key} removed from connected_agents. connected_agents={list(connected_agents.keys())}", flush=True)

@router.websocket("/ws/ui/{agent_id}")
async def ui_websocket(websocket: WebSocket, agent_id: int):
    await websocket.accept()
    ui_clients.add(websocket)
    print(f"[INFO] UI client connected for agent {agent_id}.")
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print(f"[INFO] UI client for agent {agent_id} disconnected.")
    finally:
        ui_clients.discard(websocket)


