from typing import List, Optional
from fastapi import HTTPException
from models.jugador import Jugador, JugadorCreate, JugadorUpdate, EstadoEnum, PosicionEnum
from services.csv_service import read_csv, write_csv, get_next_id, find_by_id

FILE = "jugadores.csv"
FIELDS = ["id", "nombre", "pais", "posicion", "numero_camiseta", "edad", "foto_url", "estado"]


def _row_to_jugador(row: dict) -> Jugador:
    return Jugador(
        id=int(row["id"]),
        nombre=row["nombre"],
        pais=row["pais"],
        posicion=row["posicion"],
        numero_camiseta=int(row["numero_camiseta"]),
        edad=int(row["edad"]),
        foto_url=row.get("foto_url") or None,
        estado=row["estado"],
    )


# ─── CREATE ──────────────────────────────────────────────────────────────────

def crear_jugador(data: JugadorCreate) -> Jugador:
    # Regla de negocio: no puede haber dos jugadores con mismo número y mismo país
    registros = read_csv(FILE)
    for r in registros:
        if (r["pais"].lower() == data.pais.lower()
                and r["numero_camiseta"] == str(data.numero_camiseta)
                and r["estado"] == "activo"):
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un jugador activo de {data.pais} con la camiseta #{data.numero_camiseta}.",
            )

    nuevo_id = get_next_id(FILE)
    jugador = Jugador(id=nuevo_id, **data.model_dump(), estado=EstadoEnum.activo)
    registros.append(jugador.model_dump(mode='json'))
    write_csv(FILE, registros, FIELDS)
    return jugador


# ─── READ ─────────────────────────────────────────────────────────────────────

def obtener_jugadores(solo_activos: bool = True) -> List[Jugador]:
    registros = read_csv(FILE)
    if solo_activos:
        registros = [r for r in registros if r["estado"] == "activo"]
    return [_row_to_jugador(r) for r in registros]


def obtener_jugador_por_id(jugador_id: int) -> Jugador:
    row = find_by_id(FILE, jugador_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Jugador con ID {jugador_id} no encontrado.")
    return _row_to_jugador(row)


def buscar_por_nombre(nombre: str) -> List[Jugador]:
    """Búsqueda parcial e insensible a mayúsculas por nombre."""
    registros = read_csv(FILE)
    coincidencias = [
        r for r in registros
        if nombre.lower() in r["nombre"].lower() and r["estado"] == "activo"
    ]
    return [_row_to_jugador(r) for r in coincidencias]


def filtrar_jugadores(pais: Optional[str] = None, posicion: Optional[PosicionEnum] = None) -> List[Jugador]:
    registros = read_csv(FILE)
    resultado = [r for r in registros if r["estado"] == "activo"]
    if pais:
        resultado = [r for r in resultado if r["pais"].lower() == pais.lower()]
    if posicion:
        resultado = [r for r in resultado if r["posicion"] == posicion.value]
    return [_row_to_jugador(r) for r in resultado]


# ─── UPDATE ───────────────────────────────────────────────────────────────────

def actualizar_jugador(jugador_id: int, data: JugadorUpdate) -> Jugador:
    registros = read_csv(FILE)
    encontrado = False

    for i, r in enumerate(registros):
        if r["id"] == str(jugador_id):
            if r["estado"] == "inactivo":
                raise HTTPException(status_code=400, detail="No se puede actualizar un jugador inactivo.")
            cambios = {k: v for k, v in data.model_dump(mode='json').items() if v is not None}
            registros[i].update(cambios)
            encontrado = True
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"Jugador con ID {jugador_id} no encontrado.")

    write_csv(FILE, registros, FIELDS)
    return _row_to_jugador(registros[next(i for i, r in enumerate(registros) if r["id"] == str(jugador_id))])


# ─── DELETE (soft) ────────────────────────────────────────────────────────────

def eliminar_jugador(jugador_id: int) -> dict:
    """
    Eliminación lógica: cambia estado a 'inactivo'.
    Regla de negocio: no se puede eliminar si tiene láminas activas asociadas.
    """
    from services.lamina_service import tiene_laminas_activas

    registros = read_csv(FILE)
    encontrado = False

    for i, r in enumerate(registros):
        if r["id"] == str(jugador_id):
            if r["estado"] == "inactivo":
                raise HTTPException(status_code=400, detail="El jugador ya está inactivo.")
            # Regla de negocio: verificar láminas asociadas
            if tiene_laminas_activas(jugador_id):
                raise HTTPException(
                    status_code=400,
                    detail="No se puede desactivar el jugador porque tiene láminas activas asociadas. "
                           "Primero elimine o desactive dichas láminas.",
                )
            registros[i]["estado"] = "inactivo"
            encontrado = True
            break

    if not encontrado:
        raise HTTPException(status_code=404, detail=f"Jugador con ID {jugador_id} no encontrado.")

    write_csv(FILE, registros, FIELDS)
    return {"mensaje": f"Jugador {jugador_id} desactivado correctamente. El registro se conserva en el historial."}
