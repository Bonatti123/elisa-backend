# Modelos de Datos

## User
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID (PK) | Identificador único |
| username | VARCHAR(150) | Nombre de usuario (único) |
| email | EmailField | Correo electrónico |
| first_name | VARCHAR(150) | Nombres |
| last_name | VARCHAR(150) | Apellidos |
| role | FK → Role | Rol del usuario |
| is_active | Boolean | Usuario activo |
| is_staff | Boolean | Acceso a staff |
| password | VARCHAR | Hash de contraseña |

## Role
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID (PK) | Identificador único |
| name | VARCHAR(100) | Nombre del rol (único) |
| description | Text | Descripción |
| permissions | JSON | Permisos del rol |
| is_active | Boolean | Rol activo |

## Client
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID (PK) | Identificador único |
| cupe | VARCHAR(50) | Código único ELO-XXXXX |
| name | VARCHAR(255) | Nombre o razón social |
| document_type | VARCHAR(20) | DNI o RUC |
| document_number | VARCHAR(50) | Número de documento (único) |
| email | EmailField | Correo electrónico |
| phone | VARCHAR(50) | Teléfono |
| web_type | FK → WebType | Tipo de web contratado |
| features | M2M → WebFeature | Funcionalidades extra |
| plan | VARCHAR(20) | alquiler / venta |
| status | VARCHAR(20) | desarrollo / activo / inactivo |
| base_price | Decimal(10,2) | Precio base del plan |
| extra_price | Decimal(10,2) | Suma de funcionalidades |
| total_price | Decimal(10,2) | Base + extra |
| initial_payment | Decimal(10,2) | Pago inicial |
| domain_price | Decimal(10,2) | Precio del dominio |
| payment_frequency | VARCHAR(20) | mensual / anual |
| registration_date | Date | Fecha de registro |
| delivery_date | Date | Fecha de entrega |
| next_payment_date | Date | Próximo pago |
| notes | Text | Notas internas |
| created_by | FK → User | Usuario que creó |
| is_active | Boolean | Soft delete |
| created_at | DateTime | Fecha de creación |
| updated_at | DateTime | Última modificación |

## WebType
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID (PK) | Identificador único |
| name | VARCHAR(255) | Nombre (único) |
| base_price_rent | Decimal(10,2) | Precio base alquiler |
| base_price_sale | Decimal(10,2) | Precio base venta |
| is_active | Boolean | Activo |

## WebFeature
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID (PK) | Identificador único |
| name | VARCHAR(255) | Nombre (único) |
| extra_price | Decimal(10,2) | Precio extra |
| is_active | Boolean | Activo |

## AuditLog
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID (PK) | Identificador único |
| usuario | FK → User | Usuario que realizó la acción |
| accion | VARCHAR(20) | creacion / actualizacion / eliminacion |
| modulo | VARCHAR(50) | Módulo afectado |
| registro_id | VARCHAR(100) | ID del registro afectado |
| detalle | JSON | Cambios realizados |
| ip | GenericIPAddressField | Dirección IP |
| created_at | DateTime | Fecha del registro |

## ChangeRequest
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID (PK) | Identificador único |
| cliente | FK → Client | Cliente relacionado |
| campo | VARCHAR(100) | Campo solicitado a cambiar |
| valor_anterior | JSON | Valor antes del cambio |
| valor_nuevo | JSON | Valor solicitado |
| motivo | Text | Motivo del cambio |
| estado | VARCHAR(20) | pendiente / aprobado / rechazado |
| solicitado_por | FK → User | Quién solicitó |
| revisado_por | FK → User | Quién revisó |
| created_at | DateTime | Fecha de solicitud |
| updated_at | DateTime | Última actualización |
