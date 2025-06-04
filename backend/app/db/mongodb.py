import motor.motor_asyncio
import os
from pymongo.errors import ServerSelectionTimeoutError

client = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
        await client.server_info()  # Verify connection works
        db = client.dnd_character_creator
        print("Connected to MongoDB")
    except ServerSelectionTimeoutError:
        print("Failed to connect to MongoDB")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")

def get_database():
    """Get the database instance"""
    global db
    return db