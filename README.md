# API MongoDB

API REST con **FastAPI** conectada a **MongoDB**. Incluye health check, documentación Swagger y un recurso de ejemplo `items` con CRUD.

## Requisitos

- Python 3.11 o superior
- MongoDB (local o MongoDB Atlas)

## Configuración

### 1. Clonar o entrar al proyecto

```powershell
cd "c:\Users\ferna\Downloads\Experimento cursor 1"
```

### 2. Crear el entorno virtual (venv)

```powershell
python -m venv venv
```

### 3. Activar el entorno virtual en PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

Si aparece un error de política de ejecución, ejecuta una sola vez:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Luego vuelve a activar:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5. Variables de entorno

El proyecto incluye un archivo `.env`. Si no existe, cópialo desde el ejemplo:

```powershell
Copy-Item .env.example .env
```

Edita `.env` y configura al menos:

- `MONGODB_URL`: URI de MongoDB (por defecto `mongodb://localhost:27017`)
- `DATABASE_NAME`: nombre de la base de datos (por defecto `mi_api_db`)

### 6. Ejecutar la API

```powershell
uvicorn app.main:app --reload
```

La API quedará disponible en:

- **API:** http://127.0.0.1:8000
- **Documentación Swagger:** http://127.0.0.1:8000/docs
- **Health:** http://127.0.0.1:8000/health

## Comandos PowerShell útiles

| Acción              | Comando |
|---------------------|--------|
| Entrar al proyecto  | `cd "c:\Users\ferna\Downloads\Experimento cursor 1"` |
| Crear venv          | `python -m venv venv` |
| Permitir scripts PS (una vez) | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Activar venv        | `.\venv\Scripts\Activate.ps1` |
| Desactivar venv     | `deactivate` |
| Instalar deps       | `pip install -r requirements.txt` |
| Ejecutar API        | `uvicorn app.main:app --reload` |

## Guía rápida: todos los comandos en orden (PowerShell)

```powershell
cd "c:\Users\ferna\Downloads\Experimento cursor 1"

python -m venv venv

# Solo la primera vez, para permitir ejecutar Activate.ps1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env

uvicorn app.main:app --reload
```

## Endpoints

- `GET /` — Mensaje de bienvenida y enlace a docs
- `GET /health` — Estado de la API y conexión a MongoDB
- `GET /items` — Listar items
- `POST /items` — Crear item (body: `name`, `description`, `price`)
- `GET /items/{id}` — Obtener item por ID
- `DELETE /items/{id}` — Eliminar item

## Estructura del proyecto

```
Experimento cursor 1/
├── app/
│   ├── __init__.py
│   ├── main.py          # App FastAPI y lifespan
│   ├── database.py      # Conexión MongoDB
│   └── routers/
│       ├── __init__.py
│       └── items.py     # CRUD items
├── .env                 # Variables de entorno (no subir a git)
├── .env.example         # Ejemplo de .env
├── requirements.txt
└── README.md
```

## Licencia

Uso libre para aprendizaje y desarrollo.
