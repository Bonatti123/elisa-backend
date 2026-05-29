# ELOMUX Backend — Contexto para opencode

## Proyecto
Backend ELISA (Django + PostgreSQL). Autenticación JWT, módulos: clients, suppliers, alerts.

## Estándar de Git (ELOMUX)
- Rama: `type/scope-RFXX` (type/scope en inglés, ej: `chore/settings-RF38`)
- Commit: uno por subtarea, formato `type(scope): descripción imperativo`
- PR: solo cuando todas las subtareas están listas, título `[TIPO] scope: Nombre — RF-XX`
- **PROHIBIDO** push directo a `main` o `develop`. Solo vía PR aprobado.
- Siempre `git pull` antes de empezar y antes de `git push`

## Estado actual — Resumen

### Rama `feat/clients-RF01` — Módulo CRM Clientes ✅ COMPLETO
14 commits, subido a GitHub.

| Commit | Refs | Endpoint |
|--------|------|----------|
| `modelo Client con datos personales, plan, estado, precios...` | T01 | Modelos WebType, WebFeature, Client + migración 0002 |
| `eliminación lógica de cliente` | T02 | `DELETE /api/v1/clients/{id}` soft-delete |
| `alta de cliente con validaciones, tipo de web, precios...` | T04 | `POST /api/v1/clients/` con CUPE automático |
| `validar unicidad y formato de email al crear cliente` | T03 | EmailStr + validación de email único |
| `listado de clientes con filtros y paginación` | T05 | `GET /api/v1/clients/` con filtros |
| `detalle de cliente con respuesta completa` | T06 | `GET /api/v1/clients/{id}` |
| `edición de cliente con actualización controlada y recálculo` | T07 | `PUT /api/v1/clients/{id}` con recálculo |
| `baja lógica de cliente y comentarios en español` | T08 | Comentarios en español en todos los archivos |
| `búsqueda avanzada de clientes con ordenamiento` | T09 | Ordenamiento dinámico en listado |
| `auditoría de cliente con bitácora de cambios críticos` | T10 | Modelo AuditLog + migración 0003 |
| `historial de cambios del cliente con bitácora de auditoría` | T11 | `GET /api/v1/clients/{id}/history` |
| `solicitar cambio sensible con aprobación` | T12 | ChangeRequest + aprobar/rechazar |
| `agregar TypedDicts y type hints a funciones del router` | — | HistoryEntry, ChangeRequestEntry + type hints |

**Pendiente:** —|

---

### Rama `feat/promotions-RF17` — Módulo Promociones y Campañas ✅
6 commits, subido a GitHub.

| Commit | Refs | Detalle |
|--------|------|---------|
| `crear motor de promociones con PromotionsEngine` | T01 | `api/utils/promotions_engine.py` |
| `crear esquemas de validación DTO` | T02 | `api/schemas/promotions.py` |
| `crear router REST con CRUD y endpoint evaluate` | T03 | `api/routers/promotions.py` |
| `registrar módulo de promociones` | T04 | `api/main.py` |
| `agregar applies_to y benefit_description a promociones` | T06 | Campos adicionales en promociones |
| `agregar comentarios en español a todo el módulo` | T05 | Comentarios en engine, schemas, router |

**Pendiente:** PR #1 abierto — pendiente de revisión y merge a develop.

---

### Rama `feat/accounting-RF14` — Módulo Contabilidad ✅ COMPLETO
2 commits, subido a GitHub.

| Commit | Refs | Detalle |
|--------|------|---------|
| `contabilidad con compras, ventas y resumen financiero` | T01-T06 | Modelos Purchase/Sale, schemas, router CRUD + financial-summary |
| `crear carpeta docs con contratos, modelos, reglas y glosario` | — | `docs/01-API_CONTRACTS.md`, `02-DATA_MODELS.md`, `03-BUSINESS_RULES.md`, `GLOSSARY.md` |

**Endpoints Accounting (`/api/v1/accounting`):**
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/purchases/` | JWT (staff) | Lista compras con filtros |
| POST | `/purchases/` | JWT (staff) | Crear compra |
| GET | `/purchases/{id}` | JWT (staff) | Detalle compra |
| PUT | `/purchases/{id}` | JWT (staff) | Editar compra |
| DELETE | `/purchases/{id}` | JWT (staff) | Baja lógica |
| GET | `/sales/` | JWT (staff) | Lista ventas con filtros |
| POST | `/sales/` | JWT (staff) | Crear venta |
| GET | `/sales/{id}` | JWT (staff) | Detalle venta |
| PUT | `/sales/{id}` | JWT (staff) | Editar venta |
| DELETE | `/sales/{id}` | JWT (staff) | Baja lógica |
| GET | `/financial-summary` | JWT (staff) | Balance por período |

---

### Rama `docs/quality-code` — Colaboradores API
Se creó el módulo Colaboradores con endpoint `GET /api/v1/users`.

| Archivo | Acción |
|---------|--------|
| `clients/models.py` | Agregado modelo `Collaborator` |
| `api/schemas/users.py` | Creado `CollaboratorResponse` |
| `api/routers/users.py` | Creado endpoint `GET /users/` con role check |
| `api/main.py` | Importado y registrado `users.router` |

---

### Rama `docs/quality-code` — Registro de Web Types y Web Features
Se registraron los routers de `web_types` y `web_features`.

---

## Endpoints disponibles

### Auth (`/api/v1/auth`)
| Método | Endpoint | Auth |
|--------|----------|------|
| POST | `/login` | — |
| POST | `/refresh` | — |
| GET | `/me` | JWT |

### Clientes (`/api/v1/clients`)
| Método | Endpoint | Auth |
|--------|----------|------|
| GET | `/` | JWT |
| POST | `/` | JWT |
| GET | `/{id}` | JWT |
| PUT | `/{id}` | JWT |
| DELETE | `/{id}` | JWT |
| GET | `/{id}/history` | JWT |
| GET | `/{id}/change-requests` | JWT |
| POST | `/{id}/change-requests` | JWT |
| PATCH | `/change-requests/{id}` | JWT (staff) |

### Accounting (`/api/v1/accounting`)
| Método | Endpoint | Auth |
|--------|----------|------|
| GET | `/purchases/` | JWT (staff) |
| POST | `/purchases/` | JWT (staff) |
| GET | `/purchases/{id}` | JWT (staff) |
| PUT | `/purchases/{id}` | JWT (staff) |
| DELETE | `/purchases/{id}` | JWT (staff) |
| GET | `/sales/` | JWT (staff) |
| POST | `/sales/` | JWT (staff) |
| GET | `/sales/{id}` | JWT (staff) |
| PUT | `/sales/{id}` | JWT (staff) |
| DELETE | `/sales/{id}` | JWT (staff) |
| GET | `/financial-summary` | JWT (staff) |

### Promociones (`/api/v1`)
| Método | Endpoint | Auth |
|--------|----------|------|
| GET | `/promotions/` | — |
| GET | `/promotions/{id}` | — |
| POST | `/promotions/` | JWT (superadmin) |
| PUT | `/promotions/{id}` | JWT (superadmin) |
| DELETE | `/promotions/{id}` | JWT (superadmin) |
| POST | `/promotions/evaluate` | — |
| GET | `/campaigns/` | — |
| GET | `/campaigns/{id}` | — |
| POST | `/campaigns/` | JWT (superadmin) |
| PUT | `/campaigns/{id}` | JWT (superadmin) |
| DELETE | `/campaigns/{id}` | JWT (superadmin) |

## Entorno
- Python venv: `venv/bin/python`
- Django manage: `venv/bin/python manage.py`
- Variables de entorno en `.env` (no se sube)
- `DJANGO_ENV` para seleccionar settings (dev/test/prod, default: development)
- Basedpyright es el default language server
- PostgreSQL: user `elisa_user`, db `elisa_local_db`, password en `.env`

## Archivos que NO se suben a GitHub
- `.env`
- `AGENTS.md` (este archivo)
