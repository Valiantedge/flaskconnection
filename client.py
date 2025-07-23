import asyncio
import websockets
import json
import zipfile
import os
import paramiko
from scp import SCPClient

# Configurations
TEMP_DIR = "received_playbooks"
ZIP_FILE = "playbooks.zip"
TARGET_HOST = "192.168.32.243"  # Target private server IP
SSH_USER = "ubuntu"             # SSH username
SSH_PASSWORD = "Cvbnmjkl@30263" # SSH password
CHUNK_SIZE = 4096

# Extract the received ZIP
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
    print("[INFO] Files extracted successfully.")

# SSH and deploy on target server
async def ssh_execute_and_stream(websocket):
    def run_ssh():
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(TARGET_HOST, username=SSH_USER, password=SSH_PASSWORD)

            with SCPClient(ssh.get_transport()) as scp:
                scp.put(TEMP_DIR, recursive=True, remote_path="/tmp/deployment")

            stdin, stdout, stderr = ssh.exec_command("cd /tmp/deployment && chmod +x deploy.sh && ./deploy.sh")
            output = stdout.readlines()
            error = stderr.readlines()
            ssh.close()
            return output, error
        except Exception as e:
            return [], [f"SSH ERROR: {e}"]

    output_lines, error_lines = await asyncio.to_thread(run_ssh)
    for line in output_lines:
        await websocket.send(line.strip())
    for line in error_lines:
        await websocket.send("ERR: " + line.strip())

# Main WebSocket client
async def run_client():
    uri = "ws://13.58.212.239:8000"  # Cloud server IP
    try:
        async with websockets.connect(uri, max_size=None) as websocket:
            print("[INFO] Connected to cloud server.")
            await websocket.send("deploy")
            file = open(ZIP_FILE, "wb")
            expected_size = 0
            received = 0

            while True:
                msg = await websocket.recv()
                if isinstance(msg, bytes):
                    file.write(msg)
                    received += len(msg)
                    print(f"[INFO] Received {received}/{expected_size} bytes", end="\r")
                else:
                    data = json.loads(msg)
                    if data.get("type") == "file_info":
                        expected_size = data["size"]
                        print(f"[INFO] Expecting {expected_size} bytes...")
                    elif data.get("type") == "deploy":
                        file.close()
                        print("[INFO] ZIP download complete. Extracting...")
                        await extract_zip()
                        await websocket.send("Files extracted. Running SSH deployment...")
                        await ssh_execute_and_stream(websocket)
                        await websocket.send("Deployment completed.")
                        break
                    elif data.get("type") == "error":
                        print(f"[ERROR] Server error: {data['message']}")
                        break
    except Exception as e:
        print(f"[ERROR in WebSocket client]: {e}")

if __name__ == "__main__":
    asyncio.run(run_client())
