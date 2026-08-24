from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client = None
db = None

async def init_db():
    global client
    global db
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]
    # Create indexes if they don't exist
    await db.business_cache.create_index("url_hash", unique=True)
    await db.business_cache.create_index("status")

async def get_db():
    yield db

async def close_db():
    if client:
        client.close()
