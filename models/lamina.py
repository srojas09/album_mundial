from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class EstadoEnum(str, Enum):
    activo = "activo"
    inactivo = "inactivo"


class Lamina(BaseModel):
    id: int
    numero_lamina: int          # Número en el álbum (ej: 145)
    jugador_id: int
    tengo: bool = False          # ¿Tengo esta lámina?
    cantidad_repetidas: int = 0  # Cuántas repetidas tengo
    estado: EstadoEnum = EstadoEnum.activo


class LaminaCreate(BaseModel):
    numero_lamina: int = Field(ge=1, description="Número de la lámina en el álbum")
    jugador_id: int
    tengo: bool = False
    cantidad_repetidas: int = Field(default=0, ge=0)


class LaminaUpdate(BaseModel):
    tengo: Optional[bool] = None
    cantidad_repetidas: Optional[int] = Field(default=None, ge=0)
