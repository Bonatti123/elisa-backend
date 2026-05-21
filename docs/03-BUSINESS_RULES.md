# Reglas de Negocio

## Generación de CUPE
- Se asigna automáticamente al crear un cliente.
- Formato: `ELO-XXXXX` (número correlativo de 5 dígitos).
- Se basa en el último cliente creado ordenado por `created_at`.

## Cálculo de Precios
- `base_price` se obtiene del `WebType` según el `plan` (alquiler → `base_price_rent`, venta → `base_price_sale`).
- `extra_price` es la suma de todos los `WebFeature` asociados al cliente.
- `total_price` = `base_price` + `extra_price`.
- Se recalcula automáticamente en `Client.save()` y `update_prices()`.

## Transición de Estados
- Al registrar `delivery_date`, si el cliente está en estado `desarrollo`, pasa automáticamente a `activo`.
- Al dar de baja (DELETE), el cliente pasa a `inactivo` con `is_active=False`.

## Renovación y Próximo Pago
- `next_payment_date` se calcula desde `delivery_date`:
  - Frecuencia mensual: `delivery_date + PLAN_RENEWAL_DAYS_RENT` días.
  - Frecuencia anual: `delivery_date + PLAN_RENEWAL_DAYS_SALE` días.
- Los días de renovación se configuran por variable de entorno.

## Control de Acceso (RBAC)
- Roles de escritura: L1, L2, L3, L4.
- Staff y superusuarios tienen acceso completo.
- Usuarios sin rol o con rol no autorizado no pueden crear, editar ni eliminar clientes.
- Las solicitudes de cambio solo pueden ser revisadas por staff.

## Auditoría
- Cada creación, actualización y eliminación de cliente se registra en `AuditLog`.
- Los cambios sensibles requieren aprobación mediante `ChangeRequest`.

## Validaciones de Datos
- `document_type`: solo DNI o RUC.
- `plan`: solo alquiler o venta.
- `payment_frequency`: solo mensual o anual.
- `status`: solo desarrollo, activo o inactivo.
- Email debe ser único y con formato válido.
- Documento debe ser único en el sistema.
