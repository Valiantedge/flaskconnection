def poll_for_commands():
    import time
    import requests
    import subprocess
    import json
    CREDENTIALS_FILE = "agent_credentials.json"
    API_URL = "https://socket.valiantedgetech.com/api/agent/next-command"
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
            agent_id = creds.get("agent_id")
    except Exception:
        agent_id = None
    if not agent_id:
        print("[ERROR] No agent_id found for polling commands.")
        return
    while True:
        try:
            resp = requests.get(f"{API_URL}?agent_id={agent_id}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                command = data.get("command")
                command_id = data.get("command_id")
                if command:
                    print(f"[INFO] Polled command: {command}")
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True)
                        output = result.stdout + result.stderr
                        print(f"[INFO] Command output: {output}")
                        # Report result back to backend
                        try:
                            report_url = "https://socket.valiantedgetech.com/api/command/report-output"
                            report_payload = {
                                "command_id": command_id,
                                "output": output
                            }
                            report_resp = requests.post(report_url, json=report_payload, timeout=10)
                            print(f"[INFO] Reported output: {report_resp.status_code} {report_resp.text}")
                        except Exception as e:
                            print(f"[ERROR] Failed to report output: {e}")
                    except Exception as e:
                        print(f"[ERROR] Command execution failed: {e}")
        except Exception as e:
            print(f"[ERROR] Polling exception: {e}")
        time.sleep(10)
CREDENTIALS_FILE = "agent_credentials.json"

def send_heartbeat(token):
    import time
    # Load agent_id, customer_id, environment_id from env or credentials
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
            agent_id = creds.get("agent_id")
    except Exception:
        agent_id = None
    customer_id = os.getenv("CUSTOMER_ID")
    environment_id = os.getenv("ENVIRONMENT_ID")
    while True:
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "agent_id": int(agent_id) if agent_id else None,
                "customer_id": int(customer_id) if customer_id else None,
                "environment_id": int(environment_id) if environment_id else None,
                "status": "active"
            }
            print(f"[DEBUG] Heartbeat payload: {data}")
            resp = requests.post(HEARTBEAT_URL, headers=headers, json=data, timeout=10)
            print(f"[DEBUG] Heartbeat response: {resp.status_code} {resp.text}")
            if resp.status_code == 200:
                print("[INFO] Heartbeat sent.", flush=True)
            else:
                print(f"[ERROR] Heartbeat failed: {resp.text}", flush=True)
        except Exception as e:
            print(f"[ERROR] Heartbeat exception: {e}", flush=True)
        time.sleep(60)



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
import pathlib
import sys

API_URL = "https://socket.valiantedgetech.com/api/agent/register"
HEARTBEAT_URL = "https://socket.valiantedgetech.com/api/agent/heartbeat"
WS_URL_TEMPLATE = "wss://socket.valiantedgetech.com/ws/agent/{agent_id}"
CREDENTIALS_FILE = "agent_credentials.json"


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
    print(f"[DEBUG] Registration payload: {data}")
    resp = requests.post(API_URL, json=data)
    print(f"[DEBUG] Registration response: {resp.status_code} {resp.text}")
    if resp.status_code == 200:
        data = resp.json()
        agent_id = data["agent_id"]
        token = data["token"]
        # Save credentials to file
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({"agent_id": agent_id, "token": token}, f)
        print(f"[INFO] Registered agent: {agent_id} (credentials saved)")
        return agent_id, token
    elif resp.status_code == 400 and "already exists" in resp.text.lower():
        print("[INFO] Agent already registered. Attempting to load credentials from file.")
        cred_path = pathlib.Path(CREDENTIALS_FILE)
        if cred_path.exists():
            with open(CREDENTIALS_FILE, "r") as f:
                creds = json.load(f)
                agent_id = creds.get("agent_id")
                token = creds.get("token")
                if agent_id and token:
                    print("[INFO] Loaded agent credentials from file.")
                    return agent_id, token
                else:
                    print("[ERROR] Credentials file is missing agent_id or token.")
                    return None, None
        else:
            print("[ERROR] Agent already registered but credentials file not found. Please re-register or clean up.")
            return None, None
    else:
        print(f"[ERROR] Registration failed: {resp.text}")
        exit(1)

async def main():
    import time
    print("[DEBUG] Agent starting up...", flush=True)
    agent_name = os.getenv("AGENT_NAME") or socket.gethostname()
    print(f"[DEBUG] Registering agent with name: {agent_name}", flush=True)
    agent_id, token = register_agent(agent_name)
    if not agent_id:
        print("[INFO] Skipping websocket connection due to missing credentials.", flush=True)
        while True:
            await asyncio.sleep(60)  # Stay alive, but do nothing
    else:
        print(f"[DEBUG] Agent registered with id: {agent_id}", flush=True)
        # Start heartbeat thread (token is not needed for WebSocket)
        heartbeat_thread = threading.Thread(target=send_heartbeat, args=(token,), daemon=True)
        heartbeat_thread.start()
        # Start polling thread for commands
        polling_thread = threading.Thread(target=poll_for_commands, daemon=True)
        polling_thread.start()
        customer_id = os.getenv("CUSTOMER_ID")
        environment_id = os.getenv("ENVIRONMENT_ID")
        ws_url = WS_URL_TEMPLATE.format(agent_id=agent_id)
        customer_id = os.getenv("CUSTOMER_ID")
        environment_id = os.getenv("ENVIRONMENT_ID")
        if customer_id and environment_id:
            ws_url += f"?customer_id={customer_id}&environment_id={environment_id}"
        while True:
            try:
                print(f"[DEBUG] Connecting to websocket: {ws_url}", flush=True)
                async with websockets.connect(ws_url) as ws:
                    print("[INFO] Connected to server", flush=True)
                    while True:
                        message = await ws.recv()
                        data = json.loads(message)
                        command = data.get("command")
                        print(f"[INFO] Executing: {command}", flush=True)
                        try:
                            # Stream output line by line as plain text, then send [END]
                            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                            for line in process.stdout:
                                await ws.send(line.rstrip('\n'))
                            process.stdout.close()
                            process.wait()
                            await ws.send("[END]")
                        except Exception as e:
                            await ws.send(json.dumps({"output": str(e), "end": True}))
            except Exception as e:
                print(f"[ERROR] WebSocket connection failed: {e}. Retrying in 10 seconds...", flush=True)
                await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
