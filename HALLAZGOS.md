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
| H1 | *(ejemplo de FORMATO, no un defecto de este repositorio)* `GET /health` responde sin cabecera `Cache-Control` | El handler no declara política de caché | M6 · 5. Routing y CRUD | `v0-semilla` | `curl -sI localhost:8000/health \| grep -ci cache-control` | `0` | Se añade la cabecera en la respuesta |
| H2 | Al crear una póliza con un número ya existente (el servicio trae datos de ejemplo precargados), `POST /polizas` responde `500 Internal Server Error` en vez de `409 Conflict` | No se valida la unicidad de `numero` antes del `commit`; el `IntegrityError` de SQLite no se captura ni se traduce a una respuesta HTTP controlada | <<COMPLETAR>> | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-2026-00001", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `HTTP/1.1 500 Internal Server Error` (cuerpo: `Internal Server Error`) | Se verifica unicidad antes del `commit` y se responde `409` explícitamente con `HTTPException` |
| H3 | Tras un error de integridad en una petición, todo el servicio deja de responder: incluso `GET /polizas` (una ruta de solo lectura) devuelve `500` | La sesión de base de datos es un único objeto global (`sesion`, en `database.py`), compartido por todas las peticiones; un error no revertido en una petición deja la sesión inválida para todas las siguientes | <<COMPLETAR>> | `v0-semilla` | `curl -s -i localhost:8000/polizas` (ejecutado inmediatamente después del POST que falló en H2) | `HTTP/1.1 500 Internal Server Error` (cuerpo: `Internal Server Error`) | Se reemplaza la sesión global por `database.get_db`, un generador que entrega una sesión nueva por petición con `Depends` |
| H4 | Al crear una póliza enviando `"asegurado": "Ana Rueda"`, la respuesta devuelve `"asegurado": null` | El validador `normalizar_asegurado` en `esquemas.py` calcula el valor normalizado pero no tiene sentencia `return`, así que Pydantic descarta el resultado | <<COMPLETAR>> | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-9999-99999", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `{"numero":"POL-9999-99999","asegurado":null,"fecha_inicio":"2026-01-15","token_firma":"bcfb3788a1b42277914076ebfa4f6b2d260659c17d539b963b585464ff93081e","id":13,"tipo":"auto","prima":1250000.0,"fecha_fin":"2027-01-14"}` | Se agrega `return " ".join(v.split()).title()` al final del validador |
| H5 | La respuesta de `POST /polizas` expone el campo interno `token_firma` | La función `_poliza()` en `main.py` arma el dict de respuesta incluyendo `token_firma`, sin `response_model` que lo filtre | <<COMPLETAR>> | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-9999-99999", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `{...,"token_firma":"bcfb3788a1b42277914076ebfa4f6b2d260659c17d539b963b585464ff93081e",...}` | Se declara `response_model` con un esquema de salida que no incluye `token_firma` |
| H6 | `POST /polizas` responde `200 OK` al crear una póliza, en vez de `201 Created` | La ruta no declara `status_code=201` ni usa `response_model` con el código correcto | <<COMPLETAR>> | `v0-semilla` | `curl -s -i -X POST localhost:8000/polizas -H "Content-Type: application/json" -d '{"numero": "POL-9999-99999", "asegurado": "Ana Rueda", "tipo": "auto", "prima": 1250000, "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}'` | `HTTP/1.1 200 OK` | Se agrega `status_code=201` al decorador de la ruta |
| H7 | Al actualizar una póliza enviando solo `{"prima": 999000}`, los campos no enviados (`tipo`, `fecha_fin`) quedan en `null` en vez de conservar su valor anterior | `actualizar_poliza` usa `datos.model_dump()` sin `exclude_unset=True`, así que sobrescribe con los defaults (`None`) todos los campos opcionales no enviados | <<COMPLETAR>> | `v0-semilla` | `curl -s -i -X PUT localhost:8000/polizas/13 -H "Content-Type: application/json" -d '{"prima": 999000}'` | `{"id":13,"numero":"POL-9999-99999","asegurado":null,"tipo":null,"prima":999000.0,"fecha_inicio":"2026-01-15","fecha_fin":null,"token_firma":"bcfb3788a1b42277914076ebfa4f6b2d260659c17d539b963b585464ff93081e","siniestros":[]}` | Se usa `datos.model_dump(exclude_unset=True)` para aplicar solo los campos realmente enviados |
| H8 | Consultar una póliza inexistente (`GET /polizas/999999`) responde `200 OK` con un cuerpo `{"error": ...}`, en vez de `404 Not Found` | La ruta retorna un dict de error manualmente en lugar de lanzar `HTTPException(status_code=404)` | <<COMPLETAR>> | `v0-semilla` | `curl -s -i localhost:8000/polizas/999999` | `HTTP/1.1 200 OK` ... `{"error":"no existe la póliza 999999"}` | Se reemplaza el retorno manual por `raise HTTPException(status_code=404, detail=...)` |
| H9 | No existe el endpoint `GET /health` | No está implementado en `main.py` | <<COMPLETAR>> | `v0-semilla` | `curl -s -i localhost:8000/health` | `HTTP/1.1 404 Not Found` (cuerpo: `{"detail":"Not Found"}`) | Se agrega `GET /health` que responde 200 e indica si la base de datos responde |
| H10 | El `Dockerfile` fija la imagen base en `python:latest`, sin versión concreta | `FROM python:latest` en la primera línea del `Dockerfile` | <<COMPLETAR>> | `v0-semilla` | `head -5 Dockerfile` | `FROM python:latest` | Se fija `FROM python:3.11.9-slim-bookworm` en una construcción multietapa |
| H11 | Las claves `SECRETO_FIRMA` y `CLAVE_API_REASEGURO` están hardcodeadas en texto plano en un archivo versionado | `config.py` no usa `BaseSettings`/`.env`; el propio código trae un comentario `# TODO: sacar esto a variables de entorno` que confirma el problema | <<COMPLETAR>> | `v0-semilla` | `grep -n "SECRETO\|CLAVE" config.py` | `4:SECRETO_FIRMA = "aseguradora-santo-tomas-2026-firma-7c1e"` / `5:CLAVE_API_REASEGURO = "rk-polizas-2026-4b9f0a3d"` | Se mueven ambos valores a `.env`, leídos vía `BaseSettings`, y se agregan a `.env.example` con valores de ejemplo |

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

## `/polizas/{id}`

## `/siniestros`

## `/resumen`