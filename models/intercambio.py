from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import date


class TipoEnum(str, Enum):
    intercambio = "intercambio"   # Quiere otra lámina a cambio
    venta = "venta"               # La vende por dinero
    regalo = "regalo"             # La regala


class EstadoIntercambioEnum(str, Enum):
    disponible = "disponible"
    completado = "completado"
    cancelado = "cancelado"


class Intercambio(BaseModel):
    id: int
    lamina_id: int                          # Lámina que se ofrece
    tipo: TipoEnum
    precio: Optional[float] = None          # Solo si tipo == venta
    lamina_deseada_id: Optional[int] = None # Solo si tipo == intercambio
    propietario_nombre: str
    propietario_contacto: str               # Email o teléfono
    descripcion: Optional[str] = None
    fecha_creacion: date
    estado: EstadoIntercambioEnum = EstadoIntercambioEnum.disponible


class IntercambioCreate(BaseModel):
    lamina_id: int
    tipo: TipoEnum
    precio: Optional[float] = Field(default=None, ge=0)
    lamina_deseada_id: Optional[int] = None
    propietario_nombre: str = Field(min_length=2, max_length=100)
    propietario_contacto: str = Field(min_length=5, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=300)


class IntercambioUpdate(BaseModel):
    precio: Optional[float] = Field(default=None, ge=0)
    lamina_deseada_id: Optional[int] = None
    propietario_contacto: Optional[str] = Field(default=None, min_length=5, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    estado: Optional[EstadoIntercambioEnum] = None
