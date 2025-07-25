import asyncio
import websockets
import paramiko
import json
import socket

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
        # Send agent_id (hostname) as the first message
        agent_id = socket.gethostname()
        await websocket.send(agent_id)
        print(f"Sent agent_id: {agent_id}")
        while True:
            # First message should be SSH details as JSON
            ssh_details_msg = await websocket.recv()
            try:
                ssh_details = json.loads(ssh_details_msg)
                ip = ssh_details["ip"]
                username = ssh_details["username"]
                password = ssh_details["password"]
            except Exception as e:
                print(f"Error parsing SSH details: {e}")
                continue
            print(f"Loaded SSH details: {ip}, {username}")
            # Wait for command from server
            command = await websocket.recv()
            print(f"Received command from server: {command}")
            # Run the command on the private server via SSH
            output = run_remote_command(command, ip, username, password)
            # Send output back to server
            await websocket.send(output)
            print("Output from private server:")
            print(output)

if __name__ == "__main__":
    asyncio.run(run_agent())
