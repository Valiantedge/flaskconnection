# server.py

import asyncio
import websockets

connected_agents = set()

async def handler(websocket):
    connected_agents.add(websocket)
    try:
        async for message in websocket:
            # Handle received message from agent; for example, broadcast or forward it
            print(f"Received from agent: {message}")
            # You can relay this message to private server or clients as needed
    except websockets.ConnectionClosed:
        pass
    finally:
        connected_agents.remove(websocket)

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WebSocket server started on ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
