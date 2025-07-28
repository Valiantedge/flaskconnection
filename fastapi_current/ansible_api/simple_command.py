from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from fastapi import Request
import asyncio

# Import the connected_agents dict from websocket.server
from websocket.server import connected_agents

router = APIRouter()

@router.post("/send-command/{agent_id}")
async def send_command(agent_id: int, body: dict = Body(...)):
    command = body.get("command")
    if not command or not isinstance(command, str):
        return {"error": "Missing or invalid 'command' field (must be a string)"}
    agent_ws = connected_agents.get(agent_id)
    if not agent_ws:
        return {"error": f"Agent {agent_id} is not connected"}

    async def stream_output():
        await agent_ws.send_json({"command": command})
        while True:
            msg = await agent_ws.receive_text()
            if msg == "[END]":
                break
            yield msg

    return StreamingResponse(stream_output(), media_type="text/plain")
