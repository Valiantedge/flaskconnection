import asyncio
import websockets
from agent_exec import run_remote_command

async def run_agent():
    uri = "ws://13.58.212.239:8765/ws"  # Replace with your server's IP if needed
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        # Wait for command from server
        command = await websocket.recv()
        print(f"Received command from server: {command}")
        # Run the command on the private server via agent_exec
        output = run_remote_command(command)
        # Send output back to server
        await websocket.send(output)

if __name__ == "__main__":
    asyncio.run(run_agent())
