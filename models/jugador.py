from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class EstadoEnum(str, Enum):
    activo = "activo"
    inactivo = "inactivo"


class PosicionEnum(str, Enum):
    portero = "portero"
    defensa = "defensa"
    centrocampista = "centrocampista"
    delantero = "delantero"


class Jugador(BaseModel):
    id: int
    nombre: str
    pais: str
    posicion: PosicionEnum
    numero_camiseta: int = Field(ge=1, le=99)
    edad: int = Field(ge=15, le=50)
    foto_url: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.activo


class JugadorCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    pais: str = Field(min_length=2, max_length=60)
    posicion: PosicionEnum
    numero_camiseta: int = Field(ge=1, le=99)
    edad: int = Field(ge=15, le=50)
    foto_url: Optional[str] = None


class JugadorUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    pais: Optional[str] = Field(default=None, min_length=2, max_length=60)
    posicion: Optional[PosicionEnum] = None
    numero_camiseta: Optional[int] = Field(default=None, ge=1, le=99)
    edad: Optional[int] = Field(default=None, ge=15, le=50)
    foto_url: Optional[str] = None
