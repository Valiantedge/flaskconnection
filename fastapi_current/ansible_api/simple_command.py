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

    # Use the new send_command_to_agent function
    success, result = await send_command_to_agent(agent_id, customer_id, environment_id, command)
    if not success:
        return {"error": result}
    # Beautify output: wrap in a JSON object
    return {"output": result}
