import asyncio
import websockets
import paramiko
import json

# Load SSH server details from config.json
def load_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return config["ip"], config["username"], config["password"]
    except Exception as e:
        print(f"Error loading config: {e}")
        return None, None, None

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
    ip, username, password = load_config()
    if not all([ip, username, password]):
        print("Missing SSH server details. Please check config.json.")
        return
    uri = "ws://13.58.212.239:8765/ws"  # Replace with your server's IP if needed
    async with websockets.connect(uri) as websocket:
        print("Connected to server.")
        while True:
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
