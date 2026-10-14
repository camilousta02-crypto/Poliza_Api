# Dictamen sobre `ia_tests_propuesta.py` — Parte D

**Grupo:** 1 · **Integrantes:** Camilo Andrés Velandia Suárez

## Defecto 1

- **Qué está mal:** Varios tests aceptan casi cualquier respuesta (`status_code in (200, 201, 422)`, `in (200, 404)`, `< 500`), así que no pueden fallar aunque el servicio esté roto.
- **Por qué es un defecto** (módulo · sección): M10 · 4. Framework pytest
- **Cómo lo comprobamos:** Mutación A: `GET /polizas/{id}` deja de devolver 404 y responde 200. El test original sigue en verde y el corregido falla.

```diff
diff --git a/main.py b/main.py
index 584e769..075cc20 100644
--- a/main.py
+++ b/main.py
@@ -1,146 +1,146 @@
-"""
-polizas-api — Gestión de pólizas y siniestros.
-Aseguradora Santo Tomás · prototipo interno.
-"""
-import hashlib
-import pickle
-from datetime import date
-
-from fastapi import Depends, FastAPI, HTTPException
-from sqlalchemy import func, select, text
-from sqlalchemy.exc import IntegrityError
-from sqlalchemy.orm import Session, joinedload, selectinload
-
-from config import Settings, get_settings
-from database import get_db
-from esquemas import (PolizaActualizacion, PolizaEntrada, PolizaSalida, PrediccionSalida,
-                      PuntuacionEntrada, PuntuacionSalida, ResumenFila, SiniestroEntrada,
-                      SiniestroListado, SiniestroSalida)
-from modelos import Poliza, Prediccion, Siniestro
-
-with open(get_settings().RUTA_MODELO, "rb") as fh:
-    modelo = pickle.load(fh)
-
-app = FastAPI(title="Pólizas API", version="0.2.0")
-
-
-def firmar(numero: str, settings: Settings) -> str:
-    return hashlib.sha256(f"{numero}:{settings.SECRETO_FIRMA}".encode()).hexdigest()
-
-
-def _buscar_poliza(db: Session, id_poliza: int) -> Poliza:
-    poliza = db.get(Poliza, id_poliza)
-    if poliza is None:
-        raise HTTPException(status_code=404, detail=f"no existe la póliza {id_poliza}")
-    return poliza
-
-
-@app.get("/health")
-def health(db: Session = Depends(get_db)):
-    try:
-        db.execute(text("SELECT 1"))
-        return {"status": "ok", "base_de_datos": "ok"}
-    except Exception:
-        return {"status": "degradado", "base_de_datos": "error"}
-
-
-@app.post("/polizas", response_model=PolizaSalida, status_code=201)
-def crear_poliza(datos: PolizaEntrada, db: Session = Depends(get_db),
-                 settings: Settings = Depends(get_settings)):
-    if db.scalar(select(Poliza.id).where(Poliza.numero == datos.numero)) is not None:
-        raise HTTPException(status_code=409, detail=f"ya existe la póliza {datos.numero}")
-    poliza = Poliza(numero=datos.numero, asegurado=datos.asegurado, tipo=datos.tipo,
-                    prima=datos.prima, fecha_inicio=datos.fecha_inicio, fecha_fin=datos.fecha_fin,
-                    token_firma=firmar(datos.numero, settings))
-    for s in datos.siniestros:
-        poliza.siniestros.append(Siniestro(**s.model_dump()))
-    db.add(poliza)
-    try:
-        db.commit()
-    except IntegrityError:
-        db.rollback()
-        raise HTTPException(status_code=409, detail=f"ya existe la póliza {datos.numero}")
-    db.refresh(poliza)
-    return poliza
-
-
-@app.get("/polizas", response_model=list[PolizaSalida])
-def listar_polizas(db: Session = Depends(get_db)):
-    consulta = select(Poliza).options(selectinload(Poliza.siniestros)).order_by(Poliza.id)
-    return list(db.scalars(consulta))
-
-
-@app.get("/polizas/{id_poliza}", response_model=PolizaSalida)
-def obtener_poliza(id_poliza: int, db: Session = Depends(get_db)):
-    poliza = db.get(Poliza, id_poliza, options=[joinedload(Poliza.siniestros)])
-    if poliza is None:
-        raise HTTPException(status_code=404, detail=f"no existe la póliza {id_poliza}")
-    return poliza
-
-
-@app.put("/polizas/{id_poliza}", response_model=PolizaSalida)
-def actualizar_poliza(id_poliza: int, datos: PolizaActualizacion, db: Session = Depends(get_db)):
-    poliza = _buscar_poliza(db, id_poliza)
-    for campo, valor in datos.model_dump(exclude_unset=True).items():
-        setattr(poliza, campo, valor)
-    db.commit()
-    db.refresh(poliza)
-    return poliza
-
-
-@app.post("/polizas/{id_poliza}/siniestros", response_model=SiniestroSalida, status_code=201)
-def declarar_siniestro(id_poliza: int, datos: SiniestroEntrada, db: Session = Depends(get_db)):
-    _buscar_poliza(db, id_poliza)
-    siniestro = Siniestro(poliza_id=id_poliza, **datos.model_dump())
-    db.add(siniestro)
-    db.commit()
-    db.refresh(siniestro)
-    return siniestro
-
-
-@app.get("/siniestros", response_model=list[SiniestroListado])
-def listar_siniestros(db: Session = Depends(get_db)):
-    consulta = select(Siniestro).options(joinedload(Siniestro.poliza)).order_by(Siniestro.id)
-    return [SiniestroListado(id=s.id, poliza_id=s.poliza_id, numero_poliza=s.poliza.numero,
-                             fecha=s.fecha, monto=s.monto, descripcion=s.descripcion,
-                             estado=s.estado)
-            for s in db.scalars(consulta)]
-
-
-@app.get("/resumen", response_model=list[ResumenFila])
-def resumen(db: Session = Depends(get_db)):
-    consulta = (
-        select(Poliza.numero,
-               func.count(Siniestro.id),
-               func.coalesce(func.sum(Siniestro.monto), 0.0))
-        .outerjoin(Siniestro, Siniestro.poliza_id == Poliza.id)
-        .group_by(Poliza.id)
-        .order_by(Poliza.id)
-    )
-    return [ResumenFila(numero=n, n_siniestros=c, monto_total=round(t, 2))
-            for n, c, t in db.execute(consulta)]
-
-
-@app.post("/score", response_model=PuntuacionSalida)
-def puntuar(datos: PuntuacionEntrada, db: Session = Depends(get_db),
-            settings: Settings = Depends(get_settings)):
-    poliza = db.scalar(select(Poliza).where(Poliza.numero == datos.numero))
-    if poliza is None:
-        raise HTTPException(status_code=404, detail=f"no existe la póliza {datos.numero}")
-    rasgos = [[poliza.prima, len(poliza.siniestros), sum(s.monto for s in poliza.siniestros),
-               (date.today() - poliza.fecha_inicio).days]]
-    puntaje = float(modelo.predict_proba(rasgos)[0][1])
-    prediccion = Prediccion(poliza_id=poliza.id, puntaje=puntaje,
-                            alto_riesgo=puntaje > settings.UMBRAL_ALTO_RIESGO)
-    db.add(prediccion)
-    db.commit()
-    return PuntuacionSalida(numero=poliza.numero, puntaje=round(puntaje, 4),
-                            alto_riesgo=prediccion.alto_riesgo)
-
-
-@app.get("/predicciones", response_model=list[PrediccionSalida])
-def listar_predicciones(db: Session = Depends(get_db)):
-    return [PrediccionSalida(id=pr.id, numero=pr.poliza.numero, poliza_id=pr.poliza_id,
-                             puntaje=pr.puntaje, alto_riesgo=pr.alto_riesgo,
-                             creado_en=pr.creado_en)
+"""
+polizas-api — Gestión de pólizas y siniestros.
+Aseguradora Santo Tomás · prototipo interno.
+"""
+import hashlib
+import pickle
+from datetime import date
+
+from fastapi import Depends, FastAPI, HTTPException
+from sqlalchemy import func, select, text
+from sqlalchemy.exc import IntegrityError
+from sqlalchemy.orm import Session, joinedload, selectinload
+
+from config import Settings, get_settings
+from database import get_db
+from esquemas import (PolizaActualizacion, PolizaEntrada, PolizaSalida, PrediccionSalida,
+                      PuntuacionEntrada, PuntuacionSalida, ResumenFila, SiniestroEntrada,
+                      SiniestroListado, SiniestroSalida)
+from modelos import Poliza, Prediccion, Siniestro
+
+with open(get_settings().RUTA_MODELO, "rb") as fh:
+    modelo = pickle.load(fh)
+
+app = FastAPI(title="Pólizas API", version="0.2.0")
+
+
+def firmar(numero: str, settings: Settings) -> str:
+    return hashlib.sha256(f"{numero}:{settings.SECRETO_FIRMA}".encode()).hexdigest()
+
+
+def _buscar_poliza(db: Session, id_poliza: int) -> Poliza:
+    poliza = db.get(Poliza, id_poliza)
+    if poliza is None:
+        raise HTTPException(status_code=200, detail=f"no existe la póliza {id_poliza}")
+    return poliza
+
+
+@app.get("/health")
+def health(db: Session = Depends(get_db)):
+    try:
+        db.execute(text("SELECT 1"))
+        return {"status": "ok", "base_de_datos": "ok"}
+    except Exception:
+        return {"status": "degradado", "base_de_datos": "error"}
+
+
+@app.post("/polizas", response_model=PolizaSalida, status_code=201)
+def crear_poliza(datos: PolizaEntrada, db: Session = Depends(get_db),
+                 settings: Settings = Depends(get_settings)):
+    if db.scalar(select(Poliza.id).where(Poliza.numero == datos.numero)) is not None:
+        raise HTTPException(status_code=409, detail=f"ya existe la póliza {datos.numero}")
+    poliza = Poliza(numero=datos.numero, asegurado=datos.asegurado, tipo=datos.tipo,
+                    prima=datos.prima, fecha_inicio=datos.fecha_inicio, fecha_fin=datos.fecha_fin,
+                    token_firma=firmar(datos.numero, settings))
+    for s in datos.siniestros:
+        poliza.siniestros.append(Siniestro(**s.model_dump()))
+    db.add(poliza)
+    try:
+        db.commit()
+    except IntegrityError:
+        db.rollback()
+        raise HTTPException(status_code=409, detail=f"ya existe la póliza {datos.numero}")
+    db.refresh(poliza)
+    return poliza
+
+
+@app.get("/polizas", response_model=list[PolizaSalida])
+def listar_polizas(db: Session = Depends(get_db)):
+    consulta = select(Poliza).options(selectinload(Poliza.siniestros)).order_by(Poliza.id)
+    return list(db.scalars(consulta))
+
+
+@app.get("/polizas/{id_poliza}", response_model=PolizaSalida)
+def obtener_poliza(id_poliza: int, db: Session = Depends(get_db)):
+    poliza = db.get(Poliza, id_poliza, options=[joinedload(Poliza.siniestros)])
+    if poliza is None:
+        raise HTTPException(status_code=200, detail=f"no existe la póliza {id_poliza}")
+    return poliza
+
+
+@app.put("/polizas/{id_poliza}", response_model=PolizaSalida)
+def actualizar_poliza(id_poliza: int, datos: PolizaActualizacion, db: Session = Depends(get_db)):
+    poliza = _buscar_poliza(db, id_poliza)
+    for campo, valor in datos.model_dump(exclude_unset=True).items():
+        setattr(poliza, campo, valor)
+    db.commit()
+    db.refresh(poliza)
+    return poliza
+
+
+@app.post("/polizas/{id_poliza}/siniestros", response_model=SiniestroSalida, status_code=201)
+def declarar_siniestro(id_poliza: int, datos: SiniestroEntrada, db: Session = Depends(get_db)):
+    _buscar_poliza(db, id_poliza)
+    siniestro = Siniestro(poliza_id=id_poliza, **datos.model_dump())
+    db.add(siniestro)
+    db.commit()
+    db.refresh(siniestro)
+    return siniestro
+
+
+@app.get("/siniestros", response_model=list[SiniestroListado])
+def listar_siniestros(db: Session = Depends(get_db)):
+    consulta = select(Siniestro).options(joinedload(Siniestro.poliza)).order_by(Siniestro.id)
+    return [SiniestroListado(id=s.id, poliza_id=s.poliza_id, numero_poliza=s.poliza.numero,
+                             fecha=s.fecha, monto=s.monto, descripcion=s.descripcion,
+                             estado=s.estado)
+            for s in db.scalars(consulta)]
+
+
+@app.get("/resumen", response_model=list[ResumenFila])
+def resumen(db: Session = Depends(get_db)):
+    consulta = (
+        select(Poliza.numero,
+               func.count(Siniestro.id),
+               func.coalesce(func.sum(Siniestro.monto), 0.0))
+        .outerjoin(Siniestro, Siniestro.poliza_id == Poliza.id)
+        .group_by(Poliza.id)
+        .order_by(Poliza.id)
+    )
+    return [ResumenFila(numero=n, n_siniestros=c, monto_total=round(t, 2))
+            for n, c, t in db.execute(consulta)]
+
+
+@app.post("/score", response_model=PuntuacionSalida)
+def puntuar(datos: PuntuacionEntrada, db: Session = Depends(get_db),
+            settings: Settings = Depends(get_settings)):
+    poliza = db.scalar(select(Poliza).where(Poliza.numero == datos.numero))
+    if poliza is None:
+        raise HTTPException(status_code=404, detail=f"no existe la póliza {datos.numero}")
+    rasgos = [[poliza.prima, len(poliza.siniestros), sum(s.monto for s in poliza.siniestros),
+               (date.today() - poliza.fecha_inicio).days]]
+    puntaje = float(modelo.predict_proba(rasgos)[0][1])
+    prediccion = Prediccion(poliza_id=poliza.id, puntaje=puntaje,
+                            alto_riesgo=puntaje > settings.UMBRAL_ALTO_RIESGO)
+    db.add(prediccion)
+    db.commit()
+    return PuntuacionSalida(numero=poliza.numero, puntaje=round(puntaje, 4),
+                            alto_riesgo=prediccion.alto_riesgo)
+
+
+@app.get("/predicciones", response_model=list[PrediccionSalida])
+def listar_predicciones(db: Session = Depends(get_db)):
+    return [PrediccionSalida(id=pr.id, numero=pr.poliza.numero, poliza_id=pr.poliza_id,
+                             puntaje=pr.puntaje, alto_riesgo=pr.alto_riesgo,
+                             creado_en=pr.creado_en)
             for pr in db.scalars(select(Prediccion).order_by(Prediccion.id))]
\ No newline at end of file
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

