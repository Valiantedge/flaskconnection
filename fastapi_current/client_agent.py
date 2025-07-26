import asyncio
import websockets
import json
import subprocess

SERVER_URL = "ws://your-server-ip:8000"
AGENT_TOKEN = "your-agent-token"

async def main():
    async with websockets.connect(SERVER_URL, extra_headers={"Authorization": AGENT_TOKEN}) as ws:
        print("[INFO] Connected to server")
        while True:
            message = await ws.recv()
            data = json.loads(message)
            command = data.get("command")
            print(f"[INFO] Executing: {command}")
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                await ws.send(json.dumps({"output": output}))
            except Exception as e:
                await ws.send(json.dumps({"output": str(e)}))

asyncio.run(main())
