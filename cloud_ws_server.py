# cloud_ws_server.py
"""
WebSocket server for cloud automation. Accepts agent connections and can trigger Ansible tasks.
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import uvicorn
import subprocess
import json
import asyncio


app = FastAPI()
agents = set()

class PlaybookRequest(BaseModel):
    inventory: str = "inventory.ini"
    playbook: str = "playbooks/your_playbook.yml"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    agents.add(websocket)
    print(f"Agent connected: {websocket.client}")
    try:
        while True:
            msg = await websocket.receive_text()
            print(f"Received from agent: {msg}")
            # Optionally process agent status or heartbeat
    except Exception as e:
        print(f"Agent disconnected: {e}")
    finally:
        agents.discard(websocket)

@app.post("/run-playbook")
async def run_playbook(body: PlaybookRequest):
    inventory = body.inventory
    playbook = body.playbook
    cmd = ["ansible-playbook", "-i", inventory, playbook]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        # Optionally notify all agents
        for ws in agents:
            try:
                await ws.send_text(json.dumps({"event": "playbook_complete", "output": output}))
            except Exception:
                pass
        return JSONResponse(output)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("cloud_ws_server:app", host="0.0.0.0", port=8765)
