from fastapi import APIRouter, Body

router = APIRouter()

@router.post("/api/agent/test")
async def test_command_to_agent(payload: dict = Body(...)):
    # Example payload: {"agent_id": 17, "customer_id": 5, "environment_id": 1, "command": "echo hello"}
    # Here you would normally queue or send the command to the agent
    # For now, just echo back the payload for testing
    return {"received": payload, "status": "test command accepted"}
