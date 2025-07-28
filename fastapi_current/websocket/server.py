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
# Track command queues for each agent
command_queues = {}


from fastapi import Query


@router.websocket("/ws/agent/{agent_id}")
async def websocket_command(websocket: WebSocket, agent_id: int, customer_id: int = Query(...), environment_id: int = Query(...)):
    await websocket.accept()
    key = (agent_id, customer_id, environment_id)
    connected_agents[key] = websocket
    command_queue = asyncio.Queue()
    command_queues[key] = command_queue
    print(f"[DEBUG] Agent {key} connected via websocket. connected_agents={list(connected_agents.keys())}", flush=True)
    try:
        while True:
            # Wait for a command from the queue (sent by HTTP endpoint)
            command = await command_queue.get()
            print(f"[DEBUG] Sending command to agent {key}: {command}", flush=True)
            await websocket.send_json({"command": command})
            # Wait for output from the agent
            while True:
                msg = await websocket.receive_text()
                if msg == "[END]":
                    break
                # Optionally, you can store or forward this output
                # For now, just print it
                print(f"[AGENT OUTPUT] {key}: {msg}", flush=True)
    except WebSocketDisconnect:
        print(f"[DEBUG] Agent {key} disconnected from websocket.", flush=True)
        pass
    finally:
        connected_agents.pop(key, None)
        command_queues.pop(key, None)
        print(f"[DEBUG] Agent {key} removed from connected_agents. connected_agents={list(connected_agents.keys())}", flush=True)

# Function to enqueue a command for an agent
async def send_command_to_agent(agent_id, customer_id, environment_id, command):
    key = (agent_id, customer_id, environment_id)
    if key not in command_queues:
        return False, f"Agent {key} is not connected"
    await command_queues[key].put(command)
    return True, "Command sent"

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


