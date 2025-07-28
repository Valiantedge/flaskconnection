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
            # Wait for a (command, output_queue) tuple from the queue
            item = await command_queue.get()
            if isinstance(item, tuple):
                command, output_queue = item
            else:
                command = item
                output_queue = None
            print(f"[DEBUG] Sending command to agent {key}: {command}", flush=True)
            await websocket.send_json({"command": command})
            # Wait for output from the agent and forward to output_queue if present
            while True:
                msg = await websocket.receive_text()
                if output_queue:
                    await output_queue.put(msg)
                if msg == "[END]":
                    break
                print(f"[AGENT OUTPUT] {key}: {msg}", flush=True)
    except WebSocketDisconnect:
        print(f"[DEBUG] Agent {key} disconnected from websocket.", flush=True)
        pass
    finally:
        connected_agents.pop(key, None)
        command_queues.pop(key, None)
        print(f"[DEBUG] Agent {key} removed from connected_agents. connected_agents={list(connected_agents.keys())}", flush=True)

# Function to enqueue a command for an agent and collect output
async def send_command_to_agent(agent_id, customer_id, environment_id, command):
    key = (agent_id, customer_id, environment_id)
    if key not in command_queues or key not in connected_agents:
        return False, f"Agent {key} is not connected"
    output_queue = asyncio.Queue()
    # Put a tuple (command, output_queue) in the agent's command queue
    await command_queues[key].put((command, output_queue))
    # Collect output lines from the output_queue
    output_lines = []
    while True:
        msg = await output_queue.get()
        if msg == "[END]":
            break
        output_lines.append(msg)
    # Beautify output: join lines with newlines
    beautified = "\n".join(output_lines)
    if beautified.strip() == "":
        return False, "No output received from agent."
    return True, beautified

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


