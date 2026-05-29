"""Punto de entrada de la API ELISA.
Registra los routers, configura CORS y expone el health check.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from api.routers import accounting, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación. Por ahora sin tareas de inicio/cierre."""
    yield


app = FastAPI(
    title="ELISA API",
    description="API REST del sistema ERP ELISA - ELOMUX",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────
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

# ─── ROUTERS ──────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(accounting.router, prefix="/api/v1/accounting", tags=["Accounting"])


@app.get("/api/v1/health")
def health():
    """Endpoint de verificación de estado para monitoreo."""
    return {"status": "ok", "version": "1.0.0"}
