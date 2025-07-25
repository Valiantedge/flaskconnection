import asyncio
import websockets
import paramiko
import json
import os

def run_remote_command(command: str, ip: str, username: str, password: str) -> str:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode() + stderr.read().decode()
        ssh.close()
        return output
    except Exception as e:
        return f"Error running command on private server: {e}"

async def run_agent():
    uri = "ws://13.58.212.239:8765/ws"  # Replace with your server's IP if needed
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        while True:
            # Wait for message from server
            msg = await websocket.recv()
            try:
                data = json.loads(msg)
                if data.get("action") == "write_file":
                    # Write file to disk
                    path = data["path"]
                    content = data["content"]
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    await websocket.send(f"File written to {path}")
                    print(f"File written to {path}")
                    continue
                # Otherwise, treat as SSH details
                ip = data["ip"]
                username = data["username"]
                password = data["password"]
                # Wait for command
                command = await websocket.recv()
                print(f"Received command from server: {command}")
                output = run_remote_command(command, ip, username, password)
                await websocket.send(output)
                print("Output from private server:")
                print(output)
            except Exception as e:
                print(f"Error parsing message: {e}")
                await websocket.send(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_agent())
