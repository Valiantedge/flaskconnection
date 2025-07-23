from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

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
    print(f"New WebSocket client connected: {websocket.client}")
    try:
        # Send a command to the agent
        command = "ls -l"  # You can change this to any command you want
        print(f"Sending command to agent: {command}")
        await websocket.send_text(command)

        # Wait for the agent's response
        response = await websocket.receive_text()
        print(f"Response from agent: {response}")
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8765)
