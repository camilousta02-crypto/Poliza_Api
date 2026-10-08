"""Conexión a la base de datos."""
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _activar_claves_foraneas(conexion, _registro):
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Iterator[Session]:
    """Una sesión por petición: se abre al entrar y se cierra siempre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()