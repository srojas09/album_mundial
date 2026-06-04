from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user_optional
from models.seleccion import Seleccion
from models.jugador import Jugador
from models.lamina_album import LaminaAlbum

router = APIRouter(tags=["Álbum"])
templates = Jinja2Templates(directory="templates")


@router.get("/album", response_class=HTMLResponse)
def mi_album(request: Request, seleccion_id: int = None, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    selecciones = db.query(Seleccion).filter(Seleccion.activo == True).order_by(Seleccion.nombre).all()

    query = db.query(Jugador).filter(Jugador.activo == True)
    if seleccion_id:
        query = query.filter(Jugador.seleccion_id == seleccion_id)
    jugadores = query.order_by(Jugador.nombre).all()

    # Obtener láminas del usuario
    laminas = db.query(LaminaAlbum).filter(LaminaAlbum.usuario_id == user.id).all()
    laminas_map = {l.jugador_id: l for l in laminas}

    total = len(jugadores)
    tengo = sum(1 for j in jugadores if laminas_map.get(j.id) and laminas_map[j.id].tengo)

    return templates.TemplateResponse(request=request, name="album.html", context={
        "user": user,
        "jugadores": jugadores,
        "laminas_map": laminas_map,
        "selecciones": selecciones,
        "seleccion_id": seleccion_id,
        "total": total,
        "tengo": tengo,
        "faltantes": total - tengo,
        "progreso": round((tengo / total * 100), 1) if total > 0 else 0,
    })


@router.post("/album/toggle/{jugador_id}")
def toggle_lamina(jugador_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    lamina = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.jugador_id == jugador_id
    ).first()

    if lamina:
        lamina.tengo = not lamina.tengo
        if not lamina.tengo:
            lamina.cantidad_repetidas = 0
    else:
        lamina = LaminaAlbum(
            usuario_id=user.id,
            jugador_id=jugador_id,
            tengo=True,
            cantidad_repetidas=0
        )
        db.add(lamina)

    db.commit()
    referer = request.headers.get("referer", "/album")
    return RedirectResponse(url=referer, status_code=302)


@router.get("/seleccion/{seleccion_id}", response_class=HTMLResponse)
def ver_seleccion(seleccion_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return RedirectResponse(url=f"/album?seleccion_id={seleccion_id}", status_code=302)