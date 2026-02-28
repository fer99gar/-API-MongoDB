"""API principal con FastAPI."""
from dotenv import load_dotenv

load_dotenv()

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida: conexión al arranque y cierre al terminar."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="API MongoDB",
    description="API REST conectada a MongoDB",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(items.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check y bienvenida."""
    return {"message": "API MongoDB funcionando", "docs": "/docs"}


@app.get("/health")
async def health():
    """Verifica que la API y MongoDB estén disponibles."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no conectada")
    try:
        await db.client.admin.command("ping")
        return {"status": "ok", "mongodb": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MongoDB error: {str(e)}") from e
