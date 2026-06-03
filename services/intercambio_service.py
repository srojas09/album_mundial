from typing import List, Optional
from datetime import date
from fastapi import HTTPException
from models.intercambio import (
    Intercambio, IntercambioCreate, IntercambioUpdate,
    TipoEnum, EstadoIntercambioEnum,
)
from services.csv_service import read_csv, write_csv, get_next_id, find_by_id

FILE = "intercambios.csv"
FIELDS = [
    "id", "lamina_id", "tipo", "precio", "lamina_deseada_id",
    "propietario_nombre", "propietario_contacto", "descripcion",
    "fecha_creacion", "estado",
]


def _row_to_intercambio(row: dict) -> Intercambio:
    return Intercambio(
        id=int(row["id"]),
        lamina_id=int(row["lamina_id"]),
        tipo=row["tipo"],
        precio=float(row["precio"]) if row.get("precio") and row["precio"] != "" else None,
        lamina_deseada_id=int(row["lamina_deseada_id"]) if row.get("lamina_deseada_id") and row["lamina_deseada_id"] != "" else None,
        propietario_nombre=row["propietario_nombre"],
        propietario_contacto=row["propietario_contacto"],
        descripcion=row.get("descripcion") or None,
        fecha_creacion=date.fromisoformat(row["fecha_creacion"]),
        estado=row["estado"],
    )


# ─── CREATE ──────────────────────────────────────────────────────────────────

def crear_intercambio(data: IntercambioCreate) -> Intercambio:
    from services.lamina_service import obtener_lamina_por_id

    lamina = obtener_lamina_por_id(data.lamina_id)

    # Regla de negocio: solo se pueden publicar láminas que tengo y que están repetidas
    if not lamina.tengo:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes publicar láminas que ya tienes en tu álbum.",
        )
    if lamina.cantidad_repetidas < 1:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes publicar láminas que tengas repetidas (cantidad_repetidas >= 1).",
        )

    # Regla: si es venta debe tener precio; si es intercambio debe tener lámina deseada
    if data.tipo == TipoEnum.venta and not data.precio:
        raise HTTPException(status_code=400, detail="Las publicaciones de venta deben incluir un precio.")
    if data.tipo == TipoEnum.intercambio and not data.lamina_deseada_id:
        raise HTTPException(status_code=400, detail="Los intercambios deben indicar la lámina deseada.")

    # Regla: no puede haber dos publicaciones disponibles del mismo propietario para la misma lámina
    registros = read_csv(FILE)
    for r in registros:
        if (r["lamina_id"] == str(data.lamina_id)
                and r["propietario_nombre"].lower() == data.propietario_nombre.lower()
                and r["estado"] == "disponible"):
            raise HTTPException(
                status_code=400,
                detail="Ya tienes una publicación disponible para esta lámina.",
            )

    nuevo_id = get_next_id(FILE)
    intercambio = Intercambio(
        id=nuevo_id,
        fecha_creacion=date.today(),
        estado=EstadoIntercambioEnum.disponible,
        **data.model_dump(),
    )
    registros.append({
        "id": intercambio.id,
        "lamina_id": intercambio.lamina_id,
        "tipo": intercambio.tipo.value,
        "precio": intercambio.precio or "",
        "lamina_deseada_id": intercambio.lamina_deseada_id or "",
        "propietario_nombre": intercambio.propietario_nombre,
        "propietario_contacto": intercambio.propietario_contacto,
        "descripcion": intercambio.descripcion or "",
        "fecha_creacion": intercambio.fecha_creacion.isoformat(),
        "estado": intercambio.estado.value,
    })
    write_csv(FILE, registros, FIELDS)
    return intercambio


# ─── READ ─────────────────────────────────────────────────────────────────────

def obtener_intercambios(estado: Optional[EstadoIntercambioEnum] = None) -> List[Intercambio]:
    registros = read_csv(FILE)
    if estado:
        registros = [r for r in registros if r["estado"] == estado.value]
    return [_row_to_intercambio(r) for r in registros]


def obtener_intercambio_por_id(intercambio_id: int) -> Intercambio:
    row = find_by_id(FILE, intercambio_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Intercambio con ID {intercambio_id} no encontrado.")
    return _row_to_intercambio(row)


def buscar_por_propietario(nombre: str) -> List[Intercambio]:
    """Búsqueda por nombre de propietario (diferente al ID)."""
    registros = read_csv(FILE)
    coincidencias = [r for r in registros if nombre.lower() in r["propietario_nombre"].lower()]
    return [_row_to_intercambio(r) for r in coincidencias]


def filtrar_intercambios(tipo: Optional[TipoEnum] = None, estado: Optional[EstadoIntercambioEnum] = None) -> List[Intercambio]:
    registros = read_csv(FILE)
    if tipo:
        registros = [r for r in registros if r["tipo"] == tipo.value]
    if estado:
        registros = [r for r in registros if r["estado"] == estado.value]
    return [_row_to_intercambio(r) for r in registros]


# ─── UPDATE ───────────────────────────────────────────────────────────────────

def actualizar_intercambio(intercambio_id: int, data: IntercambioUpdate) -> Intercambio:
    registros = read_csv(FILE)
    encontrado = False
    idx = None

    for i, r in enumerate(registros):
        if r["id"] == str(intercambio_id):
            if r["estado"] != "disponible":
                raise HTTPException(
                    status_code=400,
                    detail=f"Solo se pueden editar intercambios en estado 'disponible'. Estado actual: {r['estado']}.",
                )
            cambios = {k: v for k, v in data.model_dump().items() if v is not None}
            registros[i].update({k: str(v) for k, v in cambios.items()})
            encontrado = True
            idx = i
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"Intercambio con ID {intercambio_id} no encontrado.")

    write_csv(FILE, registros, FIELDS)
    return _row_to_intercambio(registros[idx])


# ─── DELETE (soft → cancelado) ───────────────────────────────────────────────

def cancelar_intercambio(intercambio_id: int) -> dict:
    """
    Eliminación lógica: cambia estado a 'cancelado'.
    Los registros cancelados y completados se conservan como historial.
    """
    registros = read_csv(FILE)
    encontrado = False

    for i, r in enumerate(registros):
        if r["id"] == str(intercambio_id):
            if r["estado"] == "cancelado":
                raise HTTPException(status_code=400, detail="El intercambio ya está cancelado.")
            if r["estado"] == "completado":
                raise HTTPException(status_code=400, detail="No se puede cancelar un intercambio ya completado.")
            registros[i]["estado"] = "cancelado"
            encontrado = True
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"Intercambio con ID {intercambio_id} no encontrado.")

    write_csv(FILE, registros, FIELDS)
    return {"mensaje": f"Intercambio {intercambio_id} cancelado. El registro se conserva en el historial."}


def completar_intercambio(intercambio_id: int) -> Intercambio:
    """Marca un intercambio como completado."""
    registros = read_csv(FILE)
    idx = None

    for i, r in enumerate(registros):
        if r["id"] == str(intercambio_id):
            if r["estado"] != "disponible":
                raise HTTPException(
                    status_code=400,
                    detail=f"Solo se pueden completar intercambios disponibles. Estado actual: {r['estado']}.",
                )
            registros[i]["estado"] = "completado"
            idx = i
            break

    if idx is None:
        raise HTTPException(status_code=404, detail=f"Intercambio con ID {intercambio_id} no encontrado.")

    write_csv(FILE, registros, FIELDS)
    return _row_to_intercambio(registros[idx])


# ─── Helper para otros servicios ─────────────────────────────────────────────

def tiene_intercambios_activos(lamina_id: int) -> bool:
    registros = read_csv(FILE)
    return any(
        r["lamina_id"] == str(lamina_id) and r["estado"] == "disponible"
        for r in registros
    )
