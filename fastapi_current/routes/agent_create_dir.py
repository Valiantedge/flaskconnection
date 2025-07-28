from fastapi import APIRouter, Body
import os

router = APIRouter()

class CreateDirRequest(BaseException):
    path: str

@router.post("/api/agent/create-directory")
async def create_directory(payload: dict = Body(...)):
    path = payload.get("path")
    if not path or not isinstance(path, str):
        return {"status": "error", "detail": "Missing or invalid 'path'"}
    try:
        os.makedirs(path, exist_ok=True)
        return {"status": "success", "created": path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
