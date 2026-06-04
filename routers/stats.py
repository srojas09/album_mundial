from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth import get_current_user_optional
from models.jugador import Jugador
from models.lamina_album import LaminaAlbum
from models.seleccion import Seleccion
from models.publicacion import Publicacion

router = APIRouter(tags=["Estadísticas"])
templates = Jinja2Templates(directory="templates")


@router.get("/stats", response_class=HTMLResponse)
def estadisticas(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Estadísticas generales
    total_jugadores = db.query(Jugador).filter(Jugador.activo == True).count()
    mis_laminas = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.tengo == True
    ).count()
    mis_repetidas = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.cantidad_repetidas > 0
    ).count()
    mis_publicaciones = db.query(Publicacion).filter(
        Publicacion.usuario_id == user.id,
        Publicacion.estado == "disponible"
    ).count()
    mis_ventas = db.query(Publicacion).filter(
        Publicacion.usuario_id == user.id,
        Publicacion.estado == "vendida"
    ).count()

    # Progreso por selección
    selecciones = db.query(Seleccion).filter(Seleccion.activo == True).all()
    progreso_selecciones = []
    for s in selecciones:
        total_s = db.query(Jugador).filter(
            Jugador.seleccion_id == s.id,
            Jugador.activo == True
        ).count()
        if total_s == 0:
            continue
        tengo_s = db.query(LaminaAlbum).join(Jugador).filter(
            LaminaAlbum.usuario_id == user.id,
            LaminaAlbum.tengo == True,
            Jugador.seleccion_id == s.id
        ).count()
        progreso_selecciones.append({
            "nombre": s.nombre,
            "logo": s.logo_url,
            "total": total_s,
            "tengo": tengo_s,
            "porcentaje": round((tengo_s / total_s) * 100, 1)
        })

    # Ordenar por porcentaje descendente
    progreso_selecciones.sort(key=lambda x: x["porcentaje"], reverse=True)

    # Distribución por posición
    posiciones = ["Portero", "Defensa", "Mediocampista", "Delantero"]
    dist_posiciones = []
    for pos in posiciones:
        total_pos = db.query(Jugador).filter(
            Jugador.posicion == pos,
            Jugador.activo == True
        ).count()
        tengo_pos = db.query(LaminaAlbum).join(Jugador).filter(
            LaminaAlbum.usuario_id == user.id,
            LaminaAlbum.tengo == True,
            Jugador.posicion == pos
        ).count()
        dist_posiciones.append({
            "posicion": pos,
            "total": total_pos,
            "tengo": tengo_pos
        })

    return templates.TemplateResponse(request=request, name="stats.html", context={
        "user": user,
        "total_jugadores": total_jugadores,
        "mis_laminas": mis_laminas,
        "faltantes": total_jugadores - mis_laminas,
        "progreso": round((mis_laminas / total_jugadores * 100), 1) if total_jugadores > 0 else 0,
        "mis_repetidas": mis_repetidas,
        "mis_publicaciones": mis_publicaciones,
        "mis_ventas": mis_ventas,
        "progreso_selecciones": progreso_selecciones,
        "dist_posiciones": dist_posiciones,
    })