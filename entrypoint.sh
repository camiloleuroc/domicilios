#!/bin/bash

export PYTHONPATH=/app/delivery

# Espera a a que la base de datos esté lista
./wait-for-it.sh db:5432 --timeout=60 --strict -- echo "PostgreSQL is up!"

# Realiza las migraciones respectivas del aplicativo
python delivery/manage.py makemigrations
python delivery/manage.py migrate

# Ejecuta el servicio
exec gunicorn delivery.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000