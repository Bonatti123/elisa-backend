# API REST ELISA — Especificación para Frontend

**Base URL:** `/api/v1`
**Autenticación:** `Bearer <token>` (JWT)
**Formato:** JSON

---

## FE-01 Autenticación y sesión

### 1. Login
| | |
|---|---|
| **Método** | `POST /auth/login` |
| **Body** | `{"username": "string", "password": "string"}` |
| **Response 200** | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer"}` |
| **Errores** | `401` Credenciales inválidas, `422` Validación |
| **Estado** | ✅ Implementado |

### 2. Logout
| | |
|---|---|
| **Método** | `POST /auth/logout` |
| **Headers** | `Authorization: Bearer <token>` |
| **Response 200** | `{"message": "Sesión cerrada"}` |
| **Errores** | `401` No autenticado |
| **Estado** | ⏳ Pendiente |

### 3. Refrescar token
| | |
|---|---|
| **Método** | `POST /auth/refresh` |
| **Body** | `{"refresh_token": "string"}` |
| **Response 200** | `{"access_token": "string", "refresh_token": "string", "token_type": "bearer"}` |
| **Errores** | `401` Token inválido/expirado |
| **Estado** | ✅ Implementado |

### 4. Obtener perfil actual
| | |
|---|---|
| **Método** | `GET /auth/me` |
| **Headers** | `Authorization: Bearer <token>` |
| **Response 200** | `{"id": "uuid", "username": "string", "email": "string", "first_name": "string", "last_name": "string", "role": {"id": "uuid", "name": "string", "permissions": {…}}, "is_active": bool}` |
| **Errores** | `401` No autenticado |
| **Estado** | ✅ Implementado (requiere agregar permisos del rol en la respuesta) |

---

## FE-02 Permisos y navegación por rol

### 5. Listar roles
| | |
|---|---|
| **Método** | `GET /roles` |
| **Headers** | `Authorization: Bearer <token>` |
| **Query** | `?is_active=true` |
| **Response 200** | `[{"id": "uuid", "name": "string", "description": "string", "hierarchy_level": int, "is_active": bool}]` |
| **Errores** | `401`, `403` |
| **Estado** | ⏳ Pendiente |

### 6. Obtener permisos de un rol
| | |
|---|---|
| **Método** | `GET /roles/{role_id}` |
| **Response 200** | `{"id": "uuid", "name": "string", "permissions": {"module": ["create","read","update","delete"]}}` |
| **Estado** | ⏳ Pendiente |

### 7. Permisos en perfil
- Se entrega en `GET /auth/me` (campo `role.permissions`)

---

## FE-03 Dashboard general

### 8. KPIs
| | |
|---|---|
| **Método** | `GET /dashboard/clientes-nuevos` |
| **Query** | `?periodo=mensual&desde=2026-01-01&hasta=2026-12-31` |
| **Response 200** | `{"total": int, "datos": [{"periodo": "string", "cantidad": int}]}` |
| **Estado** | ✅ En rama `feat/dashboard-RF13` |
| **Método** | `GET /dashboard/clientes-por-estado` |
| **Response 200** | `{"total": int, "datos": [{"estado": "string", "cantidad": int}]}` |
| **Método** | `GET /dashboard/clientes-por-plan` |
| **Response 200** | `{"total": int, "datos": [{"plan": "string", "distribucion": {"alquiler": int, "venta": int}}]}` |
| **Método** | `GET /dashboard/pagos-vencidos` |
| **Response 200** | `{"total": int, "total_monto": "decimal", "datos": [...]}` |

### 9. Próximos a vencer
| | |
|---|---|
| **Método** | `GET /dashboard/proximos-a-vencer` |
| **Query** | `?dias=30&tipo=clientes|webs|servicios` |
| **Response 200** | `[{"id": "uuid", "nombre": "string", "fecha_vencimiento": "date", "dias_restantes": int}]` |
| **Estado** | ⏳ Pendiente |

### 10. Resumen de servicios
| | |
|---|---|
| **Método** | `GET /dashboard/resumen-servicios` |
| **Response 200** | `{"activos": int, "vencidos": int, "por_renovar": int}` |
| **Estado** | ⏳ Pendiente |

### 11. Estado de plataformas
| | |
|---|---|
| **Método** | `GET /dashboard/plataformas` |
| **Response 200** | `[{"nombre": "string", "estado": "activo|caido|mantenimiento"}]` |
| **Estado** | ⏳ Pendiente |

---

## FE-04 Clientes

**Base URL:** `/api/v1/clients`
**Headers:** `Authorization: Bearer <token>`

### 12. Listado de clientes
| | |
|---|---|
| **Método** | `GET /clients` |
| **Query** | `?page=1&page_size=20&search=nombre&status=activo&plan=alquiler&web_type_id=uuid&payment_frequency=mensual&is_active=true&ordering=-created_at` |
| **Response 200** | `{"total": int, "page": int, "page_size": int, "results": [{"id": "uuid", "cupe": "ELO-00001", "name": "string", "document_type": "RUC|DNI|CE|Pasaporte", "document_number": "string", "email": "string", "phone": "string", "web_type": "string|null", "features": [{"id": "uuid", "name": "string", "extra_price": "decimal"}], "plan": "alquiler|venta", "status": "activo|inactivo|en_desarrollo", "base_price": "decimal", "extra_price": "decimal", "total_price": "decimal", "initial_payment": "decimal|null", "domain_price": "decimal|null", "payment_frequency": "mensual|anual", "registration_date": "date|null", "delivery_date": "date|null", "next_payment_date": "date|null", "notes": "string", "created_by": "string|null", "is_active": bool, "created_at": "datetime", "updated_at": "datetime"}]}` |
| **Errores** | `401` |
| **Estado** | ✅ Implementado |

### 13. Detalle de un cliente
| | |
|---|---|
| **Método** | `GET /clients/{client_id}` |
| **Response 200** | Mismo schema que un item del listado |
| **Errores** | `401`, `404` |
| **Estado** | ✅ Implementado |

### 14. Crear cliente
| | |
|---|---|
| **Método** | `POST /clients` |
| **Body** | `{"name": "string", "document_type": "RUC|DNI|CE|Pasaporte", "document_number": "string", "email": "email", "phone": "string", "web_type_id": "uuid|null", "feature_ids": ["uuid", ...], "plan": "alquiler|venta", "initial_payment": "decimal|null", "domain_price": "decimal|null", "payment_frequency": "mensual|anual", "registration_date": "date|null", "notes": "string"}` |
| **Response 201** | Cliente creado (CUPE auto-generado ELO-XXXXX) |
| **Errores** | `400` Documento/email duplicado, `404` WebType no encontrado |
| **Estado** | ✅ Implementado |

### 15. Actualizar cliente
| | |
|---|---|
| **Método** | `PUT /clients/{client_id}` |
| **Body** | Parcial (todos los campos opcionales) |
| **Response 200** | Cliente actualizado con precios recalculados |
| **Errores** | `404` No encontrado |
| **Estado** | ✅ Implementado |

### 16. Desactivar cliente
| | |
|---|---|
| **Método** | `DELETE /clients/{client_id}` |
| **Response 204** | Sin contenido (baja lógica: is_active=false, status=inactivo) |
| **Errores** | `404` No encontrado |
| **Estado** | ✅ Implementado |

### 17. Historial de cambios del cliente
| | |
|---|---|
| **Método** | `GET /clients/{client_id}/history` |
| **Headers** | `Authorization: Bearer <token>` |
| **Response 200** | `[{"id": "uuid", "accion": "creacion|actualizacion|eliminacion", "detalle": {...}, "usuario": "string|null", "created_at": "datetime"}]` |
| **Errores** | `401`, `404` |
| **Estado** | ✅ Implementado |

### 18. Solicitar cambio sensible
| | |
|---|---|
| **Método** | `POST /clients/{client_id}/change-requests` |
| **Headers** | `Authorization: Bearer <token>` |
| **Body** | `{"campo": "string", "valor_nuevo": "any", "motivo": "string (min 10 chars)"}` |
| **Response 201** | `{"id": "uuid", "cliente_id": "uuid", "campo": "string", "valor_anterior": {...}, "valor_nuevo": {...}, "motivo": "string", "estado": "pendiente", "solicitado_por": "string", "created_at": "datetime"}` |
| **Errores** | `401`, `404` |
| **Estado** | ✅ Implementado |

### 19. Listar solicitudes de cambio
| | |
|---|---|
| **Método** | `GET /clients/{client_id}/change-requests` |
| **Headers** | `Authorization: Bearer <token>` |
| **Estado** | ✅ Implementado |

### 20. Aprobar/rechazar solicitud
| | |
|---|---|
| **Método** | `PATCH /change-requests/{request_id}` |
| **Headers** | `Authorization: Bearer <token>` |
| **Body** | `{"estado": "aprobado|rechazado", "motivo_rechazo": "string|null"}` |
| **Response 200** | Solicitud actualizada (si aprueba, aplica el cambio al cliente) |
| **Errores** | `401`, `403` (solo staff), `404` |
| **Estado** | ✅ Implementado |

---

## FE-05 Prospectos

### 19. Listado de prospectos
| | |
|---|---|
| **Método** | `GET /prospects` |
| **Query** | `?page=1&page_size=20&search=&source=web&status=active&interest=alta` |
| **Response 200** | `{"total": int, "results": [{"id": "uuid", "name": "string", "email": "string", "phone": "string", "source": "string", "status": "string", "interest": "string", "assigned_to": "string", "created_at": "datetime"}]}` |
| **Estado** | ⏳ Pendiente |

### 20. Crear prospecto
| | |
|---|---|
| **Método** | `POST /prospects` |
| **Body** | `{"name": "string", "email": "string", "phone": "string", "source": "string", "interest": "string", "notes": "string"}` |
| **Response 201** | Prospecto creado |
| **Estado** | ⏳ Pendiente |

### 21. Detalle de prospecto
| | |
|---|---|
| **Método** | `GET /prospects/{prospect_id}` |
| **Response 200** | Prospecto + historial seguimientos |
| **Estado** | ⏳ Pendiente |

### 22. Actualizar prospecto
| | |
|---|---|
| **Método** | `PUT /prospects/{prospect_id}` |
| **Estado** | ⏳ Pendiente |

### 23. Agregar seguimiento
| | |
|---|---|
| **Método** | `POST /prospects/{prospect_id}/follow-ups` |
| **Body** | `{"note": "string", "type": "call|meeting", "next_action": "string", "next_action_date": "date"}` |
| **Response 201** | Seguimiento creado |
| **Estado** | ⏳ Pendiente |

### 24. Convertir prospecto a cliente
| | |
|---|---|
| **Método** | `POST /prospects/{prospect_id}/convert` |
| **Body** | `{"web_type_id": "uuid", "plan_id": "uuid"}` |
| **Response 201** | Cliente creado (prospecto se desactiva) |
| **Estado** | ⏳ Pendiente |

---

## FE-06 Webs de clientes

### 25. Listado de webs
| | |
|---|---|
| **Método** | `GET /webs` |
| **Query** | `?client_id=&status=active&plan=&renewal_date_from=&renewal_date_to=` |
| **Response 200** | `{"total": int, "results": [{"id": "uuid", "domain": "string", "client_name": "string", "status": "string", "plan": "string", "renewal_date": "date"}]}` |
| **Estado** | ⏳ Pendiente |

### 26. Crear web
| | |
|---|---|
| **Método** | `POST /webs` |
| **Body** | `{"client_id": "uuid", "domain": "string", "web_type_id": "uuid", "plan_id": "uuid", "start_date": "date", "renewal_date": "date"}` |
| **Response 201** | Web creada |
| **Estado** | ⏳ Pendiente |

### 27. Detalle de web
| | |
|---|---|
| **Método** | `GET /webs/{web_id}` |
| **Response 200** | Web + historial cambios |
| **Estado** | ⏳ Pendiente |

### 28. Actualizar web
| | |
|---|---|
| **Método** | `PUT /webs/{web_id}` |
| **Estado** | ⏳ Pendiente |

### 29. Historial de cambios de la web
| | |
|---|---|
| **Método** | `GET /webs/{web_id}/history` |
| **Estado** | ⏳ Pendiente |

---

## FE-07 Colaboradores

### 30. Listado de colaboradores
| | |
|---|---|
| **Método** | `GET /users` |
| **Headers** | `Authorization: Bearer <token>` |
| **Query** | `?page=1&page_size=20&search=nombre&is_active=true&role_id=&area=&city=` |
| **Response 200** | `{"total": int, "page": int, "page_size": int, "results": [{"id": "uuid", "username": "string", "first_name": "string", "last_name": "string", "email": "string", "role": {"name": "string"}, "area": "string", "is_active": bool}]}` |
| **Errores** | `401`, `403` |
| **Estado** | ✅ En rama `feat/users-RF03` |

### 31. Crear colaborador
| | |
|---|---|
| **Método** | `POST /users` |
| **Body** | `{"username": "string", "password": "string", "email": "string", "first_name": "string", "last_name": "string", "role_id": "uuid", "area": "string", "phone": "string", "document_number": "string", "hire_date": "date"}` |
| **Response 201** | Colaborador creado |
| **Errores** | `409` Username/email duplicado |
| **Estado** | ✅ En rama `feat/users-RF03` |

### 32. Detalle de colaborador
| | |
|---|---|
| **Método** | `GET /users/{user_id}` |
| **Response 200** | Datos completos + pagos asociados |
| **Estado** | ✅ En rama `feat/users-RF03` |

### 33. Actualizar colaborador
| | |
|---|---|
| **Método** | `PUT /users/{user_id}` |
| **Estado** | ✅ En rama `feat/users-RF03` |

### 34. Activar/desactivar colaborador
| | |
|---|---|
| **Método** | `PATCH /users/{user_id}/status` |
| **Body** | `{"is_active": bool}` |
| **Response 200** | Estado actualizado |
| **Estado** | ✅ En rama `feat/users-RF03` |

### 35. Historial del colaborador
| | |
|---|---|
| **Método** | `GET /users/{user_id}/history` |
| **Estado** | ⏳ Pendiente |

### 36. Pagos del colaborador
| | |
|---|---|
| **Método** | `GET /users/{user_id}/payments` |
| **Response 200** | `[{"id": "uuid", "amount": "decimal", "date": "date", "concept": "string"}]` |
| **Estado** | ⏳ Pendiente |

---

## FE-08 Roles

### 37. Listado de roles
| | |
|---|---|
| **Método** | `GET /roles` |
| **Response 200** | `[{"id": "uuid", "name": "string", "hierarchy_level": int, "description": "string"}]` |
| **Estado** | ⏳ Pendiente |

### 38. Detalle de rol
| | |
|---|---|
| **Método** | `GET /roles/{role_id}` |
| **Response 200** | `{"id": "uuid", "name": "string", "hierarchy_level": int, "permissions": {"module": ["create","read","update","delete"]}}` |
| **Estado** | ⏳ Pendiente |

### 39. Crear rol
| | |
|---|---|
| **Método** | `POST /roles` |
| **Body** | `{"name": "string", "hierarchy_level": int, "description": "string", "permissions": {"module": ["create","read","update","delete"]}}` |
| **Response 201** | Rol creado |
| **Estado** | ⏳ Pendiente |

### 40. Editar rol
| | |
|---|---|
| **Método** | `PUT /roles/{role_id}` |
| **Estado** | ⏳ Pendiente |

### 41. Validación de jerarquía
| | |
|---|---|
| **Método** | Validación en backend al crear/editar usuarios y roles |
| **Regla** | Un usuario no puede asignar un rol con jerarquía >= a la suya |
| **Errores** | `403` No puedes asignar un nivel superior al tuyo |
| **Estado** | ⏳ Pendiente |

---

## Resumen

| Módulo | Endpoints | Estado |
|---|---|---|
| FE-01 Auth | 4 | ✅ 3 implementados, 1 pendiente |
| FE-02 Roles | 3 | ⏳ Pendiente |
| FE-03 Dashboard | 4+ | ✅ KPIs en `feat/dashboard-RF13` |
| FE-04 Clientes | 9 | ✅ 9 implementados |
| FE-05 Prospectos | 6 | ⏳ Pendiente |
| FE-06 Webs | 5 | ⏳ Pendiente |
| FE-07 Colaboradores | 7 | ✅ 5 en `feat/users-RF03`, 2 pendientes |
| FE-08 Roles | 5 | ⏳ Pendiente |

**Nota para frontend:** Los endpoints marcados como "Pendiente" serán desarrollados próximamente. Mientras tanto, pueden usar datos mock con la estructura de respuesta indicada.
