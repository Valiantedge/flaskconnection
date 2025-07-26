from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import asyncio
import json

app = FastAPI()

# Store all agent WebSocket connections by agent_id
tagents = {}

@app.get("/")
def read_root():
    return HTMLResponse("""
        <html>
        <head><title>Agent Server</title></head>
        <body>
            <h2>Agent WebSocket Server is running!</h2>
            <p>Connect to <code>ws://[server_ip]:8765/ws</code> using a WebSocket client.</p>
        </body>
        </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # First message from agent should be its agent_id (e.g., hostname or unique id)
    try:
        agent_id = await websocket.receive_text()
        agents[agent_id] = websocket
        print(f"Agent connected: {agent_id} from {websocket.client}")
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket connection closed for {agent_id}: {e}")
        agents.pop(agent_id, None)

# HTTP endpoint to send command to a specific agent and get result
@app.post("/run")
async def run_command(request: Request):
    data = await request.json()
    agent_id = data.get("agent_id")
    command = data.get("command")
    ip = data.get("ip")
    username = data.get("username")
    password = data.get("password")
    if not all([agent_id, command, ip, username, password]):
        return JSONResponse({"error": "Missing required fields"}, status_code=400)
    agent_ws = agents.get(agent_id)
    if agent_ws is None:
        return JSONResponse({"error": f"No agent connected with id {agent_id}"}, status_code=503)
    try:
        # Send SSH details as JSON string (first message)
        ssh_details = {"ip": ip, "username": username, "password": password}
        await agent_ws.send_text(json.dumps(ssh_details))
        # Send command as plain text (second message)
        await agent_ws.send_text(command)
        result = await agent_ws.receive_text()
        return JSONResponse({"output": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("server_multi:app", host="0.0.0.0", port=8765)
