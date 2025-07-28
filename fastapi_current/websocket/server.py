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


