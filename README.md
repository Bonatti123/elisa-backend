# ELISA Backend

Backend del sistema ERP ELISA — ELOMUX.

## Requisitos previos

- Python 3.14 o superior
- PostgreSQL 16+
- `venv` (incluido con Python)

## Estructura del proyecto

```plaintext
elisa-backend/
├── api/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── routers/             # Endpoints REST
│   ├── schemas/             # Esquemas Pydantic
│   └── utils/               # Utilidades
├── clients/                 # App Django: Clientes, Usuarios, Roles
├── core/                    # Configuración Django (settings, urls)
├── docs/                    # Documentación técnica
├── suppliers/               # App Django: Proveedores
├── alerts/                  # App Django: Alertas
├── manage.py                # CLI de Django
├── start.sh                 # Script de inicio
└── requirements.txt         # Dependencias
```

## Variables de entorno

```plaintext
SECRET_KEY=mi-clave-local-elisa-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=postgresql
DB_NAME=elisa_local_db
DB_USER=elisa_user
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

PLAN_RENEWAL_DAYS_RENT=30
PLAN_RENEWAL_DAYS_SALE=365
```
