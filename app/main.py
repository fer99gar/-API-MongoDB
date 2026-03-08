"""API principal con FastAPI."""
from dotenv import load_dotenv

load_dotenv()

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import (
    close_mongo_connection,
    close_postgres_connection,
    connect_to_mongo,
    connect_to_postgres,
    create_etl_log_table,
    get_database,
    get_postgres_pool,
)
from app.routers import items, pokemon


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona conexiones al iniciar y cerrar la app."""
    await connect_to_mongo()
    await connect_to_postgres()
    await create_etl_log_table()
    yield
    await close_mongo_connection()
    await close_postgres_connection()


app = FastAPI(
    title="API MongoDB Pokemon",
    description="API REST con MongoDB, PostgreSQL y PokéAPI",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(items.router)
app.include_router(pokemon.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Mensaje de bienvenida."""
    return {"message": "API MongoDB Pokemon funcionando", "docs": "/docs"}


@app.get("/health")
async def health():
    """Verifica el estado de MongoDB y PostgreSQL sin romper la API."""
    response = {
        "status": "ok",
        "mongodb": {},
        "postgresql": {},
    }

    # Revisar MongoDB
    try:
        db = get_database()
        if db is None:
            raise Exception("Base de datos no inicializada")

        await asyncio.wait_for(db.client.admin.command("ping"), timeout=3)

        response["mongodb"] = {
            "status": "ok",
            "database": db.name,
        }
    except Exception as e:
        response["status"] = "degraded"
        response["mongodb"] = {
            "status": "error",
            "error": str(e),
        }

    # Revisar PostgreSQL
    try:
        pool = get_postgres_pool()
        if pool is None:
            raise Exception("Pool de PostgreSQL no inicializado")

        async def check_postgres():
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")

        await asyncio.wait_for(check_postgres(), timeout=3)

        response["postgresql"] = {
            "status": "ok",
            "database": "empresa_db",
        }
    except Exception as e:
        response["status"] = "degraded"
        response["postgresql"] = {
            "status": "error",
            "error": str(e),
        }

    return response