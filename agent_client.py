import asyncio
import websockets
import paramiko

PRIVATE_SERVER_IP = "192.168.32.243"  # Change to your private server IP
SSH_USER = "ubuntu"                   # Change to your SSH username
SSH_PASSWORD = "Cvbnmjkl@30263"      # Change to your SSH password

def run_remote_command(command: str) -> str:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(PRIVATE_SERVER_IP, username=SSH_USER, password=SSH_PASSWORD)
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
            # Wait for command from server
            command = await websocket.recv()
            print(f"Received command from server: {command}")
            # Run the command on the private server via SSH
            output = run_remote_command(command)
            # Send output back to server
            await websocket.send(output)
            print("Output from private server:")
            print(output)

if __name__ == "__main__":
    asyncio.run(run_agent())
