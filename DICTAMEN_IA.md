# Dictamen sobre `ia_tests_propuesta.py` — Parte D

**Grupo:** 1 · **Integrantes:** Camilo Andrés Velandia Suárez

## Defecto 1

- **Qué está mal:** Varios tests aceptan casi cualquier respuesta (`status_code in (200, 201, 422)`, `in (200, 404)`, `< 500`), así que no pueden fallar aunque el servicio esté roto.
- **Por qué es un defecto** (módulo · sección): M10 · 4. Framework pytest
- **Cómo lo comprobamos:** Mutación A: `GET /polizas/{id}` deja de devolver 404 y responde 200. El test original sigue en verde y el corregido falla.

```diff
diff --git a/main.py b/main.py
index 584e769..2af4a1f 100644
--- a/main.py
+++ b/main.py
@@ -31,7 +31,7 @@ def firmar(numero: str, settings: Settings) -> str:
 def _buscar_poliza(db: Session, id_poliza: int) -> Poliza:
     poliza = db.get(Poliza, id_poliza)
     if poliza is None:
-        raise HTTPException(status_code=404, detail=f"no existe la póliza {id_poliza}")
+        raise HTTPException(status_code=200, detail=f"no existe la póliza {id_poliza}")
     return poliza
 
 
@@ -74,7 +74,7 @@ def listar_polizas(db: Session = Depends(get_db)):
 def obtener_poliza(id_poliza: int, db: Session = Depends(get_db)):
     poliza = db.get(Poliza, id_poliza, options=[joinedload(Poliza.siniestros)])
     if poliza is None:
-        raise HTTPException(status_code=404, detail=f"no existe la póliza {id_poliza}")
+        raise HTTPException(status_code=200, detail=f"no existe la póliza {id_poliza}")
     return poliza
```

```
from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
6 passed, 1 warning in 14.11s
```

```
..\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\Sistems\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_ia_corregido.py::test_poliza_inexistente_da_404 - Assertion...
1 failed, 7 passed, 1 warning in 17.34s
```

- **Corrección:** Aserciones exactas: 201 al crear, 404 si no existe, 409 si está duplicado, 422 si es inválido.

## Defecto 2

- **Qué está mal:** Los tests no prueban lo que dicen. El «aislamiento» sobrescribe una función `get_db` local, no `database.get_db`, así que nunca se usa y los tests escriben en la base real (`app.db` pasó de 28 a 35 pólizas solo por correr el archivo). Además `test_score_de_poliza_recien_creada` solo comprueba que exista la clave `puntaje`, no que la predicción se guarde.
- **Por qué es un defecto** (módulo · sección): M10 · 6. Fixtures en pytest
- **Cómo lo comprobamos:** Mutación C: `/score` deja de guardar la predicción (se quitan `db.add` y `db.commit`). El test original sigue en verde y el corregido falla.

```diff
diff --git a/main.py b/main.py
index 584e769..a4ad672 100644
--- a/main.py
+++ b/main.py
@@ -132,8 +132,7 @@ def puntuar(datos: PuntuacionEntrada, db: Session = Depends(get_db),
     puntaje = float(modelo.predict_proba(rasgos)[0][1])
     prediccion = Prediccion(poliza_id=poliza.id, puntaje=puntaje,
                             alto_riesgo=puntaje > settings.UMBRAL_ALTO_RIESGO)
-    db.add(prediccion)
-    db.commit()
+    pass
     return PuntuacionSalida(numero=poliza.numero, puntaje=round(puntaje, 4),
                             alto_riesgo=prediccion.alto_riesgo)
```

```
from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
6 passed, 1 warning in 18.70s
```

```
..\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\Sistems\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_ia_corregido.py::test_score_registra_la_prediccion - Assert...
1 failed, 7 passed, 1 warning in 19.25s
```

- **Corrección:** Base temporal propia con Alembic, override de `database.get_db` y comprobación de que la predicción aparece en `/predicciones`.

## Defecto 3

- **Qué está mal:** La batería a veces pasa y a veces no: depende del contenido de la base real y usa `random` para `tipo` y `prima`. Con 3 siniestros de monto -50 en `app.db`, `GET /polizas` falla al serializar y el test de la IA se pone en rojo.
- **Por qué es un defecto** (módulo · sección): M10 · 7. Reproducibilidad sin Docker
- **Cómo lo comprobamos:** Aquí la «mutación» es un dato corrupto en la base real, no un cambio de código. El test original pasa de rojo a verde sin tocar una línea, y el corregido no cambia porque no usa esa base.

```sql
-- el dato corrupto que introdujimos en la base real (app.db), no un cambio de código:
INSERT INTO siniestros (poliza_id, fecha, monto, descripcion, estado)
VALUES (<id>, '2026-01-01', -50, 'Dato malo', 'abierto');
```

```
=========================== short test summary info ===========================
FAILED ia_tests_propuesta.py::test_listar_polizas_no_falla - fastapi.exceptio...
1 failed, 5 passed, 1 warning in 20.12s

# tras `rm app.db` y `alembic upgrade head`, la MISMA batería:
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
6 passed, 1 warning in 12.65s
```

```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
8 passed, 1 warning in 18.42s
```

- **Corrección:** Base temporal propia en cada corrida, datos deterministas (sin `random`) y números de póliza únicos.

