import asyncio
import websockets

async def run_client():
    uri = "ws://YOUR_CLOUD_SERVER_IP:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send("deploy")
        response = await websocket.recv()
        print("Response from cloud:", response)

if __name__ == "__main__":
    asyncio.run(run_client())
