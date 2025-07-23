import os
import zipfile
import asyncio
import websockets
import json
import traceback

PLAYBOOK_DIR = "/root/flaskconnection"  # Directory containing playbooks
ZIP_FILE = "playbooks.zip"

# -------------------------------
# Create zip of playbooks
# -------------------------------
async def create_zip():
    print(f"[DEBUG] Checking if directory exists: {PLAYBOOK_DIR} -> {os.path.exists(PLAYBOOK_DIR)}")
    if not os.path.exists(PLAYBOOK_DIR):
        raise FileNotFoundError(f"Directory {PLAYBOOK_DIR} does not exist")

    if os.path.exists(ZIP_FILE):
        os.remove(ZIP_FILE)

    with zipfile.ZipFile(ZIP_FILE, 'w', allowZip64=True) as zipf:
        for root, dirs, files in os.walk(PLAYBOOK_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, PLAYBOOK_DIR)
                zipf.write(full_path, arcname)

# -------------------------------
# Send file over WebSocket
# -------------------------------
async def send_file(websocket):
    try:
        await create_zip()
        size = os.path.getsize(ZIP_FILE)
        await websocket.send(json.dumps({"type": "file_info", "size": size}))
        print(f"[INFO] Sending ZIP of size {size} bytes")

        with open(ZIP_FILE, "rb") as f:
            while chunk := f.read(4096):
                await websocket.send(chunk)

        await asyncio.sleep(1)
        await websocket.send(json.dumps({"type": "deploy"}))
        print("[INFO] File sent successfully, deploy signal sent.")
    except Exception as e:
        print(f"[ERROR in send_file]: {e}")
        traceback.print_exc()
        await websocket.send(json.dumps({"type": "error", "message": str(e)}))

# -------------------------------
# WebSocket handler (single argument for compatibility)
# -------------------------------
async def handler(websocket):
    print(f"[INFO] Agent connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"[INFO] Received from agent: {message}")
            if message == "deploy":
                print("[INFO] Deploy command received, preparing file...")
                await send_file(websocket)
            else:
                print(f"[AGENT LOG]: {message}")
    except Exception as e:
        print(f"[ERROR in handler]: {e}")
        traceback.print_exc()
        try:
            await websocket.send(json.dumps({"type": "error", "message": str(e)}))
        except:
            pass

# -------------------------------
# Start WebSocket server
# -------------------------------
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000, max_size=None):
        print("✅ Cloud WebSocket server running on ws://0.0.0.0:8000")
        await asyncio.Future()  # Keep running

if __name__ == "__main__":
    asyncio.run(main())
with zipfile.ZipFile(ZIP_FILE, 'w', allowZip64=True) as zipf:
    for root, dirs, files in os.walk(PLAYBOOK_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, PLAYBOOK_DIR)
            zipf.write(full_path, arcname)