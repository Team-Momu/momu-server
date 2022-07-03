#!/bin/sh

echo "Collect Static Files"
python manage.py collectstatic --no-input

echo "Migration"
python manage.py migrate

exec "$@"