from fastapi import APIRouter, BackgroundTasks, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import subprocess

bearer_scheme = HTTPBearer()
router = APIRouter(dependencies=[Security(bearer_scheme)])

class LongCommandRequest(BaseModel):
    command: str

@router.post("/run", tags=["8. Ansible"])
def run_long_command(req: LongCommandRequest, background_tasks: BackgroundTasks):
    def run_cmd():
        subprocess.run(req.command, shell=True)
    background_tasks.add_task(run_cmd)
    return {"status": "started"}
