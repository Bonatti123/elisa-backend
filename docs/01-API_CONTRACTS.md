# Contratos de la API (API Contracts) — ELISA ERP

## Autenticación — `/api/v1/auth`

| Método  | Ruta      | Auth  | Descripción     |
|---------|-----------|-------|-----------------|
| POST    | `/login`  | NO    | Iniciar sesión  |
| POST    | `/refresh`| NO    | Refrescar token |
| GET     | `/logout` | JWT   | Cerrar session  |

----------------------------------------------------
>
### POST | `/login`
Inicia sesión y genera el par de tokens bajo la lógica de inactividad de ELISA ERP.
|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200 )                      |
|---------------------------------------------------------------------------------------------------|
  ```json                                  
  {                                                 {
    "username": "elomux",                              "access_token": "eyJhbGczI1I6IkpXVCJ9...",
    "password": "mi_contrasena",                       "refresh_token": "eyJhbGcikpXVCJ9...refresh",
                                                       "token_type": "bearer"
  }                                                 }       
```                                                                                               
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Roles permitidos: Todos los roles.                                                               |
|* No requiere campos obligatorios en el cuerpo de la petición.                                     |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Usuario o contrasena incorrectos.                                                          |
|* `422` Faltan campos requeridos o formato invalido.                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/refresh`
React renueva el access_token automáticamente por reactivación tras inactividad (reiniciando el refresh_token a 24h) o de forma preventiva si le quedan < 5 min de vida. Si se cumplen 24h continuas sin actividad, el backend retorna 401 y la app redirige al Login.
|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200 )                      |
|---------------------------------------------------------------------------------------------------|
```json
{                                                 {
  "refresh_token": "eypXVCJ9...refresh",              "access_token": "eyJhbGI6IkpXVCJ9...nuevo",
                                                      "refresh_token": "eyJfrstg9...refresh_nuevo",
                                                      "token_type": "bearer"
}                                                  } 
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Roles permitidos: Todos los roles.                                                               |
|* No requiere campos obligatorios en el cuerpo de la petición.                                     |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Usuario o contrasena incorrectos.                                                          |
|* `422` Faltan campos requeridos o formato invalido.                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/logout`
Invalida la sesión actual del usuario. En la arquitectura JWT actual, el Frontend es responsable de eliminar inmediatamente el `access_token` y el `refresh_token` de su almacenamiento local o estado global. Este endpoint permite registrar la salida del usuario en el servidor y deja preparada la implementación futura de una lista negra de tokens.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
      {}                                         {
                                                   "message": "Sesión cerrada correctamente"
                                                 }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Roles permitidos: Todos los roles.                                                               |
|* No requiere campos obligatorios en el cuerpo de la petición.                                     |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* No genera errores `400` o `422` de validación, ya que no procesa campos de entrada.              |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
## Clientes — `/api/clients`

| Método  | Ruta                    | Auth        | Descripción                           |
|---------|-------------------------|-------------|---------------------------------------|
| GET     | `/clients/`             | JWT (staff) | Listar Clientes con filtros           |
| POST    | `/clients/`             | JWT (staff) | Crear Clientes                        |
| GET     | `/clients/{client_id}`  | JWT (staff) | Detalle de Clientes                   |
| PUT     | `/clients/{client_id}`  | JWT (staff) | Editar Clientes                       |
| DELETE  | `/clients/{client_id}`  | JWT (staff) | Eliminación lógica                    |


### GET | `/clients/`
Devuelve un listado compacto de todos los clientes registrados. Está optimizado para renderizar tablas dinámicas en React mediante payloads livianos. Permite filtrar opcionalmente por estado.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "status": "activo"
}

                                                        {
                                                          "id": 1,
                                                          "cupe": "CLI-01007918",
                                                          "name": "Corporación Alimentos S.A.C.",
                                                          "document_type": "RUC",
                                                          "document_number": "20601234567",
                                                          "web_type_name": "Pollería",
                                                          "plan": "alquiler",
                                                          "status": "activo",
                                                          "next_payment_date": "2026-06-22",
                                                          "total_price": 250.00
                                                        }

```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles.                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Filtros opcionales                                                                           |
|* `status`: activo, desarrollo o inactivo.                                                         |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/clients/`
Registra un nuevo cliente. El sistema genera automáticamente el CUPE y asigna el estado inicial correspondiente.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (201)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "name": "Inversiones Piter",
  "document_type": "RUC",
  "document_number": "20718293811",
  "phone": "987654321",
  "email": "contacto@piterinv.com",
  "web_type_id": 2,
  "plan": "alquiler",
  "status": "desarrollo",
  "base_price": 0,
  "initial_payment": 150.00,
  "registration_date": "2026-05-22",
  "delivery_date": "2026-05-22",
  "payment_frequency": "mensual",
  "domain_price": 0,
  "notes": "Cliente solicita colores... ."
}
                                                          {
                                                            "id": 12,
                                                            "cupe": "CLI-01095027",
                                                            "name": "Inversiones Piter",
                                                            "document_type": "RUC",
                                                            "document_number": "20718293811",
                                                            "phone": "987654321",
                                                            "email": "contacto@piterinv.com",
                                                            "web_type_id": 2,
                                                            "web_type_name": "Web Corporativa Profesional",
                                                            "plan": "alquiler",
                                                            "status": "desarrollo",
                                                            "base_price": 100,
                                                            "initial_payment": 150,
                                                            "extra_price": null,
                                                            "total_price": 100,
                                                            "registration_date": "2026-05-22",
                                                            "delivery_date": "2026-05-22",
                                                            "next_payment_date": "2026-06-22",
                                                            "payment_frequency": "mensual",
                                                            "domain_price": 0,
                                                            "notes": "Cliente solicita colores...",
                                                            "created_by_id": 1,
                                                            "created_by_name": "Admin Elomux",
                                                            "created_at": "2026-05-22T15:43:54.467940Z",
                                                            "updated_at": "2026-05-22T15:43:54.492297Z"
                                                          }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los colaboradores autorizados.                                           |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* El CUPE se genera automáticamente.                                                               |
|* El estado inicial es `desarrollo`.                                                               |
|* El número de documento debe ser único.                                                           |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` El número de documento ya existe en el sistema.                                            |
|* `401` Token inválido o expirado.                                                                 |
|* `422` Faltan campos requeridos o formato inválido.                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### GET | `/clients/{client_id}`
Obtiene el detalle completo de un cliente mediante su identificador único.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/clients/1

                                                    {
                                                      "id": 1,
                                                      "cupe": "ELO-00482190",
                                                      "name": "Polleria El Buen Sabor",
                                                      "document_type": "RUC",
                                                      "document_number": "20987654321",
                                                      "email": "info@buensabor.com",
                                                      "phone": "999888777",
                                                      "web_type": "Polleria",
                                                      "plan": "alquiler",
                                                      "status": "activo",
                                                      "base_price": 149.00,
                                                      "extra_price": 0.00,
                                                      "total_price": 149.00,
                                                      "initial_payment": 100.00,
                                                      "domain_price": 200.00,
                                                      "registration_date": "2026-01-15",
                                                      "delivery_date": "2026-01-29",
                                                      "next_payment_date": "2026-02-29",
                                                      "payment_frequency": "mensual",
                                                      "features": [],
                                                      "notes": "",
                                                      "created_by": "piter"
                                                    }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos (datos limitados para Líder y Developer).                                |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `client_id` (int): ID único del cliente.                                                         |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `404` Cliente no encontrado.                                                                     |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### PUT | `/clients/{client_id}`
Actualiza la información de un cliente existente. Todos los colaboradores pueden solicitar cambios, pero únicamente Superadmin y Scrum Master pueden aprobarlos. Todas las modificaciones quedan registradas en el historial.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "delivery_date": "2026-02-14",
  "notes": "Web entregada y aprobada por..."
}
                                                      {
                                                        "id": 2,
                                                        "cupe": null,
                                                        "name": "Carlos Rodríguez",
                                                        "document_type": "DNI",
                                                        "document_number": "77889900",
                                                        "phone": "987654321",
                                                        "email": "carlos.rodriguez@gmail.com",
                                                        "web_type_id": 1,
                                                        "web_type_name": "E-commerce",
                                                        "plan": "venta",
                                                        "status": "activo",
                                                        "base_price": 1500,
                                                        "initial_payment": 500,
                                                        "extra_price": null,
                                                        "total_price": 1500,
                                                        "registration_date": "2026-05-14",
                                                        "delivery_date": "2026-02-14",
                                                        "next_payment_date": "2026-03-14",
                                                        "payment_frequency": "mensual",
                                                        "domain_price": null,
                                                        "notes": "Web entregada y aprobada por el cliente",
                                                        "created_by_id": 1,
                                                        "created_by_name": "Admin Elomux",
                                                        "created_at": "2026-05-14T16:55:11.326389Z",
                                                        "updated_at": "2026-05-22T16:32:49.873606Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Solicitar cambios: Todos los roles.                                                              |
|* Aprobar cambios: Superadmin y Scrum Master.                                                      |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `client_id` (int): ID único del cliente a actualizar.                                            |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* Todos los cambios quedan registrados en historial.                                               |
|* La fecha de entrega puede activar automáticamente el estado del cliente.                         |
|* La próxima fecha de pago puede ser calculada por el backend.                                     |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `403` Sin permisos para aprobar ediciones.                                                       |
|* `404` Cliente no encontrado.                                                                     |
|* `422` Formato de fecha inválido o datos incorrectos.                                             |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### DELETE | `/clients/{client_id}`
Solicita la baja de un cliente. Actualmente no se realiza una eliminación física del registro; el cliente es marcado como dado de baja. Solo Superadmin puede aprobar la eliminación.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/clients/5

                                                {
                                                  "message": "Cliente None dado de baja correcta..."
                                                }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Solicitar eliminación: SA, TL, LI y DEV.                                                         |
|* Aprobar eliminación: Solo Superadmin.                                                            |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `client_id` (int): ID único del cliente que se desea dar de baja.                                |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* El cliente no se elimina físicamente de la base de datos.                                        |
|* El registro queda marcado como dado de baja.                                                     |
|* Toda solicitud requiere aprobación de Superadmin.                                                |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `403` Sin permisos para solicitar o aprobar la eliminación.                                      |
|* `404` Cliente no encontrado.                                                                     |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
## Colaboradores — `/api/users`

| Método  | Ruta                        | Auth        | Descripción                           |
|---------|-----------------------------|-------------|---------------------------------------|
| GET     | `/users/`                   | JWT (staff) | Listar Colaboradores con filtros      |
| POST    | `/users/`                   | JWT (staff) | Crear Colaboradores                   |
| GET     | `/users/me`                 | JWT (staff) | Lista toda mi informacion             |
| GET     | `/users/{collaborator_id}`  | JWT (staff) | Detalle de Colaboradores              |
| PUT     | `/users/{collaborator_id}`  | JWT (staff) | Editar Colaboradores                  |
| DELETE  | `/users/{collaborator_id}`  | JWT (staff) | Eliminación lógica                    |


### GET | `/users/`
Lista todos los colaboradores registrados en el sistema. Permite filtrar por estado activo o inactivo. Los usuarios con rol Developer no tienen acceso a este endpoint.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "is_active": true
}
                                                              {
                                                                "id": 1,
                                                                "cupe": "ELO-01007918",
                                                                "first_name": "Admin",
                                                                "last_name": "Elomux",
                                                                "role_name": "Superadmin",
                                                                "city": "Lima",
                                                                "is_active": true
                                                              }
                                                            
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: SA, SM, TL y LI.                                                               |
|* Roles restringidos: Developer.                                                                   |
|---------------------------------------------------------------------------------------------------|
|##### Filtros opcionales                                                                           |
|* `is_active`: true o false.                                                                       |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido.                                                                            |
|* `403` Developer no tiene acceso.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/users/`
Registra un nuevo colaborador. El sistema genera automáticamente el CUPE y encripta la contraseña antes de almacenarla. Solo es posible crear usuarios de menor jerarquía.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (201)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "first_name": "Jherson",
  "last_name": "Serna",
  "document_type": "DNI",
  "document_number": "74581236",
  "email": "jherson.serna@gmail.com",
  "phone": "987654321",
  "city": "Lima",
  "username": "jherson123",
  "password": "MiPassword123",
  "role_id": 5,
  "area": "Desarrollo"
}
                                                      {
                                                        "id": 2,
                                                        "cupe": "ELO-01015837",
                                                        "first_name": "Jherson",
                                                        "last_name": "Serna",
                                                        "document_type": "DNI",
                                                        "document_number": "74581236",
                                                        "email": "jherson.serna@gmail.com",
                                                        "phone": "987654321",
                                                        "city": "Lima",
                                                        "username": "jherson123",
                                                        "role_id": 5,
                                                        "role_name": "Developer",
                                                        "role_level": "L5",
                                                        "area": "Desarrollo",
                                                        "is_active": true,
                                                        "created_at": "2026-05-21T14:39:17.560Z",
                                                        "updated_at": "2026-05-21T14:39:17.561Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: SA, SM, TL y LI.                                                               |
|* Roles restringidos: Developer.                                                                   |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* El CUPE se genera automáticamente.                                                               |
|* La contraseña es encriptada por el backend.                                                      |
|* Solo pueden crearse usuarios de menor jerarquía.                                                 |
|* Username, correo y documento deben ser únicos.                                                   |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` Username o documento ya existe.                                                            |
|* `401` Token inválido.                                                                            |
|* `403` No puede crear usuarios de igual o mayor jerarquía.                                        |
|* `422` Faltan campos requeridos o formato inválido.                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### GET | `/users/me`
Obtiene toda la información del usuario autenticado actualmente. Este endpoint es utilizado por React para cargar el perfil y permisos del usuario después del inicio de sesión.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{}
                                                  {
                                                    "id": 1,
                                                    "cupe": "COL-2026XYZ",
                                                    "first_name": "Admin",
                                                    "last_name": "Elomux",
                                                    "document_type": "DNI",
                                                    "document_number": "00000000",
                                                    "email": "admin@elomux.com",
                                                    "phone": "999999999",
                                                    "city": "Lima",
                                                    "username": "elomux",
                                                    "role_id": 1,
                                                    "role_name": "Superadmin",
                                                    "role_level": "L1",
                                                    "area": "Gerencia",
                                                    "is_active": true,
                                                    "created_at": "2026-05-08T16:50:20.103738Z",
                                                    "updated_at": "2026-05-24T16:26:35.508889Z"
                                                  }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Disponible para cualquier usuario autenticado.                                                   |
|---------------------------------------------------------------------------------------------------|
|##### Observaciones                                                                                |
|* No requiere parámetros de URL.                                                                   |
|* No requiere Query Parameters.                                                                    |
|* No requiere Request Body.                                                                        |
|* Utiliza el token JWT para identificar al usuario actual.                                         |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido.                                                                            |
|* `404` Usuario no encontrado.                                                                     |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### GET | `/users/{collaborator_id}`
Obtiene el detalle completo de un colaborador mediante su identificador único.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
/users/2

                                                      {
                                                        "id": 2,
                                                        "cupe": "ELO-01015837",
                                                        "first_name": "Jherson",
                                                        "last_name": "Serna",
                                                        "document_type": "DNI",
                                                        "document_number": "74581236",
                                                        "email": "jherson.serna@gmail.com",
                                                        "phone": "987654321",
                                                        "city": "Lima",
                                                        "username": "jherson123",
                                                        "role_id": 5,
                                                        "role_name": "Developer",
                                                        "role_level": "L5",
                                                        "area": "Desarrollo",
                                                        "is_active": true,
                                                        "created_at": "2026-05-19T18:11:54.348753Z",
                                                        "updated_at": "2026-05-19T18:11:54.379988Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: SA, SM, TL y LI.                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `collaborator_id` (int): ID único del colaborador.                                               |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido.                                                                            |
|* `404` Colaborador no encontrado.                                                                 |
|* `422` El parámetro collaborator_id tiene formato inválido.                                       |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### PUT | `/users/{collaborator_id}`
Actualiza la información de un colaborador. Solo Superadmin y Scrum Master pueden realizar modificaciones.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "phone": "+51987654321",
  "city": "Cusco",
  "area": "Diseño UX/UI",
  "is_active": true
}
                                                        {
                                                          "id": 2,
                                                          "cupe": "ELO-01015837",
                                                          "first_name": "Jherson",
                                                          "last_name": "Serna",
                                                          "document_type": "DNI",
                                                          "document_number": "74581236",
                                                          "email": "jherson.serna@gmail.com",
                                                          "phone": "+51987654321",
                                                          "city": "Cusco",
                                                          "username": "jherson123",
                                                          "role_id": 5,
                                                          "role_name": "Developer",
                                                          "role_level": "L5",
                                                          "area": "Diseño UX/UI",
                                                          "is_active": true,
                                                          "created_at": "2026-05-19T18:11:54.348753Z",
                                                          "updated_at": "2026-05-21T16:14:49.642077Z"
                                                        }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: SA, SM, TL y LI.                                                               |
|* Roles restringidos: Developer.                                                                   |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `collaborator_id` (int): ID único del colaborador a actualizar.                                  |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* Si se envía una nueva contraseña, el backend la encripta automáticamente.                        |
|* El rol asignado debe existir previamente en el sistema.                                          |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido.                                                                            |
|* `403` Solo SA y SM pueden editar colaboradores.                                                  |
|* `404` Colaborador no encontrado.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### DELETE | `/users/{collaborator_id}`
Realiza una baja lógica (Soft Delete) de un colaborador. El usuario no es eliminado físicamente de la base de datos, únicamente se marca como inactivo.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
  /users/2

                                                {
                                                  "message": "Colaborador ELO-01015837 dado de baja correctamente"
                                                }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: SM, TL, LI y Developer.                                                      |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `collaborator_id` (int): ID único del colaborador que será dado de baja.                         |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* Implementa baja lógica (Soft Delete).                                                            |
|* El colaborador permanece almacenado en la base de datos.                                         |
|* Solo cambia su estado a inactivo.                                                                |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` Solicitud inválida.                                                                        |
|* `401` Token inválido o expirado.                                                                 |
|* `403` No tiene permisos para realizar la acción.                                                 |
|* `404` Colaborador no encontrado.                                                                 |
|* `422` Error de validación en la solicitud.                                                       |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
## Roles — `/api/roles`

| Método  | Ruta                | Auth        | Descripción                           |
|---------|---------------------|-------------|---------------------------------------|
| GET     | `/roles/`           | JWT (staff) | Listar roles con filtros              |
| POST    | `/roles/`           | JWT (staff) | Crear roles                           |
| GET     | `/roles/{role_id}`  | JWT (staff) | Detalle de roles                      |
| PUT     | `/roles/{role_id}`  | JWT (staff) | Editar roles                          |
| DELETE  | `/roles/{role_id}`  | JWT (staff) | Eliminación lógica                    |


### GET | `/roles/`
Obtiene el listado completo de roles registrados en el sistema. El endpoint calcula dinámicamente la cantidad de colaboradores asignados a cada rol.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{}
                                                    [
                                                      {
                                                        "id": 1,
                                                        "name": "Superadmin",
                                                        "level": "L1",
                                                        "collaborators_count": 1,
                                                        "created_at": "2026-05-08T16:50:19.798196Z"
                                                      },
                                                      {
                                                        "id": 2,
                                                        "name": "Scrum Master",
                                                        "level": "L2",
                                                        "collaborators_count": 0,
                                                        "created_at": "2026-05-08T16:50:19.803422Z"
                                                      }
                                                    ]
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos.                                                                         |
|---------------------------------------------------------------------------------------------------|
|##### Observaciones                                                                                |
|* No requiere parámetros de entrada.                                                               |
|* `collaborators_count` se calcula dinámicamente en tiempo real.                                   |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/roles/`
Crea un nuevo rol dentro del sistema. El nombre y nivel jerárquico deben ser únicos.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (201)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "name": "Nuevo Rol Test",
  "level": "L6"
}
                                                      {
                                                        "id": 6,
                                                        "name": "Nuevo Rol Test",
                                                        "level": "L6",
                                                        "collaborators_count": 0,
                                                        "created_at": "2026-05-25T05:01:40.529112Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: L2, L3, L4 y L5.                                                             |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* El nombre del rol debe ser único.                                                                |
|* El nivel jerárquico debe ser único.                                                              |
|* El rol inicia con `collaborators_count = 0`.                                                     |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` Ya existe un rol con ese nombre o nivel.                                                   |
|* `401` Token inválido o expirado.                                                                 |
|* `403` Solo el Superadmin puede realizar esta acción.                                             |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### GET | `/roles/{role_id}`
Obtiene el detalle de un rol específico mediante su identificador único. Permite consultar su jerarquía y la cantidad de colaboradores asociados.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
  /roles/1

                                                    {
                                                      "id": 1,
                                                      "name": "Superadmin",
                                                      "level": "L1",
                                                      "collaborators_count": 1,
                                                      "created_at": "2026-05-08T16:50:19.798196Z"
                                                    }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos.                                                                         |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `role_id` (int): ID único del rol a consultar.                                                   |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `404` El rol solicitado no existe.                                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### PUT | `/roles/{role_id}`
Actualiza la información de un rol existente mediante su identificador único.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "name": "Tech Lead Modificado"
}
                                                      {
                                                        "id": 3,
                                                        "name": "Tech Lead Modificado",
                                                        "level": "L3",
                                                        "collaborators_count": 0,
                                                        "created_at": "2026-05-08T16:50:19.805830Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Únicamente Superadmin (L1).                                                    |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `role_id` (int): ID único del rol que se desea actualizar.                                       |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* Puede modificarse el nombre del rol.                                                             |
|* Puede modificarse el nivel jerárquico del rol.                                                   |
|* Los cambios afectan a todos los colaboradores asociados al rol.                                  |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `403` Solo el Superadmin puede realizar esta acción.                                             |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### DELETE | `/roles/{role_id}`
Elimina un rol del sistema utilizando su identificador único. El sistema valida que el rol no tenga colaboradores asociados y que no sea el rol Superadmin.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/roles/6

                                                  {
                                                    "message": "Rol Nuevo Rol Test eliminado correctamente"
                                                  }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: Scrum Master, Tech Lead, Líder y Developer.                                  |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `role_id` (int): ID único del rol a eliminar.                                                    |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* No puede eliminarse el rol Superadmin.                                                           |
|* No puede eliminarse un rol con colaboradores asignados.                                          |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` El rol tiene colaboradores asignados o es el rol Superadmin.                               |
|* `401` Token inválido o expirado.                                                                 |
|* `403` No posee permisos suficientes.                                                             |
|* `404` Rol no encontrado.                                                                         |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>

## Tipos Web — `/api/web-types`

| Método  | Ruta                        | Auth        | Descripción                           |
|---------|-----------------------------|-------------|---------------------------------------|
| GET     | `/web-types/`               | JWT (staff) | Listar Tipos web con filtros          |
| POST    | `/web-types/`               | JWT (staff) | Crear Tipos web                       |
| GET     | `/web-types/{web_type_id}`  | JWT (staff) | Detalle de Tipos web                  |
| PUT     | `/web-types/{web_type_id}`  | JWT (staff) | Editar Tipos web                      |
| DELETE  | `/web-types/{web_type_id}`  | JWT (staff) | Eliminación lógica                    |

### GET | `/web-types/`
Obtiene el listado completo de tipos de web registrados en el sistema. Permite filtrar opcionalmente por estado.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "is_active": true
}
                                                    [
                                                      {
                                                        "id": 1,
                                                        "name": "Ecomerce",
                                                        "base_price_rent": 50,
                                                        "base_price_sale": 499,
                                                        "is_active": true,
                                                        "clients_count": 0,
                                                        "created_at": "2026-05-26T14:54:43.224866Z"
                                                      }
                                                    ]
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles.                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Filtros opcionales                                                                           |
|* `is_active`: true o false.                                                                       |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido.                                                                            |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/web-types/`
Registra un nuevo tipo de web en el sistema. Antes de crear el registro se valida que no exista otro tipo de web con el mismo nombre.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (201)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "name": "Restaurante",
  "base_price_rent": 50,
  "base_price_sale": 499,
  "is_active": true
}
                                                      {
                                                        "id": 4,
                                                        "name": "Restaurante",
                                                        "base_price_rent": 50,
                                                        "base_price_sale": 499,
                                                        "is_active": true,
                                                        "clients_count": 0,
                                                        "created_at": "2026-05-26T17:13:48.341Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* El nombre del tipo de web debe ser único.                                                        |
|* Los precios deben ser mayores o iguales a cero.                                                  |
|* El contador de clientes inicia en cero.                                                          |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` Ya existe un tipo de web con ese nombre.                                                   |
|* `401` Token inválido.                                                                            |
|* `403` No tiene permisos de Superadmin.                                                           |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### GET | `/web-types/{web_type_id}`
Obtiene la información completa de un tipo de web mediante su identificador único.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/web-types/1

                                                        {
                                                          "id": 1,
                                                          "name": "Ecomerce",
                                                          "base_price_rent": 50,
                                                          "base_price_sale": 499,
                                                          "is_active": true,
                                                          "clients_count": 0,
                                                          "created_at": "2026-05-26T14:54:43.224866Z"
                                                        }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles.                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `web_type_id` (int): ID único del tipo de web.                                                   |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido.                                                                            |
|* `404` Tipo de web no encontrado.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### PUT | `/web-types/{web_type_id}`
Actualiza la información de un tipo de web existente. Es necesario proporcionar el identificador del registro y los datos a modificar.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "name": "cafeteria",
  "base_price_rent": 50,
  "base_price_sale": 299,
  "is_active": false
}
                                                    {
                                                      "id": 3,
                                                      "name": "cafeteria",
                                                      "base_price_rent": 50,
                                                      "base_price_sale": 299,
                                                      "is_active": false,
                                                      "clients_count": 0,
                                                      "created_at": "2026-05-26T15:06:10.749500Z"
                                                    }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `web_type_id` (int): ID único del tipo de web a actualizar.                                      |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* No puede existir otro tipo de web con el mismo nombre.                                           |
|* Los cambios afectan únicamente al catálogo de tipos de web.                                      |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` Ya existe un tipo de web con ese nombre.                                                   |
|* `401` Token inválido.                                                                            |
|* `403` No tiene permisos de Superadmin.                                                           |
|* `404` Tipo de web no encontrado.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### DELETE | `/web-types/{web_type_id}`
Elimina un tipo de web del sistema utilizando su identificador único. Solo puede ser ejecutado por un Superadmin.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
  /web-types/4
                                                  {
                                                    "message": "Tipo de web Restaurante eliminado correctamente"
                                                  }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: Scrum Master, Tech Lead, Líder y Developer.                                  |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `web_type_id` (int): ID único del tipo de web a eliminar.                                        |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* No puede eliminarse un tipo de web que tenga clientes asignados.                                 |
|* Solo los usuarios con rol Superadmin pueden realizar la acción.                                  |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` El tipo de web tiene clientes asignados.                                                   |
|* `401` Token inválido o expirado.                                                                 |
|* `403` No es Superadmin.                                                                          |
|* `404` Tipo de web no encontrado.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
## Funcionalidades  — `/api/web-features`

| Método  | Ruta                          | Auth        | Descripción                           |
|---------|-------------------------------|-------------|---------------------------------------|
| GET     | `/web-features/`              | JWT (staff) | Listar funcionalidades con filtros    |
| POST    | `/web-features/`              | JWT (staff) | Crear funcionalidades                 |
| GET     | `/web-features/{feature_id}`  | JWT (staff) | Detalle de funcionalidades            |
| PUT     | `/web-features/{feature_id}`  | JWT (staff) | Editar funcionalidades                |
| DELETE  | `/web-features/{feature_id}`  | JWT (staff) | Eliminación lógica                    |


### GET | `/web-features/`
Obtiene el listado completo de funcionalidades adicionales registradas en el sistema. Permite filtrar opcionalmente por estado activo o inactivo.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "is_active": true
}
                                                      [
                                                        {
                                                          "id": 1,
                                                          "name": "Sistema de citas",
                                                          "extra_price": 50.00,
                                                          "is_active": true,
                                                          "created_at": "2026-06-05T15:08:11.652766Z"
                                                        }
                                                      ]
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles.                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Filtros opcionales                                                                           |
|* `is_active`: true o false.                                                                       |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/web-features/`
Crea una nueva funcionalidad adicional dentro del catálogo general del sistema. El nombre de la funcionalidad debe ser único.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (201)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "name": "Pasarela de pagos",
  "extra_price": 150.00
}
                                                    {
                                                      "id": 2,
                                                      "name": "Pasarela de pagos",
                                                      "extra_price": 150,
                                                      "is_active": true,
                                                      "created_at": "2026-06-08T20:00:38.969028Z"
                                                    }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: L2, L3, L4 y L5.                                                             |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* El nombre de la funcionalidad debe ser único.                                                    |
|* Si no se envía `is_active`, el valor por defecto será `true`.                                    |
|* El precio adicional se expresa en soles.                                                         |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` Ya existe una funcionalidad con ese nombre.                                                |
|* `401` Token inválido o expirado.                                                                 |
|* `403` Solo el Superadmin puede realizar esta acción.                                             |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### GET | `/web-features/{feature_id}`
Obtiene la información detallada de una funcionalidad específica mediante su identificador único.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/web-features/2

                                                    {
                                                      "id": 2,
                                                      "name": "Pasarela de pagos",
                                                      "extra_price": 150,
                                                      "is_active": true,
                                                      "created_at": "2026-06-08T20:00:38.969028Z"
                                                    }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles.                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `feature_id` (int): ID único de la funcionalidad.                                                |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `404` Funcionalidad no encontrada.                                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### PUT | `/web-features/{feature_id}`
Actualiza los datos de una funcionalidad existente mediante su identificador único.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "name": "Sistema de citas Premium",
  "extra_price": 75.00
}
                                                    {
                                                      "id": 1,
                                                      "name": "Sistema de citas Premium",
                                                      "extra_price": 75,
                                                      "is_active": true,
                                                      "created_at": "2026-06-05T15:08:11.652766Z"
                                                    }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: L2, L3, L4 y L5.                                                             |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `feature_id` (int): ID único de la funcionalidad a actualizar.                                   |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* Puede modificarse el nombre, precio o estado de la funcionalidad.                                |
|* No puede existir otra funcionalidad con el mismo nombre.                                         |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` Ya existe otra funcionalidad con ese nombre.                                               |
|* `401` Token inválido o expirado.                                                                 |
|* `403` Solo el Superadmin puede realizar esta acción.                                             |
|* `404` Funcionalidad no encontrada.                                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### DELETE | `/web-features/{feature_id}`
Elimina una funcionalidad adicional del catálogo utilizando su identificador único. La eliminación solo se realizará si no existen registros vinculados que afecten la integridad de los datos.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/web-features/1

                                                  {
                                                    "message": "Funcionalidad Sistema de citas Premium eliminada correctamente"
                                                  }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: L2, L3, L4 y L5.                                                             |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `feature_id` (int): ID único de la funcionalidad a eliminar.                                     |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* No puede eliminarse una funcionalidad asociada a clientes.                                       |
|* El sistema valida relaciones existentes en `ClientFeature`.                                      |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` La funcionalidad tiene clientes asignados.                                                 |
|* `401` Token inválido o expirado.                                                                 |
|* `403` No es Superadmin.                                                                          |
|* `404` Funcionalidad no encontrada.                                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
## Funcionalidades de Clientes   — `/api/web-features`

| Método  | Ruta                                    | Auth        | Descripción                       |
|---------|-----------------------------------------|-------------|-----------------------------------|
| GET     | `/client-features/client/{client_id} `  | JWT (staff) | Listar funcionalidades extra      |
| POST    | `/client-features/ `                    | JWT (staff) | Asigna una funcionalidad adicional|
| DELETE  | `/client-features/{client_feature_id} ` | JWT (staff)| Remueve una funcionalidad extra    |


### GET | `/client-features/client/{client_id}`
Obtiene el listado de todas las funcionalidades adicionales contratadas por un cliente específico. Devuelve una versión resumida para optimizar la carga de información en el Frontend.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/client-features/client/1

                                                    [
                                                      {
                                                        "id": 1,
                                                        "feature_id": 2,
                                                        "feature_name": "Pasarela de pagos",
                                                        "feature_price": 150,
                                                        "added_at": "2026-06-08T20:43:29.219148Z"
                                                      }
                                                    ]
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles.                                                               |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `client_id` (int): ID único del cliente a consultar.                                             |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `404` Cliente no encontrado.                                                                     |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/client-features/`
Asigna una funcionalidad adicional del catálogo a un cliente. Al completarse correctamente, el sistema registra la relación, actualiza el `extra_price` del cliente y recalcula automáticamente el `total_price`.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (201)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "client_id": 1,
  "feature_id": 2
}
                                                      {
                                                        "id": 1,
                                                        "client_id": 1,
                                                        "client_name": "Jherson KSH",
                                                        "client_cupe": "CLI-2026-CORR",
                                                        "feature_id": 2,
                                                        "feature_name": "Pasarela de pagos",
                                                        "feature_price": 150,
                                                        "added_at": "2026-06-08T20:43:29.219148Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: L1, L2, L3 y L4.                                                               |
|* Roles restringidos: L5 (Developer).                                                              |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* Crea una nueva relación en la tabla `client_features`.                                           |
|* Incrementa automáticamente el campo `extra_price` del cliente.                                   |
|* Recalcula el campo `total_price` (`base_price + extra_price`).                                   |
|* Una funcionalidad no puede asignarse dos veces al mismo cliente.                                 |
|* Solo se pueden asignar funcionalidades activas.                                                  |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` La funcionalidad no está disponible.                                                       |
|* `400` El cliente ya tiene asignada la funcionalidad.                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `403` No tienes permisos para gestionar funcionalidades.                                         |
|* `404` Cliente o funcionalidad no encontrada.                                                     |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### DELETE | `/client-features/{client_feature_id}`
Elimina una funcionalidad previamente asignada a un cliente. El sistema actualiza automáticamente los costos asociados al cliente y recalcula el precio total.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/client-features/1
                                                  {
                                                    "message": "Funcionalidad Sistema de citas quitada del cliente CLI-01007918"
                                                  }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: L1, L2, L3 y L4.                                                               |
|* Roles restringidos: L5 (Developer).                                                              |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `client_feature_id` (int): ID único de la asignación a eliminar.                                 |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* Elimina el registro de la tabla `client_features`.                                               |
|* Resta automáticamente el precio de la funcionalidad del campo `extra_price`.                     |
|* Aplica una validación para evitar valores negativos (`max(0, extra_price)`).                     |
|* Recalcula el `total_price` del cliente después de la eliminación.                                |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `403` No tienes permisos para gestionar funcionalidades.                                         |
|* `404` Registro de asignación no encontrado.                                                      |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
## Historial CUPE  — `/api/cupe-log`

| Método  | Ruta                 | Auth        | Descripción                                          |
|---------|----------------------|-------------|------------------------------------------------------|
| GET     | `/cupe-log/`         | JWT (staff) | Retorna el historial completo                        |
| POST    | `/cupe-log/`         | JWT (staff) | Solicita y procesa un cambio de CUPE                 |
| GET     | `/cupe-log/{log_id}/`| JWT (staff) | Obtiene los metadatos y especificaciones de auditoría|


### GET | `/cupe-log/`
Obtiene el historial completo de cambios realizados sobre códigos CUPE en el sistema. Permite filtrar opcionalmente por tipo de entidad para facilitar auditorías y búsquedas específicas.

|---------------------------------------------------------------------------------------------------|
|          Query Parameters                 |            Response Body (200)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "entity_type": "client"
}
                                                      [
                                                        {
                                                          "id": 6,
                                                          "entity_type": "client",
                                                          "entity_id": 1,
                                                          "old_cupe": "CLI-20260001",
                                                          "new_cupe": "CLI-20269999",
                                                          "reason": "correccion_admin",
                                                          "changed_by_name": "Admin Elomux",
                                                          "authorized_by_name": "Admin Elomux",
                                                          "changed_at": "2026-05-24T20:31:36.068113Z"
                                                        },
                                                        {
                                                          "id": 1,
                                                          "entity_type": "client",
                                                          "entity_id": 1,
                                                          "old_cupe": "CLI-01007918",
                                                          "new_cupe": "CLI-20260001",
                                                          "reason": "error_generacion",
                                                          "changed_by_name": "Admin Elomux",
                                                          "authorized_by_name": "Admin Elomux",
                                                          "changed_at": "2026-05-08T17:06:40.433415Z"
                                                        }
                                                      ]
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles activos.                                                       |
|---------------------------------------------------------------------------------------------------|
|##### Filtros opcionales                                                                           |
|* `entity_type`: `client` o `collaborator`.                                                        |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido, expirado o no proporcionado.                                               |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### POST | `/cupe-log/`
Solicita y procesa un cambio de CUPE de forma inmediata. La operación se ejecuta dentro de una transacción atómica para garantizar la integridad de los datos. Si ocurre cualquier error, ningún cambio es aplicado.

|---------------------------------------------------------------------------------------------------|
|             Request Body                   |            Response Body (201)                       |
|---------------------------------------------------------------------------------------------------|
```json
{
  "entity_type": "client",
  "entity_id": 5,
  "new_cupe": "CLI-01023756",
  "reason": "error_generacion",
  "observations": "Se generó con ID inc..."
}
                                                      {
                                                        "id": 12,
                                                        "entity_type": "client",
                                                        "entity_id": 5,
                                                        "old_cupe": "CLI-01000005",
                                                        "new_cupe": "CLI-01023756",
                                                        "reason": "error_generacion",
                                                        "observations": "Se generó con ID incorrecto en la carga masiva",
                                                        "changed_by_id": 1,
                                                        "changed_by_name": "Admin Elomux",
                                                        "authorized_by_id": 1,
                                                        "authorized_by_name": "Admin Elomux",
                                                        "changed_at": "2026-06-08T21:20:25.266Z"
                                                      }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Superadmin (L1).                                                               |
|* Roles restringidos: L2, L3, L4 y L5.                                                             |
|---------------------------------------------------------------------------------------------------|
|##### Reglas de negocio                                                                            |
|* El sistema obtiene automáticamente el `old_cupe`.                                                |
|* La operación se ejecuta dentro de una transacción atómica.                                       |
|* El nuevo CUPE no puede estar duplicado dentro del mismo tipo de entidad.                         |
|* Se registra automáticamente la auditoría del cambio.                                             |
|* Los motivos válidos son: `error_generacion`, `reingreso`, `correccion_admin`, `otro`.            |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `400` El nuevo CUPE ya está en uso.                                                              |
|* `400` El valor de `entity_type` no es válido.                                                    |
|* `401` Token inválido o expirado.                                                                 |
|* `403` Solo el Superadmin puede autorizar cambios de CUPE.                                        |
|* `404` Entidad no encontrada.                                                                     |
|* `404` Colaborador autenticado no encontrado.                                                     |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
### GET | `/cupe-log/{log_id}`
Obtiene el detalle completo de un registro de auditoría asociado a un cambio de CUPE específico.

|---------------------------------------------------------------------------------------------------|
|          Parámetro URL                    |            Response Body (200)                        |
|---------------------------------------------------------------------------------------------------|
```json
/cupe-log/1

                                                  {
                                                    "id": 1,
                                                    "entity_type": "client",
                                                    "entity_id": 1,
                                                    "old_cupe": "CLI-01007918",
                                                    "new_cupe": "CLI-20260001",
                                                    "reason": "error_generacion",
                                                    "observations": "Se corrige el CUPE inicial por error en el formato automático",
                                                    "changed_by_id": 1,
                                                    "changed_by_name": "Admin Elomux",
                                                    "authorized_by_id": 1,
                                                    "authorized_by_name": "Admin Elomux",
                                                    "changed_at": "2026-05-08T17:06:40.433415Z"
                                                  }
```
|---------------------------------------------------------------------------------------------------|
|##### Autenticación                                                                                |
|* Requiere token JWT.                                                                              |
|* Roles permitidos: Todos los roles activos.                                                       |
|---------------------------------------------------------------------------------------------------|
|##### Parámetros                                                                                   |
|* `log_id` (int): Identificador único del registro de auditoría.                                   |
|---------------------------------------------------------------------------------------------------|
|##### Información retornada                                                                        |
|* Datos completos del cambio realizado.                                                            |
|* Usuario solicitante y autorizador.                                                               |
|* Motivo registrado para la modificación.                                                          |
|* Observaciones adicionales del proceso.                                                           |
|---------------------------------------------------------------------------------------------------|
|##### Posibles errores                                                                             |
|* `401` Token inválido o expirado.                                                                 |
|* `404` Registro de log no encontrado.                                                             |
|---------------------------------------------------------------------------------------------------|
>
>
---
>
>
>
>
---
>
>
======>>>>>> 









## Contabilidad — `/api/v1/accounting`

### Compras

| Método  | Ruta              | Auth        | Descripción                           |
|---------|-------------------|-------------|---------------------------------------|
| GET     | `/purchases/`     | JWT (staff) | Listar compras con filtros            |
| POST    | `/purchases/`     | JWT (staff) | Crear compra con auditoría            |
| GET     | `/purchases/{id}` | JWT (staff) | Detalle de compra                     |
| PUT     | `/purchases/{id}` | JWT (staff) | Editar compra con bloqueo y auditoría |
| DELETE  | `/purchases/{id}` | JWT (staff) | Eliminación lógica con auditoría      |

### Ventas

| Método  | Ruta          | Auth        | Descripción                         |
|---------|---------------|-------------|-------------------------------------|
| GET     | `/sales/`     | JWT (staff) | Listar ventas con filtros           |
| POST    | `/sales/`     | JWT (staff) | Crear venta con auditoría           |
| GET     | `/sales/{id}` | JWT (staff) | Detalle de venta                    |
| PUT     | `/sales/{id}` | JWT (staff) | Editar venta con bloqueo y auditoría|
| DELETE  | `/sales/{id}` | JWT (staff) | Eliminación lógica con auditoría    |

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
