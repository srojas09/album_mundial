from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from auth import hash_password, verify_password, create_access_token

router = APIRouter(tags=["Autenticación"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/home", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email o contraseña incorrectos"
        })

    token = create_access_token({"sub": user.email})
    response = RedirectResponse(url="/home", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400
    )
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirmar_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirmar_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Las contraseñas no coinciden"
        })

    existente = db.query(Usuario).filter(Usuario.email == email).first()
    if existente:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Este email ya está registrado"
        })

    usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=hash_password(password)
    )
    db.add(usuario)
    db.commit()

    token = create_access_token({"sub": usuario.email})
    response = RedirectResponse(url="/home", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=86400
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response