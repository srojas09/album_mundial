from fastapi import APIRouter, Query
from typing import List, Optional
from models.jugador import Jugador, JugadorCreate, JugadorUpdate, PosicionEnum
import services.jugador_service as svc

router = APIRouter(prefix="/jugadores", tags=["Jugadores"])


@router.get("/", response_model=List[Jugador], summary="Listar jugadores activos")
def listar_jugadores():
    return svc.obtener_jugadores(solo_activos=True)


@router.get("/todos", response_model=List[Jugador], summary="Listar todos los jugadores (incluye inactivos)")
def listar_todos():
    """Muestra el historial completo incluyendo jugadores desactivados."""
    return svc.obtener_jugadores(solo_activos=False)


@router.get("/buscar", response_model=List[Jugador], summary="Buscar jugador por nombre")
def buscar_por_nombre(nombre: str = Query(..., description="Nombre o parte del nombre del jugador")):
    return svc.buscar_por_nombre(nombre)


@router.get("/filtrar", response_model=List[Jugador], summary="Filtrar jugadores por país y/o posición")
def filtrar(
    pais: Optional[str] = Query(None, description="País de la selección, ej: Colombia"),
    posicion: Optional[PosicionEnum] = Query(None, description="Posición en el campo"),
):
    return svc.filtrar_jugadores(pais=pais, posicion=posicion)


@router.get("/{jugador_id}", response_model=Jugador, summary="Obtener jugador por ID")
def obtener_jugador(jugador_id: int):
    return svc.obtener_jugador_por_id(jugador_id)


@router.post("/", response_model=Jugador, status_code=201, summary="Crear jugador")
def crear_jugador(data: JugadorCreate):
    return svc.crear_jugador(data)


@router.put("/{jugador_id}", response_model=Jugador, summary="Actualizar jugador")
def actualizar_jugador(jugador_id: int, data: JugadorUpdate):
    return svc.actualizar_jugador(jugador_id, data)


@router.delete("/{jugador_id}", summary="Desactivar jugador (soft delete)")
def eliminar_jugador(jugador_id: int):
    return svc.eliminar_jugador(jugador_id)
