from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from fastapi import Request
import asyncio

# Import the connected_agents dict from websocket.server
from websocket.server import send_command_to_agent

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

    # Streaming generator for live output
    async def output_stream():
        key = (agent_id, customer_id, environment_id)
        from websocket.server import command_queues, connected_agents
        if key not in command_queues or key not in connected_agents:
            yield f"Agent {key} is not connected\n"
            return
        output_queue = asyncio.Queue()
        await command_queues[key].put((command, output_queue))
        while True:
            msg = await output_queue.get()
            if msg == "[END]":
                break
            yield msg if msg.endswith("\n") else msg + "\n"

    return StreamingResponse(output_stream(), media_type="text/plain")
