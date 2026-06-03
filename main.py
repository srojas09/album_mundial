from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import auth as auth_router

app = FastAPI(
    title="🌍 Álbum Mundial 2026",
    description="Gestiona tu álbum de láminas del Mundial FIFA 2026",
    version="2.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router)