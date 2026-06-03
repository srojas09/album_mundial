from typing import List, Optional
from fastapi import HTTPException
from models.lamina import Lamina, LaminaCreate, LaminaUpdate, EstadoEnum
from services.csv_service import read_csv, write_csv, get_next_id, find_by_id, str_to_bool

FILE = "laminas.csv"
FIELDS = ["id", "numero_lamina", "jugador_id", "tengo", "cantidad_repetidas", "estado"]


def _row_to_lamina(row: dict) -> Lamina:
    return Lamina(
        id=int(row["id"]),
        numero_lamina=int(row["numero_lamina"]),
        jugador_id=int(row["jugador_id"]),
        tengo=str_to_bool(row["tengo"]),
        cantidad_repetidas=int(row["cantidad_repetidas"]),
        estado=row["estado"],
    )


# ─── CREATE ──────────────────────────────────────────────────────────────────

def crear_lamina(data: LaminaCreate) -> Lamina:
    from services.jugador_service import obtener_jugador_por_id
    # Regla: el jugador debe existir y estar activo
    obtener_jugador_por_id(data.jugador_id)  # lanza 404 si no existe

    registros = read_csv(FILE)
    # Regla: no puede haber dos láminas con el mismo número_lamina activas
    for r in registros:
        if r["numero_lamina"] == str(data.numero_lamina) and r["estado"] == "activo":
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una lámina activa con el número {data.numero_lamina}.",
            )

    nuevo_id = get_next_id(FILE)
    lamina = Lamina(id=nuevo_id, **data.model_dump(), estado=EstadoEnum.activo)
    registros.append({
        "id": lamina.id,
        "numero_lamina": lamina.numero_lamina,
        "jugador_id": lamina.jugador_id,
        "tengo": lamina.tengo,
        "cantidad_repetidas": lamina.cantidad_repetidas,
        "estado": lamina.estado,
    })
    write_csv(FILE, registros, FIELDS)
    return lamina


# ─── READ ─────────────────────────────────────────────────────────────────────

def obtener_laminas(solo_activas: bool = True) -> List[Lamina]:
    registros = read_csv(FILE)
    if solo_activas:
        registros = [r for r in registros if r["estado"] == "activo"]
    return [_row_to_lamina(r) for r in registros]


def obtener_lamina_por_id(lamina_id: int) -> Lamina:
    row = find_by_id(FILE, lamina_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Lámina con ID {lamina_id} no encontrada.")
    return _row_to_lamina(row)


def obtener_faltantes() -> List[Lamina]:
    """Retorna las láminas activas que NO tengo."""
    registros = read_csv(FILE)
    resultado = [r for r in registros if r["estado"] == "activo" and not str_to_bool(r["tengo"])]
    return [_row_to_lamina(r) for r in resultado]


def obtener_repetidas() -> List[Lamina]:
    """Retorna las láminas activas con cantidad_repetidas > 0."""
    registros = read_csv(FILE)
    resultado = [
        r for r in registros
        if r["estado"] == "activo" and int(r["cantidad_repetidas"]) > 0
    ]
    return [_row_to_lamina(r) for r in resultado]


def filtrar_laminas(tengo: Optional[bool] = None, jugador_id: Optional[int] = None) -> List[Lamina]:
    registros = read_csv(FILE)
    resultado = [r for r in registros if r["estado"] == "activo"]
    if tengo is not None:
        resultado = [r for r in resultado if str_to_bool(r["tengo"]) == tengo]
    if jugador_id is not None:
        resultado = [r for r in resultado if r["jugador_id"] == str(jugador_id)]
    return [_row_to_lamina(r) for r in resultado]


def buscar_por_numero(numero_lamina: int) -> Lamina:
    """Busca una lámina por su número en el álbum (diferente al ID)."""
    registros = read_csv(FILE)
    for r in registros:
        if r["numero_lamina"] == str(numero_lamina) and r["estado"] == "activo":
            return _row_to_lamina(r)
    raise HTTPException(status_code=404, detail=f"No se encontró lámina activa con número {numero_lamina}.")


# ─── UPDATE ───────────────────────────────────────────────────────────────────

def actualizar_lamina(lamina_id: int, data: LaminaUpdate) -> Lamina:
    registros = read_csv(FILE)
    encontrado = False

    for i, r in enumerate(registros):
        if r["id"] == str(lamina_id):
            if r["estado"] == "inactivo":
                raise HTTPException(status_code=400, detail="No se puede actualizar una lámina inactiva.")
            if data.tengo is not None:
                registros[i]["tengo"] = data.tengo
                # Regla: si marco tengo=False, las repetidas vuelven a 0
                if not data.tengo:
                    registros[i]["cantidad_repetidas"] = 0
            if data.cantidad_repetidas is not None:
                registros[i]["cantidad_repetidas"] = data.cantidad_repetidas
            encontrado = True
            idx = i
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"Lámina con ID {lamina_id} no encontrada.")

    write_csv(FILE, registros, FIELDS)
    return _row_to_lamina(registros[idx])


# ─── DELETE (soft) ────────────────────────────────────────────────────────────

def eliminar_lamina(lamina_id: int) -> dict:
    """
    Eliminación lógica: cambia estado a 'inactivo'.
    Regla de negocio: no se puede eliminar si tiene intercambios disponibles asociados.
    """
    from services.intercambio_service import tiene_intercambios_activos

    registros = read_csv(FILE)
    encontrado = False

    for i, r in enumerate(registros):
        if r["id"] == str(lamina_id):
            if r["estado"] == "inactivo":
                raise HTTPException(status_code=400, detail="La lámina ya está inactiva.")
            if tiene_intercambios_activos(lamina_id):
                raise HTTPException(
                    status_code=400,
                    detail="No se puede desactivar la lámina porque tiene intercambios disponibles. "
                           "Primero cancele esos intercambios.",
                )
            registros[i]["estado"] = "inactivo"
            encontrado = True
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"Lámina con ID {lamina_id} no encontrada.")

    write_csv(FILE, registros, FIELDS)
    return {"mensaje": f"Lámina {lamina_id} desactivada correctamente. El registro se conserva en el historial."}


# ─── Helper para otros servicios ─────────────────────────────────────────────

def tiene_laminas_activas(jugador_id: int) -> bool:
    registros = read_csv(FILE)
    return any(
        r["jugador_id"] == str(jugador_id) and r["estado"] == "activo"
        for r in registros
    )
