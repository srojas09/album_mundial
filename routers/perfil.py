from fastapi import APIRouter, Depends, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user_optional
from models.usuario import Usuario
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

router = APIRouter(tags=["Perfil"])
templates = Jinja2Templates(directory="templates")


@router.get("/perfil", response_class=HTMLResponse)
def ver_perfil(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(request=request, name="perfil.html", context={
        "user": user,
    })


@router.post("/perfil/foto")
async def subir_foto(
    request: Request,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Validaciones
    if foto.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        return templates.TemplateResponse(request=request, name="perfil.html", context={
            "user": user,
            "error": "Solo se permiten imágenes JPG, PNG o WEBP."
        })

    contenido = await foto.read()
    if len(contenido) > 5 * 1024 * 1024:
        return templates.TemplateResponse(request=request, name="perfil.html", context={
            "user": user,
            "error": "La imagen no puede superar los 5MB."
        })

    # Subir a Cloudinary
    resultado = cloudinary.uploader.upload(
        contenido,
        folder="album_mundial/perfiles",
        public_id=f"usuario_{user.id}",
        overwrite=True,
        transformation=[
            {"width": 400, "height": 400, "crop": "fill", "gravity": "face"}
        ]
    )

    # Guardar URL en BD
    usuario = db.query(Usuario).filter(Usuario.id == user.id).first()
    usuario.foto_url = resultado["secure_url"]
    db.commit()

    return RedirectResponse(url="/perfil", status_code=302)