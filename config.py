"""Configuración del servicio."""

# TODO: sacar esto a variables de entorno antes de subir a producción
SECRETO_FIRMA = "aseguradora-santo-tomas-2026-firma-7c1e"
CLAVE_API_REASEGURO = "rk-polizas-2026-4b9f0a3d"

DATABASE_URL = "sqlite:///app.db"
RUTA_MODELO = "modelo.pkl"
UMBRAL_ALTO_RIESGO = 0.6
