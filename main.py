from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import jugadores_router, laminas_router, intercambios_router

app = FastAPI(
    title="🌍 Álbum Mundial 2026 - API",
    description=(
        "Sistema para gestionar el álbum de láminas del Mundial 2026. "
        "Controla las láminas que tienes, las que te faltan y las repetidas, "
        "e intercámbialas o véndelas en el marketplace."
    ),
    version="1.0.0",
)

# ─── Manejo global de excepciones ─────────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content={"detail": f"Error de validación: {str(exc)}"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Por favor intente de nuevo."},
    )


# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(jugadores_router)
app.include_router(laminas_router)
app.include_router(intercambios_router)


# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {
        "proyecto": "Álbum Mundial 2026",
        "version": "1.0.0",
        "descripcion": "API para gestionar láminas del álbum del Mundial FIFA 2026",
        "docs": "/docs",
        "modelos": ["Jugadores", "Láminas", "Intercambios"],
    }
