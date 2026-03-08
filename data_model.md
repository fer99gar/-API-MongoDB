# Data Model

## 1. Campos que conservaré de PokéAPI

La respuesta de PokéAPI tiene muchos campos. Para este proyecto conservaré los siguientes:

- id — identificador único del Pokémon
- name — nombre del Pokémon
- base_experience — experiencia base
- height — altura del Pokémon
- weight — peso del Pokémon
- types — tipos del Pokémon (fire, water, etc.)
- stats — hp, attack, defense, speed
- abilities — habilidades especiales del Pokémon

Estos campos son útiles para análisis, filtrado y cálculos de estadísticas.

## 2. Esquema del documento MongoDB

Ejemplo de documento que se guardará:

{
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
"abilities": ["static","lightning-rod"]
}

El identificador único natural será el campo **id**.

## 3. Evitar duplicados

Para evitar duplicados se utilizará una operación **upsert** en MongoDB.
Esto significa que:

- si el Pokémon no existe → se crea
- si ya existe → se actualiza

## 4. Tabla PostgreSQL para logs

Se creará una tabla llamada **etl_log** con las siguientes columnas:

- id
- pokemon_name
- action
- detail
- created_at