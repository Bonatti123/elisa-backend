# Contratos de API

## Autenticación — `/api/v1/auth`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/login` | — | Iniciar sesión |
| POST | `/refresh` | — | Refrescar token |
| GET | `/me` | JWT | Usuario actual |

## Contabilidad — `/api/v1/accounting`

### Compras

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/purchases/` | JWT (staff) | Listar compras con filtros |
| POST | `/purchases/` | JWT (staff) | Crear compra con auditoría |
| GET | `/purchases/{id}` | JWT (staff) | Detalle de compra |
| PUT | `/purchases/{id}` | JWT (staff) | Editar compra con bloqueo y auditoría |
| DELETE | `/purchases/{id}` | JWT (staff) | Eliminación lógica con auditoría |

### Ventas

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/sales/` | JWT (staff) | Listar ventas con filtros |
| POST | `/sales/` | JWT (staff) | Crear venta con auditoría |
| GET | `/sales/{id}` | JWT (staff) | Detalle de venta |
| PUT | `/sales/{id}` | JWT (staff) | Editar venta con bloqueo y auditoría |
| DELETE | `/sales/{id}` | JWT (staff) | Eliminación lógica con auditoría |

### Resumen Financiero

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/financial-summary` | JWT (staff) | Resumen financiero por período |

## Health — `/api/v1`

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | — | Estado de la API |

## Notas de implementación

- Todos los endpoints de escritura (POST, PUT, DELETE) están envueltos en `transaction.atomic()` para asegurar consistencia transaccional.
- Los endpoints PUT utilizan `select_for_update()` para bloqueo preventivo contra condiciones de carrera.
- Las eliminaciones son lógicas (`is_active=False`), no se eliminan registros físicamente.
- Cada mutación queda registrada en la tabla `accounting_entry_history` con captura de datos anteriores y nuevos.
- Las etiquetas `#BE###` en el código fuente vinculan cada endpoint con su regla de negocio en el SDD.
