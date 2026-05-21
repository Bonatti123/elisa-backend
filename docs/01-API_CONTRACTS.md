# Contratos de la API REST

## Base URL
```
http://localhost:8001/api/v1
```

## Autenticación
Todas las rutas protegidas requieren header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Auth
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/auth/login` | — | Iniciar sesión |
| POST | `/auth/refresh` | — | Renovar token |
| GET | `/auth/me` | JWT | Perfil del usuario |

### Clientes
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/clients/` | JWT | Listar clientes (filtros + paginación) |
| POST | `/clients/` | JWT (L1-L4) | Crear cliente |
| GET | `/clients/{id}` | JWT | Detalle de cliente |
| PUT | `/clients/{id}` | JWT (L1-L4) | Actualizar cliente |
| DELETE | `/clients/{id}` | JWT (L1-L4) | Baja lógica de cliente |
| GET | `/clients/{id}/history` | JWT | Historial de auditoría |
| GET | `/clients/{id}/change-requests` | JWT | Solicitudes de cambio |
| POST | `/clients/{id}/change-requests` | JWT | Crear solicitud de cambio |
| PATCH | `/change-requests/{id}` | JWT (staff) | Revisar solicitud |

### Catálogos
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/web-types/` | JWT | Tipos de web |
| POST | `/web-types/` | JWT (staff) | Crear tipo de web |
| PUT | `/web-types/{id}` | JWT (staff) | Actualizar tipo de web |
| GET | `/web-features/` | JWT | Funcionalidades extra |
| POST | `/web-features/` | JWT (staff) | Crear funcionalidad |
| PUT | `/web-features/{id}` | JWT (staff) | Actualizar funcionalidad |

### Salud
| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | — | Estado del servicio |
