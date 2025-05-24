import uuid
import fastapi
from pydantic import BaseModel
from agents.deployer import deploy

router = fastapi.APIRouter()

class DeployPayload(BaseModel):
    github_repo: str
    hostname: str
    username: str
    key: str
    env_file: str

@router.post("/deploy")
async def deploy_endpoint(payload: DeployPayload):
    deployment_id = str(uuid.uuid4())
    
    deploy(payload.github_repo, payload.hostname, payload.username, payload.key, payload.env_file)
    
    return {
        "message": "Deployment started",
        "deployment_id": deployment_id
    }

