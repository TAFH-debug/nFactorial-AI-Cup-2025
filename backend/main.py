from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from models import *
from database import get_db

async def lifespan(_):
    database = get_db()
    await database.connect()
    yield
    await database.disconnect()
    
app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users/")
async def get_all_users():
    query = select(
        User
    )
    return await get_db().fetch_all(query)
    