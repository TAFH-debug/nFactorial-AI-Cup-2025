import json
import uuid
import fastapi
from pydantic import BaseModel
from agents.deployer import deploy
from langchain_core.callbacks import AsyncCallbackHandler

router = fastapi.APIRouter()

class DeployPayload(BaseModel):
    github_repo: str
    hostname: str
    username: str
    key: str
    env_file: str

class MyCustomHandler(AsyncCallbackHandler):
    def __init__(self, websocket: fastapi.WebSocket):
        self.websocket = websocket

    async def on_tool_start(
        self, serialized, input_str, **kwargs
    ):
        """Run when tool starts running."""
        await self.websocket.send_text(input_str)

    async def on_tool_end(
        self, output, **kwargs
    ):
        await self.websocket.send_text(output['stdout'])
        await self.websocket.send_text(output['stderr'])

@router.websocket("/deploy")
async def deploy_endpoint(websocket: fastapi.WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()
    deployment_id = str(uuid.uuid4())

    def tracer(message: str):
        websocket.send_text(message)

    deploy(data["github_repo"], data["hostname"], data["username"], data["key"], data["env_file"], MyCustomHandler(websocket))



