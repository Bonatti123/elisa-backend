import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Django ORM configuration for FastAPI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from api.routers import auth, clients


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    yield


# Main REST API instance
app = FastAPI(
    title="ELISA API",
    description="API REST del sistema ERP ELISA - ELOMUX",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware — allows frontend requests from allowed origins
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

# Router registration
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clients"])


@app.get("/")
def root():
    """Root endpoint for monitoring and health check."""
    return {
        "status": "ok",
        "service": "ELISA API",
        "version": "1.0.0",
    }


@app.get("/api/v1/health")
def health():
    """Health check endpoint (legacy)."""
    return {"status": "ok", "version": "1.0.0"}
