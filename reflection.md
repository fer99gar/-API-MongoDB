# Reflection

## 1. ¿Cuál es la diferencia entre ETL y ELT? ¿Cuál patrón usaste y por qué?

La diferencia entre ETL y ELT está en el momento en que ocurre la transformación de los datos.

- **ETL** significa **Extract, Transform, Load**. Primero se extraen los datos desde una fuente externa, luego se transforman o limpian, y finalmente se cargan en la base de datos de destino.
- **ELT** significa **Extract, Load, Transform**. En este caso, los datos se extraen y se cargan primero en el sistema de destino, y después se transforman dentro de ese sistema.

En este proyecto utilicé **ETL**, porque primero obtuve los datos desde PokéAPI, después transformé la respuesta para conservar solo los campos útiles (`id`, `name`, `types`, `stats`, etc.), y finalmente guardé el documento limpio en MongoDB. Elegí este patrón porque la tarea pedía explícitamente no guardar la respuesta cruda de PokéAPI, sino solo una versión transformada.

---

## 2. ¿Por qué `bulk_write` es más eficiente que insertar registros uno por uno en un bucle?

`bulk_write` es más eficiente porque permite enviar muchas operaciones a MongoDB en una sola llamada, en lugar de hacer una petición separada por cada documento.

Si se insertaran o actualizaran registros uno por uno dentro de un bucle, habría más viajes entre la aplicación y la base de datos, lo que aumenta el tiempo total y el uso de recursos. En cambio, `bulk_write` agrupa todas las operaciones y reduce ese costo.

En un contexto de ingeniería de datos, esto es importante porque los procesos de ingestión suelen manejar muchos registros y se busca que sean rápidos y escalables.

---

## 3. PokéAPI podría estar lenta o caída. Nombra dos estrategias para hacer tu endpoint de batch más resiliente.

Dos estrategias para hacer el endpoint de batch más resiliente serían:

1. **Reintentos con backoff exponencial**  
   Si una petición falla temporalmente, la aplicación podría volver a intentarlo después de esperar un pequeño tiempo. Si vuelve a fallar, espera un poco más antes del siguiente intento. Esto ayuda cuando la API externa está momentáneamente lenta o inestable.

2. **Timeouts y manejo parcial de errores**  
   Cada request a PokéAPI debería tener un tiempo máximo de espera. Si un Pokémon falla, el batch no debería detenerse por completo. En lugar de eso, debe registrar el error y continuar con los demás registros válidos. Este enfoque ya se aplicó parcialmente en este proyecto, ya que el batch continúa aunque un nombre sea inválido.

---

## 4. Escribe el comando de MongoDB para agregar un índice en el campo `types` de la colección `pokemon`. ¿Por qué ese índice ayuda a la consulta `by-type`?

El comando sería:

```javascript
db.pokemon.createIndex({ types: 1 })


