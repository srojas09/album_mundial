from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user_optional
from models.publicacion import Publicacion
from models.jugador import Jugador
from models.lamina_album import LaminaAlbum

router = APIRouter(tags=["Marketplace"])
templates = Jinja2Templates(directory="templates")


@router.get("/marketplace", response_class=HTMLResponse)
def marketplace(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    publicaciones = db.query(Publicacion).filter(
        Publicacion.estado == "disponible",
        Publicacion.activo == True
    ).order_by(Publicacion.fecha_publicacion.desc()).all()

    return templates.TemplateResponse(request=request, name="marketplace.html", context={
        "user": user,
        "publicaciones": publicaciones,
        "total": len(publicaciones),
    })


@router.get("/marketplace/publicar", response_class=HTMLResponse)
def publicar_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    repetidas = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.tengo == True,
        LaminaAlbum.cantidad_repetidas > 0
    ).all()

    return templates.TemplateResponse(request=request, name="publicar.html", context={
        "user": user,
        "repetidas": repetidas,
    })


@router.post("/marketplace/publicar")
def publicar(
    request: Request,
    jugador_id: int = Form(...),
    precio: float = Form(...),
    descripcion: str = Form(None),
    db: Session = Depends(get_db)
):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Regla: verificar que tiene la lámina repetida
    lamina = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.jugador_id == jugador_id,
        LaminaAlbum.tengo == True,
        LaminaAlbum.cantidad_repetidas > 0
    ).first()

    if not lamina:
        return RedirectResponse(url="/marketplace/publicar?error=1", status_code=302)

    # Regla: no duplicar publicación activa del mismo jugador
    existente = db.query(Publicacion).filter(
        Publicacion.usuario_id == user.id,
        Publicacion.jugador_id == jugador_id,
        Publicacion.estado == "disponible"
    ).first()

    if existente:
        return RedirectResponse(url="/marketplace/publicar?error=2", status_code=302)

    publicacion = Publicacion(
        usuario_id=user.id,
        jugador_id=jugador_id,
        precio=precio,
        descripcion=descripcion,
        estado="disponible",
        activo=True
    )
    db.add(publicacion)
    db.commit()
    return RedirectResponse(url="/marketplace", status_code=302)


@router.post("/marketplace/cancelar/{publicacion_id}")
def cancelar_publicacion(
    publicacion_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    pub = db.query(Publicacion).filter(
        Publicacion.id == publicacion_id,
        Publicacion.usuario_id == user.id
    ).first()

    if pub:
        pub.estado = "cancelada"
        pub.activo = False
        db.commit()

    return RedirectResponse(url="/marketplace", status_code=302)


@router.get("/mis-publicaciones", response_class=HTMLResponse)
def mis_publicaciones(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    publicaciones = db.query(Publicacion).filter(
        Publicacion.usuario_id == user.id
    ).order_by(Publicacion.fecha_publicacion.desc()).all()

    return templates.TemplateResponse(request=request, name="mis_publicaciones.html", context={
        "user": user,
        "publicaciones": publicaciones,
    })
@router.get("/marketplace/comprar/{publicacion_id}", response_class=HTMLResponse)
def confirmar_compra(publicacion_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    pub = db.query(Publicacion).filter(
        Publicacion.id == publicacion_id,
        Publicacion.estado == "disponible",
        Publicacion.activo == True
    ).first()

    if not pub:
        return RedirectResponse(url="/marketplace", status_code=302)

    # No puede comprarse su propia publicacion
    if pub.usuario_id == user.id:
        return RedirectResponse(url="/marketplace", status_code=302)

    return templates.TemplateResponse(request=request, name="confirmar_compra.html", context={
        "user": user,
        "pub": pub,
    })


@router.post("/marketplace/comprar/{publicacion_id}")
def realizar_compra(publicacion_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    pub = db.query(Publicacion).filter(
        Publicacion.id == publicacion_id,
        Publicacion.estado == "disponible",
        Publicacion.activo == True
    ).first()

    if not pub or pub.usuario_id == user.id:
        return RedirectResponse(url="/marketplace", status_code=302)

    # Cambiar estado de la publicacion a vendida
    pub.estado = "vendida"
    pub.activo = False

    # Agregar la lamina al album del comprador si no la tiene
    lamina = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == user.id,
        LaminaAlbum.jugador_id == pub.jugador_id
    ).first()

    if lamina:
        lamina.tengo = True
    else:
        lamina = LaminaAlbum(
            usuario_id=user.id,
            jugador_id=pub.jugador_id,
            tengo=True,
            cantidad_repetidas=0
        )
        db.add(lamina)

    # Reducir repetidas del vendedor
    lamina_vendedor = db.query(LaminaAlbum).filter(
        LaminaAlbum.usuario_id == pub.usuario_id,
        LaminaAlbum.jugador_id == pub.jugador_id
    ).first()

    if lamina_vendedor and lamina_vendedor.cantidad_repetidas > 0:
        lamina_vendedor.cantidad_repetidas -= 1

    db.commit()
    return RedirectResponse(url="/marketplace?compra=exitosa", status_code=302)