"""Conexión a la base de datos."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import config


class Base(DeclarativeBase):
    pass


engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Una sola sesión para todo el servicio: se abre al arrancar y se reutiliza.
sesion = SessionLocal()
