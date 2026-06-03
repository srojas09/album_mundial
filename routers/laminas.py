from fastapi import APIRouter, Query
from typing import List, Optional
from models.lamina import Lamina, LaminaCreate, LaminaUpdate
import services.lamina_service as svc

router = APIRouter(prefix="/laminas", tags=["Láminas del Álbum"])


@router.get("/", response_model=List[Lamina], summary="Listar láminas activas")
def listar_laminas():
    return svc.obtener_laminas(solo_activas=True)


@router.get("/todas", response_model=List[Lamina], summary="Listar todas las láminas (incluye inactivas)")
def listar_todas():
    """Muestra el historial completo incluyendo láminas desactivadas."""
    return svc.obtener_laminas(solo_activas=False)


@router.get("/faltantes", response_model=List[Lamina], summary="Láminas que me faltan para completar el álbum")
def faltantes():
    return svc.obtener_faltantes()


@router.get("/repetidas", response_model=List[Lamina], summary="Láminas repetidas disponibles para intercambio")
def repetidas():
    return svc.obtener_repetidas()


@router.get("/buscar/{numero_lamina}", response_model=Lamina, summary="Buscar lámina por su número en el álbum")
def buscar_por_numero(numero_lamina: int):
    """Búsqueda por número de lámina (diferente al ID interno)."""
    return svc.buscar_por_numero(numero_lamina)


@router.get("/filtrar", response_model=List[Lamina], summary="Filtrar láminas por estado y/o jugador")
def filtrar(
    tengo: Optional[bool] = Query(None, description="true = tengo la lámina, false = me falta"),
    jugador_id: Optional[int] = Query(None, description="ID del jugador asociado"),
):
    return svc.filtrar_laminas(tengo=tengo, jugador_id=jugador_id)


@router.get("/{lamina_id}", response_model=Lamina, summary="Obtener lámina por ID")
def obtener_lamina(lamina_id: int):
    return svc.obtener_lamina_por_id(lamina_id)


@router.post("/", response_model=Lamina, status_code=201, summary="Registrar lámina en el álbum")
def crear_lamina(data: LaminaCreate):
    return svc.crear_lamina(data)


@router.put("/{lamina_id}", response_model=Lamina, summary="Actualizar estado de la lámina")
def actualizar_lamina(lamina_id: int, data: LaminaUpdate):
    return svc.actualizar_lamina(lamina_id, data)


@router.delete("/{lamina_id}", summary="Desactivar lámina (soft delete)")
def eliminar_lamina(lamina_id: int):
    return svc.eliminar_lamina(lamina_id)
