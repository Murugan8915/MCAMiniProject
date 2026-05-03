import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.recruitment_db
fs = AsyncIOMotorGridFSBucket(db)

def get_database():
    return db

def get_gridfs():
    return fs
