import asyncio
import websockets

async def run_client():
    uri = "ws://13.58.212.239:8000/ws"  # Match FastAPI route
    async with websockets.connect(uri) as websocket:
        await websocket.send("deploy")
        response = await websocket.recv()
        print("Response from cloud:", response)

if __name__ == "__main__":
    asyncio.run(run_client())
