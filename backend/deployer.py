import json
import uuid
import fastapi
from pydantic import BaseModel
from agents.deployer import deploy
from langchain_core.callbacks import AsyncCallbackHandler
from google.api_core.exceptions import ResourceExhausted

router = fastapi.APIRouter()

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

    try:
        deploy(data["github_repo"], data["hostname"], data["username"], data["key"], data["env_file"], data["base_path"], MyCustomHandler(websocket))
    except ResourceExhausted as e:
        await websocket.send_text("ERROR: ResourceExhausted")
    except Exception as e:
        await websocket.send_text("ERROR: UnknownError")


