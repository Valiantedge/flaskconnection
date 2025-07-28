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
    customer_id = body.get("customer_id")
    environment_id = body.get("environment_id")
    if not command or not isinstance(command, str):
        return {"error": "Missing or invalid 'command' field (must be a string)"}
    if customer_id is None or environment_id is None:
        return {"error": "customer_id and environment_id are required"}
    key = (agent_id, customer_id, environment_id)
    agent_ws = connected_agents.get(key)
    if not agent_ws:
        return {"error": f"Agent {key} is not connected"}

    async def stream_output():
        await agent_ws.send_json({"command": command})
        while True:
            msg = await agent_ws.receive_text()
            if msg == "[END]":
                break
            yield msg

    return StreamingResponse(stream_output(), media_type="text/plain")
