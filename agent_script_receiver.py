import asyncio
import websockets
import json
import os

def save_and_execute_script(script_content: str, script_name: str, exec_cmd: str) -> str:
    try:
        # Save script to file
        with open(script_name, "w") as f:
            f.write(script_content)
        os.chmod(script_name, 0o700)
        # Execute script
        stream = os.popen(f"{exec_cmd} {script_name}")
        output = stream.read()
        return output
    except Exception as e:
        return f"Error executing script: {e}"

async def run_agent():
    uri = "ws://13.58.212.239:8765/ws"  # Replace with your server's IP if needed
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        # First message should be SSH details as JSON (can be ignored for local execution)
        ssh_details_msg = await websocket.recv()
        print(f"Received initial message (ignored for script mode): {ssh_details_msg}")
        while True:
            try:
                msg = await websocket.recv()
                payload = json.loads(msg)
                script_content = payload["script_content"]
                script_name = payload.get("script_name", "remote_script.sh")
                exec_cmd = payload.get("exec_cmd", "bash")
                print(f"Received script to execute: {script_name}")
                output = save_and_execute_script(script_content, script_name, exec_cmd)
                print("Script output:")
                print(output)
                await websocket.send(output)
            except Exception as e:
                error_msg = f"Agent error: {e}"
                print(error_msg)
                await websocket.send(error_msg)
            print("Script output:")
            print(output)

if __name__ == "__main__":
    asyncio.run(run_agent())
