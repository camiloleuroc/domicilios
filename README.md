# domicilios
API para sistema de asignación de servicios de domicilio.

# Documentación de API de domicilios para el Sistema de Registro de Usuarios, Conductores y Solicitudes de Servicios.

Esta es la documentación de la API que permite gestionar usuarios, conductores, ubicaciones, y solicitudes de servicio en un sistema de domicilios. A continuación se describen las rutas, datos que solicita la API, y las respuestas posibles en formato json.

### URL base http://localhost:8000/api

# 1. Registrar Usuario (Register User)
## Ruta
`POST /register/`

## Descripción
Permite registrar un nuevo usuario (cliente o conductor).

## Datos solicitados
```
{
    "username": "string",  // Nombre de usuario
    "password": "string",  // Contraseña
    "is_driver": "boolean", // Indica si el usuario es conductor
    "plate": "string"  // (Opcional) Placa del vehículo si es conductor
}
```

## Respuestas
* 201 Created: El usuario ha sido registrado correctamente.
```
{
    "id": "UUID",
    "username": "string",
    "is_driver": "boolean"
}
```
* 400 Bad Request: Si los datos no son válidos o falta información.
```
{
    "username": ["Este campo es obligatorio."],
    "password": ["Este campo es obligatorio."]
}
```
# 2. Lista de Conductores (Driver List)
## Ruta
`GET /drivers/`

## Descripción
Devuelve la lista de todos los conductores registrados en el sistema.

## Datos solicitados
No requiere parámetros adicionales.

## Respuestas
* 200 OK: Lista de conductores encontrados.
```
[
    {
        "id": "UUID",
        "username": "string",
        "is_driver": true,
        "plate": "string"
    }
]
```
* 401 Unauthorized: Si el usuario no está autenticado.

# 3. Detalles del Usuario (User Detail)
## Ruta
`GET /user/`
`PUT /user/`
`PATCH /user/`
`DELETE /user/`

## Descripción
Permite obtener, actualizar y eliminar los detalles del usuario autenticado.

## Datos solicitados
* GET: No requiere parámetros adicionales.

* PUT/PATCH: Los datos del usuario que se desean actualizar.
```
{
    "username": "nuevo_username",
    "password": "nueva_contraseña",
    "is_driver": "boolean",
    "plate": "string"
}
```
# Respuestas
* GET 200 OK: Detalles del usuario autenticado.
```
{
    "id": "UUID",
    "username": "string",
    "is_driver": "boolean",
    "plate": "string"
}
```
* PUT/PATCH 200 OK: Usuario actualizado correctamente.
```
{
    "id": "UUID",
    "username": "string",
    "is_driver": "boolean",
    "plate": "string"
}
```
* 400 Bad Request: Si los datos proporcionados no son válidos.

* 403 Forbidden: Si se intenta modificar los detalles de otro usuario.

* 204 No Content: El usuario ha sido eliminado correctamente.

# 4. Login (Autenticación y Generación de JWT)
## Ruta
`POST /login/`

## Descripción
Permite autenticar al usuario y obtener un token JWT.

## Datos solicitados
```
{
    "username": "string",
    "password": "string"
}
```
# Respuestas
* 200 OK: Usuario autenticado y token generado.
```
{
    "access_token": "string",
    "refresh_token": "string"
}
```
* 400 Bad Request: Si falta el nombre de usuario o la contraseña.

* 401 Unauthorized: Si las credenciales son inválidas.

# 5. Asignar Ubicación al Usuario (Location Assign)
## Ruta
`GET /locations/`
`POST /locations/`
`PUT /locations/{id}/`
`PATCH /locations/{id}/`
`DELETE /locations/{id}/`

## Descripción
Permite al usuario autenticado gestionar sus ubicaciones (obtener, crear, actualizar o eliminar).

## Datos solicitados
* GET: No requiere parámetros adicionales.

* POST: Los datos de la ubicación a asignar.
```
{
    "address": "string",
    "latitude": "float",
    "longitude": "float"
}
```
* PUT/PATCH: Los datos que se desean actualizar de la ubicación.
```
{
    "address": "string",
    "latitude": "float",
    "longitude": "float"
}
```
## Respuestas
* GET 200 OK: Lista de ubicaciones del usuario.
```
[
    {
        "id": "UUID",
        "address": "string",
        "latitude": "float",
        "longitude": "float"
    }
]
```
* POST 201 Created: Ubicación asignada correctamente.
```
{
    "id": "UUID",
    "address": "string",
    "latitude": "float",
    "longitude": "float"
}
```
* PUT/PATCH 200 OK: Ubicación actualizada correctamente.
```
{
    "id": "UUID",
    "address": "string",
    "latitude": "float",
    "longitude": "float"
}
```
* 404 Not Found: Si la ubicación no existe o no pertenece al usuario.

* 204 No Content: La ubicación ha sido eliminada correctamente.

# 6. Crear Solicitud de Servicio (Service Request Create)
## Ruta
`POST /service-request/`

## Descripción
Permite a un usuario no conductor crear una solicitud de servicio.

## Datos solicitados
No requiere parámetros adicionales.

## Respuestas
* 201 Created: Solicitud de servicio creada exitosamente.
```
{
    "driver": {
        "id": "UUID",
        "username": "string",
        "plate": "string"
    },
    "estimated_time_minutes": "int"
}
```
* 400 Bad Request: Si no se tiene una ubicación registrada o hay una solicitud existente.

* 403 Forbidden: Si un conductor intenta crear una solicitud de servicio.

* 404 Not Found: Si no se encuentran conductores disponibles.

# 7. Cerrar Solicitud de Servicio (Close Service Request)
## Ruta
`POST /service-request/close/`

## Descripción
Permite cerrar una solicitud de servicio activa.

## Datos solicitados
No requiere parámetros adicionales.

## Respuestas
* 200 OK: La solicitud de servicio ha sido cerrada.
```
{
    "id": "UUID",
    "close_service_at": "string (ISO 8601)"
}
```
* 404 Not Found: Si no hay solicitudes de servicio activas para el usuario.

# Resumen de Rutas:

|Método|	Ruta	|Descripción|
|-------|-----------|-----------|
|POST|	/register/	|Registrar un nuevo usuario|
|GET|	/drivers/	|Obtener todos los conductores|
|GET|	/user/	|Obtener los detalles del usuario autenticado|
|PUT|	/user/	|Actualizar los detalles del usuario autenticado|
|PATCH|	/user/	|Actualizar parcialmente los detalles del usuario|
|DELETE|	/user/	|Eliminar el usuario autenticado|
|POST|	/login/	|Autenticación y obtención de JWT|
|GET|	/locations/	|Obtener todas las ubicaciones del usuario|
|POST|	/locations/	|Asignar una nueva ubicación al usuario|
|PUT|	/locations/{id}/	|Actualizar una ubicación específica|
|PATCH|	/locations/{id}/	|Actualizar parcialmente una ubicación|
|DELETE|	/locations/{id}/	|Eliminar una ubicación específica|
|POST|	/service-request/	|Crear una solicitud de servicio|
|POST|	/service-request/close/	|Cerrar una solicitud de servicio activa|