# cloud_send_command.py
"""
Cloud-side script to send SSH command requests to relay agent via WebSocket.
"""
import asyncio
import websockets
import json

RELAY_AGENT_WS_URL = "ws://13.58.212.239:8765/ws"  # Replace with your agent's public IP or DNS

async def send_command(target_ip, command, ssh_user="ubuntu", ssh_key=None, ssh_pass=None):
    payload = {
        "target_ip": target_ip,
        "command": command,
        "ssh_user": ssh_user,
    }
    if ssh_key:
        payload["ssh_key"] = ssh_key
    if ssh_pass:
        payload["ssh_pass"] = ssh_pass
    async with websockets.connect(RELAY_AGENT_WS_URL) as websocket:
        await websocket.send(json.dumps(payload))
        result = await websocket.recv()
        print("Result from agent:")
        print(result)

if __name__ == "__main__":
    import sys
    # Example usage: python cloud_send_command.py 192.168.32.101 "ls -l" ubuntu None password123
    if len(sys.argv) < 3:
        print("Usage: python cloud_send_command.py <target_ip> <command> [ssh_user] [ssh_key] [ssh_pass]")
        exit(1)
    target_ip = sys.argv[1]
    command = sys.argv[2]
    ssh_user = sys.argv[3] if len(sys.argv) > 3 else "ubuntu"
    ssh_key = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "None" else None
    ssh_pass = sys.argv[5] if len(sys.argv) > 5 else None
    asyncio.run(send_command(target_ip, command, ssh_user, ssh_key, ssh_pass))
