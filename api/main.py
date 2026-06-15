import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from django.db import IntegrityError, OperationalError, DataError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from api.routers import auth
from api.exceptions import AppException
from api.schemas.errors import ErrorResponse, ValidationErrorDetail, ValidationErrorResponse


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


# ─── Manejadores globales de errores — RF-37-T01 ──────────────

@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.code,
        content=ErrorResponse(detail=exc.detail, code=exc.code, field=exc.field).model_dump(),
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(x) for x in err.get("loc", []))
        errors.append(ValidationErrorDetail(field=field, detail=err.get("msg", "Error de validación")))
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(errors=errors).model_dump(),
    )


@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(detail="Error de integridad: el registro ya existe o tiene dependencias", code=400).model_dump(),
    )


@app.exception_handler(OperationalError)
def operational_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Error en la base de datos", code=500).model_dump(),
    )


@app.exception_handler(DataError)
def data_error_handler(request: Request, exc: DataError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(detail="Dato inválido en la base de datos", code=422).model_dump(),
    )


@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Error interno del servidor", code=500).model_dump(),
    )

# ─────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
