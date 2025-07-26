from fastapi import WebSocket, WebSocketDisconnect, APIRouter

router = APIRouter()

@router.websocket("/ws/agent/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Here you would handle the received data, e.g., execute command, send output
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass
