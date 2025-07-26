from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import subprocess

router = APIRouter()

class LongCommandRequest(BaseModel):
    command: str

@router.post("/run")
def run_long_command(req: LongCommandRequest, background_tasks: BackgroundTasks):
    def run_cmd():
        subprocess.run(req.command, shell=True)
    background_tasks.add_task(run_cmd)
    return {"status": "started"}
