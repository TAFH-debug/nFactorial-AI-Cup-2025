from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from models import *
from database import get_db
import dotenv
dotenv.load_dotenv(dotenv_path=".env")

from deployer import router as deployer_router
from dockerizer import router as dockerizer_router


async def lifespan(_):
    database = get_db()
    await database.connect()
    yield
    await database.disconnect()
    
app = FastAPI(lifespan=lifespan)
app.include_router(deployer_router)
app.include_router(dockerizer_router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)