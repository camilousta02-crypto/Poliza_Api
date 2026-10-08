"""Esquemas de entrada y salida."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SiniestroEntrada(BaseModel):
    fecha: date
    monto: float = Field(gt=0, description="Monto reclamado, en pesos")
    descripcion: str = Field(min_length=3, max_length=200)
    estado: str = "abierto"


class SiniestroSalida(SiniestroEntrada):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SiniestroListado(SiniestroSalida):
    poliza_id: int
    numero_poliza: str


class PolizaEntrada(BaseModel):
    numero: str = Field(min_length=8, max_length=20, description="Formato POL-AAAA-NNNNN")
    asegurado: str = Field(min_length=3, max_length=80)
    tipo: str = Field(description="auto, hogar o vida")
    prima: float = Field(gt=0, description="Prima anual, en pesos")
    fecha_inicio: date
    fecha_fin: date
    siniestros: list[SiniestroEntrada] = Field(default_factory=list)

    @field_validator("asegurado")
    @classmethod
    def normalizar_asegurado(cls, v: str) -> str:
        """Quita espacios sobrantes y pone el nombre con mayúscula inicial."""
        return " ".join(v.split()).title()

    @model_validator(mode="after")
    def fechas_coherentes(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self


class PolizaActualizacion(BaseModel):
    asegurado: Optional[str] = Field(default=None, min_length=3, max_length=80)
    tipo: Optional[str] = None
    prima: Optional[float] = Field(default=None, gt=0)
    fecha_fin: Optional[date] = None


class PolizaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    asegurado: Optional[str]
    tipo: Optional[str]
    prima: float
    fecha_inicio: date
    fecha_fin: Optional[date]
    siniestros: list[SiniestroSalida]


class ResumenFila(BaseModel):
    numero: str
    n_siniestros: int
    monto_total: float


class PuntuacionEntrada(BaseModel):
    numero: str = Field(min_length=8, max_length=20)


class PuntuacionSalida(BaseModel):
    numero: str
    puntaje: float = Field(ge=0, le=1)
    alto_riesgo: bool


class PrediccionSalida(BaseModel):
    id: int
    numero: str
    poliza_id: int
    puntaje: float
    alto_riesgo: bool
    creado_en: datetime