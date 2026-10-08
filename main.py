"""
polizas-api — Gestión de pólizas y siniestros.
Aseguradora Santo Tomás · prototipo interno.
"""
import hashlib
import pickle
from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from config import Settings, get_settings
from database import get_db
from esquemas import (PolizaActualizacion, PolizaEntrada, PolizaSalida, PrediccionSalida,
                      PuntuacionEntrada, PuntuacionSalida, ResumenFila, SiniestroEntrada,
                      SiniestroListado, SiniestroSalida)
from modelos import Poliza, Prediccion, Siniestro

with open(get_settings().RUTA_MODELO, "rb") as fh:
    modelo = pickle.load(fh)

app = FastAPI(title="Pólizas API", version="0.2.0")


def firmar(numero: str, settings: Settings) -> str:
    return hashlib.sha256(f"{numero}:{settings.SECRETO_FIRMA}".encode()).hexdigest()


def _buscar_poliza(db: Session, id_poliza: int) -> Poliza:
    poliza = db.get(Poliza, id_poliza)
    if poliza is None:
        raise HTTPException(status_code=404, detail=f"no existe la póliza {id_poliza}")
    return poliza


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "base_de_datos": "ok"}
    except Exception:
        return {"status": "degradado", "base_de_datos": "error"}


@app.post("/polizas", response_model=PolizaSalida, status_code=201)
def crear_poliza(datos: PolizaEntrada, db: Session = Depends(get_db),
                 settings: Settings = Depends(get_settings)):
    if db.scalar(select(Poliza.id).where(Poliza.numero == datos.numero)) is not None:
        raise HTTPException(status_code=409, detail=f"ya existe la póliza {datos.numero}")
    poliza = Poliza(numero=datos.numero, asegurado=datos.asegurado, tipo=datos.tipo,
                    prima=datos.prima, fecha_inicio=datos.fecha_inicio, fecha_fin=datos.fecha_fin,
                    token_firma=firmar(datos.numero, settings))
    for s in datos.siniestros:
        poliza.siniestros.append(Siniestro(**s.model_dump()))
    db.add(poliza)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"ya existe la póliza {datos.numero}")
    db.refresh(poliza)
    return poliza


@app.get("/polizas", response_model=list[PolizaSalida])
def listar_polizas(db: Session = Depends(get_db)):
    consulta = select(Poliza).options(selectinload(Poliza.siniestros)).order_by(Poliza.id)
    return list(db.scalars(consulta))


@app.get("/polizas/{id_poliza}", response_model=PolizaSalida)
def obtener_poliza(id_poliza: int, db: Session = Depends(get_db)):
    poliza = db.get(Poliza, id_poliza, options=[joinedload(Poliza.siniestros)])
    if poliza is None:
        raise HTTPException(status_code=404, detail=f"no existe la póliza {id_poliza}")
    return poliza


@app.put("/polizas/{id_poliza}", response_model=PolizaSalida)
def actualizar_poliza(id_poliza: int, datos: PolizaActualizacion, db: Session = Depends(get_db)):
    poliza = _buscar_poliza(db, id_poliza)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(poliza, campo, valor)
    db.commit()
    db.refresh(poliza)
    return poliza


@app.post("/polizas/{id_poliza}/siniestros", response_model=SiniestroSalida, status_code=201)
def declarar_siniestro(id_poliza: int, datos: SiniestroEntrada, db: Session = Depends(get_db)):
    _buscar_poliza(db, id_poliza)
    siniestro = Siniestro(poliza_id=id_poliza, **datos.model_dump())
    db.add(siniestro)
    db.commit()
    db.refresh(siniestro)
    return siniestro


@app.get("/siniestros", response_model=list[SiniestroListado])
def listar_siniestros(db: Session = Depends(get_db)):
    consulta = select(Siniestro).options(joinedload(Siniestro.poliza)).order_by(Siniestro.id)
    return [SiniestroListado(id=s.id, poliza_id=s.poliza_id, numero_poliza=s.poliza.numero,
                             fecha=s.fecha, monto=s.monto, descripcion=s.descripcion,
                             estado=s.estado)
            for s in db.scalars(consulta)]


@app.get("/resumen", response_model=list[ResumenFila])
def resumen(db: Session = Depends(get_db)):
    consulta = (
        select(Poliza.numero,
               func.count(Siniestro.id),
               func.coalesce(func.sum(Siniestro.monto), 0.0))
        .outerjoin(Siniestro, Siniestro.poliza_id == Poliza.id)
        .group_by(Poliza.id)
        .order_by(Poliza.id)
    )
    return [ResumenFila(numero=n, n_siniestros=c, monto_total=round(t, 2))
            for n, c, t in db.execute(consulta)]


@app.post("/score", response_model=PuntuacionSalida)
def puntuar(datos: PuntuacionEntrada, db: Session = Depends(get_db),
            settings: Settings = Depends(get_settings)):
    poliza = db.scalar(select(Poliza).where(Poliza.numero == datos.numero))
    if poliza is None:
        raise HTTPException(status_code=404, detail=f"no existe la póliza {datos.numero}")
    rasgos = [[poliza.prima, len(poliza.siniestros), sum(s.monto for s in poliza.siniestros),
               (date.today() - poliza.fecha_inicio).days]]
    puntaje = float(modelo.predict_proba(rasgos)[0][1])
    prediccion = Prediccion(poliza_id=poliza.id, puntaje=puntaje,
                            alto_riesgo=puntaje > settings.UMBRAL_ALTO_RIESGO)
    db.add(prediccion)
    db.commit()
    return PuntuacionSalida(numero=poliza.numero, puntaje=round(puntaje, 4),
                            alto_riesgo=prediccion.alto_riesgo)


@app.get("/predicciones", response_model=list[PrediccionSalida])
def listar_predicciones(db: Session = Depends(get_db)):
    return [PrediccionSalida(id=pr.id, numero=pr.poliza.numero, poliza_id=pr.poliza_id,
                             puntaje=pr.puntaje, alto_riesgo=pr.alto_riesgo,
                             creado_en=pr.creado_en)
            for pr in db.scalars(select(Prediccion).order_by(Prediccion.id))]