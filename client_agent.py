


import asyncio
import websockets
import json
import subprocess
import requests
import socket
import platform
import uuid
import os
import threading

API_URL = "https://socket.valiantedgetech.com/api/agent/register"
HEARTBEAT_URL = "https://socket.valiantedgetech.com/api/agent/heartbeat"
WS_URL_TEMPLATE = "wss://socket.valiantedgetech.com/ws/agent/{agent_id}"
def send_heartbeat(token):
    while True:
        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            data = {"status": "active"}
            resp = requests.post(HEARTBEAT_URL, headers=headers, json=data, timeout=10)
            if resp.status_code == 200:
                print("[INFO] Heartbeat sent.")
            else:
                print(f"[ERROR] Heartbeat failed: {resp.text}")
        except Exception as e:
            print(f"[ERROR] Heartbeat exception: {e}")
        # Wait 60 seconds before next heartbeat
        time.sleep(60)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_machine_uuid():
    return str(uuid.uuid1())

def get_os_type():
    return platform.system()

def register_agent(name):
    customer_id = os.getenv("CUSTOMER_ID")
    workspace_id = os.getenv("WORKSPACE_ID")
    environment_id = os.getenv("ENVIRONMENT_ID")
    missing = []
    if not customer_id:
        missing.append("CUSTOMER_ID")
    if not workspace_id:
        missing.append("WORKSPACE_ID")
    if not environment_id:
        missing.append("ENVIRONMENT_ID")
    if missing:
        print(f"[ERROR] The following environment variables must be set: {', '.join(missing)}")
        exit(1)
    try:
        customer_id = int(customer_id)
        workspace_id = int(workspace_id)
        environment_id = int(environment_id)
    except ValueError:
        print("[ERROR] CUSTOMER_ID, WORKSPACE_ID, and ENVIRONMENT_ID must be integers.")
        exit(1)
    data = {
        "name": name,
        "customer_id": customer_id,
        "workspace_id": workspace_id,
        "environment_id": environment_id,
        "ip_address": get_ip_address(),
        "machine_uuid": get_machine_uuid(),
        "os_type": get_os_type(),
    }
    resp = requests.post(API_URL, json=data)
    if resp.status_code == 200:
        data = resp.json()
        return data["agent_id"], data["token"]
    elif resp.status_code == 400 and "Agent already exists" in resp.text:
        print(f"[INFO] Agent already exists, continuing...")
        return None, None
    else:
        print(f"[ERROR] Registration failed: {resp.text}")
        exit(1)

async def main():
    import time
    agent_name = os.getenv("AGENT_NAME") or socket.gethostname()
    agent_id, token = register_agent(agent_name)
    if not agent_id or not token:
        print("[INFO] Skipping websocket connection due to missing credentials.")
        while True:
            await asyncio.sleep(60)  # Stay alive, but do nothing
    else:
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=send_heartbeat, args=(token,), daemon=True)
        heartbeat_thread.start()
        ws_url = WS_URL_TEMPLATE.format(agent_id=agent_id)
        async with websockets.connect(ws_url, extra_headers={"Authorization": f"Bearer {token}"}) as ws:
            print("[INFO] Connected to server")
            while True:
                message = await ws.recv()
                data = json.loads(message)
                command = data.get("command")
                print(f"[INFO] Executing: {command}")
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    await ws.send(json.dumps({"output": output}))
                except Exception as e:
                    await ws.send(json.dumps({"output": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
