from fastapi import APIRouter, Query
from typing import List, Optional
from models.intercambio import Intercambio, IntercambioCreate, IntercambioUpdate, TipoEnum, EstadoIntercambioEnum
import services.intercambio_service as svc

router = APIRouter(prefix="/intercambios", tags=["Marketplace de Intercambios"])


@router.get("/", response_model=List[Intercambio], summary="Listar intercambios disponibles")
def listar_disponibles():
    return svc.obtener_intercambios(estado=EstadoIntercambioEnum.disponible)


@router.get("/historial", response_model=List[Intercambio], summary="Historial completo de intercambios")
def historial():
    """Muestra todos los intercambios: disponibles, completados y cancelados."""
    return svc.obtener_intercambios()


@router.get("/buscar", response_model=List[Intercambio], summary="Buscar intercambios por propietario")
def buscar_por_propietario(nombre: str = Query(..., description="Nombre o parte del nombre del propietario")):
    """Búsqueda por nombre del propietario (diferente al ID)."""
    return svc.buscar_por_propietario(nombre)


@router.get("/filtrar", response_model=List[Intercambio], summary="Filtrar por tipo y/o estado")
def filtrar(
    tipo: Optional[TipoEnum] = Query(None, description="Tipo: intercambio, venta o regalo"),
    estado: Optional[EstadoIntercambioEnum] = Query(None, description="Estado del intercambio"),
):
    return svc.filtrar_intercambios(tipo=tipo, estado=estado)


@router.get("/{intercambio_id}", response_model=Intercambio, summary="Obtener intercambio por ID")
def obtener_intercambio(intercambio_id: int):
    return svc.obtener_intercambio_por_id(intercambio_id)


@router.post("/", response_model=Intercambio, status_code=201, summary="Publicar lámina en el marketplace")
def crear_intercambio(data: IntercambioCreate):
    return svc.crear_intercambio(data)


@router.put("/{intercambio_id}", response_model=Intercambio, summary="Actualizar publicación")
def actualizar_intercambio(intercambio_id: int, data: IntercambioUpdate):
    return svc.actualizar_intercambio(intercambio_id, data)


@router.patch("/{intercambio_id}/completar", response_model=Intercambio, summary="Marcar intercambio como completado")
def completar(intercambio_id: int):
    return svc.completar_intercambio(intercambio_id)


@router.delete("/{intercambio_id}", summary="Cancelar publicación (soft delete)")
def cancelar_intercambio(intercambio_id: int):
    return svc.cancelar_intercambio(intercambio_id)
