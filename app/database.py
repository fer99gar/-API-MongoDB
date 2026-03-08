"""Conexión a MongoDB y PostgreSQL."""
import os

import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mi_api_db")
POSTGRES_URL = os.getenv("POSTGRES_URL", "")

client: AsyncIOMotorClient | None = None
db = None
postgres_pool = None


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
    """Obtiene la instancia de la base de datos MongoDB."""
    return db


async def connect_to_postgres() -> None:
    """Conecta a PostgreSQL."""
    global postgres_pool

    if not POSTGRES_URL:
        raise ValueError("POSTGRES_URL no está configurado en el archivo .env")

    postgres_pool = await asyncpg.create_pool(POSTGRES_URL)


async def close_postgres_connection() -> None:
    """Cierra la conexión a PostgreSQL."""
    global postgres_pool
    if postgres_pool:
        await postgres_pool.close()
        postgres_pool = None


def get_postgres_pool():
    """Obtiene el pool de conexiones de PostgreSQL."""
    return postgres_pool


async def create_etl_log_table() -> None:
    """Crea la tabla etl_log si no existe."""
    global postgres_pool

    if not postgres_pool:
        raise ValueError("PostgreSQL no está conectado")

    query = """
    CREATE TABLE IF NOT EXISTS etl_log (
        id SERIAL PRIMARY KEY,
        pokemon_name VARCHAR(100) NOT NULL,
        action VARCHAR(20) NOT NULL,
        detail TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """

    async with postgres_pool.acquire() as connection:
        await connection.execute(query)
