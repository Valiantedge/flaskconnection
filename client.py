import asyncio
import websockets
import json
import zipfile
import os
import paramiko
from scp import SCPClient

TEMP_DIR = "received_playbooks"
ZIP_FILE = "playbooks.zip"
TARGET_HOST = "192.168.1.50"  # Replace with target server IP
SSH_USER = "ec2-user"         # Replace with SSH username
SSH_KEY = "id_rsa"            # Replace with private key path

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

def ssh_execute_and_stream(command, websocket):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(TARGET_HOST, username=SSH_USER, key_filename=SSH_KEY)

    # Copy playbooks
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(TEMP_DIR, recursive=True, remote_path="/tmp/deployment")

    # Execute deploy.sh
    stdin, stdout, stderr = ssh.exec_command("cd /tmp/deployment && chmod +x deploy.sh && ./deploy.sh")
    for line in iter(stdout.readline, ""):
        asyncio.run(websocket.send(line.strip()))
    for line in iter(stderr.readline, ""):
        asyncio.run(websocket.send("ERR: " + line.strip()))

    ssh.close()

async def run_client():
    uri = "ws://<CLOUD_SERVER_IP>:8000"
    async with websockets.connect(uri) as websocket:
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
                    await websocket.send(f"Expecting {expected_size} bytes")
                elif data.get("type") == "deploy":
                    await extract_zip()
                    await websocket.send("Files extracted. Running SSH deployment...")
                    ssh_execute_and_stream("bash deploy.sh", websocket)
                    await websocket.send("Deployment completed.")
                    break

if __name__ == "__main__":
    asyncio.run(run_client())
