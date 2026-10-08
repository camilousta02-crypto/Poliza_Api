"""Configuración del servicio, leída desde variables de entorno."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    SECRETO_FIRMA: str
    CLAVE_API_REASEGURO: str
    RUTA_MODELO: str = "modelo.pkl"
    UMBRAL_ALTO_RIESGO: float = 0.6


@lru_cache
def get_settings() -> Settings:
    return Settings()