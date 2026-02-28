"""Conexión a MongoDB."""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mi_api_db")

client: AsyncIOMotorClient | None = None
db = None


async def connect_to_mongo() -> None:
    """Conecta a MongoDB."""
    global client, db
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    try:
        await client.admin.command("ping")
    except ConnectionFailure as e:
        raise ConnectionFailure(f"No se pudo conectar a MongoDB: {e}") from e


async def close_mongo_connection() -> None:
    """Cierra la conexión a MongoDB."""
    global client
    if client:
        client.close()
        client = None


def get_database():
    """Obtiene la instancia de la base de datos."""
    return db
