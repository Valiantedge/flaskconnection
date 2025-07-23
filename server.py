from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import asyncio


app = FastAPI()

# Store the agent WebSocket connection
agent_ws = None

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
    global agent_ws
    await websocket.accept()
    agent_ws = websocket
    print(f"New WebSocket client connected: {websocket.client}")
    try:
        while True:
            # Keep connection open, agent waits for commands
            await asyncio.sleep(1)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
        agent_ws = None

# HTTP endpoint to send command to agent and get result
@app.post("/run")
async def run_command(request: Request):
    global agent_ws
    if agent_ws is None:
        return JSONResponse({"error": "No agent connected"}, status_code=503)
    data = await request.json()
    command = data.get("command")
    ip = data.get("ip")
    username = data.get("username")
    password = data.get("password")
    if not all([command, ip, username, password]):
        return JSONResponse({"error": "Missing required fields"}, status_code=400)
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
    uvicorn.run("server:app", host="0.0.0.0", port=8765)
