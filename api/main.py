import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from api.routers import auth, suppliers, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="ELISA API",
    description="API REST del sistema ERP ELISA - ELOMUX",
    version="1.0.0",
    lifespan=lifespan,
)

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

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(suppliers.router, prefix="/api/v1/suppliers", tags=["Proveedores"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alertas"])


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
