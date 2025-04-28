# Despliegue

Para realizar el despliegue se debe descargar el repositorio por medio de git Bach con el siguiente comando (o con la herramienta de su gusto):

```
git clone https://github.com/camiloleuroc/domicilios.git
```

Una vez descargado el repositorio se ingresa a la carpeta domicilios y allí encontrarán 2 archivos los cuales pueden modificarse según corresponda:

* **.env**: Archivo con las variables de conexión de la base de datos los cuales pueden modificar para cambiar las credenciales de acceso a la base de datos (se recomienda no modificar el host y el puerto a menos que sea necesario)
```
POSTGRES_DB=deliverydb
POSTGRES_USER=admdbdlvry
POSTGRES_PASSWORD=PQowie_102938
```

* **entrypoint.sh**: archivo encargado de realizar las migraciones, generar los datos de prueba de los conductores y ejecutar el aplicativo o realizar la ejecución de las pruebas.
Si se desea ejecutar el aplicativo no se modifica nada en el archivo, pero si se desea ejecutar las pruebas, ingresan al archivo y comentan la línea del ‘Run the service’ y descomentan la de ‘Run test’ :
```
# Run the service.
# exec gunicorn delivery.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Run tests.
python delivery/manage.py test services
```

Por medio de una terminal de su elección se ejecuta el siguiente comando de docker dentro del directorio para levantar el servicio (verificar que se cuenta con docker instalado y en ejecución):
```
docker compose up –d --build
```

Este se encargará de crear las imágenes tanto de la base de datos como de la API y levantar los contenedores.

# ----------------------------------------------------------------

# Primeros pasos

Lo primero que se debe realizar es la creación de un usuario no conductor el cual se realiza con el endpoint ‘POST /register/‘ el cual se encuentra especificado más abajo en la documentación de la API junto con los demás mencionados a continuación. Después de registrado el usuario, se debe de consumir el endpoint de ‘POST /login/’ el cual retorna el ‘access_token’ con el cual se permitirá registrar ubicaciones para el usuario y crear un servicio.

Una vez se tenga el ‘access_token’ este se utilizará para crear la ubicación para el usuario utilizando el endpoint ‘POST /locations/’. Después de crear la ubicación para el usuario ya se puede hacer la creación de un servicio con el endpoint ‘POST /service-request/’ en el cual se buscará el conductor más cercano y será asignado para el domicilio.

Solo los usuarios que no son conductores pueden solicitar un domicilio y una vez asignado no podrá solicitar otro hasta que no haya finalizado el o el conductor el servicio con el endpoint `POST /endservice/`. Al igual al conductor no se le asigna otro servicio hasta que no finalice el que tiene.

# ----------------------------------------------------------------

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

## Requiere autorización 
```Authorization: Bearer <access_token>```

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
`GET /users/me/`
`PUT /users/me/`
`PATCH /users/me/`
`DELETE /users/me/`

## Requiere autorización 
```Authorization: Bearer <access_token>```

## Descripción
Permite obtener, actualizar y eliminar los detalles del usuario autenticado.

## Datos solicitados
* GET: No requiere parámetros adicionales.

* PUT/PATCH: Los datos del usuario que se desean actualizar.
```
{
    "username": "nuevo_username",(obligatorio)
    "password": "nueva_contraseña",(obligatorio)
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

## Requiere autorización 
```Authorization: Bearer <access_token>```

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
`POST /delivery/`

## Requiere autorización 
```Authorization: Bearer <access_token>```

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
`POST /endservice/`

## Requiere autorización 
```Authorization: Bearer <access_token>```

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
|GET|	/user/me/	|Obtener los detalles del usuario autenticado|
|PUT|	/user/me/	|Actualizar los detalles del usuario autenticado|
|PATCH|	/user/me/	|Actualizar parcialmente los detalles del usuario|
|DELETE|	/user/me/	|Eliminar el usuario autenticado|
|POST|	/login/	|Autenticación y obtención de JWT|
|GET|	/locations/	|Obtener todas las ubicaciones del usuario|
|POST|	/locations/	|Asignar una nueva ubicación al usuario|
|PUT|	/locations/{id}/	|Actualizar una ubicación específica|
|PATCH|	/locations/{id}/	|Actualizar parcialmente una ubicación|
|DELETE|	/locations/{id}/	|Eliminar una ubicación específica|
|POST|	/delivery/	|Crear una solicitud de servicio|
|POST|	/endservice/	|Cerrar una solicitud de servicio activa|

# ----------------------------------------------------------------

# Recomendaciones para despliegue de servicio en AWS:

## Recomendación para ejecución de la API incluyendo el contenedor de base de datos en el mismo servidor.

### Servicios:
* **Amazon EC2**
* **Elastic IP** 
* **Security Groups**
* **IAM Roles**
* **Route 53 (opcional para dominio)**

### Como realizar el despliegue:

1.	Construir la imagen Docker y cargarla en Docker Hub o Amazon ECR.
2.	Creas una instancia EC2 (la capacidad de la maquina depende de la cantidad de peticiones que se vayan a tener) en una VPC privada.
3.	Configurar Docker y lo necesario en EC2, hacer un pull con docker en el servidor y levantar los contenedores mapeando los puertos que se vayan a utilizar.
4.	Configuras Security Groups para permitir tráfico en lo posible HTTPS (puerto 443) para seguridad y permitir acceso solo interno para la base de datos si fuera expuesta (no se recomienda exponerla).
5.	Configurar un Elastic IP para una IP estática o un balanceador si se tiene contemplada mucha concurrencia.
6.	Configurar backups del EC2 automáticos vía snapshot.
Esta es una forma para el despliegue lo cual permite levantar los contenedores de manera fácil, tiene un costo más bajo al no usar servicios adicionales y se tiene control completo sobre el servidor.
Para la escalabilidad de este modelo se requiere replicar las instancias y realizar procesos extra para la sincronización de los datos.

### Recomendaciones adicionales de seguridad:
-	Nunca exponer puertos en internet que permitan accesos indebidos al sistema, como el puerto de la base de datos.
-	Actualizar el sistema operativo y los paquetes para mantener los últimos parches de seguridad.
-	Usar claves SSH para acceso y no contraseñas, adicional de no realizar accesos por el puerto 22 si no por otro.

## Recomendación para ejecución de la API separando la base de datos a una RDS.

### Servicios:
* **Amazon ECS (Elastic Container Service)**
* **Amazon RDS (PostgreSQL)**
* **Elastic Load Balancer (opcional, para balanceo)**
* **Security Groups**
* **IAM Roles**
* **CloudWatch (para logs/monitoreo)**
* **Secrets Manager (opcional para guardar contraseñas de la DB)**
* **Route 53 (opcional para dominio)**

### Como realizar el despliegue:
1.	Construir la imagen Docker y cargarla a Amazon ECR (Elastic Container Registry).
2.	Levantar la API en ECS usando Fargate.
3.	Definir una Task Definition con los detalles del contenedor.
4.	Crear una base de datos RDS PostgreSQL.
5.	Habilitar los backups automáticos y según los recursos que sean Multi-AZ para alta disponibilidad.
6.	Usar Security Groups para restringir acceso solo al servicio ECS.
7.	Configurar Secret Manager para manejar las credenciales de conexión a RDS (y no ponerlas en el código).
8.	Configurar autoescalado en ECS basado en CPU/RAM si se espera tráfico variable.
9.	Monitoreas con CloudWatch los logs y métricas.

De esta forma tanto la API como la base de datos se pueden actualizar y escalar independiente, adicional a ello se cuenta con alta disponibilidad de la base de datos al tener replicas automáticas y failover configurado para control de fallos. Todo lo anterior es pago por uso y AWS es el encargado de mantener los parches actualizados.

Se debe considerar que es más costoso que la primera opción, pero mucho más resiliente y seguro.

### Recomendaciones adicionales de seguridad:
-	Nunca exponer la base de datos públicamente.
