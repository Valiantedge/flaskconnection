from fastapi import APIRouter, Body, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, StreamingResponse
from models import Command
from config import SessionLocal
import subprocess
import asyncio


from fastapi import Request
from typing import Dict

router = APIRouter()

# Track connected agent websockets in memory
connected_agents: Dict[int, WebSocket] = {}

# Add missing get_db function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/run-command")
async def run_command(payload: dict = Body(...)):
    agent_id = payload.get("agent_id")
    command = payload.get("command")
    missing = [k for k in ("agent_id", "command") if not payload.get(k)]
    if missing:
        return {"status": "error", "detail": f"Missing fields: {', '.join(missing)}"}
    if not isinstance(command, str):
        return {"status": "error", "detail": "'command' must be a string"}
    agent_ws = connected_agents.get(int(agent_id))
    if not agent_ws:
        return {"status": "error", "detail": f"Agent {agent_id} is not connected"}

    async def stream_from_agent():
        await agent_ws.send_json({"command": command})
        while True:
            msg = await agent_ws.receive_text()
            if msg == "[END]":
                break
            yield msg

    return StreamingResponse(stream_from_agent(), media_type="text/plain")

# New endpoint: stream output for a command by command_id (SaaS style)
@router.get("/stream-output/{command_id}")
async def stream_output(command_id: int):
    db = next(get_db())
    cmd = db.query(Command).filter_by(id=command_id).first()
    if not cmd:
        async def error_gen():
            yield f"No such command_id: {command_id}\n"
        return StreamingResponse(error_gen(), media_type="text/plain")
    agent_ws = connected_agents.get(int(cmd.agent_id))
    if not agent_ws:
        async def error_gen():
            yield f"Agent {cmd.agent_id} is not connected\n"
        return StreamingResponse(error_gen(), media_type="text/plain")

    async def stream_from_agent():
        # Send command to agent
        await agent_ws.send_json({"command": cmd.command})
        while True:
            msg = await agent_ws.receive_text()
            if msg == "[END]":
                break
            yield msg

    return StreamingResponse(stream_from_agent(), media_type="text/plain")

@router.post("/stream-command")
async def stream_command(payload: dict = Body(...)):
    command = payload.get("command")
    if not command or not isinstance(command, str):
        async def error_gen():
            yield "Missing or invalid 'command' field (must be a string)\n"
        return StreamingResponse(error_gen(), media_type="text/plain")

    async def run_and_stream():
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            yield line.decode()
        await process.wait()

    return StreamingResponse(run_and_stream(), media_type="text/plain")

@router.websocket("/ws/agent/{agent_id}")
async def websocket_command(websocket: WebSocket, agent_id: int):
    await websocket.accept()
    connected_agents[agent_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("command")
            if not command or not isinstance(command, str):
                await websocket.send_text("Missing or invalid 'command' field (must be a string)\n")
                continue
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                await websocket.send_text(line.decode())
            await process.wait()
            await websocket.send_text("[END]")
    except WebSocketDisconnect:
        pass
    finally:
        connected_agents.pop(agent_id, None)
