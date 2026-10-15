# Dictamen sobre `ia_tests_propuesta.py` — Parte D

**Grupo:** 1 · **Integrantes:** Camilo Andrés Velandia Suárez

## Defecto 1

-**Qué está mal**: Varias aserciones aceptan más de un resultado, incluido el incorrecto (`status_code in (200, 201, 422)`, `in (200, 404)`) o solo descartan que el servidor se caiga (`< 500`). Por eso no distinguen un servicio sano de uno roto: con la mutación A el 404 pasó a 200 y el test original siguió en verde.
- **Por qué es un defecto** (módulo · sección): M10 · 4. Framework pytest
- **Cómo lo comprobamos**: Mutación A: `GET /polizas/{id}` deja de devolver 404 y responde 200. El test original sigue en verde y el corregido falla.

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

- **Corrección**: Cada test exige un único código y comprueba el contenido: 201 al crear, 404 si no existe, 409 si está duplicado, 422 si la prima no es positiva, y valores concretos en `/resumen` y en `/predicciones`. Con la misma mutación, `test_poliza_inexistente_da_404` falla.

## Defecto 2

- **Qué está mal**: Varias aserciones aceptan más de un resultado, incluido el incorrecto (`status_code in (200, 201, 422)`, `in (200, 404)`) o solo descartan que el servidor se caiga (`< 500`). Por eso no distinguen un servicio sano de uno roto: con la mutación A el 404 pasó a 200 y el test original siguió en verde.
- **Por qué es un defecto** (módulo · sección): M10 · 6. Fixtures en pytest
- **Cómo lo comprobamos**: Mutación C: `/score` deja de guardar la predicción (se quitan `db.add` y `db.commit`). El test original sigue en verde y el corregido falla.

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

- **Corrección**: Cada test exige un único código y comprueba el contenido: 201 al crear, 404 si no existe, 409 si está duplicado, 422 si la prima no es positiva, y valores concretos en `/resumen` y en `/predicciones`. Con la misma mutación, `test_poliza_inexistente_da_404` falla.

## Defecto 3

- **Qué está mal**: Varias aserciones aceptan más de un resultado, incluido el incorrecto (`status_code in (200, 201, 422)`, `in (200, 404)`) o solo descartan que el servidor se caiga (`< 500`). Por eso no distinguen un servicio sano de uno roto: con la mutación A el 404 pasó a 200 y el test original siguió en verde.
- **Por qué es un defecto** (módulo · sección): M10 · 7. Reproducibilidad sin Docker
- **Cómo lo comprobamos**: Aquí la «mutación» es un dato corrupto en la base real, no un cambio de código. El test original pasa de rojo a verde sin tocar una línea, y el corregido no cambia porque no usa esa base.

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

- **Corrección**: Cada test exige un único código y comprueba el contenido: 201 al crear, 404 si no existe, 409 si está duplicado, 422 si la prima no es positiva, y valores concretos en `/resumen` y en `/predicciones`. Con la misma mutación, `test_poliza_inexistente_da_404` falla.

