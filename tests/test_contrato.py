"""
Contrato que el servicio debe cumplir al terminar el taller.

Estos tests están ROJOS en su mayoría sobre el repositorio tal como se entrega.
Todos deben pasar cuando terminen la Parte B. Que pasen es el mínimo, no la
meta: hay criterios de la rúbrica que estos tests no ven.

    pytest tests/test_contrato.py -v

Se aíslan en una base propia, `.test_contrato.db`:
  · ponen DATABASE_URL antes de importar la aplicación,
  · aplican las migraciones si hay alembic.ini,
  · y si existe `database.get_db` (restricción B3) la sustituyen, antes de cada
    test, con una sesión sobre esa base: así no dependen de cuándo se importó
    la aplicación ni de lo que hagan las fixtures de otros archivos.
Mientras nada de eso exista, escriben donde escriba la aplicación.
"""
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

DB = RAIZ / ".test_contrato.db"
DB.unlink(missing_ok=True)
URL = f"sqlite:///{DB}"
os.environ["DATABASE_URL"] = URL
if (RAIZ / "alembic.ini").exists():
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)

import database  # noqa: E402
from main import app  # noqa: E402

if hasattr(database, "get_db"):
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker

    _engine = create_engine(URL, connect_args={"check_same_thread": False})

    @event.listens_for(_engine, "connect")
    def _fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    if not (RAIZ / "alembic.ini").exists():
        database.Base.metadata.create_all(_engine)
    _Sesion = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)

    def _get_db():
        db = _Sesion()
        try:
            yield db
        finally:
            db.close()

    @pytest.fixture(autouse=True)
    def _aislar():
        """Se instala antes de CADA test: una fixture ajena que haga
        `dependency_overrides.clear()` no puede dejar estos tests sin aislamiento."""
        previo = app.dependency_overrides.get(database.get_db)
        app.dependency_overrides[database.get_db] = _get_db
        yield
        if previo is None:
            app.dependency_overrides.pop(database.get_db, None)
        else:
            app.dependency_overrides[database.get_db] = previo

cliente = TestClient(app, raise_server_exceptions=False)


def _poliza(**extra):
    base = {
        "numero": f"POL-CT-{uuid.uuid4().hex[:6].upper()}",
        "asegurado": "Ana Rueda",
        "tipo": "auto",
        "prima": 1_250_000,
        "fecha_inicio": "2026-01-15",
        "fecha_fin": "2027-01-14",
    }
    base.update(extra)
    return base


SINIESTRO = {"fecha": "2026-03-02", "monto": 850_000, "descripcion": "Choque leve", "estado": "abierto"}


# --- M6 · arquitectura y contrato HTTP ------------------------------------

def test_health_responde_200():
    assert cliente.get("/health").status_code == 200


def test_crear_poliza_devuelve_201():
    r = cliente.post("/polizas", json=_poliza())
    assert r.status_code == 201, f"devolvió {r.status_code}"
    assert "id" in r.json() and "numero" in r.json()


def test_la_respuesta_no_filtra_campos_internos():
    r = cliente.post("/polizas", json=_poliza())
    assert "token_firma" not in r.json(), "la respuesta expone token_firma"


def test_poliza_inexistente_da_404():
    assert cliente.get("/polizas/999999").status_code == 404
    assert cliente.put("/polizas/999999", json={"prima": 10}).status_code == 404


def test_siniestro_de_poliza_inexistente_da_404():
    r = cliente.post("/polizas/999999/siniestros", json=SINIESTRO)
    assert r.status_code == 404, f"devolvió {r.status_code}"


def test_put_parcial_conserva_los_campos():
    creada = cliente.post("/polizas", json=_poliza(asegurado="Bruno Celis", tipo="hogar")).json()
    r = cliente.put(f"/polizas/{creada['id']}", json={"prima": 999_000})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["asegurado"] == "Bruno Celis", f"asegurado quedó en {cuerpo['asegurado']!r}"
    assert cuerpo["tipo"] == "hogar" and cuerpo["fecha_fin"] == "2027-01-14"


# --- M7 · validación --------------------------------------------------------

def test_prima_no_positiva_da_422():
    assert cliente.post("/polizas", json=_poliza(prima=0)).status_code == 422


def test_fechas_invertidas_dan_422():
    r = cliente.post("/polizas", json=_poliza(fecha_inicio="2027-01-14", fecha_fin="2026-01-15"))
    assert r.status_code == 422, f"devolvió {r.status_code}"


def test_siniestro_anidado_con_monto_negativo_da_422():
    r = cliente.post("/polizas", json=_poliza(siniestros=[{**SINIESTRO, "monto": -50}]))
    assert r.status_code == 422, f"devolvió {r.status_code}"


def test_el_asegurado_se_conserva():
    r = cliente.post("/polizas", json=_poliza(asegurado="Carla Ibáñez"))
    assert r.json().get("asegurado") == "Carla Ibáñez", f"asegurado quedó en {r.json().get('asegurado')!r}"


# --- M9 · persistencia -------------------------------------------------------

def test_score_registra_la_prediccion():
    datos = _poliza()
    cliente.post("/polizas", json=datos)
    r = cliente.post("/score", json={"numero": datos["numero"]})
    assert r.status_code == 200 and 0.0 <= r.json()["puntaje"] <= 1.0
    registradas = cliente.get("/predicciones").json()
    assert any(p["numero"] == datos["numero"] for p in registradas), \
        "la predicción no quedó registrada con el número de la póliza"


# Va el último a propósito: en un servicio con la sesión compartida, el
# conflicto deja la sesión inservible y arrastraría a los tests siguientes.
def test_numero_duplicado_da_409_y_el_servicio_sigue_vivo():
    datos = _poliza()
    assert cliente.post("/polizas", json=datos).status_code < 500
    r = cliente.post("/polizas", json=datos)
    assert r.status_code == 409, f"devolvió {r.status_code}"
    assert cliente.get("/polizas").status_code == 200, "tras el conflicto el servicio dejó de responder"
