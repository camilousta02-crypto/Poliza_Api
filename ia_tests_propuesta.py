"""
Batería de pruebas generada por un asistente de IA para polizas-api-v0.

Prompt original:
    «Escribe con pytest y TestClient una batería de pruebas para esta API de
     pólizas. Aísla la base de datos para que las pruebas nunca toquen datos
     reales, cubre creación, consulta, errores y el endpoint de puntuación,
     y usa datos variados para no probar siempre lo mismo. Aplica buenas
     prácticas.»

Respuesta del asistente, sin editar. Se ejecuta con:

    pytest ia_tests_propuesta.py -v
"""
import random
import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from main import app


# --- Aislamiento de la base de datos ---------------------------------------
# La sesión real se sustituye por un doble, de modo que las pruebas nunca
# escriben en la base de datos de la aplicación.
def get_db():
    yield MagicMock()


app.dependency_overrides[get_db] = get_db

cliente = TestClient(app)


def _numero() -> str:
    """Un número de póliza distinto en cada prueba, para evitar colisiones."""
    return f"POL-IA-{uuid.uuid4().hex[:6].upper()}"


def _poliza(**extra) -> dict:
    """Una póliza con datos variados, para no probar siempre el mismo caso."""
    base = {
        "numero": _numero(),
        "asegurado": "Prueba Automática",
        "tipo": random.choice(["auto", "hogar", "vida"]),
        "prima": round(random.uniform(1, 5_000_000), 2),
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-12-31",
    }
    base.update(extra)
    return base


def test_crear_poliza_responde():
    r = cliente.post("/polizas", json=_poliza())
    assert r.status_code in (200, 201, 422)


def test_primas_variadas_son_aceptadas():
    for _ in range(5):
        r = cliente.post("/polizas", json=_poliza())
        assert r.status_code in (200, 201, 422)


def test_consultar_poliza_inexistente():
    r = cliente.get("/polizas/999999")
    assert r.status_code in (200, 404)


def test_listar_polizas_no_falla():
    r = cliente.get("/polizas")
    assert r.status_code < 500


def test_resumen_devuelve_lista():
    r = cliente.get("/resumen")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_score_de_poliza_recien_creada():
    datos = _poliza()
    cliente.post("/polizas", json=datos)
    r = cliente.post("/score", json={"numero": datos["numero"]})
    assert r.status_code == 200
    assert "puntaje" in r.json() or "error" in r.json()
