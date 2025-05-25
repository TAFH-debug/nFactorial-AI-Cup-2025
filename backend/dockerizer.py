import fastapi

from agents.dockerizer import get_dockerfile_code

router = fastapi.APIRouter()

@router.post("/dockerize")
async def dockerize(github_repo: str):
    return {"dockerfile": await get_dockerfile_code(github_repo)}

