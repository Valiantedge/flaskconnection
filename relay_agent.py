# relay_agent.py
"""
Relay agent for SaaS automation. Runs on one machine inside the private network.
Receives commands from the cloud server and executes them on any reachable private server via SSH.
"""
import asyncio
import websockets
import json
import subprocess

CLOUD_WS_URL = "ws://13.58.212.239:8765/ws"  # Replace with your cloud server IP

async def run_agent():
    async with websockets.connect(CLOUD_WS_URL) as websocket:
        print("Connected to cloud server.")
        while True:
            msg = await websocket.recv()
            print(f"Received from cloud: {msg}")
            try:
                payload = json.loads(msg)
                target_ip = payload["target_ip"]
                command = payload["command"]
                ssh_user = payload.get("ssh_user", "ubuntu")
                ssh_key = payload.get("ssh_key", None)  # Optional: path to private key
                ssh_pass = payload.get("ssh_pass", None)  # Optional: password
                import platform
                if platform.system() == "Windows":
                    if ssh_pass:
                        ssh_cmd = ["plink", "-ssh", f"{ssh_user}@{target_ip}", "-pw", ssh_pass, command]
                    else:
                        ssh_cmd = ["plink", "-ssh", f"{ssh_user}@{target_ip}", command]
                    if ssh_key:
                        ssh_cmd += ["-i", ssh_key]
                else:
                    if ssh_pass:
                        ssh_cmd = ["sshpass", "-p", ssh_pass, "ssh"]
                    else:
                        ssh_cmd = ["ssh"]
                    if ssh_key:
                        ssh_cmd += ["-i", ssh_key]
                    ssh_cmd += [f"{ssh_user}@{target_ip}", command]
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                output = {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                output = {"error": str(e)}
            await websocket.send(json.dumps(output))

if __name__ == "__main__":
    asyncio.run(run_agent())
