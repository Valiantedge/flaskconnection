from fastapi import FastAPI, WebSocket
import subprocess
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            command = await websocket.receive_text()
            print(f"Received command: {command}")

            if command == "deploy":
                process = subprocess.run(["bash", "deploy.sh"], capture_output=True, text=True)
                output = process.stdout + process.stderr
                await websocket.send_text(output)
            else:
                await websocket.send_text(f"Unknown command: {command}")
        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            break

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
