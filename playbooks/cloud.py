import os
import zipfile
import asyncio
import websockets
import json

PLAYBOOK_DIR = "/opt/playbooks"
ZIP_FILE = "playbooks.zip"

async def create_zip():
    if os.path.exists(ZIP_FILE):
        os.remove(ZIP_FILE)
    with zipfile.ZipFile(ZIP_FILE, 'w') as zipf:
        for root, dirs, files in os.walk(PLAYBOOK_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, PLAYBOOK_DIR)
                zipf.write(full_path, arcname)

async def send_file(websocket):
    await create_zip()
    size = os.path.getsize(ZIP_FILE)
    await websocket.send(json.dumps({"type": "file_info", "size": size}))

    with open(ZIP_FILE, "rb") as f:
        while chunk := f.read(4096):
            await websocket.send(chunk)

    await asyncio.sleep(1)
    await websocket.send(json.dumps({"type": "deploy"}))

async def handler(websocket, path):
    print("Agent connected.")
    async for message in websocket:
        if message == "deploy":
            print("Deploy command received. Sending files...")
            await send_file(websocket)
        else:
            print(f"Agent Log: {message}")

start_server = websockets.serve(handler, "0.0.0.0", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
print("Cloud WebSocket server running on ws://0.0.0.0:8000")
asyncio.get_event_loop().run_forever()
