"""Conexión a PostgreSQL."""
import os

import asyncpg

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://localhost:5432/postgres",
)

pool: asyncpg.Pool | None = None


async def connect_to_postgres() -> None:
    """Crea el pool de conexiones a PostgreSQL."""
    global pool
    pool = await asyncpg.create_pool(
        POSTGRES_URL,
        min_size=1,
        max_size=5,
        command_timeout=10,
    )


async def close_postgres_connection() -> None:
    """Cierra el pool de PostgreSQL."""
    global pool
    if pool is not None:
        await pool.close()
        pool = None


def get_pool() -> asyncpg.Pool | None:
    """Obtiene el pool de PostgreSQL."""
    return pool
