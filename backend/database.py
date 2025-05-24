from os import environ
from dotenv import load_dotenv
import databases

load_dotenv()

SQLALCHEMY_DATABASE_URL = environ.get("DATABASE_URL")

__database = databases.Database(SQLALCHEMY_DATABASE_URL)

def get_db():
    return __database