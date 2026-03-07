import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from models import (
    Student,
    Teacher,
    SuperAdmin,
    Post,
    LifeItem,
    ShowcaseItem,
    Activity,
    Project,
    Software,
    InviteCode,
    RegistrationGradePolicy,
    ForumPost,
    ForumComment,
)

_client = None
_database = None

def get_mongo_uri():
    return os.getenv("LAB_MONGO_URI", "mongodb://localhost:27017")

def get_mongo_db_name():
    return os.getenv("LAB_MONGO_DB", "lab_ecosystem")

async def init_db():
    global _client, _database
    _client = AsyncIOMotorClient(get_mongo_uri())
    _database = _client[get_mongo_db_name()]
    
    # Register models here
    await init_beanie(
        database=_database,
        document_models=[
            Student,
            Teacher,
            SuperAdmin,
            Post,
            LifeItem,
            ShowcaseItem,
            Activity,
            Project,
            Software,
            InviteCode,
            RegistrationGradePolicy,
            ForumPost,
            ForumComment,
        ],
    )

async def ping_db():
    if _database is None:
        return False
    try:
        await _database.command("ping")
        return True
    except Exception:
        return False
