#!/bin/bash

export PYTHONPATH=/app/delivery

# Wait until the database is ready.
./wait-for-it.sh db:5432 --timeout=60 --strict -- echo "PostgreSQL is up!"

# Performs the respective migrations of the application.
python delivery/manage.py makemigrations
python delivery/manage.py migrate
python delivery/manage.py generate_fake_data

# Run the service.
exec gunicorn delivery.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Run tests.
# python delivery/manage.py test services
