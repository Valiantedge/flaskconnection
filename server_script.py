from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import json

app = FastAPI()
agent_ws = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global agent_ws
    await websocket.accept()
    agent_ws = websocket
    print(f"New WebSocket client connected: {websocket.client}")
    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
        agent_ws = None

@app.post("/send-script")
async def send_script(request):
    global agent_ws
    if agent_ws is None:
        return JSONResponse({"error": "No agent connected"}, status_code=503)
    data = await request.json()
    script_content = data.get("script_content")
    script_name = data.get("script_name", "remote_script.sh")
    exec_cmd = data.get("exec_cmd", "bash")
    if not script_content:
        return JSONResponse({"error": "Missing script content"}, status_code=400)
    payload = {
        "script_content": script_content,
        "script_name": script_name,
        "exec_cmd": exec_cmd
    }
    await agent_ws.send_text(json.dumps(payload))
    result = await agent_ws.receive_text()
    return JSONResponse({"output": result})

if __name__ == "__main__":
    uvicorn.run("server_script:app", host="0.0.0.0", port=8765)
