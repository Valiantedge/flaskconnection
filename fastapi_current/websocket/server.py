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

@router.websocket("/ws/agent/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: int):
    await websocket.accept()
    db = next(get_db())
    try:
        # Authenticate agent by agent_id, customer_id, and environment_id
        # Expect these as query parameters
        customer_id = websocket.query_params.get("customer_id")
        environment_id = websocket.query_params.get("environment_id")
        agent = db.query(Agent).filter(
            Agent.id == agent_id,
            Agent.customer_id == customer_id,
            Agent.environment_id == environment_id
        ).first()
        if not agent:
            await websocket.close()
            return
        print(f"[INFO] Agent {agent_id} connected via websocket.")
        while True:
            # Check for queued command
            cmd = db.query(Command).filter_by(agent_id=agent_id, status='queued').first()
            if cmd:
                await websocket.send_text(json.dumps({"command": cmd.command}))
                cmd.status = 'running'
                db.commit()
                # Stream output
                output_accum = ""
                try:
                    while True:
                        msg = await websocket.receive_text()
                        response = json.loads(msg)
                        chunk = response.get('output', '')
                        end = response.get('end', False)
                        output_accum += chunk
                        # Forward chunk to all connected UI clients for this agent
                        for ui_ws in list(ui_clients):
                            try:
                                await ui_ws.send_text(chunk)
                            except Exception:
                                ui_clients.discard(ui_ws)
                        # Optionally, print or forward chunk here for live UI
                        if end:
                            break
                    cmd.status = 'completed'
                    cmd.output = output_accum
                    db.commit()
                except Exception as e:
                    print(f"[ERROR] Failed to receive output: {e}")
            else:
                await asyncio.sleep(2)
    except WebSocketDisconnect:
        print(f"[INFO] Agent {agent_id} disconnected.")
    finally:
        db.close()
