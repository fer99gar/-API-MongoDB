# Tarea: API de Ingeniería de Datos con Pokémon

**Idioma:** Español — [Read in English](HOMEWORK_EN.md)

---

## Descripción general

Ya construiste una API REST con FastAPI y MongoDB — ¡excelente trabajo!

Ahora la extenderás integrando tres cosas:

1. La **PokéAPI** pública (`https://pokeapi.co/`) para ingestión de datos
2. Una **base de datos PostgreSQL en Neon DB** para almacenamiento relacional y health checks
3. Una **colección completa de Postman** que documente todos los endpoints

Practicarás conceptos fundamentales de **Ingeniería de Datos**: ETL, ingestión por lotes, modelado de datos, pipelines de agregación, arquitecturas multi-base de datos y documentación de APIs.

Usa **Cursor** (IDE con IA) activamente — pero asegúrate de entender cada línea que genera.

---

## Objetivos de aprendizaje

| Concepto | Dónde lo aplicas |
|---|---|
| ETL (Extract, Transform, Load) | Consumir PokéAPI → limpiar datos → guardar en MongoDB |
| Modelado de datos | Diseñar esquemas para MongoDB y PostgreSQL |
| Ingestión por lotes | Cargar muchos registros en una sola operación |
| Pipelines de agregación | Calcular estadísticas sobre documentos almacenados |
| Arquitectura multi-base de datos | MongoDB (NoSQL) + PostgreSQL (SQL) en la misma API |
| Documentación de APIs | Construir una colección completa de Postman |

---

## Contexto: PokéAPI

API pública gratuita, no requiere autenticación.

| Endpoint de PokéAPI | Retorna |
|---|---|
| `GET https://pokeapi.co/api/v2/pokemon/{nombre}` | Todos los datos de un Pokémon |
| `GET https://pokeapi.co/api/v2/pokemon?limit=20&offset=0` | Lista paginada |
| `GET https://pokeapi.co/api/v2/type/{tipo}` | Todos los Pokémon de un tipo |

Explora la API en [https://pokeapi.co/](https://pokeapi.co/).

---

## Tarea 1 — Modelado de datos (Sin código aún)

Antes de escribir cualquier código, responde estas preguntas en un archivo llamado `data_model.md`:

1. La respuesta cruda de PokéAPI para un Pokémon tiene más de 30 campos. ¿Cuáles importan para un caso de uso de ingeniería de datos? Lista al menos **8 campos** que conservarás y explica por qué cada uno es útil.
2. Describe el esquema del documento MongoDB que usarás para almacenar un Pokémon. ¿Cuál campo es el identificador único natural?
3. ¿Qué pasa si ejecutas el endpoint de "fetch y almacenamiento" dos veces para el mismo Pokémon? ¿Cómo evitarás duplicados?
4. Diseña una tabla PostgreSQL llamada `etl_log` que registre cada operación ETL (fetch + almacenamiento). ¿Qué columnas tendrá?

> **Pista:** Considera `name`, `id`, `base_experience`, `height`, `weight`, `types`, `stats` (hp, attack, defense, speed) y `abilities`.

---

## Tarea 2 — Endpoint ETL para un solo Pokémon

**Endpoint:** `POST /pokemon/fetch/{nombre_o_id}`

**Qué debe hacer (ETL):**

1. **Extract** — Llama a `https://pokeapi.co/api/v2/pokemon/{nombre_o_id}` usando `httpx`.
2. **Transform** — Construye un documento limpio con solo los campos que definiste en la Tarea 1. Aplana estructuras anidadas (por ejemplo, extrae los valores numéricos de `stats`).
3. **Load** — Inserta el documento limpio en la colección `pokemon` de MongoDB. Si ya existe, **actualízalo** (`upsert`).
4. **Log** — Escribe un registro en la tabla `etl_log` de PostgreSQL con: `pokemon_name`, `action` (`created` o `updated`), `timestamp`.

**Respuesta esperada:**

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

**Requisitos:**
- Retorna `"status": "created"` o `"status": "updated"` según corresponda.
- Si PokéAPI retorna 404, devuelve un error claro al cliente y **no** escribas en el log.
- **No** almacenes la respuesta cruda de PokéAPI — solo tu documento transformado.

---

## Tarea 3 — Endpoint de Ingestión por Lotes

**Endpoint:** `POST /pokemon/batch`

**Cuerpo de la solicitud:**

```json
{
  "names": ["bulbasaur", "charmander", "squirtle", "pikachu", "mewtwo"]
}
```

**Qué debe hacer:**

1. Para cada nombre, llama a PokéAPI y transforma los datos (reutiliza la lógica de la Tarea 2).
2. Inserta o actualiza todos los registros en MongoDB en una **única operación bulk** (`bulk_write`).
3. Escribe un registro de log por Pokémon en la tabla `etl_log` de PostgreSQL.
4. Retorna un resumen:

```json
{
  "total_requested": 5,
  "created": 3,
  "updated": 2,
  "errors": []
}
```

**Requisitos:**
- Si un nombre es inválido, no falles todo el batch — registra el error y continúa.
- Usa `asyncio.gather` para llamar a PokéAPI de forma **concurrente** (no uno por uno en bucle).

> **Nota de Ingeniería de Datos:** Este patrón se llama **ingestión masiva**. Es una habilidad fundamental para construir pipelines de datos.

---

## Tarea 4 — Endpoints de Consulta

Todas las consultas deben ejecutarse contra tu colección `pokemon` de MongoDB — **no** llames a PokéAPI aquí.

#### 4a. Listar todos los Pokémon almacenados
`GET /pokemon`
- Retorna `id`, `name`, `types` de todos los Pokémon almacenados.
- Soporta `?limit=10&offset=0` para paginación.

#### 4b. Obtener un Pokémon
`GET /pokemon/{name}`
- Retorna el documento completo almacenado.
- Retorna 404 si no se encuentra.

#### 4c. Filtrar por tipo
`GET /pokemon/by-type/{type}`
- Retorna todos los Pokémon almacenados con el tipo dado (`fire`, `water`, `electric`, etc.).

#### 4d. Eliminar un Pokémon
`DELETE /pokemon/{name}`
- Elimina de MongoDB y agrega una entrada `deleted` en el `etl_log` de PostgreSQL.
- Retorna 404 si no se encuentra.

---

## Tarea 5 — Pipeline de Agregación

**Endpoint:** `GET /pokemon/stats/summary`

Usa un **pipeline de agregación de MongoDB** para calcular estas estadísticas en una sola consulta:

**Respuesta esperada:**

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

**Requisitos:**
- Todo el cálculo debe ocurrir **dentro del pipeline** — no cargues documentos en Python para calcular en memoria.
- Ordena `stats_by_type` por `count` descendente.
- Si la colección está vacía, retorna un mensaje significativo en lugar de un error.

> **Nota de Ingeniería de Datos:** Los pipelines de agregación de MongoDB son el equivalente de SQL `GROUP BY` con funciones de agregado — el mismo concepto que usan Apache Spark o dbt.

---

## Tarea 6 — Integración PostgreSQL con Neon DB

Esta tarea introduce una **segunda base de datos** (relacional / SQL) junto a MongoDB.

### 6a. Configurar Neon DB

1. Ve a [https://neon.tech](https://neon.tech) y crea una cuenta gratuita.
2. Crea un nuevo proyecto y copia el **connection string** (se ve así: `postgresql://user:pass@host/dbname?sslmode=require`).
3. Agrégalo a tu archivo `.env` como `POSTGRES_URL`.

### 6b. Crear la tabla `etl_log`

Al iniciar la app, debe crear esta tabla si no existe:

```sql
CREATE TABLE IF NOT EXISTS etl_log (
    id           SERIAL PRIMARY KEY,
    pokemon_name VARCHAR(100) NOT NULL,
    action       VARCHAR(20)  NOT NULL,  -- 'created', 'updated', 'deleted', 'error'
    detail       TEXT,                   -- mensaje de error u info adicional
    created_at   TIMESTAMP DEFAULT NOW()
);
```

Usa `asyncpg` (async) o `psycopg2` (sync) para conectar desde FastAPI.

### 6c. Actualizar el Endpoint de Health

Extiende el `GET /health` existente para que verifique **ambas** bases de datos:

**Respuesta esperada:**

```json
{
  "status": "ok",
  "mongodb": {
    "status": "ok",
    "database": "mi_api_db"
  },
  "postgresql": {
    "status": "ok",
    "host": "tu-host.neon.tech",
    "database": "neondb"
  }
}
```

Si alguna base de datos no es alcanzable, establece su `"status"` en `"error"` con un campo `"error"` que explique el problema. El `"status"` del nivel superior debe ser `"degraded"` si alguna base de datos está caída.

**Ejemplo de respuesta degradada:**

```json
{
  "status": "degraded",
  "mongodb": { "status": "ok", "database": "mi_api_db" },
  "postgresql": { "status": "error", "error": "Connection refused" }
}
```

**Requisitos:**
- Usa un timeout al verificar las conexiones (no dejes que el health check espere más de 3 segundos por base de datos).
- El health check nunca debe crashear la API — siempre retorna una respuesta JSON, aunque ambas bases de datos estén caídas.

> **Nota de Ingeniería de Datos:** En plataformas de datos reales, los health checks son usados por orquestadores (Airflow, Kubernetes, etc.) para decidir si enrutar tráfico o disparar alertas. Verificar múltiples datastores en un solo endpoint es práctica estándar.

---

## Tarea 7 — Colección de Postman

Crea una **colección completa de Postman** que cubra todos los endpoints del proyecto (items + pokemon + health).

### Qué debe incluir la colección

Exporta la colección como `API_MongoDB_Pokemon.postman_collection.json` y súbela al repositorio.

| Carpeta | Requests |
|---|---|
| **Health** | `GET /health` |
| **Items** | `GET /items`, `POST /items`, `GET /items/{id}`, `DELETE /items/{id}` |
| **Pokemon — ETL** | `POST /pokemon/fetch/{nombre_o_id}` (ejemplos: pikachu, charizard) |
| **Pokemon — Batch** | `POST /pokemon/batch` (body con 5 nombres) |
| **Pokemon — Consultas** | `GET /pokemon`, `GET /pokemon/{name}`, `GET /pokemon/by-type/{type}` |
| **Pokemon — Analítica** | `GET /pokemon/stats/summary` |
| **Pokemon — Eliminar** | `DELETE /pokemon/{name}` |

### Requisitos para cada request

- Agrega una **descripción** explicando qué hace el endpoint.
- Incluye al menos una **respuesta de ejemplo** guardada en la colección.
- Usa una **variable de colección** llamada `base_url` (por defecto: `http://127.0.0.1:8000`) para que todos los requests usen `{{base_url}}/ruta` en lugar de URLs con el host hardcodeado.
- Para los requests `POST`, incluye un ejemplo de body válido.

> **Nota de Ingeniería de Datos:** Las colecciones de Postman son la forma estándar de documentar y compartir contratos de APIs con tu equipo. En entornos profesionales se suben al repositorio y a veces se usan para generar pruebas de integración automatizadas.

---

## Tarea 8 — Preguntas de Reflexión

Responde en un archivo llamado `reflection.md`:

1. ¿Cuál es la diferencia entre **ETL** y **ELT**? ¿Cuál patrón usaste y por qué?
2. ¿Por qué `bulk_write` es más eficiente que insertar registros uno por uno en un bucle?
3. PokéAPI podría estar lenta o caída. Nombra **dos estrategias** para hacer tu endpoint de batch más resiliente.
4. Escribe el comando de MongoDB para agregar un índice en el campo `types` de la colección `pokemon`. ¿Por qué ese índice ayuda a la consulta `by-type`?
5. Ahora tienes dos bases de datos: MongoDB y PostgreSQL. Explica en un párrafo por qué una plataforma de datos real podría usar ambas simultáneamente (¿para qué es buena cada una?).
6. Si necesitaras programar la ingestión por lotes para que se ejecute automáticamente cada noche (cargando los primeros 150 Pokémon), ¿qué herramienta o enfoque usarías?

---

## Entregables

| # | Archivo | Descripción |
|---|---|---|
| 1 | `data_model.md` | Respuestas de la Tarea 1 |
| 2 | `app/routers/pokemon.py` | Todos los endpoints nuevos de Pokémon |
| 3 | `app/database.py` | Actualizado — agregar conexión a PostgreSQL |
| 4 | `app/main.py` | Actualizado — registrar nuevo router, crear `etl_log` al iniciar |
| 5 | `requirements.txt` | Actualizado — agregar `httpx`, `asyncpg` (o `psycopg2`) |
| 6 | `reflection.md` | Respuestas de la Tarea 8 |
| 7 | `API_MongoDB_Pokemon.postman_collection.json` | Colección completa de Postman |
| 8 | `README.md` | Actualizado — documentar todos los endpoints nuevos |

Sube todo a tu repositorio de GitHub y comparte el enlace.

---

## Estructura sugerida del proyecto

```text
app/
├── __init__.py
├── main.py            ← actualizado: nuevo router + creación de etl_log
├── database.py        ← actualizado: agregar conexión PostgreSQL
└── routers/
    ├── __init__.py
    ├── items.py       ← ya existe
    └── pokemon.py     ← NUEVO
data_model.md          ← NUEVO
reflection.md          ← NUEVO
API_MongoDB_Pokemon.postman_collection.json  ← NUEVO
requirements.txt       ← actualizado
README.md              ← actualizado
```

---

## Rúbrica de evaluación

| Criterio | Puntos |
|---|---|
| Tarea 1 — Modelo de datos documentado con justificación | 10 |
| Tarea 2 — Endpoint ETL funciona, upsert + log implementados | 15 |
| Tarea 3 — Batch endpoint con concurrencia y manejo de errores | 15 |
| Tarea 4 — Los 4 endpoints de consulta funcionan correctamente | 15 |
| Tarea 5 — Pipeline de agregación (sin cálculo en memoria) | 15 |
| Tarea 6 — Neon DB conectado, tabla `etl_log` creada, `/health` verifica ambas DBs | 15 |
| Tarea 7 — Colección Postman completa con variable `base_url` | 10 |
| Tarea 8 — Respuestas de reflexión son reflexivas y correctas | 5 |
| **Total** | **100** |

---

## Consejos para usar Cursor

- Usa **Cursor Chat** (`Cmd+L` / `Ctrl+L`) para preguntas como: *"¿Cómo conecto asyncpg a FastAPI?"* o *"Escribe un pipeline de agregación de MongoDB que haga unwind de un campo array y lo agrupe."*
- Usa **edición inline** (`Cmd+K` / `Ctrl+K`) para completar funciones que empezaste.
- Siempre **lee y entiende** el código que genera Cursor — te preguntarán sobre él.
- No le pidas a Cursor que escriba todo de una vez. Empieza con el modelo de datos, luego la conexión, luego los endpoints.

---

## Recursos útiles

- Documentación PokéAPI: [https://pokeapi.co/docs/v2](https://pokeapi.co/docs/v2)
- Documentación Neon DB: [https://neon.tech/docs](https://neon.tech/docs)
- Documentación FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- Agregación MongoDB: [https://www.mongodb.com/docs/manual/aggregation/](https://www.mongodb.com/docs/manual/aggregation/)
- httpx: [https://www.python-httpx.org/](https://www.python-httpx.org/)
- asyncpg: [https://magicstack.github.io/asyncpg/](https://magicstack.github.io/asyncpg/)
- Documentación colecciones Postman: [https://learning.postman.com/docs/collections/collections-overview/](https://learning.postman.com/docs/collections/collections-overview/)
