from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user_optional
from models.jugador import Jugador
from models.lamina_album import LaminaAlbum

router = APIRouter(tags=["Repetidas"])
templates = Jinja2Templates(directory="templates")


@router.get("/repetidas", response_class=HTMLResponse)
def mis_repetidas(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    repetidas = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.tengo == True,
        LaminaAlbum.cantidad_repetidas > 0
    ).all()

    return templates.TemplateResponse(request=request, name="repetidas.html", context={
        "user": user,
        "repetidas": repetidas,
        "total": len(repetidas),
    })


@router.post("/repetidas/actualizar/{jugador_id}")
def actualizar_repetidas(
    jugador_id: int,
    request: Request,
    cantidad: int = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    lamina = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.jugador_id == jugador_id
    ).first()

    if lamina:
        lamina.cantidad_repetidas = max(0, cantidad)
        db.commit()

    return RedirectResponse(url="/repetidas", status_code=302)


@router.get("/repetidas/agregar", response_class=HTMLResponse)
def agregar_repetidas_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Jugadores que tengo en el album
    mis_laminas = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.tengo == True
    ).all()

    return templates.TemplateResponse(request=request, name="agregar_repetidas.html", context={
        "user": user,
        "mis_laminas": mis_laminas,
    })