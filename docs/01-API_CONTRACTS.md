# Contratos de API

## Autenticación — `/api/v1/auth`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/login` | — | Iniciar sesión |
| POST | `/refresh` | — | Refrescar token |
| GET | `/me` | JWT | Usuario actual |

## Contabilidad — `/api/v1/accounting`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/purchases/` | JWT | Listar compras |
| POST | `/purchases/` | JWT | Crear compra |
| GET | `/purchases/{id}` | JWT | Detalle de compra |
| PUT | `/purchases/{id}` | JWT | Editar compra |
| DELETE | `/purchases/{id}` | JWT | Eliminar compra |
| GET | `/sales/` | JWT | Listar ventas |
| POST | `/sales/` | JWT | Crear venta |
| GET | `/sales/{id}` | JWT | Detalle de venta |
| PUT | `/sales/{id}` | JWT | Editar venta |
| DELETE | `/sales/{id}` | JWT | Eliminar venta |
| GET | `/financial-summary` | JWT | Resumen financiero |

## Health — `/api/v1`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | — | Estado de la API |
