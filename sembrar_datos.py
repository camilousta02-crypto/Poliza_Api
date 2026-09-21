"""
Siembra pólizas y siniestros sintéticos A TRAVÉS DE LA API, de forma
determinista: la póliza i siempre sale igual, se siembre sola o en lote.

    # contra un servicio corriendo:
    python sembrar_datos.py --polizas 12
    python sembrar_datos.py --polizas 2000 --base http://localhost:8001 --prefijo POL-C

`contar_consultas.py` importa `sembrar()` y la usa en proceso, con TestClient.
No toca las tablas directamente: solo hace POST /polizas con siniestros anidados,
así que sirve igual antes y después de que cambien el modelado.
"""
import argparse
import random
from datetime import date, timedelta

TIPOS = ["auto", "hogar", "vida"]
NOMBRES = ["Ana Rueda", "Bruno Celis", "Carla Ibáñez", "Diego Fajardo", "Elena Ortiz",
           "Fabio Moreno", "Gloria Pardo", "Hernán Salcedo", "Inés Vargas", "Julián Rojas",
           "Karen Nieto", "Luis Ángel Peña", "Marta Quintero", "Nicolás Barrera",
           "Olga Restrepo", "Pablo Cifuentes", "Rocío Amaya", "Sergio Lindo",
           "Tatiana Mesa", "Víctor Hoyos"]
DESCRIPCIONES = ["Choque leve en vía urbana", "Daño por agua en cocina", "Robo de equipo",
                 "Granizada sobre el vehículo", "Incendio parcial", "Rotura de vidrios",
                 "Pérdida total por inundación", "Hurto en estacionamiento"]
ESTADOS = ["abierto", "pagado", "rechazado"]


def poliza_sintetica(indice: int, prefijo: str, por_poliza: int, semilla: int) -> dict:
    """La póliza número `indice`, siempre la misma para la misma semilla."""
    rng = random.Random(f"{semilla}:{indice}")
    inicio = date(2024, 1, 1) + timedelta(days=rng.randint(0, 600))
    return {
        "numero": f"{prefijo}-{indice:05d}",
        "asegurado": rng.choice(NOMBRES),
        "tipo": rng.choice(TIPOS),
        "prima": round(rng.uniform(350_000, 4_800_000), 2),
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": (inicio + timedelta(days=365)).isoformat(),
        "siniestros": [
            {"fecha": (inicio + timedelta(days=rng.randint(1, 360))).isoformat(),
             "monto": round(rng.uniform(80_000, 6_500_000), 2),
             "descripcion": rng.choice(DESCRIPCIONES),
             "estado": rng.choice(ESTADOS)}
            for _ in range(por_poliza)],
    }


def sembrar(cliente, n: int, por_poliza: int = 3, semilla: int = 20262,
            prefijo: str = "POL-2026", desde: int = 1) -> list[int]:
    """Crea n pólizas con `cliente.post` y devuelve sus ids.

    `cliente` puede ser un httpx.Client o un TestClient: solo se usa `.post`.
    """
    ids = []
    for i in range(desde, desde + n):
        r = cliente.post("/polizas", json=poliza_sintetica(i, prefijo, por_poliza, semilla))
        if r.status_code >= 400:
            raise RuntimeError(
                f"POST /polizas devolvió {r.status_code} en la póliza {i}: {r.text[:200]}")
        ids.append(r.json()["id"])
    return ids


def main():
    import httpx

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--polizas", type=int, default=12)
    ap.add_argument("--por-poliza", type=int, default=3)
    ap.add_argument("--semilla", type=int, default=20262)
    ap.add_argument("--prefijo", default="POL-2026")
    ap.add_argument("--desde", type=int, default=1)
    a = ap.parse_args()
    with httpx.Client(base_url=a.base, timeout=60) as cliente:
        ids = sembrar(cliente, a.polizas, a.por_poliza, a.semilla, a.prefijo, a.desde)
    print(f"{len(ids)} pólizas creadas (ids {ids[0]}…{ids[-1]}), {a.por_poliza} siniestros cada una.")


if __name__ == "__main__":
    main()
