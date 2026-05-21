import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configuración de Django ORM para usarlo desde FastAPI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from api.routers import auth, clients, web_types, web_features


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida de la aplicación."""
    yield


# Instancia principal de la API REST
app = FastAPI(
    title="ELISA API",
    description="API REST del sistema ERP ELISA - ELOMUX",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers con sus prefijos y tags
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clients"])
app.include_router(web_types.router, prefix="/api/v1/web-types", tags=["Web Types"])
app.include_router(web_features.router, prefix="/api/v1/web-features", tags=["Web Features"])


@app.get("/api/v1/health")
def health():
    """Endpoint de verificación de salud del servicio."""
    return {"status": "ok", "version": "1.0.0"}
