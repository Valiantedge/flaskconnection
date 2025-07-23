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
        while True:
            data = await websocket.receive_text()
            print(f"Received message: {data}")
            # Echo back for demo
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8765)
