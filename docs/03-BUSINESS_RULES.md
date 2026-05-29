# Reglas de Negocio

## Generales
- Ningún registro se elimina físicamente. Todos usan soft delete (`is_active=False`).
- Todos los endpoints de escritura requieren autenticación JWT.
- Los tokens JWT tienen expiración configurable (default: 30 min access, 24 h refresh).

## Contabilidad
- `amount` debe ser mayor a 0 en compras y ventas.
- El resumen financiero calcula `balance = total_sales - total_purchases`.
- Los filtros de fecha son obligatorios en el resumen financiero.

## Roles y Permisos
- Solo usuarios con `is_staff=True` pueden acceder a endpoints administrativos.
