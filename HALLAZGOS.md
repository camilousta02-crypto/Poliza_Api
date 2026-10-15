# Hallazgos — Parte A

**Grupo:** 1 · **Integrantes:** Camilo Andrés Velandia Suárez

> No borren la fila de ejemplo hasta haber comprobado que su tabla se parsea
> (`python verificar_entrega.py`). El formato es rígido: ocho columnas, en este
> orden. Una tabla torcida se rechaza indicando la línea, no se «entiende igual».
>
> **Tuberías dentro de una celda:** si su comando lleva `|` —y varios lo llevarán,
> por `grep`, `head` o `jq`— escríbanlo `\|`. Sin escapar, Markdown lo lee como
> separador de columna y su fila pasa a tener nueve.

| ID | Síntoma observable | Causa | Módulo · Sección | SHA donde se observa | Comando de evidencia | Salida obtenida | Corrección aplicada |
|----|--------------------|-------|------------------|----------------------|----------------------|-----------------|---------------------|
| H2 | Al crear una póliza con un número ya existente (el servicio trae datos de ejemplo precargados), `POST /polizas` responde `500 Internal Server Error` en vez de `409 Conflict` | No se valida la unicidad de `numero` antes del `commit`; el `IntegrityError` de SQLite no se captura ni se traduce a una respuesta HTTP controlada | M6 · 5. Routing y CRUD | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-2026-00001", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `HTTP/1.1 500 Internal Server Error` (cuerpo: `Internal Server Error`) | Se verifica unicidad antes del `commit` y se responde `409` explícitamente con `HTTPException` |
| H3 | Tras un error de integridad en una petición, todo el servicio deja de responder: incluso `GET /polizas` (una ruta de solo lectura) devuelve `500` | La sesión de base de datos es un único objeto global (`sesion`, en `database.py`), compartido por todas las peticiones; un error no revertido en una petición deja la sesión inválida para todas las siguientes | M8 · 4. Inyección de dependencias con Depends | `v0-semilla` | `curl -s -i localhost:8000/polizas` (ejecutado inmediatamente después del POST que falló en H2) | `HTTP/1.1 500 Internal Server Error` (cuerpo: `Internal Server Error`) | Se reemplaza la sesión global por `database.get_db`, un generador que entrega una sesión nueva por petición con `Depends` |
| H4 | Al crear una póliza enviando `"asegurado": "Ana Rueda"`, la respuesta devuelve `"asegurado": null` | El validador `normalizar_asegurado` en `esquemas.py` calcula el valor normalizado pero no tiene sentencia `return`, así que Pydantic descarta el resultado | M7 · 4. Validadores de campo | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-9999-99999", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `{"numero":"POL-9999-99999","asegurado":null,"fecha_inicio":"2026-01-15","token_firma":"bcfb3788a1b42277914076ebfa4f6b2d260659c17d539b963b585464ff93081e","id":13,"tipo":"auto","prima":1250000.0,"fecha_fin":"2027-01-14"}` | Se agrega `return " ".join(v.split()).title()` al final del validador |
| H5 | La respuesta de `POST /polizas` expone el campo interno `token_firma` | La función `_poliza()` en `main.py` arma el dict de respuesta incluyendo `token_firma`, sin `response_model` que lo filtre | M6 · 5. Routing y CRUD | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-9999-99999", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `{...,"token_firma":"bcfb3788a1b42277914076ebfa4f6b2d260659c17d539b963b585464ff93081e",...}` | Se declara `response_model` con un esquema de salida que no incluye `token_firma` |
| H6 | `POST /polizas` responde `200 OK` al crear una póliza, en vez de `201 Created` | La ruta no declara `status_code=201` ni usa `response_model` con el código correcto | M6 · 5. Routing y CRUD | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-9999-99999", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `HTTP/1.1 200 OK` | Se agrega `status_code=201` al decorador de la ruta |
| H7 | Al actualizar una póliza enviando solo `{"prima": 999000}`, los campos no enviados (`tipo`, `fecha_fin`) quedan en `null` en vez de conservar su valor anterior | `actualizar_poliza` usa `datos.model_dump()` sin `exclude_unset=True`, así que sobrescribe con los defaults (`None`) todos los campos opcionales no enviados | M6 · 5. Routing y CRUD | `v0-semilla` | `curl -s -i -X PUT localhost:8000/polizas/13 -H "Content-Type: application/json" -d '{"prima": 999000}'` | `{"id":13,"numero":"POL-9999-99999","asegurado":null,"tipo":null,"prima":999000.0,"fecha_inicio":"2026-01-15","fecha_fin":null,"token_firma":"bcfb3788a1b42277914076ebfa4f6b2d260659c17d539b963b585464ff93081e","siniestros":[]}` | Se usa `datos.model_dump(exclude_unset=True)` para aplicar solo los campos realmente enviados |
| H8 | Consultar una póliza inexistente (`GET /polizas/999999`) responde `200 OK` con un cuerpo `{"error": ...}`, en vez de `404 Not Found` | La ruta retorna un dict de error manualmente en lugar de lanzar `HTTPException(status_code=404)` | M6 · 5. Routing y CRUD | `v0-semilla` | `curl -s -i localhost:8000/polizas/999999` | `HTTP/1.1 200 OK` ... `{"error":"no existe la póliza 999999"}` | Se reemplaza el retorno manual por `raise HTTPException(status_code=404, detail=...)` |
| H9 | No existe el endpoint `GET /health` | No está implementado en `main.py` | M8 · 4. Inyección de dependencias con Depends | `v0-semilla` | `curl -s -i localhost:8000/health` | `HTTP/1.1 404 Not Found` (cuerpo: `{"detail":"Not Found"}`) | Se agrega `GET /health` que responde 200 e indica si la base de datos responde |
| H10 | El `Dockerfile` fija la imagen base en `python:latest`, sin versión concreta | `FROM python:latest` en la primera línea del `Dockerfile` | M11 · 7. Imagen base slim-bookworm | `v0-semilla` | `head -5 Dockerfile` | `FROM python:latest` | Se fija `FROM python:3.11.9-slim-bookworm` en una construcción multietapa |
| H11 | Las claves `SECRETO_FIRMA` y `CLAVE_API_REASEGURO` están hardcodeadas en texto plano en un archivo versionado | `config.py` no usa `BaseSettings`/`.env`; el propio código trae un comentario `# TODO: sacar esto a variables de entorno` que confirma el problema | M8 · 3. De lo duro a lo flexible: variables de entorno | `v0-semilla` | `grep -n "SECRETO\|CLAVE" config.py` | `4:SECRETO_FIRMA = "aseguradora-santo-tomas-2026-firma-7c1e"` / `5:CLAVE_API_REASEGURO = "rk-polizas-2026-4b9f0a3d"` | Se mueven ambos valores a `.env`, leídos vía `BaseSettings`, y se agregan a `.env.example` con valores de ejemplo |

**Reglas que se verifican automáticamente:**

- `Módulo · Sección` debe citar una lección que exista en los módulos 6 a 11, con el
  título tal como aparece en el menú lateral del material.
- **`SHA donde se observa`** es el commit donde el defecto todavía está: normalmente
  `v0-semilla`, la etiqueta del repositorio tal como se les entregó. El calificador hace
  *checkout* de ese commit para reproducir la evidencia. Si lo dejan en el commit final
  —donde ya está corregido— el comando no reproducirá nada y la fila no cuenta.
- `Comando de evidencia` se ejecuta ahí, con el servicio levantado. Escríbanlo contra
  `localhost:8000`; el calificador sustituye el puerto por el que use. Un comando `docker`
  también vale: se reproduce si hay Docker en la máquina que califica.
- `Salida obtenida` es literal, copiada de su terminal. **Se compara con lo que salga de
  verdad**, así que una salida inventada se detecta.
- Entre 8 y 14 hallazgos. Una fila que no corresponda a un defecto real resta la mitad de
  lo que suma una correcta: el máximo se alcanza con precisión, no con volumen.

---

# Parte C — Interpretación de las consultas

> Un párrafo por endpoint. Expliquen **los conteos que ustedes obtuvieron** con
> `contar_consultas.py`: por qué ese número, por qué cambia o no entre 10 y 2000
> pólizas, y qué estrategia dejaron en el código. Si un resultado los sorprendió,
> díganlo: eso se premia.

## `/polizas`

La estrategia en el código es `selectinload`. Con `lazy` medí 11 consultas con 10 pólizas y 2001 con 2000. Hace una consulta para obtener las pólizas y una consulta adicional por cada póliza para cargar sus siniestros, porque accedo a `p.siniestros` dentro del bucle, lo que provoca el problema N+1. Con `selectinload` medí 2 y 5 consultas, porque carga los siniestros mediante `WHERE poliza_id IN (...)` en lotes de unos 500 identificadores. Con 10 pólizas cabe en un lote (1 + 1 = 2) y con 2000 hacen falta 4 (1 + 4 = 5). Por tanto, lo que cambia es el número de lotes, no el número de consultas por póliza. Con 2000 pólizas, el tiempo bajó de 3356.8 ms con `lazy` a 400.8 ms con `selectinload`.

## `/polizas/{id}`

La estrategia en el código es `joinedload`. Con `lazy` medí 2 consultas tanto con 10 como con 2000 pólizas, porque solo se solicita una póliza y se ejecuta una consulta para obtenerla y otra para cargar sus siniestros, que se incluyen en la respuesta. `selectinload` también dio 2 consultas, porque carga la póliza y sus siniestros por separado. En cambio, `joinedload` dio 1 consulta porque obtiene ambos mediante un JOIN. En este caso, `selectinload` no mejora el número de consultas frente a `lazy`, mientras que `joinedload` permite obtener los datos en una sola consulta.

## `/siniestros`

La estrategia en el código es `joinedload`. La consulta base obtiene los 6000 siniestros. Con `lazy` medí 11 consultas con 10 pólizas y 2001 con 2000: 1 por los siniestros y 1 por cada póliza distinta al leer `s.poliza`. No son 6001 porque varios siniestros comparten póliza y el identity map de SQLAlchemy reutiliza los objetos que ya están cargados. Con `joinedload` medí 1 consulta en ambos tamaños, porque es una relación a uno y el JOIN no multiplica filas. No incluyo una cifra medida para `selectinload`.

## `/resumen`

La estrategia en el código es `agregada`. Con `lazy` medí 11 y 2001 consultas. Con `selectinload` medí 2 y 5 consultas, y 343.3 ms con 2000 pólizas, porque carga las 2000 pólizas y los 6000 siniestros como objetos para luego contar y sumar en Python. Con `agregada` medí 1 consulta en ambos tamaños y 47.0 ms con 2000: la base de datos calcula `COUNT` y `SUM` con `GROUP BY` y devuelve solo las filas de resumen, sin cargar los siniestros en memoria. Esto demuestra que reducir el número de consultas no siempre es suficiente: también importa cuántos datos se recuperan y dónde se realiza el cálculo.