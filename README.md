# API MongoDB

Multi-language README: **English** and **Español**.

- [English](#english)
- [Español](#espa%C3%B1ol)

## English

### Overview

REST API built with **FastAPI** connected to **MongoDB**.  
It includes a health check, Swagger documentation, and an example `items` resource with basic CRUD.

### Requirements

- Python 3.11 or higher (Python 3.14 is supported)
- MongoDB (local or MongoDB Atlas)

### Setup (PowerShell)

#### 1. Go to the project folder

```powershell
cd "c:\Users\ferna\Downloads\Experimento cursor 1"
```

#### 2. Create the virtual environment (venv)

```powershell
python -m venv venv
```

#### 3. Allow PowerShell scripts (only once)

If you get an error about execution policy when running `Activate.ps1`, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You only need to do this once for your user.

#### 4. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

#### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

#### 6. Environment variables

The project includes a `.env.example` file. Copy it to `.env`:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set at least:

- `MONGODB_URL`: MongoDB URI (for Atlas it looks like `mongodb+srv://user:pass@cluster/...`)
- `DATABASE_NAME`: database name (for example `mi_api_db`)

> **Note:** The real `.env` file is ignored by git (see `.gitignore`), so secrets will not be committed.

#### 7. Run the API

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

- **API:** http://127.0.0.1:8000
- **Swagger docs:** http://127.0.0.1:8000/docs
- **Health:** http://127.0.0.1:8000/health

### Useful PowerShell commands

| Action                      | Command |
|-----------------------------|---------|
| Go to project               | `cd "c:\Users\ferna\Downloads\Experimento cursor 1"` |
| Create venv                 | `python -m venv venv` |
| Allow scripts (once)        | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Activate venv               | `.\venv\Scripts\Activate.ps1` |
| Deactivate venv             | `deactivate` |
| Install dependencies        | `pip install -r requirements.txt` |
| Run API                     | `uvicorn app.main:app --reload` |

### Quick start: all commands in order (PowerShell)

```powershell
cd "c:\Users\ferna\Downloads\Experimento cursor 1"

python -m venv venv

# Only the first time, to allow running Activate.ps1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env

uvicorn app.main:app --reload
```

### Endpoints

- `GET /` — Welcome message and link to docs
- `GET /health` — API and MongoDB status
- `GET /items` — List items
- `POST /items` — Create item (body: `name`, `description`, `price`)
- `GET /items/{id}` — Get item by ID
- `DELETE /items/{id}` — Delete item

### Project structure

```text
Experimento cursor 1/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app and lifespan
│   ├── database.py      # MongoDB connection
│   └── routers/
│       ├── __init__.py
│       └── items.py     # Items CRUD
├── .env                 # Environment variables (NOT committed to git)
├── .env.example         # Example env file
├── requirements.txt
└── README.md
```

---

## Español

### Descripción

API REST con **FastAPI** conectada a **MongoDB**.  
Incluye health check, documentación Swagger y un recurso de ejemplo `items` con CRUD básico.

### Requisitos

- Python 3.11 o superior (soporta Python 3.14)
- MongoDB (local o MongoDB Atlas)

### Configuración (PowerShell)

#### 1. Entrar al proyecto

```powershell
cd "c:\Users\ferna\Downloads\Experimento cursor 1"
```

#### 2. Crear el entorno virtual (venv)

```powershell
python -m venv venv
```

#### 3. Permitir ejecución de scripts (solo una vez)

Si PowerShell muestra un error de política de ejecución al activar el venv, ejecuta:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Esto se hace una sola vez por usuario.

#### 4. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

#### 5. Instalar dependencias

```powershell
pip install -r requirements.txt
```

#### 6. Variables de entorno

El proyecto incluye un archivo `.env.example`. Cópialo a `.env`:

```powershell
Copy-Item .env.example .env
```

Edita `.env` y configura al menos:

- `MONGODB_URL`: URI de MongoDB (por ejemplo, la URL de Atlas)
- `DATABASE_NAME`: nombre de la base de datos (por ejemplo `mi_api_db`)

> **Nota:** El archivo real `.env` está ignorado en git (`.gitignore`), por lo que no se subirá al repositorio.

#### 7. Ejecutar la API

```powershell
uvicorn app.main:app --reload
```

La API quedará disponible en:

- **API:** http://127.0.0.1:8000
- **Documentación Swagger:** http://127.0.0.1:8000/docs
- **Health:** http://127.0.0.1:8000/health

### Comandos PowerShell útiles

| Acción                               | Comando |
|--------------------------------------|---------|
| Entrar al proyecto                   | `cd "c:\Users\ferna\Downloads\Experimento cursor 1"` |
| Crear venv                           | `python -m venv venv` |
| Permitir scripts PS (una vez)        | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Activar venv                         | `.\venv\Scripts\Activate.ps1` |
| Desactivar venv                      | `deactivate` |
| Instalar dependencias                | `pip install -r requirements.txt` |
| Ejecutar API                         | `uvicorn app.main:app --reload` |

### Guía rápida: comandos en orden (PowerShell)

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

### Endpoints

- `GET /` — Mensaje de bienvenida y enlace a docs
- `GET /health` — Estado de la API y conexión a MongoDB
- `GET /items` — Listar items
- `POST /items` — Crear item (body: `name`, `description`, `price`)
- `GET /items/{id}` — Obtener item por ID
- `DELETE /items/{id}` — Eliminar item

### Estructura del proyecto

```text
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

### Licencia

Uso libre para aprendizaje y desarrollo.
