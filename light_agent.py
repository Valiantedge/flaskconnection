# light_agent.py
"""
This agent only connects to the cloud server and reports status. No script execution.
"""
import asyncio
import websockets
import json

async def run_agent():
    uri = "ws://13.58.212.239:8765/ws"  # Replace with your cloud server IP
    async with websockets.connect(uri) as websocket:
        print("Connected to cloud server.")
        while True:
            msg = await websocket.recv()
            print(f"Received message from server: {msg}")
            # Optionally send status or heartbeat
            await websocket.send(json.dumps({"status": "alive"}))

if __name__ == "__main__":
    asyncio.run(run_agent())
