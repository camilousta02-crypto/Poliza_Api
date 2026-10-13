"""Batería corregida (Parte D): base temporal propia, aserciones exactas, datos deterministas."""
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

DB = Path(tempfile.mkdtemp(prefix="ia-corregido-")) / "prueba.db"
URL = f"sqlite:///{DB}"
os.environ["DATABASE_URL"] = URL
subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)

import database  # noqa: E402
from main import app  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

_engine = create_engine(URL, connect_args={"check_same_thread": False})


@event.listens_for(_engine, "connect")
def _fk(conn, _):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


_Sesion = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


def _get_db():
    db = _Sesion()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _aislar():
    app.dependency_overrides[database.get_db] = _get_db
    yield
    app.dependency_overrides.pop(database.get_db, None)


cliente = TestClient(app, raise_server_exceptions=False)


def _poliza(**extra):
    base = {"numero": f"POL-IA-{uuid.uuid4().hex[:6].upper()}", "asegurado": "Ana Rueda",
            "tipo": "auto", "prima": 1_250_000,
            "fecha_inicio": "2026-01-15", "fecha_fin": "2027-01-14"}
    base.update(extra)
    return base


def test_crear_poliza_devuelve_201_y_se_puede_consultar():
    datos = _poliza()
    r = cliente.post("/polizas", json=datos)
    assert r.status_code == 201, r.text
    creada = r.json()
    assert creada["numero"] == datos["numero"] and creada["asegurado"] == "Ana Rueda"
    r2 = cliente.get(f"/polizas/{creada['id']}")
    assert r2.status_code == 200 and r2.json()["numero"] == datos["numero"]


def test_prima_no_positiva_da_422():
    assert cliente.post("/polizas", json=_poliza(prima=0)).status_code == 422
    assert cliente.post("/polizas", json=_poliza(prima=-5)).status_code == 422


def test_poliza_inexistente_da_404():
    assert cliente.get("/polizas/999999").status_code == 404
    assert cliente.put("/polizas/999999", json={"prima": 10}).status_code == 404


def test_numero_duplicado_da_409():
    datos = _poliza()
    assert cliente.post("/polizas", json=datos).status_code == 201
    assert cliente.post("/polizas", json=datos).status_code == 409


def test_listar_incluye_la_poliza_creada():
    datos = _poliza()
    cliente.post("/polizas", json=datos)
    r = cliente.get("/polizas")
    assert r.status_code == 200
    assert datos["numero"] in [p["numero"] for p in r.json()]


def test_resumen_cuenta_y_suma_los_siniestros():
    sin = [{"fecha": "2026-03-01", "monto": 100, "descripcion": "Primero", "estado": "abierto"},
           {"fecha": "2026-04-01", "monto": 250, "descripcion": "Segundo", "estado": "abierto"}]
    datos = _poliza(siniestros=sin)
    assert cliente.post("/polizas", json=datos).status_code == 201
    fila = next(f for f in cliente.get("/resumen").json() if f["numero"] == datos["numero"])
    assert fila["n_siniestros"] == 2 and fila["monto_total"] == 350.0


def test_score_registra_la_prediccion():
    datos = _poliza()
    cliente.post("/polizas", json=datos)
    r = cliente.post("/score", json={"numero": datos["numero"]})
    assert r.status_code == 200 and 0.0 <= r.json()["puntaje"] <= 1.0
    registradas = cliente.get("/predicciones").json()
    assert datos["numero"] in [p["numero"] for p in registradas]


def test_score_de_poliza_inexistente_da_404():
    assert cliente.post("/score", json={"numero": "POL-NO-EXISTE"}).status_code == 404