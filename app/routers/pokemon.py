"""Router de Pokemon."""
import asyncio

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import UpdateOne

from app.database import get_database, get_postgres_pool

router = APIRouter(prefix="/pokemon", tags=["pokemon"])


class PokemonBatchRequest(BaseModel):
    names: list[str]


def transform_pokemon_data(data: dict) -> dict:
    """Transforma la respuesta cruda de PokéAPI en un documento limpio."""
    stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
    types = [t["type"]["name"] for t in data["types"]]
    abilities = [a["ability"]["name"] for a in data["abilities"]]

    return {
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],
        "weight": data["weight"],
        "base_experience": data["base_experience"],
        "types": types,
        "hp": stats.get("hp"),
        "attack": stats.get("attack"),
        "defense": stats.get("defense"),
        "speed": stats.get("speed"),
        "abilities": abilities,
    }


async def fetch_pokemon_from_api(nombre_o_id: str) -> dict:
    """Busca un Pokémon en PokéAPI y devuelve los datos crudos."""
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre_o_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"Pokémon '{nombre_o_id}' no encontrado en PokéAPI",
        )

    response.raise_for_status()
    return response.json()


@router.post("/fetch/{nombre_o_id}")
async def fetch_pokemon(nombre_o_id: str):
    """Obtiene un Pokémon desde PokéAPI, lo transforma y lo guarda."""
    data = await fetch_pokemon_from_api(nombre_o_id)
    pokemon = transform_pokemon_data(data)

    db = get_database()

    result = await db.pokemon.update_one(
        {"name": pokemon["name"]},
        {"$set": pokemon},
        upsert=True,
    )

    status = "created" if result.upserted_id else "updated"

    pool = get_postgres_pool()
    if pool:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO etl_log (pokemon_name, action, detail)
                VALUES ($1, $2, $3)
                """,
                pokemon["name"],
                status,
                "Fetched from PokeAPI",
            )

    return {
        "status": status,
        "pokemon": pokemon,
    }


@router.post("/batch")
async def batch_fetch_pokemon(request: PokemonBatchRequest):
    """Carga varios Pokémon desde PokéAPI y los guarda en MongoDB en una operación bulk."""

    async def process_name(name: str):
        try:
            raw_data = await fetch_pokemon_from_api(name)
            pokemon = transform_pokemon_data(raw_data)
            return {"success": True, "pokemon": pokemon}
        except HTTPException as e:
            return {"success": False, "name": name, "error": e.detail}
        except Exception as e:
            return {"success": False, "name": name, "error": str(e)}

    results = await asyncio.gather(*(process_name(name) for name in request.names))

    valid_pokemon = [result["pokemon"] for result in results if result["success"]]
    errors = [
        {"name": result["name"], "error": result["error"]}
        for result in results
        if not result["success"]
    ]

    db = get_database()

    existing_names = set()
    if valid_pokemon:
        existing_docs = await db.pokemon.find(
            {"name": {"$in": [pokemon["name"] for pokemon in valid_pokemon]}},
            {"name": 1, "_id": 0},
        ).to_list(length=None)
        existing_names = {doc["name"] for doc in existing_docs}

    operations = [
        UpdateOne(
            {"name": pokemon["name"]},
            {"$set": pokemon},
            upsert=True,
        )
        for pokemon in valid_pokemon
    ]

    if operations:
        await db.pokemon.bulk_write(operations)

    created_count = 0
    updated_count = 0

    for pokemon in valid_pokemon:
        if pokemon["name"] in existing_names:
            updated_count += 1
        else:
            created_count += 1

    pool = get_postgres_pool()
    if pool:
        async with pool.acquire() as conn:
            for pokemon in valid_pokemon:
                action = "updated" if pokemon["name"] in existing_names else "created"
                await conn.execute(
                    """
                    INSERT INTO etl_log (pokemon_name, action, detail)
                    VALUES ($1, $2, $3)
                    """,
                    pokemon["name"],
                    action,
                    "Batch fetch from PokéAPI",
                )

    return {
        "total_requested": len(request.names),
        "created": created_count,
        "updated": updated_count,
        "errors": errors,
    }


@router.get("")
async def list_pokemon(limit: int = 10, offset: int = 0):
    """Lista los Pokémon almacenados con paginación."""
    db = get_database()

    pokemon_list = await db.pokemon.find(
        {},
        {"_id": 0, "id": 1, "name": 1, "types": 1},
    ).skip(offset).limit(limit).to_list(length=limit)

    return pokemon_list


@router.get("/stats/summary")
async def get_pokemon_stats_summary():
    """Genera un resumen estadístico usando un pipeline de agregación de MongoDB."""
    db = get_database()

    pipeline = [
        {
            "$facet": {
                "overall_stats": [
                    {
                        "$group": {
                            "_id": None,
                            "total_pokemon": {"$sum": 1},
                            "avg_hp": {"$avg": "$hp"},
                            "avg_attack": {"$avg": "$attack"},
                            "avg_defense": {"$avg": "$defense"},
                            "avg_speed": {"$avg": "$speed"},
                        }
                    }
                ],
                "heaviest": [
                    {"$sort": {"weight": -1}},
                    {"$limit": 1},
                    {"$project": {"_id": 0, "name": 1}},
                ],
                "lightest": [
                    {"$sort": {"weight": 1}},
                    {"$limit": 1},
                    {"$project": {"_id": 0, "name": 1}},
                ],
                "most_common_type": [
                    {"$unwind": "$types"},
                    {
                        "$group": {
                            "_id": "$types",
                            "count": {"$sum": 1},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {"$limit": 1},
                ],
                "stats_by_type": [
                    {"$unwind": "$types"},
                    {
                        "$group": {
                            "_id": "$types",
                            "count": {"$sum": 1},
                            "avg_attack": {"$avg": "$attack"},
                        }
                    },
                    {"$sort": {"count": -1}},
                    {
                        "$project": {
                            "_id": 0,
                            "type": "$_id",
                            "count": 1,
                            "avg_attack": {"$round": ["$avg_attack", 2]},
                        }
                    },
                ],
            }
        }
    ]

    result = await db.pokemon.aggregate(pipeline).to_list(length=1)

    if not result:
        return {"message": "No hay datos disponibles"}

    summary = result[0]

    if not summary["overall_stats"]:
        return {"message": "No hay Pokémon almacenados en la colección"}

    overall = summary["overall_stats"][0]

    return {
        "total_pokemon": overall["total_pokemon"],
        "avg_hp": round(overall["avg_hp"], 2) if overall["avg_hp"] is not None else 0,
        "avg_attack": round(overall["avg_attack"], 2) if overall["avg_attack"] is not None else 0,
        "avg_defense": round(overall["avg_defense"], 2) if overall["avg_defense"] is not None else 0,
        "avg_speed": round(overall["avg_speed"], 2) if overall["avg_speed"] is not None else 0,
        "heaviest_pokemon": summary["heaviest"][0]["name"] if summary["heaviest"] else None,
        "lightest_pokemon": summary["lightest"][0]["name"] if summary["lightest"] else None,
        "most_common_type": summary["most_common_type"][0]["_id"] if summary["most_common_type"] else None,
        "stats_by_type": summary["stats_by_type"],
    }


@router.get("/by-type/{type_name}")
async def get_pokemon_by_type(type_name: str):
    """Obtiene Pokémon almacenados por tipo."""
    db = get_database()

    pokemon_list = await db.pokemon.find(
        {"types": type_name},
        {"_id": 0},
    ).to_list(length=None)

    return pokemon_list


@router.get("/{name}")
async def get_pokemon(name: str):
    """Obtiene un Pokémon almacenado por nombre."""
    db = get_database()

    pokemon = await db.pokemon.find_one(
        {"name": name},
        {"_id": 0},
    )

    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")

    return pokemon


@router.delete("/{name}")
async def delete_pokemon(name: str):
    """Elimina un Pokémon almacenado y registra la acción en PostgreSQL."""
    db = get_database()

    result = await db.pokemon.delete_one({"name": name})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")

    pool = get_postgres_pool()
    if pool:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO etl_log (pokemon_name, action, detail)
                VALUES ($1, $2, $3)
                """,
                name,
                "deleted",
                "Deleted from MongoDB",
            )

    return {"message": f"Pokémon '{name}' eliminado correctamente"}