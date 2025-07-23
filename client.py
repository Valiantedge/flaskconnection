import asyncio
import websockets
import json
import zipfile
import os
import paramiko
from scp import SCPClient

TEMP_DIR = "received_playbooks"
ZIP_FILE = "playbooks.zip"
TARGET_HOST = "192.168.32.243"  # Replace with target server IP
SSH_USER = "ubuntu"             # Replace with SSH username
SSH_PASSWORD = "Cvbnmjkl@30263" # Replace with SSH password

# Extract zip
async def extract_zip():
    if os.path.exists(TEMP_DIR):
        for root, dirs, files in os.walk(TEMP_DIR, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(TEMP_DIR)

    os.makedirs(TEMP_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(TEMP_DIR)

# SSH to target and deploy
async def ssh_execute_and_stream(command, websocket):
    def run_ssh():
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(TARGET_HOST, username=SSH_USER, password=SSH_PASSWORD)

        # Copy playbooks to remote /tmp/deployment
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(TEMP_DIR, recursive=True, remote_path="/tmp/deployment")

        # Run deploy.sh on target
        stdin, stdout, stderr = ssh.exec_command(f"cd /tmp/deployment && chmod +x deploy.sh && {command}")
        output_lines = stdout.readlines()
        error_lines = stderr.readlines()
        ssh.close()
        return output_lines, error_lines

    # Run SSH in thread
    output_lines, error_lines = await asyncio.to_thread(run_ssh)

    # Send logs back to cloud
    for line in output_lines:
        await websocket.send(line.strip())
    for line in error_lines:
        await websocket.send("ERR: " + line.strip())

async def run_client():
    uri = "ws://13.58.212.239:8000"  # Replace with cloud IP
    async with websockets.connect(uri, max_size=None) as websocket:
        await websocket.send("deploy")
        file = open(ZIP_FILE, "wb")
        expected_size = 0
        received = 0

        while True:
            msg = await websocket.recv()
            if isinstance(msg, bytes):
                file.write(msg)
                received += len(msg)
                if received >= expected_size and expected_size > 0:
                    file.close()
            else:
                data = json.loads(msg)
                if data.get("type") == "file_info":
                    expected_size = data["size"]
                    print(f"Expecting {expected_size} bytes...")
                elif data.get("type") == "deploy":
                    file.close()
                    await extract_zip()
                    await websocket.send("Files extracted. Running SSH deployment...")
                    await ssh_execute_and_stream("./deploy.sh", websocket)
                    await websocket.send("Deployment completed.")
                    break

if __name__ == "__main__":
    asyncio.run(run_client())
