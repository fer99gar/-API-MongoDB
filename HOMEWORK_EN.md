# Homework: Pokémon Data Engineering API

**Language:** English — [Ver en Español](HOMEWORK_ES.md)

---

## Overview

You already built a REST API with FastAPI and MongoDB — great work!

Now you will extend it by integrating three things:

1. The public **PokéAPI** (`https://pokeapi.co/`) for data ingestion
2. A **PostgreSQL database on Neon DB** for relational storage and health checks
3. A complete **Postman collection** documenting every endpoint

You will practice core **Data Engineering** concepts: ETL, batch ingestion, data modeling, aggregation pipelines, multi-database architectures, and API documentation.

Use **Cursor** (AI-powered IDE) actively — but make sure you understand every line it generates.

---

## Learning Objectives

| Concept | Where you apply it |
|---|---|
| ETL (Extract, Transform, Load) | Fetch from PokéAPI → clean data → store in MongoDB |
| Data Modeling | Design schemas for MongoDB and PostgreSQL |
| Batch Ingestion | Load many records in a single operation |
| Aggregation Pipelines | Compute statistics across stored documents |
| Multi-database Architecture | MongoDB (NoSQL) + PostgreSQL (SQL) in the same API |
| API Documentation | Build a complete Postman collection |

---

## Context: PokéAPI

Free public API, no authentication required.

| PokéAPI endpoint | Returns |
|---|---|
| `GET https://pokeapi.co/api/v2/pokemon/{name}` | Full data for one Pokémon |
| `GET https://pokeapi.co/api/v2/pokemon?limit=20&offset=0` | Paginated list |
| `GET https://pokeapi.co/api/v2/type/{type}` | All Pokémon of a given type |

Explore the API at [https://pokeapi.co/](https://pokeapi.co/).

---

## Task 1 — Data Modeling (No code yet)

Before writing any code, answer these questions in a file called `data_model.md`:

1. The raw PokéAPI response for a single Pokémon has over 30 fields. Which fields matter for a data engineering use case? List at least **8 fields** you will keep and explain why each is useful.
2. Describe the MongoDB document schema you will use to store a Pokémon. Which field is the natural unique identifier?
3. What happens if you run the "fetch and store" endpoint twice for the same Pokémon? How will you prevent duplicates?
4. Design a PostgreSQL table called `etl_log` that records every ETL operation (fetch + store). What columns will it have?

> **Hint:** Think about `name`, `id`, `base_experience`, `height`, `weight`, `types`, `stats` (hp, attack, defense, speed), and `abilities`.

---

## Task 2 — Single Pokémon ETL Endpoint

**Endpoint:** `POST /pokemon/fetch/{name_or_id}`

**What it must do (ETL):**

1. **Extract** — Call `https://pokeapi.co/api/v2/pokemon/{name_or_id}` using `httpx`.
2. **Transform** — Build a clean document with only the fields you defined in Task 1. Flatten nested structures (e.g., extract numeric values from `stats`).
3. **Load** — Insert the cleaned document into the MongoDB `pokemon` collection. If it already exists, **update** it (`upsert`).
4. **Log** — Write a record to the PostgreSQL `etl_log` table with: `pokemon_name`, `action` (`created` or `updated`), `timestamp`.

**Expected response:**

```json
{
  "status": "created",
  "pokemon": {
    "id": 25,
    "name": "pikachu",
    "height": 4,
    "weight": 60,
    "base_experience": 112,
    "types": ["electric"],
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "speed": 90,
    "abilities": ["static", "lightning-rod"]
  }
}
```

**Requirements:**
- Return `"status": "created"` or `"status": "updated"` accordingly.
- If PokéAPI returns 404, return a clear error to the client and do **not** write to the log.
- Do **not** store the raw PokéAPI response — only your transformed document.

---

## Task 3 — Batch Ingestion Endpoint

**Endpoint:** `POST /pokemon/batch`

**Request body:**

```json
{
  "names": ["bulbasaur", "charmander", "squirtle", "pikachu", "mewtwo"]
}
```

**What it must do:**

1. For each name, call PokéAPI and transform the data (reuse Task 2 logic).
2. Insert or update all records in MongoDB in a **single bulk operation** (`bulk_write`).
3. Write one log row per Pokémon to the PostgreSQL `etl_log` table.
4. Return a summary:

```json
{
  "total_requested": 5,
  "created": 3,
  "updated": 2,
  "errors": []
}
```

**Requirements:**
- If one name is invalid, do not fail the whole batch — record the error and continue.
- Use `asyncio.gather` to fetch from PokéAPI **concurrently** (not one by one).

> **Data Engineering note:** This pattern is called **bulk ingestion**. It is a fundamental skill for building data pipelines.

---

## Task 4 — Query Endpoints

All queries run against your local MongoDB `pokemon` collection — do **not** call PokéAPI here.

#### 4a. List all stored Pokémon
`GET /pokemon`
- Returns `id`, `name`, `types` for every stored Pokémon.
- Supports `?limit=10&offset=0` for pagination.

#### 4b. Get one Pokémon
`GET /pokemon/{name}`
- Returns the full stored document.
- Returns 404 if not found.

#### 4c. Filter by type
`GET /pokemon/by-type/{type}`
- Returns all stored Pokémon with the given type (`fire`, `water`, `electric`, etc.).

#### 4d. Delete a Pokémon
`DELETE /pokemon/{name}`
- Removes from MongoDB and adds a `deleted` entry in the PostgreSQL `etl_log`.
- Returns 404 if not found.

---

## Task 5 — Aggregation Pipeline

**Endpoint:** `GET /pokemon/stats/summary`

Use a **MongoDB aggregation pipeline** to compute these statistics in a single query:

**Expected response:**

```json
{
  "total_pokemon": 10,
  "avg_hp": 62.5,
  "avg_attack": 74.2,
  "avg_defense": 63.8,
  "avg_speed": 71.0,
  "heaviest_pokemon": "snorlax",
  "lightest_pokemon": "gastly",
  "most_common_type": "water",
  "stats_by_type": [
    { "type": "fire",     "count": 2, "avg_attack": 90.0 },
    { "type": "water",    "count": 3, "avg_attack": 72.5 },
    { "type": "electric", "count": 1, "avg_attack": 55.0 }
  ]
}
```

**Requirements:**
- All computation must happen **inside the pipeline** — do not load documents into Python and calculate in memory.
- Sort `stats_by_type` by `count` descending.
- If the collection is empty, return a meaningful message instead of an error.

> **Data Engineering note:** MongoDB aggregation pipelines are the equivalent of SQL `GROUP BY` with aggregate functions — the same concept used in Apache Spark or dbt.

---

## Task 6 — PostgreSQL Integration with Neon DB

This task introduces a **second database** (relational / SQL) alongside MongoDB.

### 6a. Set up Neon DB

1. Go to [https://neon.tech](https://neon.tech) and create a free account.
2. Create a new project and copy the **connection string** (it looks like `postgresql://user:pass@host/dbname?sslmode=require`).
3. Add it to your `.env` file as `POSTGRES_URL`.

### 6b. Create the `etl_log` table

When the app starts, it must create this table if it does not exist:

```sql
CREATE TABLE IF NOT EXISTS etl_log (
    id         SERIAL PRIMARY KEY,
    pokemon_name VARCHAR(100) NOT NULL,
    action     VARCHAR(20)  NOT NULL,  -- 'created', 'updated', 'deleted', 'error'
    detail     TEXT,                   -- error message or extra info
    created_at TIMESTAMP DEFAULT NOW()
);
```

Use `asyncpg` (async) or `psycopg2` (sync) to connect from FastAPI.

### 6c. Update the Health Endpoint

Extend the existing `GET /health` endpoint so it checks **both** databases:

**Expected response:**

```json
{
  "status": "ok",
  "mongodb": {
    "status": "ok",
    "database": "mi_api_db"
  },
  "postgresql": {
    "status": "ok",
    "host": "your-host.neon.tech",
    "database": "neondb"
  }
}
```

If either database is unreachable, set its `"status"` to `"error"` with an `"error"` field explaining the problem. The top-level `"status"` must be `"degraded"` if any database is unhealthy.

**Example degraded response:**

```json
{
  "status": "degraded",
  "mongodb": { "status": "ok", "database": "mi_api_db" },
  "postgresql": { "status": "error", "error": "Connection refused" }
}
```

**Requirements:**
- Use a timeout when checking connections (do not let the health check hang for more than 3 seconds per database).
- The health check must never crash the API — always return a JSON response even if both databases are down.

> **Data Engineering note:** In real data platforms, health checks are used by orchestrators (Airflow, Kubernetes, etc.) to decide whether to route traffic or trigger alerts. Checking multiple datastores in a single endpoint is standard practice.

---

## Task 7 — Postman Collection

Create a complete **Postman collection** that covers every endpoint in the project (items + pokemon + health).

### What the collection must include

Export the collection as `API_MongoDB_Pokemon.postman_collection.json` and commit it to the repository.

| Folder | Requests |
|---|---|
| **Health** | `GET /health` |
| **Items** | `GET /items`, `POST /items`, `GET /items/{id}`, `DELETE /items/{id}` |
| **Pokemon — ETL** | `POST /pokemon/fetch/{name_or_id}` (examples: pikachu, charizard) |
| **Pokemon — Batch** | `POST /pokemon/batch` (body with 5 names) |
| **Pokemon — Query** | `GET /pokemon`, `GET /pokemon/{name}`, `GET /pokemon/by-type/{type}` |
| **Pokemon — Analytics** | `GET /pokemon/stats/summary` |
| **Pokemon — Delete** | `DELETE /pokemon/{name}` |

### Requirements for each request

- Add a **description** explaining what the endpoint does.
- Include at least one **example response** saved in the collection.
- Use a **collection variable** called `base_url` (default: `http://127.0.0.1:8000`) so all requests reference `{{base_url}}/path` instead of hardcoded URLs.
- For `POST` requests, include a valid request body example.

> **Data Engineering note:** Postman collections are the standard way to document and share API contracts with your team. In professional environments they are committed to the repo and sometimes used to generate automated integration tests.

---

## Task 8 — Reflection Questions

Answer in a file called `reflection.md`:

1. What is the difference between **ETL** and **ELT**? Which pattern did you use and why?
2. Why is `bulk_write` more efficient than inserting records one by one in a loop?
3. PokéAPI could be slow or down. Name **two strategies** to make your batch endpoint more resilient.
4. Write the MongoDB command to add an index on the `types` field in the `pokemon` collection. Why does this index help the `by-type` query?
5. You now have two databases: MongoDB and PostgreSQL. Explain in one paragraph why a real data platform might use both simultaneously (what is each good for?).
6. If you needed to schedule the batch ingestion to run every night automatically (loading the first 150 Pokémon), what tool or approach would you use?

---

## Deliverables

| # | File | Description |
|---|---|---|
| 1 | `data_model.md` | Task 1 answers |
| 2 | `app/routers/pokemon.py` | All new Pokémon endpoints |
| 3 | `app/database.py` | Updated — add PostgreSQL connection |
| 4 | `app/main.py` | Updated — register new router, create `etl_log` on startup |
| 5 | `requirements.txt` | Updated — add `httpx`, `asyncpg` (or `psycopg2`) |
| 6 | `reflection.md` | Task 8 answers |
| 7 | `API_MongoDB_Pokemon.postman_collection.json` | Complete Postman collection |
| 8 | `README.md` | Updated — document all new endpoints |

Push everything to your GitHub repository and share the link.

---

## Suggested Project Structure

```text
app/
├── __init__.py
├── main.py            ← updated: new router + etl_log creation
├── database.py        ← updated: add PostgreSQL connection
└── routers/
    ├── __init__.py
    ├── items.py       ← already exists
    └── pokemon.py     ← NEW
data_model.md          ← NEW
reflection.md          ← NEW
API_MongoDB_Pokemon.postman_collection.json  ← NEW
requirements.txt       ← updated
README.md              ← updated
```

---

## Evaluation Rubric

| Criterion | Points |
|---|---|
| Task 1 — Data model documented with justification | 10 |
| Task 2 — ETL endpoint works, upsert + log implemented | 15 |
| Task 3 — Batch endpoint with concurrency and error handling | 15 |
| Task 4 — All 4 query endpoints work correctly | 15 |
| Task 5 — Aggregation pipeline (no in-memory computation) | 15 |
| Task 6 — Neon DB connected, `etl_log` table created, `/health` checks both DBs | 15 |
| Task 7 — Postman collection is complete and uses `base_url` variable | 10 |
| Task 8 — Reflection answers are thoughtful and correct | 5 |
| **Total** | **100** |

---

## Tips for Using Cursor

- Use **Cursor Chat** (`Cmd+L` / `Ctrl+L`) for questions like: *"How do I connect asyncpg to FastAPI?"* or *"Write a MongoDB aggregation pipeline that unwinds an array field and groups by it."*
- Use **inline edit** (`Cmd+K` / `Ctrl+K`) to complete functions you started.
- Always **read and understand** the code Cursor generates — you will be asked about it.
- Do not ask Cursor to write everything at once. Start with the data model, then the connection, then the endpoints.

---

## Useful Resources

- PokéAPI docs: [https://pokeapi.co/docs/v2](https://pokeapi.co/docs/v2)
- Neon DB docs: [https://neon.tech/docs](https://neon.tech/docs)
- FastAPI docs: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- MongoDB aggregation: [https://www.mongodb.com/docs/manual/aggregation/](https://www.mongodb.com/docs/manual/aggregation/)
- httpx: [https://www.python-httpx.org/](https://www.python-httpx.org/)
- asyncpg: [https://magicstack.github.io/asyncpg/](https://magicstack.github.io/asyncpg/)
- Postman collection docs: [https://learning.postman.com/docs/collections/collections-overview/](https://learning.postman.com/docs/collections/collections-overview/)
