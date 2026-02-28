"""Endpoints de ejemplo para una colección 'items' en MongoDB."""
from datetime import datetime
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import get_database

router = APIRouter(prefix="/items", tags=["items"])


def _doc_to_json(doc: dict[str, Any]) -> dict[str, Any]:
    """Convierte un documento MongoDB a un dict JSON-serializable."""
    out: dict[str, Any] = {}
    for k, v in doc.items():
        if k == "_id":
            out["id"] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, ObjectId):
            out[k] = str(v)
        else:
            out[k] = v
    return out


class ItemCreate(BaseModel):
    """Modelo para crear un item."""
    name: str
    description: str | None = None
    price: float | None = None


class ItemResponse(BaseModel):
    """Modelo de respuesta de un item."""
    id: str
    name: str
    description: str | None
    price: float | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[dict[str, Any]])
async def list_items():
    """Lista todos los items de la colección."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    try:
        cursor = db.items.find()
        items = []
        async for doc in cursor:
            items.append(_doc_to_json(doc))
        return items
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al conectar con MongoDB: {e!s}") from e


@router.post("", response_model=dict[str, Any])
async def create_item(item: ItemCreate):
    """Crea un nuevo item."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    doc = item.model_dump()
    result = await db.items.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    return doc


@router.get("/{item_id}", response_model=dict[str, Any])
async def get_item(item_id: str):
    """Obtiene un item por ID."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    try:
        doc = await db.items.find_one({"_id": ObjectId(item_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    if not doc:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return _doc_to_json(doc)


@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """Elimina un item por ID."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    try:
        result = await db.items.delete_one({"_id": ObjectId(item_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"message": "Item eliminado"}
