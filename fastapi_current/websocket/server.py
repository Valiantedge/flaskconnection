
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
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

@router.websocket("/ws/agent/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: int):
    await websocket.accept()
    db = next(get_db())
    try:
        # Authenticate agent by token in header
        token = websocket.headers.get("authorization")
        if not token:
            await websocket.close()
            return
        if token.lower().startswith("bearer "):
            token = token[7:]
        agent = db.query(Agent).filter(Agent.id == agent_id, Agent.token == token).first()
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
                # Wait for output
                try:
                    msg = await websocket.receive_text()
                    response = json.loads(msg)
                    cmd.status = 'completed'
                    cmd.output = response.get('output', '')
                    db.commit()
                except Exception as e:
                    print(f"[ERROR] Failed to receive output: {e}")
            else:
                await asyncio.sleep(2)
    except WebSocketDisconnect:
        print(f"[INFO] Agent {agent_id} disconnected.")
    finally:
        db.close()
