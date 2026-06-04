from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import auth as auth_router, marketplace
from routers import home as home_router
from routers import album as album_router
from routers import repetidas as repetidas_router
from routers import marketplace as marketplace_router

app = FastAPI(
    title="🌍 Álbum Mundial 2026",
    description="Gestiona tu álbum de láminas del Mundial FIFA 2026",
    version="2.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router)
app.include_router(home_router.router)
app.include_router(album_router.router)
app.include_router(repetidas_router.router)
app.include_router(marketplace_router.router)