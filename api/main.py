import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.core.wsgi import get_wsgi_application
from api.routers import auth, suppliers, alerts, renewals


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
app.include_router(renewals.router, prefix="/api/v1/renewals", tags=["Renovaciones"])

# Sirve archivos estáticos de Django (admin CSS/JS)
static_dir = Path(__file__).resolve().parent.parent / "staticfiles"
if static_dir.exists():
    app.mount("/admin/static", StaticFiles(directory=str(static_dir)), name="static")

# Monta el admin de Django bajo /admin
django_app = get_wsgi_application()
app.mount("/admin", WSGIMiddleware(django_app))


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
