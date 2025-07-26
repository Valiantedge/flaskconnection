import asyncio
import websockets
import json
from app import db
from models import Agent, Command

connected_agents = {}

async def handler(websocket, path):
    # Authenticate agent
    params = dict(websocket.request_headers)
    token = params.get("Authorization")
    if not token:
        await websocket.close()
        return

    agent = Agent.query.filter_by(token=token).first()
    if not agent:
        await websocket.close()
        return

    connected_agents[agent.agent_id] = websocket
    print(f"[INFO] Agent {agent.agent_id} connected")

    try:
        while True:
            await asyncio.sleep(2)
            # Check for pending commands
            cmd = Command.query.filter_by(agent_id=agent.agent_id, status='queued').first()
            if cmd:
                await websocket.send(json.dumps({"command": cmd.command}))
                cmd.status = 'running'
                db.session.commit()

            # Receive agent response
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=1)
                response = json.loads(msg)
                cmd.status = 'completed'
                cmd.output = response.get('output', '')
                db.session.commit()
            except asyncio.TimeoutError:
                pass
    except websockets.ConnectionClosed:
        print(f"[INFO] Agent {agent.agent_id} disconnected")
        connected_agents.pop(agent.agent_id, None)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("[INFO] WebSocket server running on ws://0.0.0.0:8000")
        await asyncio.Future()

asyncio.run(main())
