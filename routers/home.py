from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user_optional
from models.seleccion import Seleccion
from models.jugador import Jugador
from models.lamina_album import LaminaAlbum

router = APIRouter(tags=["Home"])
templates = Jinja2Templates(directory="templates")


@router.get("/home", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    selecciones = db.query(Seleccion).filter(Seleccion.activo == True).order_by(Seleccion.nombre).all()

    # Estadísticas generales del usuario
    total_jugadores = db.query(Jugador).filter(Jugador.activo == True).count()
    tengo = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.tengo == True
    ).count()

    progreso = round((tengo / total_jugadores * 100), 1) if total_jugadores > 0 else 0

    return templates.TemplateResponse(request=request, name="home.html", context={
        "user": user,
        "selecciones": selecciones,
        "total_jugadores": total_jugadores,
        "tengo": tengo,
        "faltantes": total_jugadores - tengo,
        "progreso": progreso,
    })


@router.get("/buscar", response_class=HTMLResponse)
def buscar(request: Request, q: str = "", db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    jugadores = []
    if q:
        jugadores = db.query(Jugador).join(Jugador.seleccion).filter(
            Jugador.nombre.ilike(f"%{q}%"),
            Jugador.activo == True
        ).all()

    return templates.TemplateResponse(request=request, name="buscar.html", context={
        "user": user,
        "jugadores": jugadores,
        "query": q,
    })