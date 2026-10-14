# Bitácora de uso de IA

**Grupo:** 1 · **Integrantes:** Camilo Andrés Velandia Suárez
**Herramientas usadas:** Claude

> Las tres secciones son obligatorias. **`## Rechazado` es la que se califica.**
> Una bitácora que solo lista prompts aceptados vale la mitad.

## Prompts

| # | Parte | Quién | Prompt (resumido si es largo) |
|---|-------|-------|-------------------------------|
| 1 | General | Camilo | Pedí que leyera el enunciado del taller y me explicara qué había que hacer, con un paso a paso. |
| 2 | A | Camilo | Pegué README, config.py, main.py, database.py, esquemas.py, modelos.py y Dockerfile y pedí un diagnóstico de defectos. |
| 3 | A | Camilo | Pegué salidas de curl y del traceback de uvicorn para armar las filas de HALLAZGOS.md. |
| 4 | B | Camilo | Pedí el código de config.py (BaseSettings), database.py (get_db), esquemas.py y main.py con las restricciones B1 a B10. |
| 5 | B | Camilo | Pedí los pasos de Alembic y del Dockerfile multietapa, y pegué los errores y salidas al ejecutarlos. |
| 6 | C | Camilo | Pegué la salida de contar_consultas.py y pedí ayuda para decidir y justificar la estrategia de cada endpoint. |
| 7 | D | Camilo | Pedí una batería corregida (tests/test_ia_corregido.py) y los comandos para las mutaciones. |
| 8 | A/D | Camilo | Pasé capturas del menú lateral de los módulos para las citas de módulo y sección. |

## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | config.py con BaseSettings y lru_cache, más .env y .env.example | Cumple B1 y B2 y el comando de prueba imprimió los valores | Corregí la versión de pydantic-settings en requirements.txt (2.15.0, la real) |
| 2 | database.py con get_db como generador y PRAGMA foreign_keys | Cumple B3 y B4 | Ninguno |
| 3 | esquemas.py y main.py con response_model, 201/404/409/422, PUT parcial y /health | Los 12 tests de test_contrato.py pasaron | Tuve que reemplazar main.py completo tras aplicar mal los cambios por partes |
| 4 | Estrategias de carga: selectinload, joinedload y agregada | Los conteos medidos bajaron de 11/2001 a 2/5, 1/1, 1/1 y 1/1 | Ninguno |
| 5 | Dockerfile multietapa, usuario no root y HEALTHCHECK | Construyó, respondió /health desde el host y quedó (healthy) | Ninguno |
| 6 | tests/test_ia_corregido.py y mutaciones A y C | Pasa 8/8 y las mutaciones lo ponen en rojo mientras el original sigue verde | Ninguno |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | Hipótesis de que el 500 de POST /polizas venía de devolver el objeto ORM sin response_model | El traceback real mostró PendingRollbackError por UNIQUE constraint, es decir, la sesión global envenenada tras un duplicado | Documenté dos hallazgos distintos (falta de 409 y sesión global) con la causa real |
| 2 | Hipótesis de que test_contrato.py figuraba modificado por core.autocrlf | El git diff salía vacío y no verificamos la hipótesis. El aviso desapareció al restaurar el archivo con git checkout | Restauré el archivo desde el commit semilla y volví a correr verificar_entrega.py |
| 3 | Escribir .gitignore con un echo multilínea | En Git Bash escribió el comando literal dentro del archivo, como mostró git diff | Lo reescribí con cat y un heredoc |
| 4 | pydantic-settings==2.6.1 en requirements.txt | Era una versión supuesta, sin verificar. pip show dio 2.15.0 | Fijé las versiones reales instaladas |
| 5 | Decir que sustituyera los cuatro endpoints en main.py | No están seguidos en el archivo. Quedaron fuera PUT y /score y fallaron 4 tests | Reemplacé main.py completo y volvieron a pasar los 12 tests |
| 6 | Decir que la batería corregida tenía 7 tests | pytest mostró 8 passed | Usé la cifra real |
| 7 | Mutar el commit de /score con sed | db.commit() aparece en muchas rutas y el sed afectaba a todas | Usé un script de Python con assert que solo cambia el bloque de puntuar |
| 8 | docker run polizas-api ls -a /app | Git Bash convirtió /app en una ruta de Windows | Usé //app |
